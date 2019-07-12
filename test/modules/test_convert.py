import unittest
from unittest import mock
from shutil import rmtree
from pathlib import Path

# fixtures
from locations import test_paths, test_dirs

# modules to test
from modules.convert import convert_pdf_to_text

mock_dirs = {
    "pdfs": Path("../fixtures/pdfs/"),
    "extracted_text": Path("../output/extracted_text/"),
}

class TestConvertPdfToText(unittest.TestCase):

    def setUp(self) -> None:
        # create directory
        mock_dirs["extracted_text"].mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        rmtree(mock_dirs["extracted_text"])


    @mock.patch.dict(test_dirs, mock_dirs, clear=True)
    def test_text_file_is_generated(self):
        """
        Test that a text file is generated
        """
        docketnum = "MJ-19301-CR-0000267-2019"
        pdf_path = mock_dirs['pdfs'] / (docketnum + ".pdf")

        # convert pdf to text
        convert_pdf_to_text(pdf_path, docketnum)
        expected_path = mock_dirs["extracted_text"] / (docketnum + ".txt")
        # assert
        self.assertTrue(expected_path.is_file())



if __name__ == "__main__":
    unittest.main()
