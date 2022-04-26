"""A setuptools based setup module.

See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""
from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name='voltalis-cli',
    version='0.0.1',
    url='https://github.com/nilleb/voltalis-cli',
    author='Ivo Bellin Salarin',
    author_email='ivo@nilleb.com',
    description='voltalis python client',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),    
    install_requires=['requests >= 1.11.1', 'matplotlib >= 1.5.1'],
    extras_require = {
        'dev': ['black', 'isort', 'ipython', 'build', 'twine'],
        'build': ['requests']
    }
)
