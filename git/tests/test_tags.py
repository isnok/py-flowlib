import os
import pytest

from flowtool_git import tags

from itertools import product

tag_prefixes = ['a/', 'b/', 'c/']
tag_suffixes = ['12', '34', '56']

@pytest.fixture
def tagged_repo(fresh_repo):
    for pref, suff in product(tag_prefixes, tag_suffixes):
        fresh_repo.git.tag(pref + suff)
    return fresh_repo

def test_local_tags(tagged_repo):
    taglist = tags.local_tags(path=tagged_repo)
    assert len(taglist) == 3 * 3
    taglist = tags.local_tags('a', path=tagged_repo)
    assert len(taglist) == 1 * 3
    taglist = tags.local_tags('c/', path=tagged_repo)
    assert len(taglist) == 1 * 3

def test_delete_local_tags(tagged_repo):
    tags.delete_local_tags(path=tagged_repo)

    taglist = tags.local_tags(path=tagged_repo)
    assert len(taglist) == 3*3

    tags.delete_local_tags(['a/12', 'b/34', 'c/56'], path=tagged_repo)

    taglist = tags.local_tags(path=tagged_repo)
    assert len(taglist) == 2*3
