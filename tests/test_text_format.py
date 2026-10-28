import unittest

from Football_Project.services.text_format import plain_text, render_post


class RenderPostTests(unittest.TestCase):
    def test_plain_text_keeps_paragraphs_and_line_breaks(self):
        self.assertEqual(
            render_post("Hi all\nsee you Sunday\n\nThanks"),
            "<p>Hi all<br>see you Sunday</p><p>Thanks</p>",
        )

    def test_html_is_escaped(self):
        html = render_post('<script>alert(1)</script> <b onclick="x">hi</b>')
        self.assertNotIn("<script>", html)
        self.assertNotIn("<b ", html)
        self.assertIn("&lt;script&gt;", html)

    def test_bold_and_italic(self):
        self.assertEqual(
            render_post("**Picks lock** at *kickoff* and _no_ later"),
            "<p><strong>Picks lock</strong> at <em>kickoff</em> and <em>no</em> later</p>",
        )

    def test_markers_inside_words_and_math_are_left_alone(self):
        self.assertEqual(render_post("snake_case_name and 5*3*2"), "<p>snake_case_name and 5*3*2</p>")
        self.assertEqual(render_post("** not bold **"), "<p>** not bold **</p>")

    def test_bullet_and_numbered_lists(self):
        self.assertEqual(
            render_post("Rules:\n- one\n* two\n\n1. first\n2) second"),
            "<p>Rules:</p><ul><li>one</li><li>two</li></ul><ol><li>first</li><li>second</li></ol>",
        )

    def test_bold_line_is_not_a_bullet(self):
        self.assertEqual(render_post("**Reminder** pay up"), "<p><strong>Reminder</strong> pay up</p>")

    def test_list_items_get_inline_formatting(self):
        self.assertEqual(render_post("- **Week 9** is a bye"), "<ul><li><strong>Week 9</strong> is a bye</li></ul>")

    def test_heading(self):
        self.assertEqual(render_post("# Playoffs\nstart soon"), "<h4>Playoffs</h4><p>start soon</p>")

    def test_links(self):
        html = render_post("See [the rules](https://example.com/rules?a=1&b=2) or https://example.com/x_y_z.")
        self.assertIn('<a href="https://example.com/rules?a=1&amp;b=2" target="_blank" rel="noopener noreferrer nofollow">the rules</a>', html)
        self.assertIn('<a href="https://example.com/x_y_z" target="_blank" rel="noopener noreferrer nofollow">https://example.com/x_y_z</a>.', html)
        self.assertNotIn("<em>", html)

    def test_non_http_links_are_not_linked(self):
        html = render_post("[click](javascript:alert(1))")
        self.assertNotIn("<a", html)

    def test_crlf_and_empty(self):
        self.assertEqual(render_post("a\r\nb"), "<p>a<br>b</p>")
        self.assertEqual(render_post(None), "")


class PlainTextTests(unittest.TestCase):
    def test_strips_markers(self):
        self.assertEqual(
            plain_text("# Heads up\n**Picks** lock *early*\n- [rules](https://x.io)"),
            "Heads up\nPicks lock early\n• rules (https://x.io)",
        )


if __name__ == "__main__":
    unittest.main()
