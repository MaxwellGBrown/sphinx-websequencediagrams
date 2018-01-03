"""Setuptools packaging for sphinx-sequencediagrams."""

from setuptools import setup

install_requires = [
    "demjson==2.2.4",
    "Sphinx==1.6.5",
]
tests_require = install_requires + ["pytest==3.3.1"]

setup(
    name="sphinx-websequencediagrams",
    version="0.0",
    license="MIT",
    url="https://github.com/MaxwellGBrown/sphinx-websequencediagrams",
    install_requires=install_requires,
    tests_require=tests_require,
    setup_requires=["pytest-runner>=2.0"],
    py_modules=["sphinx_websequencediagrams"],
    entry_points={
        "sphinx.builders": [
            "sphinx-websequencediagrams = sphinx_websequencediagrams"
        ],
    },
)
