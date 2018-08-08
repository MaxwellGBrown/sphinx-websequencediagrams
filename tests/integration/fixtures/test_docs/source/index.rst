.. sequencediagram::
   :format: png
   :alt: This is an inline sequence diagram

   title Inline Sequence Diagram

   sphinx-websequencediagram ->+ www.websequencediagram.com: POST /  { message: <message> }
   www.websequencediagram.com ->- sphinx-websequencediagram: 200 OK  { img: "?png=abc123" }

   sphinx-websequencediagram ->+ www.websequencediagram.com: GET /?png=abc123
   www.websequencediagram.com ->- sphinx-websequencediagram: 200 OK


.. sequencediagram::
   :file: sequence_diagram.txt
