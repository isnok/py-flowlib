""" This file will be copied as a static drop-in into your source tree.
    This is the version of this file, that resides in the git repository.

    Inspired by https://github.com/warner/python-versioneer, this file can
    also be a template, if you see markers like @MARKER@ in the dict below.
"""

template = '''"""
    This file was generated by flowtool-versioning.
"""

VERSION_INFO = {}

def get_version():
    global VERSION_INFO
    return VERSION_INFO.get('version', 'no_version')
'''

exec(template)

from pprint import pformat

def render_template():
    global VERSION_INFO
    return template.format(pformat(VERSION_INFO))

import os
from os.path import join, dirname, isfile
import configparser

def get_setup_cfg():
    """ Return the nearest directory in the parent dirs,
        that contains a setup.cfg, or None if no such
        parent dir exists.
    """

    current = os.getcwd()

    while not isfile(join(current, 'setup.cfg')):
        old = current
        current = dirname(current)
        if old == current:
            # if current == dirname(current)
            # then we cant ascend any further
            return None
    else:
        # loop was left without a break,
        # so there was a file with the name
        parser = configparser.ConfigParser()
        parser.read(join(current, 'setup.cfg'))
        return parser

setup_cfg = get_setup_cfg()


import subprocess
def get_stdout(*command):
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE
    )
    stdout, stderr = process.communicate()
    return stdout.decode('utf-8')

#prefixed = [tag for tag in tags if tag.startswith(prefix)]
#print('--> %s' % prefixed)


import re
import sys

pep440_regex = re.compile('((?P<epoch>[0-9]*)!)?(?P<release>[0-9][0-9]*(\.[0-9][0-9]*)*)\.?((?P<pre_stage>a|b|rc)?(?P<pre_ver>[0-9]*))((\.post(?P<post>[0-9]*)))?((\.dev(?P<dev>[0-9]*)))?')

def parse_pep440(version_string):
    """ PEP440 versions look like this:

        [N!]N(.N)*[{a|b|rc}N][.postN][.devN]

        Epoch segment: N!
        Release segment: N(.N)*
        Pre-release segment: {a|b|rc}N
        Post-release segment: .postN
        Development release segment: .devN
    """

    PYTHON3 = sys.version_info[0] == 3
    if PYTHON3:
        match = pep440_regex.fullmatch(version_string)
    else:
        match = pep440_regex.match(version_string)
    if match is None:
        return None

    parsed = match.group
    result = dict(
        version=version_string,
    )
    release = parsed('release')
    result.update(
        release=tuple(int(v) for v in release.split('.')),
    )

    if parsed('pre_stage'):
        pre_ver = 0 if not parsed('pre_ver') else int(parsed('pre_ver'))
        result['pre_release'] = (parsed('pre_stage'), pre_ver)

    if parsed('post'):
        result['post_release'] = 0 if not parsed('post') else int(parsed('post'))

    if parsed('dev'):
        result['dev_release'] = 0 if not parsed('dev') else int(parsed('dev'))

    if parsed('epoch'):
        result['epoch'] = parsed('epoch')

    result['normalized'] = normalize_pep440(**result)

    return result


def normalize_pep440(**kwd):
    normalized = '.'.join(map(str, kwd['release']))
    if 'pre_release' in kwd:
        normalized += '%s%s' % kwd['pre_release']
    if 'post_release' in kwd:
        normalized += '.post' + str(kwd['post_release'])
    if 'dev_release' in kwd:
        normalized += '.dev' + str(kwd['dev_release'])
    if 'epoch' in kwd:
        normalized = '{}!{}'.format(kwd['epoch'], normalized)
    return normalized


#parsed = [parse_pep440(tag[len(prefix):]) for tag in prefixed]
#print(parsed)

def get_commit(identifier):
    return get_stdout('git', 'rev-parse', identifier).strip()


def commit_distance(a, b):
    rng = '%s...%s' % (a, b)
    return int(get_stdout('git', 'rev-list', '--count', rng))


def git_tags():
    return get_stdout('git', 'tag', '--list').split()

def git_is_dirty():
    return get_stdout('git', 'status', '--short', '--untracked-files=no')

def get_tags_matching(prefix=''):
    tags = git_tags()
    distances = {
        tag: commit_distance('HEAD', tag)
        for tag in tags if tag.startswith(prefix)
    }
    return distances


def get_nearest_tag(distances):
    return sorted(distances, key=distances.__getitem__)[0]

def gather_vcs_info(tag, prefix):
    vcs_info = dict(
        latest_tag=tag,
        latest_tag_version=tag[len(prefix):],
        latest_tag_commit=get_commit(tag),
        commit=get_commit('HEAD'),
        dirt=git_is_dirty(),
    )
    return vcs_info

def assemble_vcs_version(info, distances):
    vcs_version = info['latest_tag_version']
    tag = info['latest_tag']
    distance = distances[tag]
    if distance:
        commit = info['latest_tag_commit'][:8]
        vcs_version += '+%s.git:%s' % (distance, commit)

    if git_is_dirty():
        vcs_version += '.dirty'

    return vcs_version

prefix = setup_cfg.get('versioning', 'tag_prefix')

distances = get_tags_matching(prefix)
latest_tag = get_nearest_tag(distances)

vcs_info = gather_vcs_info(latest_tag, prefix)

VERSION_INFO.update(
    vcs_version=assemble_vcs_version(vcs_info, distances),
    vcs_info=vcs_info,
    tag_version=parse_pep440(vcs_info['latest_tag_version']),
)

def assemble_version(version_info):
    """ Assemble the version from the now available, relevant information. """
    # kiss-scheme: just use the tag-version, but add -SNAPSHOT if git is dirty
    version = version_info['tag_version']['version']
    if version_info['vcs_info']['dirt']:
        version += '-SNAPSHOT'
    return version

VERSION_INFO['version'] = assemble_version(VERSION_INFO)

print(VERSION_INFO)

print(render_template())
