import unittest
from pathlib import Path
from shutil import rmtree
import dotenv

# project modules
from tests.fixtures.dict_list.docket_list_with_duplicates import docket_list
from modules.misc import pdf_path_gen, clean_list_of_dicts, create_folders
from logs.config.logging import logs_config
from locations import paths, root_dir, test_dir

# LOGGING
logs_config(paths["logs_config_test"])

# ENV VARS
dotenv.load_dotenv(root_dir / ".dev.env")

# MOCK DIRS
mock_dir = {
    "pdfs": test_dir / "output/pdfs/",
    "create_dirs": test_dir / "output/create_dirs/"

}

class TestPdfPathGen(unittest.TestCase):
    def setUp(self) -> None:
        if mock_dir["pdfs"].is_dir():
            rmtree(mock_dir["pdfs"])
        mock_dir["pdfs"].mkdir(exist_ok=True, parents=True)


    def tearDown(self) -> None:
        pass

    def test_generate_unique_pdf_names(self):
        """
        Test that we create unique PDF names when there are existing filenames in a directory.
        """
        # input vars
        docket1 = "1969-12-30,MJ-12101-CR-0000441-2019"
        docket2 = "1969-12-30,MJ-12102-CR-0000442-2019"
        docketnum_list = [docket1, docket1, docket2, docket1]

        # expected
        desired_output = [
            mock_dir["pdfs"] / f"{docket1}.pdf",
            mock_dir["pdfs"] / f"{docket1}_1.pdf",
            mock_dir["pdfs"] / f"{docket2}.pdf",
            mock_dir["pdfs"] / f"{docket1}_2.pdf",
        ]

        # test
        pdf_paths = []
        for docketnum in docketnum_list:
            path = pdf_path_gen(mock_dir["pdfs"], docketnum)
            with open(path, "w") as fout:
                fout.write("DUMMY DATA")
            pdf_paths.append(path)

        # assert
        self.assertEqual(pdf_paths, desired_output)


class TestCleanList(unittest.TestCase):
    def test_duplicates_are_removed(self):
        """
        Test that duplicate dicts in list are removed
        """
        expected_list = docket_list[2:]
        test_list = clean_list_of_dicts(docket_list)
        self.assertEqual(expected_list, test_list)

    def test_no_duplicates_in_results(self):
        """
        Test that duplicate results are NOT in final results
        """
        expected_list = docket_list
        test_list = clean_list_of_dicts(docket_list)
        self.assertNotEqual(expected_list, test_list)

    def test_handles_empty_list(self):
        empty_list = []
        test_list = clean_list_of_dicts(empty_list)
        self.assertFalse(test_list)


class TestCreateFolders(unittest.TestCase):
    def setUp(self) -> None:
        if mock_dir["create_dirs"].is_dir():
            rmtree(mock_dir["create_dirs"])
        mock_dir["create_dirs"].mkdir()
        self.output_dir = mock_dir["create_dirs"]
        self.list_of_subdirs_to_create = [
            self.output_dir / "test1",
            self.output_dir / "test2",
            self.output_dir / "test3",
        ]

    def tearDown(self) -> None:
        pass

    def test_directories_are_created(self):
        # create
        create_folders(self.list_of_subdirs_to_create)
        # assert
        list_of_dirs_created = [
            subdir for subdir in self.output_dir.iterdir() if subdir.is_dir()
        ]
        print("to create", self.list_of_subdirs_to_create)
        print("created", list_of_dirs_created)
        self.assertCountEqual(list_of_dirs_created, self.list_of_subdirs_to_create)


if __name__ == "__main__":
    unittest.main()
