import unittest
from unittest import mock
from shutil import rmtree

# project modules
from locations import dirs, root_dir, test_dir
from modules.convert import convert_pdf_to_text

mock_dirs = {
    'pdfs': test_dir / 'fixtures/pdfs/',
    'extracted_text': test_dir / 'fixtures/extracted_text/'
}


class TestConvertPdfToText(unittest.TestCase):
    def setUp(self) -> None:
        rmtree(mock_dirs["extracted_text"])
        # create directory
        mock_dirs["extracted_text"].mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        pass

    @mock.patch.dict(dirs, mock_dirs, clear=True)
    def test_text_file_is_generated(self):
        """
        Test that a text file is generated
        """
        # set vars
        docketnum = "MJ-19301-CR-0000267-2019"
        pdf_path = mock_dirs["pdfs"] / (docketnum + ".pdf")
        expected_path = mock_dirs["extracted_text"] / (docketnum + ".txt")
        # convert pdf to text
        convert_pdf_to_text(pdf_path, docketnum)
        # assert
        self.assertTrue(expected_path.is_file())


if __name__ == "__main__":
    unittest.main()
