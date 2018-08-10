"""Integration tests for sphinx_websequencediagram.py."""
import os
import os.path
import subprocess

from bs4 import BeautifulSoup
import pytest
import sphinx


pytestmark = [pytest.mark.integration]


FIXTURES_PATH = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),  # abs path of this file
    'fixtures',
)

DOCS_FIXTURE_PATH = os.path.join(FIXTURES_PATH, 'test_docs')
SOURCE_PATH = os.path.join(DOCS_FIXTURE_PATH, 'source')
BUILD_PATH = os.path.join(DOCS_FIXTURE_PATH, 'build')

IMAGES_FIXTURE_PATH = os.path.join(FIXTURES_PATH, 'images')


@pytest.fixture
def build_docs(request):
    """Return a function that builds the documentation."""
    def _clean_up_build():
        subprocess.call(['rm', '-rf', BUILD_PATH])

    request.addfinalizer(_clean_up_build)

    def build_docs():
        """Build test sphinx documentation & return HTML of build."""
        sphinx.main(['sphinx-build', SOURCE_PATH, BUILD_PATH])

        build_file = os.path.join(BUILD_PATH, 'index.html')
        with open(build_file, 'r') as output_file:
            raw_html = output_file.read()

        return BeautifulSoup(raw_html, 'html.parser')

    return build_docs


def test_sphinx_websequencediagrams(build_docs):
    """Assert sphinx_websequencediagrams can build sequence diagrams."""
    html = build_docs()

    # based on tests/interation/fixtures/test_docs/source/index.rst
    inline_sequence_diagram = html.find("img", id="sequencediagram-index-0")
    file_sequence_diagram = html.find("img", id="sequencediagram-index-1")

    assert inline_sequence_diagram["src"] == './_images/sequencediagram-index-0.png'  # noqa
    assert file_sequence_diagram["src"] == './_images/sequencediagram-index-1.png'  # noqa

    # compare file contents to make sure the created image isn't malformed
    generated_vs_expected = [
        ('sequencediagram-index-0.png', 'inline_sequence_diagram.png'),
        ('sequencediagram-index-1.png', 'file_sequence_diagram.png'),
    ]
    for generated, expected in generated_vs_expected:
        generated_filepath = os.path.join(BUILD_PATH, '_images', generated)
        expected_filepath = os.path.join(IMAGES_FIXTURE_PATH, expected)
        with open(generated_filepath, 'rb') as generated_image:
            with open(expected_filepath, 'rb') as expected_image:
                assert generated_image.read() == expected_image.read()
