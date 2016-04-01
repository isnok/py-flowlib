from .common import local_git_command

def list_config():
    return local_git_command().config('--list')
