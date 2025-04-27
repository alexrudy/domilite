Getting Started
===============

Installing :mod:`domilite`
--------------------------

Install :mod:`domilite` with ``pip``::

    pip install domilite

That's about all there is to it!

Now you can import domilite and start creating tags::

    from domilite import tags

    title = tags.h1('welcome', id='title')
    article = tags.article(title)
