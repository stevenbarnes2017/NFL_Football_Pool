// Formatting toolbar for message board and announcement textareas.
// Usage: <textarea data-format-toolbar ...>. Inserts the plain-text markers
// that Football_Project/services/text_format.py renders (**bold**, *italic*, lists, links).
(function () {
  const BUTTONS = [
    { label: "B", title: "Bold (Ctrl+B)", style: "font-weight:700", action: "wrap", marker: "**", key: "b" },
    { label: "I", title: "Italic (Ctrl+I)", style: "font-style:italic", action: "wrap", marker: "*", key: "i" },
    { label: "H", title: "Heading", style: "font-weight:700", action: "prefix", prefix: () => "# " },
    { label: "• List", title: "Bulleted list", action: "prefix", prefix: () => "- " },
    { label: "1. List", title: "Numbered list", action: "prefix", prefix: (i) => `${i + 1}. ` },
    { label: "Link", title: "Insert link", action: "link" },
  ];

  function replaceSelection(ta, text, selectFrom, selectTo) {
    const start = ta.selectionStart;
    ta.setRangeText(text, start, ta.selectionEnd, "end");
    if (selectFrom !== undefined) ta.setSelectionRange(start + selectFrom, start + selectTo);
    ta.focus();
    ta.dispatchEvent(new Event("input", { bubbles: true }));
  }

  function wrap(ta, marker, placeholder) {
    const sel = ta.value.slice(ta.selectionStart, ta.selectionEnd);
    const inner = sel || placeholder;
    replaceSelection(ta, marker + inner + marker, marker.length, marker.length + inner.length);
  }

  function prefixLines(ta, prefixFor) {
    const value = ta.value;
    const lineStart = value.lastIndexOf("\n", ta.selectionStart - 1) + 1;
    let lineEnd = value.indexOf("\n", ta.selectionEnd);
    if (lineEnd === -1) lineEnd = value.length;
    ta.setSelectionRange(lineStart, lineEnd);
    const lines = value.slice(lineStart, lineEnd).split("\n");
    const text = lines.map((line, i) => prefixFor(i) + line.replace(/^\s*([-*•]|\d+[.)]|#{1,3})\s+/, "")).join("\n");
    replaceSelection(ta, text);
  }

  function link(ta) {
    const url = window.prompt("Link address (https://…)", "https://");
    if (!url || !/^https?:\/\/\S+$/.test(url.trim())) return;
    const sel = ta.value.slice(ta.selectionStart, ta.selectionEnd) || "link text";
    replaceSelection(ta, `[${sel}](${url.trim()})`, 1, 1 + sel.length);
  }

  function run(ta, b) {
    if (b.action === "wrap") wrap(ta, b.marker, b.key === "b" ? "bold text" : "italic text");
    else if (b.action === "prefix") prefixLines(ta, b.prefix);
    else if (b.action === "link") link(ta);
  }

  function attach(ta) {
    const bar = document.createElement("div");
    bar.className = "pf-toolbar";
    bar.setAttribute("role", "toolbar");
    bar.setAttribute("aria-label", "Text formatting");
    BUTTONS.forEach((b) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "pf-btn";
      btn.textContent = b.label;
      btn.title = b.title;
      btn.setAttribute("aria-label", b.title);
      if (b.style) btn.style.cssText = b.style;
      btn.addEventListener("mousedown", (e) => e.preventDefault()); // keep the textarea selection
      btn.addEventListener("click", () => run(ta, b));
      bar.appendChild(btn);
    });
    ta.parentNode.insertBefore(bar, ta);
    ta.classList.add("pf-textarea");

    ta.addEventListener("keydown", (e) => {
      if (!(e.ctrlKey || e.metaKey)) return;
      const b = BUTTONS.find((x) => x.key && x.key === e.key.toLowerCase());
      if (b) { e.preventDefault(); run(ta, b); }
    });

    const hint = document.createElement("div");
    hint.className = "pf-hint";
    hint.textContent = "**bold**  *italic*  # heading  - list  1. list  [text](https://…)";
    ta.insertAdjacentElement("afterend", hint);
  }

  function init() {
    document.querySelectorAll("textarea[data-format-toolbar]").forEach(attach);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
