"""
This module converts PDFs to text.
"""


# inbuilt or third party libs
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.layout import LAParams, LTTextBox, LTTextLine
from pdfminer.converter import PDFPageAggregator
import logging
from typing import Union

# project modules
from modules.misc import extracted_text_path_gen
from locations import dirs


def convert_pdf_to_text(pdf_path: Union[object, str], docketnum: str) -> str:

    """ Takes path (or pathlib Path object) to a PDF file, docketnum and
    returns text inside PDF"""

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

    # Create a device object which translates interpreted information into desired format
    # Device needs to be connected to resource manager to store shared resources
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
    logging.info("Text extracted successfully")
    return extracted_text
