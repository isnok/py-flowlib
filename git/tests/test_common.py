# -*- coding: utf-8 -*-
import os
import pytest

from os.path import dirname

from flowtool_git import common


def test_check_git(fresh_repo):
    assert not common.check_git(fresh_repo.git_dir)
    assert common.check_git(dirname(fresh_repo.git_dir))
    assert not common.check_git('/mclkav/ncaönrv/cna')


def test_local_repo(nogit, fresh_repo, capsys):

    assert common.local_repo(nogit, or_exit=False) is None

    with pytest.raises(SystemExit) as exc_info:
        common.local_repo(nogit)
    assert exc_info.value.code == 1
    out, err = capsys.readouterr()
    assert 'not under git version control' in out

    assert fresh_repo is common.local_repo(fresh_repo)

    assert fresh_repo.git_dir == common.local_repo(fresh_repo.git_dir).git_dir
    assert fresh_repo.git_dir == common.local_repo(dirname(fresh_repo.git_dir)).git_dir


from flowtool.files import append_to_file

def test_short_status(fresh_repo):

    assert not common.short_status(path=fresh_repo)

    test_file = os.path.join(
        dirname(fresh_repo.git_dir),
        'dirty_file.txt'
    )
    append_to_file(test_file, 'YAFM!')
    fresh_repo.git.add('dirty_file.txt')

    assert common.short_status(path=fresh_repo)
