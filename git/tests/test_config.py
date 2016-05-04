import os
import pytest

from flowtool_git import config


def test_list_config():
    local_config = config.list_config(local=True)
    full_config = config.list_config()

    assert len(local_config) <= len(full_config)

    local_config = local_config.split('\n')
    full_config = full_config.split('\n')

    assert len(local_config) <= len(full_config)


def test_getconfig_simple():

    local_config = config.getconfig_simple(local=True)
    full_config = config.getconfig_simple()

    assert len(local_config) <= len(full_config)

    for key, value in local_config.items():
        assert key in full_config
        assert value == full_config[key]
