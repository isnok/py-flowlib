import os
import pytest

from flowtool import files

from os.path import isdir, dirname, basename

my_name, my_dir = basename(__file__), dirname(__file__)

def test_find_parent_containing():

    found = files.find_parent_containing('.', check='isdir')
    assert isdir(found)

    found = files.find_parent_containing(my_name, my_dir, check='isfile')
    assert found == my_dir

    found = files.find_parent_containing('.')
    found_dir = files.find_parent_containing('.', check='isdir')
    assert found == found_dir
