import glob
from os.path import exists, join, isdir, split

import sh
from pythonforandroid.logger import info, shprint, warning
from pythonforandroid.toolchain import Recipe, current_directory

LOCAL_DEBUG = False


class CertifiRecipe(Recipe):
    certifi_git = 'https://github.com/certifi/python-certifi.git'
    certifi_branch = 'master'
    version = '5.0'
    toolchain_version = 4.9  # default GCC toolchain version we try to use
    depends = ['python3']  # any other recipe names that must be built before this one

    def get_newest_toolchain(self, arch):

        toolchain_versions = []
        toolchain_prefix = arch.toolchain_prefix
        toolchain_path = join(self.ctx.ndk_dir, 'toolchains')
        if isdir(toolchain_path):
            toolchain_contents = glob.glob('{}/{}-*'.format(toolchain_path,
                                                            toolchain_prefix))
            toolchain_versions = [split(path)[-1][len(toolchain_prefix) + 1:]
                                  for path in toolchain_contents]
        else:
            warning('Could not find toolchain subdirectory!')
        toolchain_versions.sort()

        toolchain_versions_gcc = []
        for toolchain_version in toolchain_versions:
            if toolchain_version[0].isdigit():
                toolchain_versions_gcc.append(toolchain_version)  # GCC toolchains begin with a number

        if toolchain_versions:
            toolchain_version = toolchain_versions_gcc[-1]  # the latest gcc toolchain
        else:
            warning('Could not find any toolchain for {}!'.format(toolchain_prefix))

        self.toolchain_version = toolchain_version

    def prebuild_arch(self, arch):
        super(CertifiRecipe, self).prebuild_arch(arch)

        build_dir = self.get_build_dir(arch.arch)
        try:
            shprint(sh.rm, '-r',
                    build_dir,
                    _tail=20,
                    _critical=True)
        except:
            pass

        info("Cloning certifi sources from {}".format(self.certifi_git))
        shprint(sh.git,
                'clone', '-b',
                self.certifi_branch,
                '--depth=1',
                self.certifi_git,
                build_dir,
                _tail=20,
                _critical=True)

        self.get_newest_toolchain(arch)

    def build_arch(self, arch):
        super(CertifiRecipe, self).build_arch(arch)

        env = self.get_recipe_env(arch)
        # self.build_cython_components(arch)

        with current_directory(self.get_build_dir(arch.arch)):
            hostpython = sh.Command(self.ctx.hostpython)

            shprint(hostpython, 'setup.py', 'install', '-O2', _env=env, _tail=10, _critical=True)

    def postbuild_arch(self, arch):
        super(CertifiRecipe, self).postbuild_arch(arch)

    
recipe = CertifiRecipe()
