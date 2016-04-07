#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" flowtool-versioning cmdclass file. flowtool-versioning provides an
    automatic versioning system based on git tags. This is the command
    set, that it brings to add capabilities to your setup.py file to
    deal with git tags and handle the versioning. See the link for more
    information:

        https://github.com/isnok/py-flowlib
"""

# TODO: make these files pass pylint regularly
# pylint: disable=E0401,E1101

import os
from os.path import join, exists, isfile, isdir, dirname, basename
try:
    from configparser import ConfigParser
except:
    from ConfigParser import ConfigParser

def find_parent_containing(name, path=None, check='exists'):
    """ Return the nearest directory in the parent dirs of path,
        that contains name, or None if no such parent dir exists.
        The check can be customized/chosen from exists, isfile
        and isdir.
    """

    current = os.path.dirname(__file__) if path is None else path

    if check == 'exists':
        check = exists
    elif check in ('isfile', 'file'):
        check = isfile
    elif check in ('isdir', 'dir'):
        check = isdir

    while not check(join(current, name)):
        old = current
        current = dirname(current)
        if old == current:
            break
    else:
        return current

def read_config(*filenames):
    """Read the project setup.cfg file to determine Versioneer config."""
    # This might raise EnvironmentError (if setup.cfg is missing), or
    # configparser.NoSectionError (if it lacks a [versioneer] section), or
    # configparser.NoOptionError (if it lacks "VCS="). See the docstring at
    # the top of versioneer.py for instructions on writing your setup.cfg .
    parser = ConfigParser()
    parser.read(filenames)
    return parser

setup_cfg = join(
    find_parent_containing('setup.cfg', check=isfile),
    'setup.cfg',
)
parser = read_config(setup_cfg)
source_versionfile = parser.get('versioning', 'source_versionfile')

def import_file(name, path):
    try: # py3.5
        import importlib.util
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except:
        pass

    try: # py3.3, py3.4
        from importlib.machinery import SourceFileLoader
        module = SourceFileLoader(name, path).load_module()
        return module
    except:
        pass

    try: # py2
        import imp
        return imp.load_source(name, path)
    except:
        pass

if __name__ != 'flowtool_versioning.dropins.cmdclass':

    version_in_git = import_file('versions', source_versionfile)
    if version_in_git:
        get_version = version_in_git.get_version
    else:
        print("== Warning: source_versionfile %s could not be imported. (no tags found?)" % source_versionfile)
        get_version = lambda: 'versionfile_not_installed'


def build_versionfile():
    if parser.has_option('versioning', 'build_versionfile'):
        return parser.get('versioning', 'build_versionfile')
    else:
        return source_versionfile

#print(build_versionfile())


def render_versionfile():
    print(version_in_git.render_versionfile())

import sys
from distutils.core import Command

class cmd_version_info(Command):
    description = "show versioning configuration and current project version"
    user_options = []
    boolean_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from pprint import pformat
        print('== Version-Config (setup.cfg):\n%s' % pformat(dict(parser.items('versioning'))))
        print('== Version-Info:\n%s' % pformat(version_in_git.VERSION_INFO))

def bump_version(info):
    if 'dev_release' in info:
        info['dev_release'] += 1
    elif 'post_release' in info:
        info['post_release'] += 1
    elif 'pre_release' in info:
        stage, number = info['pre_release']
        info['pre_release'] = (stage, number + 1)
    else:
        segments = info['release']
        info['release'] = segments[:-1] + (segments[-1] + 1,)
    return info


def render_bumped(**kwd):
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

class cmd_version_bump(Command):
    description = "bump the (pep440) version by adding one to the smallest version component"
    user_options = []
    boolean_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from pprint import pformat
        vcs_info = version_in_git.VERSION_INFO['vcs_info']
        tag_info = bump_version(vcs_info['tag_version'])
        print('== Current Version:\n%s' % pformat(tag_info))
        if vcs_info['dirt']:
            print("==> Auto bump aborted due to dirty git repository.")
            sys.exit(1)
        tag = vcs_info['prefix'] + render_bumped(**tag_info)
        print('== Tagging: %s' % tag)
        os.system('git tag ' + tag)

class cmd_update_versionfile(Command):
    description = "update the versioning"
    user_options = []
    boolean_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        print('== Updating file:\n%s' % source_versionfile)
        from flowtool_versioning.dropins import version
        versionfile = version.__file__
        with open(versionfile, 'r') as f_in, open(source_versionfile, 'w') as f_out:
            f_out.write(f_in.read())


if "setuptools" in sys.modules:
    from setuptools.command.build_py import build_py as _build_py
else:
    from distutils.command.build_py import build_py as _build_py

class cmd_build_py(_build_py):
    def run(self):
        _build_py.run(self)
        # now locate _version.py in the new build/ directory and replace
        # it with an updated value
        #deploy_to = build_versionfile()
        #print("== Deploying %s" % deploy_to)
        #deploy_versionfile(deploy_to)


#if "cx_Freeze" in sys.modules:  # cx_freeze enabled?
    #from cx_Freeze.dist import build_exe as _build_exe

    #class cmd_build_exe(_build_exe):
        #def run(self):
            #root = get_root()
            #cfg = get_config_from_root(root)
            #versions = get_version()
            #target_versionfile = cfg.versionfile_source
            #print("UPDATING %s" % target_versionfile)
            #write_to_version_file(target_versionfile, versions)

            #_build_exe.run(self)
            #os.unlink(target_versionfile)
            #with open(cfg.versionfile_source, "w") as f:
                #LONG = LONG_VERSION_PY[cfg.VCS]
                #f.write(LONG %
                        #{"DOLLAR": "$",
                            #"STYLE": cfg.style,
                            #"TAG_PREFIX": cfg.tag_prefix,
                            #"PARENTDIR_PREFIX": cfg.parentdir_prefix,
                            #"VERSIONFILE_SOURCE": cfg.versionfile_source,
                            #})
    #cmds["build_exe"] = cmd_build_exe
    #del cmds["build_py"]

# we override different "sdist" commands for both environments
if "setuptools" in sys.modules:
    from setuptools.command.sdist import sdist as _sdist
else:
    from distutils.command.sdist import sdist as _sdist

class cmd_sdist(_sdist):
    def run(self):
        self.distribution.metadata.version = get_version()
        return _sdist.run(self)

    def make_release_tree(self, base_dir, files):
        _sdist.make_release_tree(self, base_dir, files)
        os.link(__file__, join(base_dir, basename(__file__)))
        # now locate _version.py in the new base_dir directory
        # (remembering that it may be a hardlink) and replace it with an
        # updated value
        target_versionfile = os.path.join(base_dir, build_versionfile())
        print("== Rendering: %s" % target_versionfile)
        os.unlink(target_versionfile)
        with open(target_versionfile, 'w') as fh:
            fh.write(version_in_git.render_static_file())

from distutils.command.upload import upload as _upload

class cmd_upload(_upload):

    description="Do the normal upload, but prevent pushing with Python2."

    def run(self):
        if sys.version_info.major == 3:
            return _upload.run(self)
        print('==> For backwards compatibility you should only upload packages built with Python 3 to PyPI.')
        sys.exit(1)

class cmd_release(cmd_upload):

    description="Do the protected upload, but push git things first"

    def run(self):
        print("=== git push")
        os.system('git push')
        print("=== pushing tags also")
        os.system('git push --tags')
        return cmd_upload.run(self)


def get_cmdclass():
    """Return the custom setuptools/distutils subclasses."""
    cmds = dict(
        version=cmd_version_info,
        #versioning_update=cmd_versioning_update,
        bump=cmd_version_bump,
        build_py=cmd_build_py,
        sdist=cmd_sdist,
        upload=cmd_upload,
        release=cmd_release,
    )
    return cmds


def main():
    print(get_version())

if __name__ == '__main__':
    main()
