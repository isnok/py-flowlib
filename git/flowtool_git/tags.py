from .common import local_git_command

def local_tags(prefix=''):
    tags = local_git_command().tag().split()
    return [t for t in tags if t.startswith(prefix)]

def delete_local_tags(tags):
    cmd_args = ['--delete'] + list(tags)
    return local_git_command().tag(*cmd_args)

