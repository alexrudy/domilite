from domilite.dom_tag import Flags
from domilite.tags import html_tag

DASHED_ATTRIBUTES = {
    "accent",
    "alignment",
    "arabic",
    "baseline",
    "cap",
    "clip",
    "color",
    "dominant",
    "enable",
    "fill",
    "flood",
    "font",
    "glyph",
    "horiz",
    "image",
    "letter",
    "lighting",
    "marker",
    "overline",
    "paint",
    "panose",
    "pointer",
    "rendering",
    "shape",
    "stop",
    "strikethrough",
    "stroke",
    "text",
    "underline",
    "unicode",
    "units",
    "v",
    "vector",
    "vert",
    "word",
    "writing",
    "x",
}


class svg_tag(html_tag):
    @staticmethod
    def normalize_attribute(attribute: str) -> str:
        words = attribute.split("_")
        if words[0] in DASHED_ATTRIBUTES:
            return attribute.replace("_", "-")
        return attribute


class svg(svg_tag):
    """SVG tag class"""


class animate(svg_tag):
    """The animate tag class is used to animate an element's attributes over time."""


class animateMotion(svg_tag):
    """The animateMotion tag is used to animate an element's motion over time."""


class animateTransform(svg_tag):
    """The animateTransform tag is used to animate an element's transformation over time."""

    flags = Flags.SINGLE | Flags.PRETTY


class circle(svg_tag):
    """The circle tag is used to draw a circle."""


class clipPath(svg_tag):
    """The clipPath tag is used to define a clipping path."""


class defs(svg_tag):
    """The defs tag is used to define elements that can be reused throughout the SVG document."""


class desc(svg_tag):
    """The desc tag is used to provide a description of the SVG document."""


class ellipse(svg_tag):
    """The ellipse tag is used to draw an ellipse."""


class g(svg_tag):
    """The g tag is used to group SVG elements together."""


class image(svg_tag):
    """The image tag is used to embed an image into an SVG document."""


class line(svg_tag):
    """The line tag is used to draw a line."""


class linearGradient(svg_tag):
    """The linearGradient tag is used to define a linear gradient."""


class marker(svg_tag):
    """The <marker> element defines the graphic that is to be used for drawing arrowheads or polymarkers on a given <path>, <line>, <polyline> or <polygon> element."""


class mask(svg_tag):
    """The <mask> element defines a mask."""


class mpath(svg_tag):
    """The <mpath> element is used to reference a path element for use in a mask."""


class pattern(svg_tag):
    """The <pattern> element is used to define a pattern that can be used to fill or stroke an element."""


class polygon(svg_tag):
    """The polygon tag is used to draw a polygon."""


class radialGradient(svg_tag):
    """The radialGradient tag is used to define a radial gradient."""


class path(svg_tag):
    """The path tag is used to define a path."""


class rect(svg_tag):
    """The rect tag is used to draw a rectangle."""


class stop(svg_tag):
    """The svg tag is used to define an SVG document."""


class switch(svg_tag):
    """The switch tag is used to define a group of elements that can be used to switch between different elements."""


class symbol(svg_tag):
    """The symbol tag is used to define a graphics object that can be referenced by other elements."""


class text(svg_tag):
    """The text tag is used to define text."""


class textPath(svg_tag):
    """The textPath tag is used to define a path for text."""


class title(svg_tag):
    """The title tag is used to define a title for an element."""


class tspan(svg_tag):
    """The tspan tag is used to define a subregion of text."""


class use(svg_tag):
    """The use tag is used to reuse an element."""


class view(svg_tag):
    """The view tag is used to define a view of an SVG document."""


class filter(svg_tag):
    pass


class feBlend(svg_tag):
    pass


class feColorMatrix(svg_tag):
    pass


class feComponentTransfer(svg_tag):
    pass


class feComposite(svg_tag):
    pass


class feConvolveMatrix(svg_tag):
    pass


class feDiffuseLighting(svg_tag):
    pass


class feDisplacementMap(svg_tag):
    pass


class feFlood(svg_tag):
    pass


class feGaussianBlur(svg_tag):
    pass


class feImage(svg_tag):
    pass


class feMerge(svg_tag):
    pass


class feMorphology(svg_tag):
    pass


class feOffset(svg_tag):
    pass


class feSpecularLighting(svg_tag):
    pass


class feTile(svg_tag):
    pass


class feTurbulence(svg_tag):
    pass


class feDistantLight(svg_tag):
    pass


class fePointLight(svg_tag):
    pass


class feSpotLight(svg_tag):
    pass
