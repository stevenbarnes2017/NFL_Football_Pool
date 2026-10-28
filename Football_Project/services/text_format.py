"""Lightweight, safe formatting for message board posts and announcements.

Bodies are stored as plain text. On display they are HTML-escaped first and
then a small set of markers is turned into markup, so users can never inject
their own HTML:

    **bold**   *italic* / _italic_   # Heading   - bullet   1. numbered
    [link text](https://...)   bare https://... URLs   blank line = new paragraph
    ![alt](/board/images/<token>)   uploaded image (only our own image URLs)

Existing plain-text posts render as before (line breaks preserved).
"""

import re

from markupsafe import Markup, escape

_BULLET = re.compile(r"^\s*[-*•]\s+(.*)$")
_NUMBERED = re.compile(r"^\s*\d+[.)]\s+(.*)$")
_HEADING = re.compile(r"^\s*#{1,3}\s+(.*)$")

_IMAGE = re.compile(r"!\[([^\]\n]*)\]\((/board/images/[A-Za-z0-9_-]{8,64})\)")
_LINK = re.compile(r"\[([^\]\n]+)\]\((https?://[^\s)]+)\)")
_URL = re.compile(r"(?<![\"'=>])\bhttps?://[^\s<]+[^\s<.,:;!?)\]'\"]")
_BOLD = re.compile(r"\*\*(?=\S)(.+?)(?<=\S)\*\*")
_ITALIC_STAR = re.compile(r"(?<![\w*])\*(?=\S)([^*\n]+?)(?<=\S)\*(?![\w*])")
_ITALIC_UNDERSCORE = re.compile(r"(?<!\w)_(?=\S)([^_\n]+?)(?<=\S)_(?!\w)")

_A = '<a href="{href}" target="_blank" rel="noopener noreferrer nofollow">{text}</a>'
_IMG = '<a href="{src}" target="_blank" rel="noopener"><img class="post-img" src="{src}" alt="{alt}" loading="lazy"></a>'


def _inline(escaped_line: str, images: bool = True) -> str:
    """Apply inline markers to one already-escaped line."""
    placeholders = []

    def stash(html):
        placeholders.append(html)
        return f"\x00{len(placeholders) - 1}\x00"

    # Images and links first, and stashed, so URLs aren't mangled by bold/italic rules.
    text = _IMAGE.sub(
        lambda m: stash(_IMG.format(src=m.group(2), alt=m.group(1) or "image") if images else "[image]"),
        escaped_line,
    )
    text = _LINK.sub(lambda m: stash(_A.format(href=m.group(2), text=m.group(1))), text)
    text = _URL.sub(lambda m: stash(_A.format(href=m.group(0), text=m.group(0))), text)

    text = _BOLD.sub(r"<strong>\1</strong>", text)
    text = _ITALIC_STAR.sub(r"<em>\1</em>", text)
    text = _ITALIC_UNDERSCORE.sub(r"<em>\1</em>", text)

    return re.sub(r"\x00(\d+)\x00", lambda m: placeholders[int(m.group(1))], text)


def render_post(text, images: bool = True) -> Markup:
    """Render a stored post/announcement body to safe HTML.

    images=False shows uploaded images as "[image]" (e.g. in emails, where
    the login-protected image URLs can't load).
    """
    if not text:
        return Markup("")

    lines = str(escape(str(text).replace("\r\n", "\n").replace("\r", "\n"))).split("\n")
    blocks = []
    paragraph = []
    list_tag, list_items = None, []

    def flush_paragraph():
        if paragraph:
            blocks.append("<p>" + "<br>".join(_inline(l, images) for l in paragraph) + "</p>")
            paragraph.clear()

    def flush_list():
        nonlocal list_tag
        if list_tag:
            items = "".join(f"<li>{_inline(i, images)}</li>" for i in list_items)
            blocks.append(f"<{list_tag}>{items}</{list_tag}>")
            list_tag = None
            list_items.clear()

    for line in lines:
        bullet, numbered, heading = _BULLET.match(line), _NUMBERED.match(line), _HEADING.match(line)
        # "**bold** line" also starts with "*"; only treat "* " (star + space) as a bullet.
        if bullet and line.lstrip().startswith("**"):
            bullet = None

        if bullet or numbered:
            tag = "ul" if bullet else "ol"
            flush_paragraph()
            if list_tag and list_tag != tag:
                flush_list()
            list_tag = tag
            list_items.append((bullet or numbered).group(1))
        elif heading:
            flush_paragraph()
            flush_list()
            blocks.append(f"<h4>{_inline(heading.group(1), images)}</h4>")
        elif not line.strip():
            flush_paragraph()
            flush_list()
        else:
            flush_list()
            paragraph.append(line)

    flush_paragraph()
    flush_list()
    return Markup("".join(blocks))


def plain_text(text) -> str:
    """Strip formatting markers, for push notifications and the notification bell."""
    if not text:
        return ""
    out = []
    for line in str(text).replace("\r\n", "\n").split("\n"):
        m = _HEADING.match(line)
        if m:
            line = m.group(1)
        elif not line.lstrip().startswith("**"):
            m = _BULLET.match(line)
            if m:
                line = "• " + m.group(1)
        line = _IMAGE.sub("[image]", line)
        line = _LINK.sub(r"\1 (\2)", line)
        line = _BOLD.sub(r"\1", line)
        line = _ITALIC_STAR.sub(r"\1", line)
        line = _ITALIC_UNDERSCORE.sub(r"\1", line)
        out.append(line)
    return "\n".join(out).strip()
