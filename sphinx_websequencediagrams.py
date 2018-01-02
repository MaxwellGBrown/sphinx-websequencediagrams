"""Module for connecting to sphinx."""
import os
import os.path
import re
import urllib.request
import urllib.parse

from docutils import nodes
from docutils.parsers.rst import Directive
from sphinx.util import logging
from sphinx.util.osutil import ensuredir

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
        # TODO Read directive attributes for alt
        node["alt"] = target_id
        # Create a future URI for the eventual sequencediagram
        filename = "{}.png".format(target_id)
        node["uri"] = os.path.join("/", env.app.builder.outdir, env.app.builder.imagedir, filename)  # noqa
        log.info("node['uri']: %s", node["uri"])

        return [target_node, node]


def purge_sequencediagrams(app, env, docname):
    """Clear any data in the environment persistant env."""
    pass


def process_sequencediagram_nodes(app, doctree, fromdocname):
    """Extra processing on collected sequencediagram nodes."""
    # Ensure the images directory exists before we start writing to it
    ensuredir(os.path.join(app.builder.outdir, app.builder.imagedir))

    for node in doctree.traverse(sequencediagram):
        log.info("Processing %s", node["uri"])
        # hit www.websequencediagrams.com to create an image
        # https://www.websequencediagrams.com/embedding.html#python
        with open("/" + node["uri"], "w") as image_file:
            request = {
                "message": node.sequence_text,
                # TODO Make "style" configurable via node &/or settings
                "style": "default",
                "appVersion": "1"
            }

            url = urllib.parse.urlencode(request).encode()
            with urllib.request.urlopen("http://websequencediagrams.com/", url) as raw_response:  # noqa
                response = raw_response.readline()
                log.info(response)

            expression = re.compile("(\?(img|pdf|png|svg)=[a-zA-Z0-9]+)")
            message = expression.search(response)

            if message is None:
                log.warning("Could not build sequence diagram %s", node["alt"])

            image_file.write(message)


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
