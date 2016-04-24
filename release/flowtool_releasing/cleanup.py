""" Tag cleanup for the auto release mechanism.

    >>> from click.testing import CliRunner
    >>> runner = CliRunner()
    >>> result = runner.invoke(local_tag_cleanup, ('--yes', '--all'))
    >>> result.output.startswith('setup.cfg from /')
    True
    >>> result = runner.invoke(local_tag_cleanup, ('--yes', '--all', '--', '-10'))
    >>> result.exit_code
    1
    >>> result = runner.invoke(local_tag_cleanup, ('--noop', '--yes', '--all', '0'))
"""

import os
import re
import sys
import click
from flowtool.ui import abort
from flowtool.style import colors, echo
from flowtool.files import find_parent_containing
from flowtool.files import find_subdirs_containing
from flowtool.python import get_configparser
from flowtool_git.common import local_repo
from flowtool_git.tags import local_tags, delete_local_tags

pep440_regex = re.compile('((?P<epoch>[0-9]*)!)?(?P<release>[0-9][0-9]*(\.[0-9][0-9]*)*)\.?((?P<pre_stage>a|b|rc)?(?P<pre_ver>[0-9]*))((\.post(?P<post>[0-9]*)))?((\.dev(?P<dev>[0-9]*)))?')

def parse_pep440(version_string):
    """ PEP440 versions look like this:

        [N!]N(.N)*[{a|b|rc}N][.postN][.devN]

        Epoch segment: N!
        Release segment: N(.N)*
        Pre-release segment: {a|b|rc}N
        Post-release segment: .postN
        Development release segment: .devN

        >>> parse_pep440('invalid')
        >>> parse_pep440('1.2.3.4')['release']
        (1, 2, 3, 4)
        >>> v = parse_pep440('0!1.2.3.4.b5.post6.dev7')
        >>> v['release']
        (1, 2, 3, 4)
        >>> v['pre_release']
        ('b', 5)
        >>> v['post_release']
        6
        >>> v['dev_release']
        7
        >>> v['epoch']
        '0'
    """

    try:
        match = pep440_regex.fullmatch(version_string)
    except AttributeError:
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
    result['sort_tuple'] = sort_tuple(**result)

    return result

def sort_tuple(**kwd):
    return (
        kwd.get('epoch', ''),
        kwd['release'],
        kwd.get('pre_release', ('x',))[0],
        -kwd.get('pre_release', ('', -1))[1],
        kwd.get('post_release', -1),
        kwd.get('dev_release', -1),
    )

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


def get_confed_prefix(path=None):
    """ Get the tag_prefix from setup.cfg

        >>> get_confed_prefix()
    """
    setup_dir = find_parent_containing('setup.cfg', path=path, check='isfile')
    if not setup_dir:
        return
    parser = get_configparser()
    parser.read(os.path.join(setup_dir, 'setup.cfg'))
    return parser.get('versioning', 'tag_prefix')

@click.command()
@click.option('-a', '--all', is_flag=True, help='Clean all tags found in setup.cfgs in this repo.')
@click.option('-p', '--prefix', type=str, default=None, help='Specify prefix for tags (else uses setup.cfg).')
@click.option('-y', '--yes', is_flag=True, help='Assume yes on all safety questions.')
@click.option('-n', '--noop', is_flag=True, help='Do not actually delete tags.')
@click.argument('n', type=int, default=3)
def local_tag_cleanup(n=3, prefix=None, yes=None, all=None, noop=None):
    """ Delete all but the last n version tags. """

    if n < 0:
        abort('Negative n supplied: %s' % n)
    elif n == 0 and not yes:
        yes or click.confirm('Really keep zero (0) of the selected tags?', abort=True)

    if all:
        git_root = os.path.dirname(local_repo().git_dir)
        for cfgdir in find_subdirs_containing(
                'setup.cfg',
                path=git_root,
                check='isfile',
                not_found=(),
            ):
            echo.white('setup.cfg from', colors.cyan(cfgdir))
            parser = get_configparser()
            parser.read(os.path.join(cfgdir, 'setup.cfg'))
            prefix = parser.get('versioning', 'tag_prefix')
            noop or clean_tag_prefix(prefix, n, yes)

    else:
        if prefix is None:
            prefix = get_confed_prefix()
            if prefix is None:
                if yes:
                    abort('No tag prefix found or specified.')
                prefix = click.prompt('No config found. Enter prefix manually')

        noop or clean_tag_prefix(prefix, n, yes)


def clean_tag_prefix(prefix, n, yes):
    """ Clean one tag prefix as requested. """

    echo.white(
        'Cleanup:', prefix,
        'n =', n,
        'yes =', yes,
    )

    tags = local_tags(prefix=prefix)
    def version_sort(tag):
        return parse_pep440(tag[len(prefix):])['sort_tuple']

    versions = sorted(tags, key=version_sort, reverse=True)
    keep = versions[:n]

    echo.white(
        'Keeping %s tags with prefix %s: %s' % (
            colors.bold(str(n)),
            colors.cyan(repr(prefix)),
            ', '.join([colors.green(tag) for tag in keep])
        )
    )

    to_delete = versions[n:]
    echo.red('tags to be removed:', colors.bold(str(len(to_delete))))
    if len(to_delete) <= 3:
        for tag in to_delete:
            echo.yellow('->', tag)
    else:
        echo.yellow('->', to_delete[-1])
        echo.yellow('  ', '...', len(to_delete) - 2, 'more', '...')
        echo.yellow('->', to_delete[0])


    if yes or click.confirm('Delete these tags locally?', default=n):
        echo.green(delete_local_tags(to_delete))
    else:
        echo.cyan('Not deleting any of these.')
