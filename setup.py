# coding:utf-8

from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext
import sys
import setuptools

from youdao.config import VERSION
__version__ = VERSION


class get_pybind_include(object):
    """Helper class to determine the pybind11 include path
    The purpose of this class is to postpone importing pybind11
    until it is actually installed, so that the ``get_include()``
    method can be invoked. """
    def __init__(self, user=False):
        self.user = user

    def __str__(self):
        import pybind11
        return pybind11.get_include(self.user)


ext_modules = [
    Extension(
        'youdao.lib.CPyStarDictIndex',
        ['youdao/lib/CPyStarDictIndex.cpp'],
        include_dirs=[
            # Path to pybind11 headers
            get_pybind_include(),
            get_pybind_include(user=True)
        ],
        language='c++'),
]


# As of Python 3.6, CCompiler has a `has_flag` method.
# cf http://bugs.python.org/issue26689
def has_flag(compiler, flagname):
    """Return a boolean indicating whether a flag name is supported on
    the specified compiler.
    """
    import tempfile
    with tempfile.NamedTemporaryFile('w', suffix='.cpp') as f:
        f.write('int main (int argc, char **argv) { return 0; }')
        try:
            compiler.compile([f.name], extra_postargs=[flagname])
        except setuptools.distutils.errors.CompileError:
            return False
    return True


def cpp_flag(compiler):
    """Return the -std=c++[11/14/17] compiler flag.
    The newer version is prefered over c++11 (when it is available).
    """
    flags = ['-std=c++17', '-std=c++14', '-std=c++11']

    for flag in flags:
        if has_flag(compiler, flag): return flag

    raise RuntimeError('Unsupported compiler -- at least C++11 support '
                       'is needed!')


class BuildExt(build_ext):
    """A custom build extension for adding compiler-specific options."""
    c_opts = {
        'msvc': ['/EHsc'],
        'unix': [],
    }
    l_opts = {
        'msvc': [],
        'unix': [],
    }

    if sys.platform == 'darwin':
        darwin_opts = ['-stdlib=libc++', '-mmacosx-version-min=10.7']
        c_opts['unix'] += darwin_opts
        l_opts['unix'] += darwin_opts

    def build_extensions(self):
        ct = self.compiler.compiler_type
        opts = self.c_opts.get(ct, [])
        link_opts = self.l_opts.get(ct, [])
        if ct == 'unix':
            opts.append('-DVERSION_INFO="%s"' %
                        self.distribution.get_version())
            opts.append(cpp_flag(self.compiler))
            if has_flag(self.compiler, '-fvisibility=hidden'):
                opts.append('-fvisibility=hidden')
        elif ct == 'msvc':
            opts.append('/DVERSION_INFO=\\"%s\\"' %
                        self.distribution.get_version())
        for ext in self.extensions:
            ext.extra_compile_args = opts
            ext.extra_link_args = link_opts
        build_ext.build_extensions(self)


if __name__ == "__main__":
    setup(
        name='youdao',
        version=VERSION,
        description="基于有道API和有道词典web版的在terminal查询词的小工具,支持单词发音",
        long_description=
        """基于有道API和有道词典web版的在terminal查询词的小工具,抓取web版后使用beautifulsoup解析, 详情请见github""",
        keywords='python youdao dictionary terminal',
        author='longcw',
        author_email='longch1024@gmail.com',
        url='https://github.com/longcw/youdao',
        license='MIT',
        packages=find_packages(exclude=['tests']),
        include_package_data=True,
        zip_safe=False,
        setup_requires=['pybind11>=2.4'],
        install_requires=[
            'termcolor', 'requests', 'beautifulsoup4', 'peewee', 'lxml',
            'pybind11', 'cppimport'
        ],
        entry_points={'console_scripts': [
            'yd = youdao.main:main',
        ]},
        ext_modules=ext_modules,
        cmdclass={'build_ext': BuildExt},
        classifiers=[
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.2',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6'
        ],
    )
