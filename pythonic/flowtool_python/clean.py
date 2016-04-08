import os
import fnmatch
import click
import shutil
from flowtool.style import echo, colors

# from flowtool.style import debug

cleaning_config = {
    'dirnames': [
        'build',
        'dist',
        '*.egg-info',
        '__pycache__',
        '.cache',
        '.tox',
    ],
    'filenames': [
        '*.py[cod]',
    ],
}


def filter_fn(names, patterns):
    filtered = []
    for pattern in patterns:
        filtered.extend([n for n in names if fnmatch.fnmatch(n, pattern)])
    return filtered


def determine_what_to_clean(loc, dirs, files):
    def add_loc(lst):
        return [os.sep.join([loc, name]) for name in lst]
    rm_dirs = filter_fn(dirs, cleaning_config['dirnames'])
    rm_files = filter_fn(files, cleaning_config['filenames'])
    return (add_loc(rm_dirs), add_loc(rm_files))


def confirm_clean(files_to_delete, dirs_to_remove):

    if not (files_to_delete or dirs_to_remove):
        echo.green('\nNothing that would require cleaning was found.\n')
        return False

    if files_to_delete:
        echo.red('\nFiles to be deleted:\n')
        for fname in files_to_delete:
            echo.white(fname)

    if dirs_to_remove:
        echo.red('\nDirectories to be deleted:\n')
        for dirname in dirs_to_remove:
            echo.white(dirname)

    confirmed = click.confirm(
        colors.bold('\nDelete these files / directories?'),
        default=True,
        abort=True,
    )
    return confirmed


@click.command()
@click.argument('directory', type=click.Path(exists=True), default=os.curdir)
def clean(directory):
    """ Recursively clean python temporary files. """

    echo.white('==============================\n= python temp files cleaning =\n==============================')

    files_to_delete = []
    dirs_to_remove = []

    for step in os.walk(directory):
        dirs, files = determine_what_to_clean(*step)
        dirs_to_remove.extend(dirs)
        files_to_delete.extend(files)

    if confirm_clean(files_to_delete, dirs_to_remove):
        for fname in files_to_delete:
            try:
                os.unlink(fname)
            except FileNotFoundError:
                pass
        for dirname in dirs_to_remove:
            try:
                shutil.rmtree(dirname)
            except FileNotFoundError:
                pass

    echo.white('Done.')
