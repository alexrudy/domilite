import pytest

from domilite.render import ContextFlags
from domilite.render import RenderFlags
from domilite.render import RenderParts
from domilite.render import RenderStream


class TestRenderFlags:
    def test_pretty_flag(self):
        flags = RenderFlags.PRETTY
        assert flags & RenderFlags.PRETTY
        assert not (flags & RenderFlags.XHTML)

    def test_xhtml_flag(self):
        flags = RenderFlags.XHTML
        assert flags & RenderFlags.XHTML
        assert not (flags & RenderFlags.PRETTY)

    def test_combined_flags(self):
        flags = RenderFlags.PRETTY | RenderFlags.XHTML
        assert flags & RenderFlags.PRETTY
        assert flags & RenderFlags.XHTML

    def test_no_flags(self):
        flags = RenderFlags(0)
        assert not (flags & RenderFlags.PRETTY)
        assert not (flags & RenderFlags.XHTML)


class TestContextFlags:
    def test_comment_flag(self):
        flags = ContextFlags.COMMENT
        assert flags & ContextFlags.COMMENT

    def test_no_flags(self):
        flags = ContextFlags(0)
        assert not (flags & ContextFlags.COMMENT)


class TestRenderStream:
    @pytest.fixture
    def stream(self):
        return RenderStream(flags=RenderFlags.PRETTY)

    def test_write_single_line(self, stream):
        stream.write("hello")
        assert stream.getvalue() == "hello"

    def test_write_multiline(self, stream):
        stream.write("line1\nline2\nline3")
        assert stream.getvalue() == "line1\nline2\nline3"

    def test_write_with_indentation(self, stream):
        stream.current_indent = 1
        stream.write("line1\nline2")
        assert stream.getvalue() == "line1\n  line2"

    def test_newline_basic(self, stream):
        stream.write("hello")
        stream.newline()
        stream.write("world")
        assert stream.getvalue() == "hello\nworld"

    def test_newline_with_indentation(self, stream):
        stream.current_indent = 2
        stream.write("hello")
        stream.newline()
        stream.write("world")
        assert stream.getvalue() == "hello\n    world"

    def test_newline_custom_indent_text(self):
        stream = RenderStream(indent_text="\t")
        stream.current_indent = 1
        stream.write("hello")
        stream.newline()
        stream.write("world")
        assert stream.getvalue() == "hello\n\tworld"

    def test_indented_context_manager(self, stream):
        assert stream.current_indent == 0
        with stream.indented():
            assert stream.current_indent == 1
            with stream.indented():
                assert stream.current_indent == 2
            assert stream.current_indent == 1
        assert stream.current_indent == 0

    def test_indented_with_writing(self, stream):
        stream.write("start")
        with stream.indented():
            stream.newline()
            stream.write("indented")
        stream.newline()
        stream.write("end")
        assert stream.getvalue() == "start\n  indented\nend"

    def test_comment_context_manager(self, stream):
        assert not (stream.context & ContextFlags.COMMENT)
        with stream.comment():
            assert stream.context & ContextFlags.COMMENT
        assert not (stream.context & ContextFlags.COMMENT)

    def test_nested_comment_context(self, stream):
        with stream.comment():
            assert stream.context & ContextFlags.COMMENT
            with stream.comment():
                assert stream.context & ContextFlags.COMMENT
            assert stream.context & ContextFlags.COMMENT
        assert not (stream.context & ContextFlags.COMMENT)

    def test_comment_preserves_existing_flags(self, stream):
        stream.context = ContextFlags.COMMENT
        with stream.comment():
            assert stream.context & ContextFlags.COMMENT
        assert stream.context & ContextFlags.COMMENT

    def test_parts_context_manager(self, stream):
        with stream.parts() as parts:
            assert isinstance(parts, RenderParts)
            assert parts.stream is stream
            assert parts.joiner == " "
            parts.append("hello")
            parts.append("world")
        assert stream.getvalue() == "hello world"

    def test_parts_with_custom_joiner(self, stream):
        with stream.parts(joiner=", ") as parts:
            parts.append("one")
            parts.append("two")
            parts.append("three")
        assert stream.getvalue() == "one, two, three"

    def test_getvalue_empty(self, stream):
        assert stream.getvalue() == ""

    def test_getvalue_after_operations(self, stream):
        stream.write("hello")
        stream.newline()
        with stream.indented():
            stream.write("world")
        assert stream.getvalue() == "hello\nworld"


class TestRenderParts:
    @pytest.fixture
    def stream(self):
        return RenderStream()

    @pytest.fixture
    def parts(self, stream):
        return RenderParts(stream)

    def test_flags_property(self, parts):
        parts.stream.flags = RenderFlags.PRETTY
        assert parts.flags == RenderFlags.PRETTY

    def test_append(self, parts):
        parts.append("hello")
        parts.append("world")
        assert parts.parts == ["hello", "world"]

    def test_prepend(self, parts):
        parts.append("world")
        parts.prepend("hello")
        assert parts.parts == ["hello", "world"]

    def test_prepend_empty(self, parts):
        parts.prepend("first")
        assert parts.parts == ["first"]

    def test_prepend_multiple(self, parts):
        parts.append("three")
        parts.prepend("two")
        parts.prepend("one")
        assert parts.parts == ["one", "two", "three"]

    def test_close_empty(self, stream, parts):
        parts.close()
        assert stream.getvalue() == ""

    def test_close_single_item(self, stream, parts):
        parts.append("hello")
        parts.close()
        assert stream.getvalue() == "hello"

    def test_close_multiple_items(self, stream, parts):
        parts.append("hello")
        parts.append("world")
        parts.close()
        assert stream.getvalue() == "hello world"

    def test_close_custom_joiner(self, stream):
        parts = RenderParts(stream, joiner=" | ")
        parts.append("one")
        parts.append("two")
        parts.append("three")
        parts.close()
        assert stream.getvalue() == "one | two | three"

    def test_context_manager_integration(self, stream):
        with stream.parts(joiner="-") as parts:
            parts.append("a")
            parts.prepend("start")
            parts.append("b")
        assert stream.getvalue() == "start-a-b"

    def test_complex_rendering_scenario(self, stream):
        stream.write("prefix:")
        stream.newline()
        with stream.indented():
            with stream.parts(joiner=" + ") as parts:
                parts.append("item1")
                parts.append("item2")
        stream.newline()
        stream.write("suffix")
        assert stream.getvalue() == "prefix:\nitem1 + item2\nsuffix"

    def test_empty_parts_render(self, stream):
        with stream.parts():
            pass
        assert stream.getvalue() == ""


class TestIntegration:
    def test_complex_rendering_with_all_features(self):
        stream = RenderStream(indent_text="    ", flags=RenderFlags.PRETTY | RenderFlags.XHTML)

        stream.write("document:")
        with stream.indented():
            stream.newline()
            with stream.comment():
                with stream.parts(joiner=" ") as parts:
                    parts.append("comment")
                    parts.append("content")

            stream.newline()
            with stream.parts(joiner=", ") as parts:
                parts.append("attr1")
                parts.append("attr2")
                parts.prepend("start")

        expected = "document:\n    comment content\n    start, attr1, attr2"
        assert stream.getvalue() == expected

    def test_nested_indentation_and_parts(self):
        stream = RenderStream(flags=RenderFlags.PRETTY)

        with stream.indented():
            stream.write("level1")
            with stream.indented():
                stream.newline()
                with stream.parts(joiner=" - ") as parts:
                    parts.append("a")
                    parts.append("b")
                    parts.append("c")

        assert stream.getvalue() == "level1\n    a - b - c"

    def test_multiple_comment_contexts(self):
        stream = RenderStream()

        with stream.comment():
            assert stream.context & ContextFlags.COMMENT
            stream.write("outer comment")

            with stream.comment():
                assert stream.context & ContextFlags.COMMENT
                stream.newline()
                stream.write("inner stays comment context")

        assert not (stream.context & ContextFlags.COMMENT)
        assert stream.getvalue() == "outer comment\ninner stays comment context"
