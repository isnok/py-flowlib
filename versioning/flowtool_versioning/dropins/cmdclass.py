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
# pylint: disable=E0401,E1101,E0611

import os
import sys
from os.path import join, exists, isfile, isdir, dirname, basename

from pprint import pformat
from distutils.core import Command


def find_in_parents(path, name):
    """ Return the nearest finding in the parent dirs of path,
       while searching for name. Returns None if no such parent dir exists.

        >>> find_in_parents('/tmp/', '__not_to_be_founfd_filename.txt__')
        >>> find_in_parents(dirname(__file__), basename(__file__)) == __file__
        True
    """

    while not isfile(join(path, name)):
        old = path
        path = dirname(path)
        if old == path:
            break
    else:
        return join(path, name)


def find_setup_cfg():
    """ Return the nearest directory in the parent dirs of path,
        that contains setup.cfg, or None if no such parent dir exists.

        >>> found = find_setup_cfg()
        >>> found is None or found.endswith('setup.cfg')
        True
    """
    for path in (os.getcwd(), dirname(__file__)):
        found = find_in_parents(path, 'setup.cfg')
        if found:
            return found

import sys
PYTHON = sys.version_info
configparser_module = 'ConfigParser' if PYTHON.major == 2 else 'configparser'
configparser = __import__(configparser_module)

def parse_setup_cfg():
    """ Find and parse the project setup.cfg that contains the versioning config.

        >>> hasattr(parse_setup_cfg(), 'has_option')
        True
    """
    parser = configparser.ConfigParser()
    parser.read(find_setup_cfg())
    return parser

def read_setup_cfg():
    """ Read relevant information from setup.cfg

        >>> all(x.endswith('.py') for x in read_setup_cfg())
        True
    """
    section = 'versioning'
    parser = parse_setup_cfg()

    source_versionfile = parser.get(section, 'source_versionfile')

    has_build = parser.has_option(section, 'build_versionfile')
    build_versionfile = parser.get(section, 'build_versionfile') if has_build else source_versionfile

    return source_versionfile, build_versionfile



def import_file(name, path):
    """ Import a python source file by its filesystem path.

        >>> from os.path import join, dirname
        >>> module = import_file('import_file_test', join(dirname(__file__), '__init__.py'))
    """

    module = None

    try: # py2
        import imp
        module = imp.load_source(name, path)
    except IOError:
        pass

    try: # py3.5
        import importlib.util
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except:
        pass

    try: # py3.3, py3.4
        from importlib.machinery import SourceFileLoader
        module = SourceFileLoader(name, path).load_module()
    except:
        pass

    return module


def get_version():
    """ Fallback & Test version function.

        >>> get_version()
        'no_version'
    """
    return 'no_version'


def setup_versioning():
    """ Here some magic happens.

        >>> import sys
        >>> type(setup_versioning()) in (type(sys), type(None))
        True
    """

    global get_version

    source_versionfile, build_versionfile = read_setup_cfg()

    versionfile = import_file('_version', source_versionfile) if isfile(source_versionfile) else None

    get_version = versionfile.get_version if hasattr(versionfile, 'get_version') else get_version

    return versionfile

versionfile = setup_versioning()

def print_version_info():
    """ Testable body of a setuptools/distutils command.

        >>> print_version_info()
        == Version-Config (setup.cfg):
        ...
    """
    parser = parse_setup_cfg()

    pretty_version_info = pformat(dict(parser.items('versioning')))
    print('== Version-Config (setup.cfg):\n' + pretty_version_info)

    if versionfile is not None and hasattr(versionfile, 'VERSION_INFO'):
        print('== Version-Info:\n' + pformat(versionfile.VERSION_INFO))


class cmd_version_info(Command):
    """ Version info command.

        Run `./setup.py version` to get detailed info on the latest version.
    """

    description = "show versioning configuration and current project version"
    user_options = []
    boolean_options = []

    def initialize_options(self): pass
    def finalize_options(self): pass

    def run(self):
        print_version_info()



def bump_version(info):
    """ Bump a parsed version.

        >>> bump_version({'release':(8, 1)})
        {'release': (8, 2)}
        >>> bump_version({'release':(8, 1), 'post_release':0})['post_release']
        1
        >>> bump_version({'release':(8, 1), 'pre_release':('a', 0), 'dev_release':4})['dev_release']
        5
        >>> bump_version({'release':(8, 1), 'pre_release':('b', 0)})['pre_release']
        ('b', 1)
    """
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
    """ Render the bumped version.
        >>> render_bumped(release=(1,2,3,4))
        '1.2.3.4'
        >>> render_bumped(release=(1,2,3,4), pre_release=('a', 5), post_release=6, dev_release=7, epoch=0)
        '0!1.2.3.4a5.post6.dev7'
        >>> render_bumped(release=(1,2,3), post_release=4, dev_release=5)
        '1.2.3.post4.dev5'
    """
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


def do_bump(not_really=None):
    """ Execute a version bump (if not testing)

        >>> do_bump(not_really={'dirt':'','tag_version':{'release':(1,1,2)},'prefix':''})
        == Next Version: {'release': (1, 1, 3)}
        == Tagging: 1.1.3
        >>> do_bump(not_really={'dirt':'XXX','tag_version':{'release':(1,1,2)},'prefix':''})
        Traceback (most recent call last):
        ...
        SystemExit: 1
    """
    vcs_info = versionfile.VERSION_INFO['vcs_info'] if not_really is None else not_really
    tag_info = bump_version(vcs_info['tag_version'])
    print('== Next Version: %s' % pformat(tag_info))
    if vcs_info['dirt']:
        print("==> Auto bump aborted due to dirty git repository.")
        sys.exit(1)
    tag = vcs_info['prefix'] + render_bumped(**tag_info)
    print('== Tagging: %s' % tag)
    not_really or os.system('git tag ' + tag)

class cmd_version_bump(Command):
    """ Version bump command.

        Run `./setup.py bump` to create a new git tag
        with the smallest version component increased
        by one.
    """
    description = "bump the (pep440) version by adding one to the smallest version component"
    user_options = []
    boolean_options = []

    def initialize_options(self): pass
    def finalize_options(self): pass
    def run(self): do_bump()


#class cmd_update_versionfile(Command):
    #description = "update the versioning"
    #user_options = []
    #boolean_options = []

    #def initialize_options(self):
        #pass

    #def finalize_options(self):
        #pass

    #def run(self):
        #print('== Updating file:\n%s' % source_versionfile)
        #from flowtool_versioning.dropins import version
        #versionfile = version.__file__
        #with open(versionfile, 'r') as f_in, open(source_versionfile, 'w') as f_out:
            #f_out.write(f_in.read())



if "setuptools" in sys.modules:
    from setuptools.command.build_py import build_py as _build_py
else:
    from distutils.command.build_py import build_py as _build_py


class cmd_build_py(_build_py):
    """ It seems as if build_py is executed when the distributed package is installed. """

    #def run(self):
        #_build_py.run(self)
        # now locate _version.py in the new build/ directory and replace
        # it with an updated value
        #deploy_to = build_versionfile
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

def add_to_sdist(base_dir):
    """ The custom part of the sdist command.

        >>> add_to_sdist('/tmp')
        == Rendering:
        ...
        >>> add_to_sdist('/tmp')
        == Rendering:
        ...
    """
    # now locate _version.py in the new base_dir directory
    # (remembering that it may be a hardlink) and replace it with an
    # updated value

    source_versionfile, build_versionfile = read_setup_cfg()
    target_versionfile = os.path.join(base_dir, build_versionfile)
    static_versionfile = versionfile.render_static_file()
    print("== Rendering:\n%s\n== To Versionfile: %s" % (static_versionfile, target_versionfile))

    try:
        # handles the hard link case correctly
        if os.path.exists(target_versionfile):
            os.unlink(target_versionfile)
        with open(target_versionfile, 'w') as fh:
            fh.write(static_versionfile)
    except:
        print("=== Could not render static _version.py to sdist!")

    self_target = join(base_dir, basename(__file__))
    print("== Updating:\n%s" % self_target)
    if not os.path.exists(self_target):
        try:
            os.link(__file__, self_target)
        except OSError:
            print("=== Could not add %s to sdist!" % basename(__file__))


class cmd_sdist(_sdist):

    def run(self):
        self.distribution.metadata.version = setup_versioning().get_version()
        return _sdist.run(self)

    def make_release_tree(self, base_dir, files):
        _sdist.make_release_tree(self, base_dir, files)
        add_to_sdist(base_dir)


from distutils.command.upload import upload as _upload


class cmd_upload(_upload):

    description="Do the normal upload, but prevent pushing with Python2."

    def run(self):
        if sys.version_info.major == 3:
            return _upload.run(self)
        print('==> For backwards compatibility you should only upload packages built with Python 3 to PyPI.')
        sys.exit(1)


def publish_code(not_really=None):
    """ push git and its tags

        >>> publish_code(not_really=True)
        === git push
        === pushing tags also
    """
    print("=== git push")
    not_really or os.system('git push')
    print("=== pushing tags also")
    not_really or os.system('git push --tags')


class cmd_release(cmd_upload):

    description="Do the protected upload, but push git things first"

    def run(self):
        publish_code()
        return cmd_upload.run(self)



def get_cmdclass():
    """ Return the custom setuptools/distutils subclasses.

        >>> sorted(get_cmdclass().keys())
        ['build_py', 'bump', 'release', 'sdist', 'upload', 'version']
    """
    cmds = dict(
        version=cmd_version_info,
        bump=cmd_version_bump,
        build_py=cmd_build_py,
        sdist=cmd_sdist,
        upload=cmd_upload,
        release=cmd_release,
    )
    return cmds


def main():
    """ Prints the current version.

        >>> main()
        no_version
    """
    print(get_version())

if __name__ == '__main__':
    main()
