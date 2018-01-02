"""Module for connecting to sphinx."""
import os.path
import re
import urllib

from docutils import nodes
from docutils.parsers.rst import Directive
from sphinx.util import logging


log = logging.getLogger(__name__)


class sequencediagram(nodes.image):
    """Node class for sequencediagram directive."""

    def __init__(self, content):
        """Save content & then instantiate nodes.image."""
        self.sequence_text = content
        super().__init__()


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
        target_id = "sequencediagram-{}".format(
            env.new_serialno("sequencediagram")
        )
        target_node = nodes.target("", "", ids=[target_id])

        # Create a sequence diagarm w/ the text in the directive
        node = sequencediagram("\n".join(self.content))
        # node["uri"] = "https://vignette.wikia.nocookie.net/seinfeld/images/7/76/George-costanza.jpg/revision/latest?cb=20110406222711" # noqa
        # TODO Read directive attributes for alt
        node["alt"] = target_id

        return [target_node, node]


def purge_sequencediagrams(app, env, docname):
    """Clear any data in the environment persistant env."""
    pass


def process_sequencediagram_nodes(app, doctree, fromdocname):
    """Extra processing on collected sequencediagram nodes."""
    for node in doctree.traverse(sequencediagram):
        log.info("Processing %s", node["alt"])
        # hit www.websequencediagrams.com to create an image
        # https://www.websequencediagrams.com/embedding.html#python
        image_path = os.path.join(app.builder.outdir, "_static", node["alt"])
        with open(image_path, "w") as image_file:
            request = {
                "message": node.sequence_text,
                # TODO Make "style" configurable via node &/or settings
                "style": "default",
                "appVersion": "1"
            }

            url = urllib.urlencode(request)
            with urllib.urlopen("http://websequencediagrams.com/", url) as f:
                response = f.readline()

            expression = re.compile("(\?(img|pdf|png|svg)=[a-zA-Z0-9]+)")
            message = expression.search(response)

            if message is None:
                log.warning("Could not build sequence diagram %s", node["alt"])

            image_file.write(message)

        node["uri"] = app.builder.get_relative_uri("_static", node["alt"])


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
