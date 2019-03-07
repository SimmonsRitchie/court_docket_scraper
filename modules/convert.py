"""
This module converts PDFs to text and then extracts important docket info from that text

"""


# load PDF miner imports
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.layout import LAParams, LTTextBox, LTTextLine
from pdfminer.converter import PDFPageAggregator

# Other modules
import re
from collections import namedtuple

# My modules
from modules import misc

# Collections
ParsedData = namedtuple("ParsedData", ('charge','bail'))




def convert_pdf_to_text(docket_num, base_folder_pdfs, base_folder_text):
    print("Converting pdf to text...")
    pdf_path = misc.pdf_path_generator(base_folder_pdfs, docket_num)
    extracted_text_path = misc.extracted_text_path_generator(base_folder_text, docket_num)

    password = ""
    extracted_text = ""

    # Open and read the pdf file in binary mode
    fp = open(pdf_path, "rb")

    # Create parser object to parse the pdf content
    parser = PDFParser(fp)

    # Store the parsed content in PDFDocument object
    document = PDFDocument(parser, password)

    # Check if document is extractable, if not abort
    if not document.is_extractable:
        raise PDFTextExtractionNotAllowed

    # Create PDFResourceManager object that stores shared resources such as fonts or images
    rsrcmgr = PDFResourceManager()

    # set parameters for analysis
    laparams = LAParams()

    # Create a PDFDevice object which translates interpreted information into desired format
    # Device needs to be connected to resource manager to store shared resources
    # device = PDFDevice(rsrcmgr)
    # Extract the decive to page aggregator to get LT object elements
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)

    # Create interpreter object to process page content from PDFDocument
    # Interpreter needs to be connected to resource manager for shared resources and device
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    # Ok now that we have everything to process a pdf document, lets process it page by page
    for page in PDFPage.create_pages(document):
        # As the interpreter processes the page stored in PDFDocument object
        interpreter.process_page(page)
        # The device renders the layout from interpreter
        layout = device.get_result()
        # Out of the many LT objects within layout, we are interested in LTTextBox and LTTextLine
        for lt_obj in layout:
            if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
                extracted_text += lt_obj.get_text()
    # close the pdf file
    fp.close()

    # print (extracted_text.encode("utf-8"))
    # This commented line formerly saved the file. It's no longer necessary
    with open(extracted_text_path, "wb") as fout:
        fout.write(extracted_text.encode("utf-8"))
    print("Text extracted succesfully")
    return extracted_text


def parse_extracted_text(text):
        try:
            print("Attempting to extract charges from text with Regex...")
            pattern = re.compile(
                r'(Grade Description\n)((F|F1|F2|F3|M|M1|M2|M3|S)?\n)*(.*?)(\nOffense Dt|\nCHARGES|\nDISPOSITION|\nDisposition|\nFiled Date)',
                re.DOTALL)
            match = pattern.search(text)
            charges = match.group(4)
            print("Charges found:")
            print()
            print(charges)
            print()
            #Replacing newline characters
            charges = charges.replace("\n", "; ")
            charges = charges[0:100]
        except AttributeError:
            print("Error: Something went wrong with charge parsing for that docket")
            charges = "None found (check docket)"
        try:
            print("Attempting to extract bail from text with Regex...")
            pattern = re.compile(r'(Amount\n)\$(.*)\.00', re.DOTALL)
            match = pattern.search(text)
            bail = match.group(2)
            print("Bail found:")
            print()
            print(bail)
            print()
            # Removing newline characters
            bail = bail[0:15]
            bail = bail.replace("\n", "").replace(",", "")
        except AttributeError:
            print("Error: None found or something went wrong with bail parsing for that docket")
            bail = "None found"
        except ValueError:
            print("Error: None found or something went wrong with bail parsing for that docket")
            bail = "None found"
        return ParsedData(charges,bail)
