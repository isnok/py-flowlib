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
    found_dir = files.find_parent_containing('.', check='dir')
    assert found == found_dir

    my_top = basename(my_dir)
    found = files.find_parent_containing(my_top, path=my_dir, check=isdir)
    assert found == dirname(my_dir)

    my_top = basename(my_dir)
    found = files.find_parent_containing(my_top, check=isdir, not_found='-_-')
    assert found == '-_-'


def test_find_subdirs_containing():

    found1 = files.find_subdirs_containing('.', check='isdir')
    found2 = files.find_subdirs_containing('.')
    assert found1 == found2

    found = files.find_subdirs_containing(my_name, my_dir, check='isfile')
    assert len(found) >= 1

    found1 = files.find_subdirs_containing(my_name, my_dir, check='isfile')
    found2 = files.find_subdirs_containing(my_name, my_dir)
    assert len(found1) <= len(found2)


def test_check_file():

    assert files.check_file(__file__, 'check_file')
    assert not files.check_file(__file__, '_'.join(['random', 'pattern']))
    assert not files.check_file('/_not_/_here_/_not_/_there_', 'pattern')


def test_append_file():
    assert files.append_to_file('/dev/null', '100 thousand bytes')


def test_cached_reads():

    cached = files._read_cache(__file__)
    assert len(cached) > 10
    assert len(files._read_cache(__file__)) > 10
    assert files._read_cache(__file__) is cached

    assert files.cached_read(__file__).split('\n') == cached

    assert files.cached_readlines(__file__) == cached[:-1]

    test_file = '/tmp/no_final_newline'
    files.append_to_file(test_file, 'Har!')
    assert files.cached_read(test_file)
    os.unlink(test_file)


def test_executables():

    assert not files.is_executable(__file__)

    with pytest.raises(OSError) as exc_info:
        files.is_executable('/never/to/b/fount')

    test_file = '/tmp/exec_test.foo'
    files.append_to_file(test_file, 'Some content.\n')
    files.make_not_executable(test_file)
    assert not files.is_executable(test_file)

    files.make_executable(test_file)
    assert files.is_executable(test_file)

    files.toggle_executable(test_file)
    assert not files.is_executable(test_file)

    files.toggle_executable(test_file)
    assert files.is_executable(test_file)

    os.unlink(test_file)


def test_cd():

    oldpwd = os.getcwd()
    with files.cd('/tmp/'):
        cwd = os.getcwd()
        assert cwd != oldpwd
    assert cwd.startswith('/tmp')
    assert oldpwd == os.getcwd()


def test_topdirs():

    result = list(files.topdirs('/foo/bar/baz'))
    assert result == ['/foo/bar/baz', '/foo/bar', '/foo', '/']
