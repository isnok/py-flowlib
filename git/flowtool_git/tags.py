from .common import local_git_command

def local_tags(prefix='', path=None):
    """ Retrieve the tag names from the local repo.
        The selection can be filtered using a prefix.
    """
    tags = local_git_command(path=path).tag().split()
    return [t for t in tags if t.startswith(prefix)]

def delete_local_tags(tags=(), path=None):
    """ Delete a list of git tags from the local repository path. """
    cmd_args = ['--delete'] + list(tags)
    return local_git_command(path=path).tag(*cmd_args)

