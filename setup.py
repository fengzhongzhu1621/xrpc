# -*- coding: utf-8 -*-
import sys
import os
import codecs
# from setuptools import Extension
from setuptools import find_packages
from setuptools import setup
from setuptools.command.test import test as TestCommand
from importlib import import_module
from Cython.Build import cythonize

if sys.version_info < (3, 6, 8):
    raise RuntimeError("trpc requires Python 3.6+")


def read_version():
    version = import_module('x_rpc.version').version
    return version


class PyTest(TestCommand):
    """python setup.py test support pytest"""

    user_options = [("pytest-args=", "a", "Arguments to pass to pytest")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ""

    def run_tests(self):
        import shlex
        import pytest

        errno = pytest.main(shlex.split(self.pytest_args))
        sys.exit(errno)


class Tox(TestCommand):
    user_options = [('tox-args=', None, "Arguments to pass to tox")]

    def __init__(self, *args, **kwargs):
        self.tox_args = ''
        self.test_args = []
        self.test_suite = True

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.tox_args = ''

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import tox
        errno = tox.cmdline(args=self.tox_args.split())
        sys.exit(errno)


def read(filename):
    """读取项目根目录下的文件 ."""
    project_dir = os.path.abspath(os.path.dirname(__file__))
    return codecs.open(os.path.join(project_dir, filename), 'r').read()


ext_modules = [

]

tests_require = [
    'pytest',
    "pytest-cov",
    'pytest-asyncio',
    "pytest-sugar",
    "pytest-benchmark",
    "pytest-dependency",
]


long_description = read('README.md') + '\n\n'

install_requires = []
if os.path.exists("requirements.txt"):
    _install_requires = read("requirements.txt").split("\n")
    for package in _install_requires:
        if package.startswith("-f "):
            continue
        if package:
            install_requires.append(package)
    if "win" in sys.platform:
        for item in ['pexpect']:
            try:
                install_requires.remove(item)
            except ValueError as e:
                pass

install_requires.extend([

])

setup(
    name="x_rpc",
    version=read_version(),
    description="A rpc framework for python",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/fengzhongzhu1621/xrpc",
    project_urls={
        "Documentation": "https://github.com/fengzhongzhu1621/xrpc",
        "Code": "https://github.com/fengzhongzhu1621/xrpc",
        "Issue tracker": "https://github.com/fengzhongzhu1621/xrpc/issues",
    },
    license="MIT",
    author='jinyinqiao',
    author_email='jinyinqiao@gmail.com',
    maintainer="jinyinqiao@gmail.com",
    zip_safe=False,
    scripts=None,
    keywords='rpc',
    python_requires=">=3.6",
    install_requires=install_requires,
    ext_modules=cythonize(ext_modules),
    test_suite='tests',
    tests_require=tests_require,
    cmdclass={
        'test': PyTest
    },
    packages=find_packages(exclude=['tests*']),
)
