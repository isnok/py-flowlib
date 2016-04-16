import os
import sys
import click
import filecmp

from collections import namedtuple
from pkg_resources import iter_entry_points

from flowtool.style import echo, colors
from flowtool.style import debug
from flowtool.files import is_executable, make_executable, make_not_executable

from flowtool_git.common import local_repo


# a reminder/description of what git hooks (can) take as input
#  - stdin not yet supported, not needed yet
#  - are there hooks whose stdout is used?
HookSignature = namedtuple('HookSignature', ['name', 'args', 'stdin'])

#  - this is currently just the hooks i want to focus on first
HOOK_SIGNATURES = [
    HookSignature('pre-commit', (), False),
    HookSignature('commit-msg', ('message_file',), False),
    HookSignature('pre-push', (), True),
]
hook_specs = {sig.name: sig for sig in HOOK_SIGNATURES}

RUNNER = os.sep.join([
    os.path.dirname(__file__), 'scripts', 'generic-hook-runner.sh'
])

InstalledHook = namedtuple('InstalledHook', ['name', 'active', 'file', 'is_runner', 'runner_dir'])

def script_group_name(hook_name):
    """ Derive the entry point group name from the git hook name.

        >>> script_group_name('pre-commit')
        'flowtool_githooks.pre_commit'
    """
    return 'flowtool_githooks.' + hook_name.replace('-', '_')

def get_script_entry_points(hook_name):
    """ Get the script entrypoints as a dict, using
        names as keys and entry points as values.

        >>> isinstance(get_script_entry_points('pre-commit'), dict)
        True
    """
    group = script_group_name(hook_name)
    result = {}
    itr = iter_entry_points(group)
    while True:
        try:
            e = next(itr)
            result[e.name] = e
        except StopIteration:
            break
        except:
            pass
    return result

def find_entry_scripts(hook_name):
    """ Find managed git hooks via the entry points for the respective hooks.
        This is done by intersecting the names in the virtual environments bin
        directory with the found entry points.

        Returns a dictionary with the absolute file names

        >>> find_entry_scripts('unknown-hook')
        {}
    """
    scripts = get_script_entry_points(hook_name)
    bindir = os.path.dirname(str(sys.executable))
    binscripts = set(scripts).intersection(os.listdir(bindir))
    entrypoint_scripts = {
        os.path.join(bindir, s): scripts[s]
        for s in binscripts
    }
    debug.bold('scripts for %r:' % hook_name, entrypoint_scripts)

    return entrypoint_scripts


def gather_file_hooks(repo=None):
    """ Gather information on installed git hook files.

        >>> type(gather_file_hooks()) == list
        True
    """

    if repo is None:
        repo = local_repo()

    hook_dir = os.path.join(repo.git_dir, 'hooks')
    files = os.listdir(hook_dir)
    hooks = [os.path.join(hook_dir,f) for f in files if f in hook_specs]
    found = []
    for filename in hooks:
        is_runner = filecmp.cmp(filename, RUNNER)
        runner_dir = filename + '.d'
        info = InstalledHook(
            name=os.path.basename(filename),
            active=is_executable(filename),
            file=filename,
            is_runner=is_runner,
            runner_dir=runner_dir if os.path.isdir(runner_dir) else None,
        )
        found.append(info)
    return sorted(found)


def gather_hooks(repo=None):
    """ Gather information on active git hooks.

        >>> gather_hooks() == gather_file_hooks()
        True
    """

    if repo is None:
        repo = local_repo()

    debug.cyan('Collecting information on installed hooks in', repo.git_dir)
    # config_hooks = gather_config_hooks(repo)
    file_hooks = gather_file_hooks(repo)
    return file_hooks
