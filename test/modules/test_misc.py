import unittest
from pathlib import Path
from shutil import rmtree

# modules to test
from modules.misc import pdf_path_gen

class TestMisc(unittest.TestCase):
    def setUp(self) -> None:
        self.docket1 = "1969-12-30,MJ-12101-CR-0000441-2019"
        self.docket2 = "1969-12-30,MJ-12102-CR-0000442-2019"
        self.docketnum_list = [self.docket1, self.docket1, self.docket2, self.docket1]
        self.dir = Path("../output_files/pdfs/")
        self.dir.mkdir(parents=True)

    def tearDown(self) -> None:
        rmtree(self.dir)

    def test_generate_unique_pdf_names(self):
        """
        Test that we create unique PDF names when there are existing filenames in a directory.
        """
        pdf_paths = []
        desired_output = [self.dir / f"{self.docket1}.pdf",
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


if __name__ == "__main__":
    unittest.main()
