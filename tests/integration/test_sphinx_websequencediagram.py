"""Integration tests for sphinx_websequencediagram.py."""
import os
import os.path
import subprocess

import pytest


pytestmark = [pytest.mark.integration]


@pytest.fixture
def fixture_path():
    """Return the fixture path for integration test fixtures."""
    integration_tests_directory = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(integration_tests_directory, 'fixtures')


@pytest.fixture
def build_docs(request, fixture_path):
    """Return a function that builds the documentation."""
    docs_path = os.path.join(fixture_path, 'test_docs')

    source_path = os.path.join(docs_path, 'source')
    build_path = os.path.join(docs_path, 'build')

    def _clean_up_build():
        subprocess.call(['rm', '-rf', build_path])

    request.addfinalizer(_clean_up_build)

    def build_docs():
        """Build test sphinx documentation & return HTML of build."""
        subprocess.call(['sphinx-build', source_path, build_path])

        build_file = os.path.join(build_path, 'index.html')
        with open(build_file, 'r') as output_file:
            return output_file.read()

    return build_docs


def test_sphinx_websequencediagrams(build_docs):
    """Assert sphinx_websequencediagrams can build sequence diagrams."""
    raw_html = build_docs()
    # TODO Compare the <img src=URL /> to a static file
    assert 'sequencediagram-index-0' in raw_html
    assert 'sequencediagram-index-1' in raw_html
