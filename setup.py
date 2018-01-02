"""Setuptools packaging for sphinx-sequencediagrams."""

from setuptools import setup


setup(
    name="sphinx-websequencediagrams",
    version="0.0",
    license="MIT",
    url="https://github.com/MaxwellGBrown/sphinx-websequencediagrams",
    entry_points={
        "sphinx.builders": [
            "sphinx-websequencediagrams = sphinx_wsd"
        ],
    },
    py_modules=["sphinx_wsd"]
)
