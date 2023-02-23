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
    name="voltalis-cli",
    version="1.2.0",
    url="https://github.com/nilleb/voltalis-cli",
    author="Ivo Bellin Salarin",
    author_email="ivo@nilleb.com",
    description="voltalis python client",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "requests >= 1.11.1",
        "requests_cache >= 0.9.8",
        "python-dateutil >= 2.7.3",
    ],
    extras_require={
        "dev": ["black", "isort", "ipython", "build", "twine", "python-json-logger"],
        "build": ["requests", "python-dateutil" "requests_cache", "pandas"],
    },
)
