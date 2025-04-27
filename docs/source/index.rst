Domilite - Code your HTML in Python
===================================

.. language: python

:mod:`domilite` is a lightweight library for programatically building HTML fragments and documents. It is heavily inspired by
`dominate`_, but built with a little bit less in mind. `dominate`_ supports context managers, function decorators, and other
syntax helpers - if those features are important to you, head to that library. :mod:`domilite` does not support those features,
favoring to only expose the more explicit interfaces, and with that practice, add strong typing support:

>>> from domilite import tags
>>> html = tags.html(tags.head(tags.title('welcome')))
>>> html.add(tags.body(tags.h1('welcome to domilite', id='title')))
>>> html[1].classes.add('style-from-code')
>>> print(html)
<html>
    <head><title>welcome</title></head>
    <body>
    <h1>hello</h1>
    </body>
</html>

:mod:`domilite` also adds support for css classes as first class components. Each element has a :attr:`~dom_tag.classes` which can be used to
interact with classes as a set-like object, rather than a whitespace delimited string:

>>> from domilite import tags
>>> html = tags.html()
>>> html.classes.add('my-class', 'beautify')
>>> print(html)
<html class="my-class beautify"></html>


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   install
   reference
   internals

.. _dominate: https://pypi.org/project/dominate/
