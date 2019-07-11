
from unittest import mock
from modules.simple import names, subjects
from modules.simple2 import print_names_in_imported_dict
from mock_locations import mock_names, mock_subjects

# print_names_in_imported_dict()


# with mock.patch.dict(names, mock_names, clear=True):
#     print_names_in_imported_dict()


@mock.patch.dict(names, mock_names, clear=True)
@mock.patch.dict(subjects, {'path': 'go '}, clear=True)
def test():
    print_names_in_imported_dict()

test()