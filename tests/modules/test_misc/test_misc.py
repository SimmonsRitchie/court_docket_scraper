import unittest
from pathlib import Path
from shutil import rmtree

# import fixtures
from tests.fixtures.dict_list.docket_list_with_duplicates import docket_list

# modules to test
from modules.misc import pdf_path_gen, clean_list_of_dicts, create_folders


class TestPdfPathGen(unittest.TestCase):
    def setUp(self) -> None:
        self.docket1 = "1969-12-30,MJ-12101-CR-0000441-2019"
        self.docket2 = "1969-12-30,MJ-12102-CR-0000442-2019"
        self.docketnum_list = [self.docket1, self.docket1, self.docket2, self.docket1]
        self.dir = Path("../../output_files/pdfs/")
        self.dir.mkdir(parents=True)

    def tearDown(self) -> None:
        rmtree(self.dir)

    def test_generate_unique_pdf_names(self):
        """
        Test that we create unique PDF names when there are existing filenames in a directory.
        """
        pdf_paths = []
        desired_output = [
            self.dir / f"{self.docket1}.pdf",
            self.dir / f"{self.docket1}_1.pdf",
            self.dir / f"{self.docket2}.pdf",
            self.dir / f"{self.docket1}_2.pdf",
        ]
        for docketnum in self.docketnum_list:
            path = pdf_path_gen(self.dir, docketnum)
            with open(path, "w") as fout:
                fout.write("DUMMY DATA")
            pdf_paths.append(path)
        self.assertEqual(pdf_paths, desired_output)
        print(pdf_paths)


class TestCleanList(unittest.TestCase):
    def test_duplicates_are_removed(self):
        """
        Test that duplicate dicts in list are removed
        """
        expected_list = docket_list[2:]
        test_list = clean_list_of_dicts(docket_list)
        self.assertEqual(expected_list, test_list)
        print(test_list)

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
        print(test_list)
        self.assertFalse(test_list)


class TestCreateFolders(unittest.TestCase):
    def setUp(self) -> None:
        self.output_dir = Path("../../output/create_folders/")
        self.list_of_subdirs_to_create = [
            self.output_dir / "test1",
            self.output_dir / "test2",
            self.output_dir / "test3",
        ]

    def tearDown(self) -> None:
        rmtree(self.output_dir)

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
