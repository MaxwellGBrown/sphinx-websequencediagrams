"""Module for connecting to sphinx."""
import os
import os.path
import shutil
import urllib.request
import urllib.parse

import demjson
from docutils import nodes
from docutils.parsers.rst import Directive
from docutils.parsers.rst import directives
from sphinx.util import logging
from sphinx.util.osutil import ensuredir


log = logging.getLogger(__name__)


# The directive in .rst to activate a sequence diagram
SEQUENCE_DIAGRAM_DIRECTIVE = "sequencediagram"


class WebSequenceDiagram(object):
    """Manages interaction with www.websequencediagrams.com.

    This class's only responsibility is to ensure that requests made to the
    api are made correctly, and that the responses are read into an io stream.
    """

    _api_url = "https://www.websequencediagrams.com/"

    class WebSequenceDiagramError(Exception):
        """Exception for any errors returned by www.websequencediagrams.com."""

        pass

    def __init__(self, message, **kwargs):
        """Send message to websequencediagram.com."""
        self.request_body = {"message": message, **kwargs}
        self.request_body.setdefault("style", "default")
        self.request_body.setdefault("format", "png")
        self.request_body.setdefault("appVersion", "1")
        # There is no default for width but one can be sent
        # self.request_body.setdefault("width", 1000)

        self._context = None

    def create_diagram(self):
        """Create diagram via websequencediagram.com. Returns diagram URL."""
        body = urllib.parse.urlencode(self.request_body).encode()
        with urllib.request.urlopen(self._api_url, body) as response_io:
            response_body = response_io.read().decode()

        # The response is a JavaScript object instead of a JSON object
        response = demjson.decode(response_body)

        if response.get("errors"):
            raise self.WebSequenceDiagramError(response["errors"])

        return urllib.parse.urljoin(self._api_url, response["img"])

    def __enter__(self):
        """Create and operate on a diagram as a file-like object."""
        image_url = self.create_diagram()
        return urllib.request.urlopen(image_url)

    def __exit__(self, *args):
        """Close any open URL connections made for retrieving diagrams."""
        return  # the responses from urllib.request.urlopen close themselves


class SequenceDiagramDirective(Directive):
    """Class that determines directive attributes, markup, & run results."""

    has_content = True  # this enables content in the dierective

    option_spec = {
        "file": directives.path,
        "style": str,
        "format": str,
        "alt": str,
    }

    default_options = {
        "style": "default",
        "format": "png",
    }

    _target_id = ""  # See @property target_id

    @property
    def env(self):
        """Shortcut to self.state.document.settings.env.

        This is the Sphinx runtime environment that is referenced for many
        operations.
        """
        return self.state.document.settings.env

    @property
    def target_id(self):
        """Create or return this directive's `target_id`.

        If one hasn't been created yet one is generated with the help of
        the Sphinx Environment's `new_serialno`.
        """
        if not self._target_id:
            self._target_id = "{}-{}-{}".format(
                SEQUENCE_DIAGRAM_DIRECTIVE,
                os.path.basename(self.env.docname),
                self.env.new_serialno(SEQUENCE_DIAGRAM_DIRECTIVE)
            )
        return self._target_id

    @property
    def build_filepath(self):
        """Compose the output filepath of the generated sequence diagram."""
        filename = "{}.{}".format(self.target_id, self.options["format"])
        return os.path.join(
            self.env.app.builder.outdir,
            self.env.app.builder.imagedir,
            filename,
        )

    @property
    def src(self):
        """Compose the node's src relative to it's parent document."""
        relative_location = os.path.relpath(
            self.env.srcdir,
            os.path.dirname(self.env.doc2path(self.env.docname)),
        )
        return os.path.join(
            relative_location,
            os.path.relpath(self.build_filepath, self.env.app.outdir),
        )

    def _ensure_build_images_dir(self):
        """Ensure build directories for self.build_filepath exist.

        This will create directories that do not already exist in that path.
        """
        build_image_dir = os.path.join(self.env.app.builder.outdir,
                                       self.env.app.builder.imagedir)
        ensuredir(build_image_dir)

    def _read_contents(self):
        """Read the contents of the directive.

        If :file: was supplied, read them from the specified file.

        If :file: cannot be read, returns an empty string.
        """
        if "file" in self.options:
            source_filepath = os.path.join(self.env.srcdir,
                                           self.options["file"])
            try:
                with open(source_filepath, 'r') as sequence_diagram_file:
                    log.info("Reading sequence diagram from %s",
                             source_filepath)
                    return sequence_diagram_file.read()
            except FileNotFoundError:
                log.error("Could not read Sequence Diagram from file %s",
                          self.options["file"])
                return ""

        return "\n".join(self.content)

    def run(self):
        """Process an RST sequencediagram directive and return it's nodes."""
        self.options = {**self.default_options, **self.options}

        text_diagram = self._read_contents()
        if not text_diagram:
            log.warning("No contents for sequence diagram %s in %s.",
                        self.target_id, self.env.docname)
            return []

        log.info("Downloading %s", self.build_filepath)
        with WebSequenceDiagram(text_diagram, **self.options) as http_diagram:
            self._ensure_build_images_dir()
            with open(self.build_filepath, "wb") as source_diagram:
                shutil.copyfileobj(http_diagram, source_diagram)

        # Create a "target_node" so we can link to this sequencediagram
        target_node = nodes.target("", "", ids=[self.target_id])

        node = sequencediagram()
        node["src"] = self.src
        node["alt"] = self.options.get("alt", self.target_id)

        return [target_node, node]


# -----------------------------------------------------------------------------
# Docutil Nodes used to handle .. sequencediagram::
# -----------------------------------------------------------------------------
class sequencediagram(nodes.literal):
    """Node class for sequencediagram directive that inherits from literal.

    Opted NOT to inherit from nodes.image because there's too much
    baggage coming from Sphinx processing image nodes.
    """

    pass


def visit_sequencediagram_node(self, node):
    """Start node context for a sequencediagram.

    For example, the opening html tag...
    --> <p>
          Some Text
        </p>
    """
    # Simplified from docutils.writers._html_base.HTMLTranslator.visit_image
    attrs = {"src": node["src"], "alt": node["alt"]}
    self.body.append(self.emptytag(node, "img", "\n", **attrs))


def depart_sequencediagram_node(self, node):
    """Close node context for a sequencediagram.

    For example, the closing html tag...
        <p>
          Some Text
    --> </p>
    """
    pass
# -----------------------------------------------------------------------------


def setup(app):
    """Add the sequencediagram directive to Sphinx."""
    app.add_config_value("include_sequencediagrams", True, "html")

    # custom directive for parsing ..sequencediagram:: from .rst
    app.add_directive(SEQUENCE_DIAGRAM_DIRECTIVE, SequenceDiagramDirective)

    # custom node for writing sequencediagram directive to HTML
    app.add_node(
        sequencediagram,
        html=(visit_sequencediagram_node, depart_sequencediagram_node),
    )

    return {'version': '0.3.3'}
