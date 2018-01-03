"""Module for connecting to sphinx."""
import os
import os.path
import shutil
import tempfile
import urllib.request
import urllib.parse

from docutils import nodes
from docutils.parsers.rst import Directive
from sphinx.util import logging
from sphinx.util.osutil import ensuredir

log = logging.getLogger(__name__)


class WebSequenceDiagram(object):
    """Manages interaction with WebSequenceDiagrams."""

    api_url = "http://www.websequencediagrams.com/"

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
        with urllib.request.urlopen(self.api_url, body) as connection:
            response_body = connection.read().decode()

        response = urllib.parse.parse_qs(response_body)

        if response.get("errors"):
            raise self.WebSequenceDiagramError(response["errors"])

        return urllib.parse.urljoin(self.api_url, response["img"])

    def __enter__(self):
        """Create and operate on a diagram as a file-like object."""
        image_url = self.create_diagram()
        return urllib.request.urlopen(image_url)

    def __exit__(self, *args):
        """Close any open URL connections made for retrieving diagrams."""
        return  # the responses from urllib.request.urlopen close themselves


class sequencediagram(nodes.image):
    """Node class for sequencediagram directive."""

    pass


def visit_sequencediagram_node(self, node):
    """Start node context for a sequencediagram.

    For example, the opening html tag
    --> <p>
          Some Text
        </p>
    """
    self.visit_image(node)


def depart_sequencediagram_node(self, node):
    """Close node context for a sequencediagram.

    For example, the opening html tag
        <p>
          Some Text
    --> </p>
    """
    self.depart_image(node)


class SequenceDiagramDirective(Directive):
    """Class that determines directive attributes, markup, & run results."""

    # this enables content in the directive (wtf does that mean?)
    has_content = True

    def run(self):
        """Process an RST sequencediagram directive and return it's nodes."""
        env = self.state.document.settings.env

        # Create a "target_node" so we can link to this sequencediagram
        # TODO Read directive attributes for name/title/id
        target_id = "sequencediagram-{}".format(
            env.new_serialno("sequencediagram")
        )
        target_node = nodes.target("", "", ids=[target_id])

        # Create a sequence diagarm w/ the text in the directive
        # TODO Read directive attributes for a file to get content from
        sequence_diagram_text = "\n".join(self.content)

        node = sequencediagram()
        options = {
            # TODO Read directive attributes for alt
            # TODO Read directive attributes for style
            # TODO Read directive attributes for format
        }
        with WebSequenceDiagram(sequence_diagram_text, **options) as diagram:
            # TODO Have suffix be set by whatever is determining the filetype
            temp_diagram = tempfile.NamedTemporaryFile("wb", suffix="png",
                                                       delete=False)
            shutil.copyfileobj(diagram, temp_diagram)
            node['uri'] = temp_diagram.name

        node["alt"] = target_id
        log.info("node['uri']: %s", node["uri"])
        return [target_node, node]


def purge_sequencediagrams(app, env, docname):
    """Clear any data in the environment persistant env."""
    pass


def process_sequencediagram_nodes(app, doctree, fromdocname):
    """Extra processing on sequencediagram nodes after all nodes are created.

    This is the point in which we can do the web requests, copy the images
    into the build, & reassociate the URI with the build file.
    """
    # Ensure the images directory exists before we start writing to it
    ensuredir(os.path.join(app.builder.outdir, app.builder.imagedir))

    for node in doctree.traverse(sequencediagram):
        # Move diagram's temporary file to the build
        filename = os.path.basename(node["uri"])
        build_uri = os.path.join(app.builder.imagedir, filename)
        log.info("Moving diagram from %s to %s", node["uri"], build_uri)
        shutil.move(node["uri"], build_uri)


def setup(app):
    """Add the sequencediagram directive to Sphinx."""
    app.add_config_value("include_sequencediagrams", True, "html")

    app.add_node(
        sequencediagram,
        html=(visit_sequencediagram_node, depart_sequencediagram_node),
    )

    app.add_directive("sequencediagram", SequenceDiagramDirective)

    app.connect("doctree-resolved", process_sequencediagram_nodes)
    app.connect("env-purge-doc", purge_sequencediagrams)

    return {'version': '0.0'}  # Identify version of the extension in return
