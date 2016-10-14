# nose-tag

nose-tag plugin enhances the existing built-in attrib plugin.

Enhancements:

Attribute Prefix - Attributes added using the attr decorator should pre prefixed with a unique string to make finding all nose attributes easier and to minimize the likelihood of name collisions.

Collect Attributes - Because we now know all attributes added by nose we can ask the question what are all the attributes a method has. Option --attr-collect will print all selected tests and the attributes for that test in JSON form to stdout.

Better Selection - Improve the evaluation of expression parameters.
       - Not yet implemented