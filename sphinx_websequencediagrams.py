"""Module for connecting to sphinx."""
from docutils import nodes
from docutils.parsers.rst import Directive


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
        target_id = "sequencediagram-{}".format(
            env.new_serialno("sequencediagram")
        )
        target_node = nodes.target("", "", ids=[target_id])

        # TODO Make a sequence diagram image using www.websequenceiagrams.com
        node = sequencediagram()
        node["src"] = "https://vignette.wikia.nocookie.net/seinfeld/images/7/76/George-costanza.jpg/revision/latest?cb=20110406222711" # noqa
        node["alt"] = "sequencediagram"

        return [target_node, node]


def purge_sequencediagrams(app, env, docname):
    """Clear any data in the environment persistant env."""
    pass


def process_sequencediagram_nodes(app, doctree, fromdocname):
    """Extra processing on collected sequencediagram nodes."""
    pass


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
