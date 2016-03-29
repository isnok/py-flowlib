""" Inspired by https://github.com/warner/python-versioneer. """
import os
from os.path import join, exists, isfile, isdir, dirname
try:
    import configparser
except:
    import ConfigParser as configparser

def find_parent_containing(name, path=None, check='exists'):
    """ Return the nearest directory in the parent dirs of path,
        that contains name, or None if no such parent dir exists.
        The check can be customized/chosen from exists, isfile
        and isdir.
    """

    current = os.getcwd() if path is None else path

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
    parser = configparser.ConfigParser()
    parser.read(filenames)
    return parser

setup_cfg = join(
    find_parent_containing('setup.cfg', check=isfile),
    'setup.cfg',
)
parser = read_config(setup_cfg)
configured_versionfile = parser.get('versioning', 'source_versionfile')

print(configured_versionfile)

def deploy_versionfile(to_file):
    versionfile = join(dirname(__file__), 'version.py')
    with open(versionfile, 'r') as f_in, open(to_file, 'w') as f_out:
        f_out.write(f_in.read())

deploy_versionfile(configured_versionfile)



def get_cmdclass():
    """Return the custom setuptools/distutils subclasses."""
    cmds = {}

    # we add "version" to both distutils and setuptools
    from distutils.core import Command

    class cmd_version(Command):
        description = "report generated version string"
        user_options = []
        boolean_options = []

        def initialize_options(self):
            pass

        def finalize_options(self):
            pass

        def run(self):
            vers = get_versions(verbose=True)
            print("Version: %s" % vers["version"])
            print(" full-revisionid: %s" % vers.get("full-revisionid"))
            print(" dirty: %s" % vers.get("dirty"))
            if vers["error"]:
                print(" error: %s" % vers["error"])
    cmds["version"] = cmd_version

    # we override "build_py" in both distutils and setuptools
    #
    # most invocation pathways end up running build_py:
    #  distutils/build -> build_py
    #  distutils/install -> distutils/build ->..
    #  setuptools/bdist_wheel -> distutils/install ->..
    #  setuptools/bdist_egg -> distutils/install_lib -> build_py
    #  setuptools/install -> bdist_egg ->..
    #  setuptools/develop -> ?

    # we override different "build_py" commands for both environments
    if "setuptools" in sys.modules:
        from setuptools.command.build_py import build_py as _build_py
    else:
        from distutils.command.build_py import build_py as _build_py

    class cmd_build_py(_build_py):
        def run(self):
            root = get_root()
            cfg = get_config_from_root(root)
            versions = get_versions()
            _build_py.run(self)
            # now locate _version.py in the new build/ directory and replace
            # it with an updated value
            if cfg.versionfile_build:
                target_versionfile = os.path.join(self.build_lib,
                                                  cfg.versionfile_build)
                print("UPDATING %s" % target_versionfile)
                write_to_version_file(target_versionfile, versions)
    cmds["build_py"] = cmd_build_py

    if "cx_Freeze" in sys.modules:  # cx_freeze enabled?
        from cx_Freeze.dist import build_exe as _build_exe

        class cmd_build_exe(_build_exe):
            def run(self):
                root = get_root()
                cfg = get_config_from_root(root)
                versions = get_versions()
                target_versionfile = cfg.versionfile_source
                print("UPDATING %s" % target_versionfile)
                write_to_version_file(target_versionfile, versions)

                _build_exe.run(self)
                os.unlink(target_versionfile)
                with open(cfg.versionfile_source, "w") as f:
                    LONG = LONG_VERSION_PY[cfg.VCS]
                    f.write(LONG %
                            {"DOLLAR": "$",
                             "STYLE": cfg.style,
                             "TAG_PREFIX": cfg.tag_prefix,
                             "PARENTDIR_PREFIX": cfg.parentdir_prefix,
                             "VERSIONFILE_SOURCE": cfg.versionfile_source,
                             })
        cmds["build_exe"] = cmd_build_exe
        del cmds["build_py"]

    # we override different "sdist" commands for both environments
    if "setuptools" in sys.modules:
        from setuptools.command.sdist import sdist as _sdist
    else:
        from distutils.command.sdist import sdist as _sdist

    class cmd_sdist(_sdist):
        def run(self):
            versions = get_versions()
            self._versioneer_generated_versions = versions
            # unless we update this, the command will keep using the old
            # version
            self.distribution.metadata.version = versions["version"]
            return _sdist.run(self)

        def make_release_tree(self, base_dir, files):
            root = get_root()
            cfg = get_config_from_root(root)
            _sdist.make_release_tree(self, base_dir, files)
            # now locate _version.py in the new base_dir directory
            # (remembering that it may be a hardlink) and replace it with an
            # updated value
            target_versionfile = os.path.join(base_dir, cfg.versionfile_source)
            print("UPDATING %s" % target_versionfile)
            write_to_version_file(target_versionfile,
                                  self._versioneer_generated_versions)
    cmds["sdist"] = cmd_sdist

    return cmds
