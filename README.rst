sphinx-websequencediagrams
==========================

A Sphinx Directive for creating Sequence Diagrams using www.websequencediagrams.com.

Setup
-----

#. Install the package

   ::
   
     pip install sphinx-websequencediagrams


#. Update your sphinx ``conf.py`` to include the package

   ::
   
     extensions = ["sphinx_websequencediagrams"]


#. Use the ``sequencediagram`` directive in your RST!

   ::
   
     .. sequencediagram:
     
        A->B: A to B
        B->A: B to A


Usage
-----

Visit www.websequencediagrams.com to see how to compose a sequence diagram!


Sequence Diagram from text
~~~~~~~~~~~~~~~~~~~~~~~~~~

To compose a sequence diagram, use the ``.. sequencediagram::`` directive.

::

  .. sequencediagram::

     A -> B
     B -> A

.. TODO Show an image of the example output


Sequence Diagram from file
~~~~~~~~~~~~~~~~~~~~~~~~~~

The contents of a ``.. sequencediagram::`` directive can also be supplied via a file.

::

  # source/index.rst
 
  .. sequencediagram::
     :file: a_to_b.txt

::

  # source/a_to_b.txt

  A -> B
  B -> A


.. TODO Show an image of the example output


.. note::

   All filepaths supplied to the ``:file:`` option are relative to your documentation's source directory
