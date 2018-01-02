# sphinx-websequencediagrams
A Sphinx Directive for creating Sequence Diagrams using www.websequencediagrams.com

# Setup

1. Install the package

   ```
   pip install git+https://github.com/MaxwellGBrown/sphinx-websequencediagrams
   ```

2. Update your sphinx `conf.py` to include the package

   ```
   extensions = ["sphinx_websequencediagrams"]
   ```

3. Use the `sequencediagram` directive in your RST!

   ```
   .. sequencediagram:
   
      A->B: A to B
	  B->A: B to A
   ```
