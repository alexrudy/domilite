# Domilite

[![PyPI - Version](https://img.shields.io/pypi/v/domilite.svg)](https://pypi.org/project/domilite)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/domilite.svg)](https://pypi.org/project/domilite)
[![Tests](https://github.com/alexrudy/domilite/workflows/Tests/badge.svg)](https://github.com/alexrudy/domilite/workflows/Tests/)
[![Docs](https://img.shields.io/readthedocs/domilite)](https://domilite.readthedocs.io/en/latest/)

[Domilite][] is a lightweight (0-dependency) Python library for creating and manipulating HTML elements.

It takes inspiration from [dominate][], a great library for creating HTML elements in Python. Domilite aims to simplify the interface from [dominate][], providing a smaller set of APIs while maintaining general compatibility with the library.

Create HTML elements from code, and render them formatted:
```python
from domilite import tags

html = tags.html(tags.head(tags.title('welcome')))
html.add(tags.body(tags.h1('welcome to domilite', id='title')))
html[1].classes.add('style-from-code')
print(html)
```

This produces

```html
<html>
  <head><title>welcome</title></head>
  <body class="style-from-code">
    <h1 id="title">welcome to domilite</h1>
  </body>
</html>
```

You can find the docs at <https://domilite.readthedocs.io/en/latest/>

[dominate]: https://github.com/Knio/dominate
[Domilite]: https://domilite.readthedocs.io/en/latest/
