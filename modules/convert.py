"""
This module converts PDFs to text and then extracts important docket info from that text.

"""


# inbuilt or third party libs
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.layout import LAParams, LTTextBox, LTTextLine
from pdfminer.converter import PDFPageAggregator
import re
import logging

# project modules
from modules.misc import extracted_text_path_gen
from locations import dirs


def convert_pdf_to_text(pdf_path, docketnum):

    # SET PATHS
    extracted_text_path = extracted_text_path_gen(dirs["extracted_text"], docketnum)

    logging.info(f"Converting pdf to text for docket {docketnum}...")
    password = ""
    extracted_text = ""

    # Open and read the pdf file in binary mode
    fp = open(pdf_path, "rb")

    # Create parser object to parse the pdf content
    parser = PDFParser(fp)

    # Store the parsed content in PDFDocument object
    try:
        document = PDFDocument(parser, password)
    except Exception as e:
        logging.error("Something went wrong during conversion")
        logging.exception(e)
        logging.info("Returning no extracted text for docket {}".format(docketnum))
        return extracted_text

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

    with open(extracted_text_path, "wb") as fout:
        fout.write(extracted_text.encode("utf-8"))
    logging.info("Text extracted succesfully")
    return extracted_text


def parse_extracted_text(text):

    """
    Parse texted from PDFs using regex.

    :param text: Text to search
    :return: dictionary with desired values
    """

    # parsing text file for charges
    try:
        logging.info("Attempting to extract charges from text with Regex...")
        pattern = re.compile(
            r"(Grade Description\n)((F|F1|F2|F3|M|M1|M2|M3|S)?\n)*(.*?)(\nOffense Dt|\nCHARGES|\nDISPOSITION|\nDisposition|\nFiled Date)",
            re.DOTALL,
        )
        match = pattern.search(text)
        charges = match.group(4)
        logging.info("Charges found:")
        logging.info(charges)
        charges = charges.replace(
            "\n", "; "
        )  # Replacing newline characters so easier to display data in tabular format
        charges = charges[0:400]  # Limit size of captured text
    except AttributeError as e:
        logging.error("Error: Something went wrong with charges parsing")
        logging.exception(e)
        charges = None

    # parsing text file for bail
    try:
        logging.info("Attempting to extract bail from text with Regex...")
        pattern = re.compile(r"(Amount\n)\$(.*)\.00", re.DOTALL)
        match = pattern.search(text)
        bail = match.group(2)
        logging.info(f"Bail: {bail}")
        # Removing newline characters
        bail = bail[0:15]
        bail = bail.replace("\n", "").replace(",", "")
    except (AttributeError, ValueError) as e:
        logging.error("Something went wrong with bail parsing for that docket")
        logging.exception(e)
        bail = None

    return {"charges": charges, "bail": bail}
