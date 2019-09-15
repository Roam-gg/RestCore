import os
import sys

from setuptools import setup
from setuptools.command.install import install

VERSION = "0.3.3"

def readme():
    """print long description"""
    with open('README.md') as f:
        return f.read()

class VerifyVersionCommand(install):
    description = 'verify that the git tag matches our version'
    def run(self):
        tag = os.getenv('CIRCLE_TAG')
        if tag != version:
            info = f"Git tag: {tag} does not match the version of this package: {VERSION}"
            sys.exit(info)

setup(
        name="roamrs",
        version=VERSION,
        description="A package to allow you to make REST APIs easy",
        long_description=readme(),
        url="https://github.com/Roam-gg/RestCore",
        author='Yui Yukihira',
        author_email='yuiyukihira@pm.me',
        license="GPLv3",
        classifiers=[
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: GNU General Public License (GPL)",
            "Operating System :: OS Independent",
            "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
            "Topic :: Software Development :: Libraries :: Python Modules",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3 :: Only",
        ],
        keywords='roamrs roam.gg roam rest api',
        packages=['roamrs'],
        package_dir = {'': 'src'},
        install_requires=[
            'aiohttp',
            'aiostream >= 0.3.3'
        ],
        python_requires='>=3.7',
        cmdclass={
            'verify': VerifyVersionCommand,
        }
)
