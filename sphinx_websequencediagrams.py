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


class WebSequenceDiagram(object):
    """Manages interaction with www.websequencediagrams.com.

    This class's only responsibility is to ensure that requests made to the
    api are made correctly, and that the responses are read into an io stream.
    """

    _api_url = "http://www.websequencediagrams.com/"

    class WebSequenceDiagramError(Exception):
        """Exception for any errors returned by www.websequencediagrams.com."""

        pass

    def __init__(self, message, **kwargs):
        """Send message to websequencediagram.com."""
        self.request_body = {"message": message, **kwargs}
        self.request_body.setdefault("style", "default")
        self.request_body.setdefault("format", "png")
        self.request_body.setdefault("appVersion", "1")
        # TODO The application sets this in request; do we mess w/ this too?
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

    # this enables content in the directive (wtf does that mean?)
    has_content = True

    option_spec = {
        "file": directives.path,
        # TODO Discover the other style names
        "style": lambda x: directives.choice(x, ("default", "forest")),
        "format": lambda x: directives.choice(x, ("png", "svg", "pdf")),
        "alt": str,
    }

    default_options = {
        "style": "default",
        "format": "png",
    }

    def run(self):
        """Process an RST sequencediagram directive and return it's nodes."""
        self.options = {**self.default_options, **self.options}

        env = self.state.document.settings.env

        # Create a "target_node" so we can link to this sequencediagram
        target_id = "sequencediagram-{}-{}".format(
            os.path.basename(env.docname), env.new_serialno('sequencediagram')
        )
        target_node = nodes.target("", "", ids=[target_id])

        # Create a sequence diagarm w/ the text in the directive
        if "file" in self.options:
            try:
                with open(self.options["file"], 'r') as sequence_diagram_file:
                    text_diagram = sequence_diagram_file.read()
            except FileNotFoundError:
                log.error("Could not read Sequence Diagram from file %s",
                          self.options["file"])
                return []
        else:
            text_diagram = "\n".join(self.content)

        node = sequencediagram()

        filename = "{}.{}".format(target_id, self.options["format"])
        ensuredir(
            os.path.join(env.app.builder.outdir, env.app.builder.imagedir)
        )
        build_filepath = os.path.join(
            env.app.builder.outdir,
            env.app.builder.imagedir,
            filename,
        )

        log.info("Downloading %s", build_filepath)
        with WebSequenceDiagram(text_diagram, **self.options) as http_diagram:
            with open(build_filepath, "wb") as source_diagram:
                shutil.copyfileobj(http_diagram, source_diagram)

        # Set src relative to build path & document build location
        relative_location = os.path.relpath(
            env.srcdir, os.path.dirname(env.doc2path(env.docname))
        )
        node["src"] = os.path.join(
            relative_location,
            os.path.relpath(build_filepath, env.app.outdir),
        )

        node["uri"] = os.path.relpath(build_filepath, env.app.outdir)
        node["alt"] = self.options.get("alt", target_id)
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
    app.add_directive("sequencediagram", SequenceDiagramDirective)

    # custom node for writing sequencediagram directive to HTML
    app.add_node(
        sequencediagram,
        html=(visit_sequencediagram_node, depart_sequencediagram_node),
    )

    return {'version': '0.0'}  # Identify version of the extension in return
