import os
import re
import sys
import click
from flowtool.style import colors, echo
from flowtool.files import find_parent_containing
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

def get_configparser():
    try:
        from configparser import ConfigParser
    except:
        from ConfigParser import ConfigParser
    return ConfigParser()

def get_confed_prefix():
    setup_dir = find_parent_containing('setup.cfg', check='isfile')
    if not setup_dir:
        return
    parser = get_configparser()
    parser.read(os.path.join(setup_dir, 'setup.cfg'))
    return parser.get('versioning', 'tag_prefix')

@click.command()
@click.argument('n', type=int, default=3)
def local_tag_cleanup(n=3):
    """ Delete all but the last n version tags. """

    prefix = get_confed_prefix()
    if not prefix:
        prefix = click.prompt('No config found. Enter prefix manually')

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

    echo.red('Local git tags to be removed:')
    to_delete = versions[n:]
    for tag in to_delete:
        echo.yellow('->', tag)
    click.confirm('Delete these tags locally?', abort=True)
    echo.green(delete_local_tags(to_delete))
