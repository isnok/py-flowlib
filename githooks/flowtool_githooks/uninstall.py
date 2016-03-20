import os
import shutil
import sys
import click
import git
from flowtool.style import colors, echo
from flowtool_githooks.manager import hook_specs

@click.command()
@click.argument('name', nargs=-1)
@click.option('-y', '--yes', is_flag=True, help='Answer yes to all questions.')
def run_hook(yes=None, name=()):
    """ Remove git hooks and scripts. """
    name = ''.join(name)
    chosen = [h for h in hook_specs if name.lower() in h]
    if not chosen:
        echo.yellow('No hook found for %r:' % name, list(hook_specs))
        sys.exit(1)

    git_dir = git.Repo(search_parent_directories=True).git_dir

    for hook_name in chosen:

        spec = hook_specs[hook_name]

        hook_file = os.sep.join([git_dir, 'hooks', hook_name])
        hook_dir = hook_file + '.d'

        echo.white(
            colors.underline('Removing'),
            colors.bold(hook_name),
            colors.white('->'),
            colors.yellow(hook_file),
            spec.args
        )

        if yes or click.confirm('Delete this hook?'):
            os.unlink(hook_file)
            echo.cyan('Removed', hook_name, 'hook script.')
        else:
            echo.cyan(hook_name, 'was preserved.')


        if os.path.isdir(hook_dir):
            echo.yellow('->', os.listdir(hook_dir))
            if yes or click.confirm('Delete hook folder recursively?'):
                os.unlink(hook_file)
                echo.cyan('Removed', hook_name, 'hook dir.')
            else:
                echo.cyan(hook_name, 'scripts were preserved.')

