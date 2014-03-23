from flib.env import args, config
from flib.local import LocalHost
from flib.remote import RemoteHost
from flib.repo import GitRepository
from flib.repo import Directory

def env_host():
    if args.host:
        return args.host
    elif 'host' in config:
        return config.host
    elif 'repo' in config and 'host' in config.repo:
        return config.repo.host
    else:
        return None

_cache = None
def host_obj():
    global _cache
    if _cache is not None:
        return _cache
    cfg = env_host()
    if cfg:
        _cache = RemoteHost(cfg)
    else:
        _cache = LocalHost()
    return _cache


def env_path():
    if args.path != '.':
        return args.path
    elif 'repo' in config and 'location' in config.repo:
            return config.repo.location
    else:
        return args.path

def path_obj(git=True):
    cls = GitRepository if git else Directory
    return cls(host_obj(), env_path())
