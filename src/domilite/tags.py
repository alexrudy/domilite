from markupsafe import Markup

from domilite.accessors import PrefixAccessor
from domilite.dom_tag import dom_tag
from domilite.dom_tag import Flags


class html_tag(dom_tag):
    """Any valid HTML tag"""

    data = PrefixAccessor("data")
    aria = PrefixAccessor("aria")
    hx = PrefixAccessor("hx")


class html(html_tag):
    """The root element of an HTML document"""


class head(html_tag):
    """The <head> HTML element contains machine-readable information (metadata) about the document, like its title, scripts, and style sheets. There can be only one <head> element in an HTML document."""


class title(html_tag):
    """The <title> HTML element defines the document's title that is shown in a browser's title bar or a page's tab. It only contains text; tags within the element are ignored."""

    flags = Flags.SINGLE | Flags.PRETTY

    @property
    def text(self) -> str:
        return "".join(child for child in self.children if isinstance(child, Markup))

    @text.setter
    def text(self, value: str) -> None:
        self.children[:] = [Markup(value)]


class base(html_tag):
    """The <base> HTML element specifies the base URL to use for all relative URLs contained within a document. There can be only one <base> element in an HTML document."""

    flags = Flags.SINGLE | Flags.PRETTY


class link(html_tag):
    """The <link> HTML element specifies relationships between the current document and an external resource. This element is most commonly used to link to stylesheets, but is also used to establish site icons (both "favicon" style icons and icons for the home screen and apps on mobile devices) among other things."""

    flags = Flags.SINGLE | Flags.PRETTY


class meta(html_tag):
    """The <meta> HTML element represents metadata that cannot be represented by other HTML meta-related elements, like base, link, script, style or title."""

    flags = Flags.SINGLE | Flags.PRETTY


class style(html_tag):
    """The <style> HTML element contains style information for a document, or part of a document. It contains CSS, which is applied to the contents of the document containing the <style> element."""

    flags = Flags(0)


class script(html_tag):
    """The <script> HTML element is used to embed executable code or data; this is typically used to embed or refer to JavaScript code."""

    flags = Flags(0)


class noscript(html_tag):
    """The <noscript> HTML element defines a section of HTML to be inserted if a script type on the page is unsupported or if scripting is currently turned off in the browser."""


class body(html_tag):
    """The <body> HTML element represents the content of an HTML document. There can be only one <body> element in an HTML document."""


class main(html_tag):
    """The <main> HTML element represents the dominant content of the body of a document. The main content area consists of content that is directly related to or expands upon the central topic of a document, or the central functionality of an application."""


class section(html_tag):
    """The <section> HTML element represents a standalone section of functionality contained within an HTML document, typically with a heading, which doesn't have a more specific semantic element to represent it."""


class nav(html_tag):
    """The <nav> HTML element represents a section of a page that links to other pages or to parts within the page: a section with navigation links."""


class article(html_tag):
    """The <article> HTML element represents a self-contained composition in a document, page, application, or site, which is intended to be independently distributable or reusable (e.g., in syndication). Examples include: a forum post, a magazine or newspaper article, or a blog entry, a product card, a user-submitted comment, an interactive widget or gadget, or any other independent item of content."""


class aside(html_tag):
    """The <aside> HTML element represents a section of a document with content connected tangentially to the rest, which could be considered separate from that content. These sections are often represented as sidebars or inserts. They often contain the definitions on the sidebars, such as definitions from the glossary; there may also be other types of information, such as related advertisements; the biography of the author; web applications; profile information or related links on the blog."""


class h1(html_tag):
    """The <h1> HTML element represents the most important heading on the page."""


class h2(html_tag):
    """The <h2> HTML element represents a second-level heading on the page."""


class h3(html_tag):
    """The <h3> HTML element represents a third-level heading on the page."""


class h4(html_tag):
    """The <h4> HTML element represents a fourth-level heading on the page."""


class h5(html_tag):
    """The <h5> HTML element represents a fifth-level heading on the page."""


class h6(html_tag):
    """The <h6> HTML element represents a sixth-level heading on the page."""


class hgroup(html_tag):
    """The <hgroup> HTML element represents a group of <h1> to <h6> elements that form a heading for a section of the document."""


class header(html_tag):
    """The <header> HTML element represents introductory content for a document or an article. It typically contains a section heading followed by a brief summary of the document or article."""


class address(html_tag):
    """The <address> HTML element indicates that the enclosed HTML provides contact information for a person or people, or for an organization."""


class p(html_tag):
    """The <p> HTML element represents a paragraph of text."""


class hr(html_tag):
    """The <hr> HTML element represents a thematic break between paragraph-level elements."""

    flags = Flags.SINGLE | Flags.PRETTY


class pre(html_tag):
    """The <pre> HTML element represents preformatted text which is to be presented exactly as written in the HTML file."""

    flags = Flags(0)


class blockquote(html_tag):
    """The <blockquote> HTML element indicates that the enclosed text is an extended quotation. Usually, this is rendered visually by indentation."""


class ol(html_tag):
    """The <ol> HTML element represents an ordered list of items, typically rendered with a numbered list."""


class ul(html_tag):
    """The <ul> HTML element represents an unordered list of items, typically rendered with bullet points."""


class li(html_tag):
    """The <li> HTML element represents an item in a list."""


class dl(html_tag):
    """The <dl> HTML element represents a description list. The element encloses a list of groups of terms (specified using the <dt> element) and descriptions (provided by <dd> elements). Common uses for this element are to implement a glossary or to display metadata (a list of key-value pairs)."""


class dt(html_tag):
    """The <dt> HTML element specifies a term in a description or definition list, and as such must be used inside a <dl> element."""


class dd(html_tag):
    """The <dd> HTML element provides the description, definition, or value for the preceding term (dt) in a description list (dl)."""


class figure(html_tag):
    """The <figure> HTML element represents self-contained content, potentially with an optional caption, which is specified using the <figcaption> element."""


class figcaption(html_tag):
    """The <figcaption> HTML element represents a caption or legend describing the rest of the contents of its parent <figure> element."""


class div(html_tag):
    """The <div> HTML element is a generic container for flow content. It has no effect on the content or layout until styled in some way using CSS (e.g. styling is directly applied to it, or some kind of layout model like Flexbox is applied to its parent element)."""


class a(html_tag):
    """The <a> HTML element (or anchor element), with its href attribute, creates a hyperlink to web pages, files, email addresses, locations in the same page, or anything else a URL can address."""


class em(html_tag):
    """The <em> HTML element marks text that has stress emphasis. The <em> element can be nested, with each level of nesting indicating a greater degree of emphasis."""


class strong(html_tag):
    """The <strong> HTML element indicates that its contents have strong importance, seriousness, or urgency. Browsers typically render the contents in bold type."""


class small(html_tag):
    """The <small> HTML element represents side comments such as copyright, contact information, or legal restrictions for the document or an article."""


class s(html_tag):
    """The <s> HTML element represents content that is no longer accurate or no longer relevant."""


class cite(html_tag):
    """The <cite> HTML element is used to describe a reference to a cited creative work, and must include the title of that work."""


class q(html_tag):
    """The <q> HTML element indicates that the enclosed text is a short inline quotation. Most modern browsers implement this by surrounding the text in quotation marks."""


class dfn(html_tag):
    """The <dfn> HTML element represents the defining instance of a term."""


class abbr(html_tag):
    """The <abbr> HTML element represents an abbreviation or acronym."""


class time(html_tag):
    """The <time> HTML element represents a specific period in time."""


class code(html_tag):
    """The <code> HTML element represents a fragment of computer code."""


class var(html_tag):
    """The <var> HTML element represents a variable in a mathematical expression or a programming context."""


class samp(html_tag):
    """The <samp> HTML element represents sample output from a computer program."""


class kbd(html_tag):
    """The <kbd> HTML element represents user input text."""


class sub(html_tag):
    """The <sub> HTML element represents a subscript."""


class sup(html_tag):
    """The <sup> HTML element represents a superscript."""


class i(html_tag):
    """The <i> HTML element represents a range of text that is set off from the normal text for some reason, such as idiomatic text, technical terms, taxonomical designations, among others."""

    flags = Flags.INLINE | Flags.PRETTY


class b(html_tag):
    """The <b> HTML element represents a span of text stylistically different from normal text, without conveying any special importance or relevance. It is typically used for keywords in a summary, product names in a review, or other spans of text whose typical presentation would be boldfaced. Another example of its use is to mark the lead sentence of each paragraph of an article."""


class u(html_tag):
    """The <u> HTML element represents a span of text with an unarticulated, though explicitly rendered, non-textual annotation, such as labeling the text as being a proper name in Chinese text (a Chinese proper name mark), or labeling the text as being misspelt."""


class mark(html_tag):
    """The <mark> HTML element represents text which is marked or highlighted for reference or notation purposes, due to the marked passage's relevance or importance in the enclosing context."""


class ruby(html_tag):
    """The <ruby> HTML element represents small annotations that are rendered above, below, or next to base text, usually used for showing the pronunciation of East Asian characters."""


class rt(html_tag):
    """The <rt> HTML element specifies the ruby text component of a ruby annotation, which is used to provide pronunciation, translation, or transliteration information for East Asian typography. The <rt> element must always be contained within a <ruby> element."""


class rp(html_tag):
    """The <rp> HTML element is used to provide fall-back parentheses for browsers that do not support display of ruby annotations using the ruby element."""


class bdi(html_tag):
    """The <bdi> HTML element tells the browser's bidirectional algorithm to treat the text it contains in isolation from its surrounding text."""


class bdo(html_tag):
    """The <bdo> HTML element overrides the current directionality of text, so that the text within is rendered in a different direction."""


class span(html_tag):
    """The <span> HTML element is a generic inline container for phrasing content, which does not inherently represent anything. It can be used to group elements for styling purposes (using the class or id attributes), or because they share attribute values, such as lang. It should be used only when no other semantic element is appropriate. <span> is very much like a <div> element, but <div> is a block-level element whereas a <span> is an inline element."""


class br(html_tag):
    """The <br> HTML element produces a line break in text (carriage-return). It is useful for writing a poem or an address, where the division of lines is significant."""

    flags = Flags.SINGLE | Flags.INLINE | Flags.PRETTY


class wbr(html_tag):
    """The <wbr> HTML element represents a word break opportunity—a position within text where the browser may optionally break a line, though its line-breaking rules would not otherwise create a break at that location."""

    flags = Flags.SINGLE | Flags.INLINE | Flags.PRETTY


class ins(html_tag):
    """The <ins> HTML element represents a range of text that has been added to a document."""


class del_(html_tag):
    """The <del> HTML element represents a range of text that has been deleted from a document."""


class img(html_tag):
    """The <img> HTML element embeds an image into the document."""

    flags = Flags.SINGLE | Flags.PRETTY


class iframe(html_tag):
    """The <iframe> HTML element represents a nested browsing context, embedding another HTML page into the current one."""


class embed(html_tag):
    """The <embed> HTML element embeds external content at the specified point in the document. This content is provided by an external application or other source of interactive content such as a browser plug-in."""

    flags = Flags.SINGLE | Flags.PRETTY


class object(html_tag):
    """The <object> HTML element represents an external resource, which can be treated as an image, a nested browsing context, or a resource to be handled by a plugin."""


class param(html_tag):
    """The <param> HTML element defines parameters for an <object> element."""

    flags = Flags.SINGLE | Flags.PRETTY


class video(html_tag):
    """The <video> HTML element embeds a media player which supports video playback into the document."""


class audio(html_tag):
    """The <audio> HTML element embeds sound content in documents."""


class source(html_tag):
    """The <source> HTML element specifies multiple media resources for media elements (<video> and <audio>). It is an empty element, meaning that it has no content and does not have a closing tag."""

    flags = Flags.SINGLE | Flags.PRETTY


class track(html_tag):
    """The <track> HTML element specifies text tracks for media elements (<video> and <audio>). It allows users to add captions, subtitles, or descriptions to media content."""

    flags = Flags.SINGLE | Flags.PRETTY


class canvas(html_tag):
    """The <canvas> HTML element provides scripts with a resolution-dependent bitmap canvas, which can be used for rendering graphs, game graphics, art, or other visual images on the fly."""


class map(html_tag):
    """The <map> HTML element is used with <area> elements to define an image map (a clickable link area)."""


class area(html_tag):
    """The <area> HTML element defines a hot-spot region on an image, and optionally associates it with a hypertext link."""

    flags = Flags.SINGLE | Flags.PRETTY


class table(html_tag):
    """The <table> HTML element represents tabular data — that is, information presented in a two-dimensional table comprised of rows and columns of cells containing data."""


class caption(html_tag):
    """The <caption> HTML element specifies the caption (or title) of a table."""


class colgroup(html_tag):
    """The <colgroup> HTML element defines a group of columns within a table."""


class col(html_tag):
    """The <col> HTML element defines a column within a table and is used for defining common semantics on all common cells."""

    flags = Flags.SINGLE | Flags.PRETTY


class tbody(html_tag):
    """The <tbody> HTML element encapsulates a set of table rows (<tr> elements), indicating that they comprise the body of the table."""


class thead(html_tag):
    """The <thead> HTML element defines a set of rows defining the head of the columns of the table."""


class tfoot(html_tag):
    """The <tfoot> HTML element defines a set of rows summarizing the columns of the table."""


class tr(html_tag):
    """The <tr> HTML element defines a row of cells in a table."""


class th(html_tag):
    """The <th> HTML element defines a cell as header of a group of table cells. The exact nature of this group is defined by the scope and headers attributes."""


class td(html_tag):
    """The <td> HTML element defines a cell of a table that contains data."""


class form(html_tag):
    """The <form> HTML element represents a document section that contains interactive controls to submit information to a web server."""


class fieldset(html_tag):
    """The <fieldset> HTML element is used to group several controls as well as labels (<label>) within a web form."""


class legend(html_tag):
    """The <legend> HTML element represents a caption for the content of its parent <fieldset>."""


class label(html_tag):
    """The <label> HTML element represents a caption for an item in a user interface."""


class input(html_tag):
    """The <input> HTML element is used to create interactive controls for web-based forms in order to accept data from the user."""

    flags = Flags.SINGLE | Flags.PRETTY


class button(html_tag):
    """The <button> HTML element is an interactive element activated by a user with a mouse, keyboard, finger, voice command, or other assistive technology."""


class select(html_tag):
    """The <select> HTML element represents a control that provides a menu of options."""


class datalist(html_tag):
    """The <datalist> HTML element contains a set of <option> elements that represent the permissible or recommended options available to choose from within other controls."""


class option(html_tag):
    """The <option> HTML element is used to define an item contained in a <select>, an <optgroup>, or a <datalist> element."""


class optgroup(html_tag):
    """The <optgroup> HTML element creates a grouping of options within a <select> element."""


class textarea(html_tag):
    """The <textarea> HTML element represents a multi-line plain-text editing control, useful when you want to allow users to enter a sizeable amount of free-form text, for example a comment on a review or feedback form."""


class keygen(html_tag):
    """The <keygen> HTML element exists to facilitate generation of key material, and submission of the public key as part of an HTML form. This mechanism is designed for use with Web-based certificate management systems."""

    flags = Flags.SINGLE | Flags.PRETTY


class output(html_tag):
    """The <output> HTML element is a container element into which a site or app can inject the results of a calculation or the outcome of a user action."""


class progress(html_tag):
    """The <progress> HTML element displays an indicator showing the completion progress of a task, typically displayed as a progress bar."""


class meter(html_tag):
    """The <meter> HTML element represents either a scalar value within a known range or a fractional value."""


class details(html_tag):
    """The <details> HTML element creates a disclosure widget in which information is visible only when the widget is toggled into an "open" state."""


class summary(html_tag):
    """The <summary> HTML element specifies a summary, caption, or legend for a <details> HTML element's disclosure box."""


class command(html_tag):
    """The <command> HTML element represents a command that a user can invoke."""

    flags = Flags.SINGLE | Flags.PRETTY


class menu(html_tag):
    """The <menu> HTML element is used to group a set of commands that a user can perform or activate. This includes both list menus, which might appear across the top of a screen, as well as context menus, such as those that might appear underneath a button after it has been clicked."""


class font(html_tag):
    """The <font> HTML element is used to specify the font family, size, and weight of text."""


class comment(html_tag):
    """The <comment> HTML element is used to add comments to the HTML code."""
