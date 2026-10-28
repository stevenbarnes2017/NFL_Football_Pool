// Visual editor for message board posts and announcements.
//
// Usage: <textarea name="body" data-format-toolbar [data-upload-context="announcement"]>.
// The textarea is hidden and replaced by an editable box with a toolbar
// (Bold, Italic, Heading, lists, Link, Picture). People see formatting as they
// type; pictures can be pasted, dragged in, or picked with the button.
// On every change the box is converted back into the plain-text format that
// Football_Project/services/text_format.py renders (**bold**, _italic_, # heading,
// - / 1. lists, [text](url), ![image](/board/images/...)) and stored in the
// textarea, so the server never receives HTML.
(function () {
  const MAX_BYTES = 5 * 1024 * 1024;
  const MAX_DIMENSION = 1600;
  const ALLOWED = ["image/png", "image/jpeg", "image/gif", "image/webp"];
  const BLOCKS = new Set(["P", "DIV", "H1", "H2", "H3", "H4", "H5", "H6", "UL", "OL", "LI", "BLOCKQUOTE", "PRE"]);

  const BUTTONS = [
    { label: "B", title: "Bold", style: "font-weight:700", cmd: "bold" },
    { label: "I", title: "Italic", style: "font-style:italic", cmd: "italic" },
    { label: "Heading", title: "Heading", cmd: "heading" },
    { label: "• List", title: "Bulleted list", cmd: "insertUnorderedList" },
    { label: "1. List", title: "Numbered list", cmd: "insertOrderedList" },
    { label: "Link", title: "Add a link", cmd: "link" },
    { label: "📷 Picture", title: "Add a picture", cmd: "image" },
  ];

  // ---------------------------------------------------------------------
  // Editor DOM -> stored text
  // ---------------------------------------------------------------------
  function escapeText(text) {
    return text.replace(/ /g, " ").replace(/\\/g, "\\\\").replace(/\*/g, "\\*").replace(/\[/g, "\\[");
  }

  // Lines that would accidentally turn into a list or heading are escaped.
  function escapeLineStarts(text) {
    return text
      .split("\n")
      .map((line) => line
        .replace(/^(\s*)([-•#])(?=\s)/, "$1\\$2")
        .replace(/^(\s*\d+)([.)])(?=\s)/, "$1\\$2"))
      .join("\n");
  }

  // Wrap each line of an inline run in markers; markers must hug the text.
  function wrapLines(inner, marker) {
    return inner
      .split("\n")
      .map((part) => {
        const m = part.match(/^(\s*)(.*?)(\s*)$/);
        return m[2] ? `${m[1]}${marker}${m[2]}${marker}${m[3]}` : part;
      })
      .join("\n");
  }

  function inlineText(node) {
    let out = "";
    node.childNodes.forEach((child) => {
      out += inline(child);
    });
    return out;
  }

  function inline(node) {
    if (node.nodeType === Node.TEXT_NODE) return escapeText(node.nodeValue);
    if (node.nodeType !== Node.ELEMENT_NODE) return "";
    const tag = node.tagName;
    if (tag === "BR") return "\n";
    if (tag === "IMG") return node.dataset.mdSrc ? `\n![image](${node.dataset.mdSrc})\n` : "";
    if (tag === "B" || tag === "STRONG") {
      return insideFormat(node, "bold") ? inlineText(node) : wrapLines(inlineText(node), "**");
    }
    if (tag === "I" || tag === "EM") {
      return insideFormat(node, "italic") ? inlineText(node) : wrapLines(inlineText(node), "_");
    }
    if (tag === "A") {
      const href = node.getAttribute("href") || "";
      const text = inlineText(node).trim();
      if (!/^https?:\/\//i.test(href)) return text;
      return text && text !== href ? `[${text}](${href})` : href;
    }
    if (BLOCKS.has(tag)) return "\n" + inlineText(node) + "\n";
    if (tag === "SPAN") {
      const { bold, italic } = styleFlags(node);
      let text = inlineText(node);
      if (italic && !insideFormat(node, "italic")) text = wrapLines(text, "_");
      if (bold && !insideFormat(node, "bold")) text = wrapLines(text, "**");
      return text;
    }
    return inlineText(node); // font, u, etc.
  }

  // Is an ancestor (below the editor) already bold/italic? Avoids "****".
  function insideFormat(node, kind) {
    for (let el = node.parentElement; el && !el.classList.contains("pf-editor"); el = el.parentElement) {
      const t = el.tagName;
      if (kind === "bold" && (t === "B" || t === "STRONG" || styleFlags(el).bold)) return true;
      if (kind === "italic" && (t === "I" || t === "EM" || styleFlags(el).italic)) return true;
    }
    return false;
  }

  // Bold/italic expressed as inline styles (Google Docs, Word, some browsers).
  function styleFlags(el) {
    const weight = (el.style && el.style.fontWeight) || "";
    const fontStyle = (el.style && el.style.fontStyle) || "";
    return {
      bold: weight === "bold" || weight === "bolder" || Number(weight) >= 600,
      italic: fontStyle === "italic" || fontStyle === "oblique",
      notBold: weight === "normal" || (Number(weight) > 0 && Number(weight) < 600),
      notItalic: fontStyle === "normal",
    };
  }

  // ---------------------------------------------------------------------
  // Pasted HTML -> the small set of tags the editor supports
  // ---------------------------------------------------------------------
  // Keeps bold, italic, headings, lists, links and paragraphs from web pages,
  // emails, Word and Google Docs; drops fonts, colours, sizes, images,
  // scripts and anything else.
  const DROP = new Set(["SCRIPT", "STYLE", "META", "LINK", "TITLE", "HEAD", "NOSCRIPT", "TEMPLATE",
    "IFRAME", "OBJECT", "EMBED", "SVG", "CANVAS", "VIDEO", "AUDIO", "IMG", "PICTURE", "BUTTON",
    "INPUT", "SELECT", "TEXTAREA", "FORM"]);

  function cleanPastedHtml(html) {
    const doc = new DOMParser().parseFromString(html, "text/html");
    const out = document.createElement("div");
    cleanChildren(doc.body, out);
    groupWordLists(out);
    return out;
  }

  function cleanChildren(src, dest) {
    src.childNodes.forEach((n) => cleanNode(n, dest));
  }

  function cleanNode(node, dest) {
    if (node.nodeType === Node.TEXT_NODE) {
      const text = node.nodeValue.replace(/\s+/g, " ");
      if (text) dest.appendChild(document.createTextNode(text));
      return;
    }
    if (node.nodeType !== Node.ELEMENT_NODE) return; // comments (Word's <!--[if ...]>), etc.
    const tag = node.tagName.toUpperCase();
    const style = node.getAttribute("style") || "";
    if (DROP.has(tag) || /mso-list:\s*ignore/i.test(style) || tag.includes(":")) return; // Word's bullet glyphs, <o:p>

    let el = null;
    const flags = styleFlags(node);
    if (tag === "B" || tag === "STRONG") {
      el = flags.notBold ? null : document.createElement("strong"); // Google Docs wraps everything in <b style="font-weight:normal">
    } else if (tag === "I" || tag === "EM") {
      el = flags.notItalic ? null : document.createElement("em");
    } else if (/^H[1-6]$/.test(tag)) {
      el = document.createElement("h4");
    } else if (tag === "UL" || tag === "OL" || tag === "LI") {
      el = document.createElement(tag.toLowerCase());
    } else if (tag === "BR") {
      dest.appendChild(document.createElement("br"));
      return;
    } else if (tag === "A") {
      const href = (node.getAttribute("href") || "").trim();
      if (/^https?:\/\//i.test(href)) {
        el = document.createElement("a");
        el.href = href;
      }
    } else if (tag === "P" || tag === "DIV" || tag === "BLOCKQUOTE" || tag === "PRE" || tag === "TR" || tag === "SECTION" || tag === "ARTICLE") {
      el = document.createElement("p");
      if (/MsoListParagraph/i.test(node.className || "") || /mso-list:\s*l\d/i.test(style)) el.dataset.wordList = "1";
    } else if (tag === "TD" || tag === "TH") {
      cleanChildren(node, dest);
      dest.appendChild(document.createTextNode(" "));
      return;
    }

    let container = dest;
    if (el) {
      dest.appendChild(el);
      container = el;
    }
    // Bold/italic set by inline style on spans, paragraphs and list items
    // (Google Docs, Word). Headings are already bold.
    if (!el || ["P", "LI", "H4"].includes(el.tagName)) {
      if (flags.bold && !(el && el.tagName === "H4")) {
        container = container.appendChild(document.createElement("strong"));
      }
      if (flags.italic) {
        container = container.appendChild(document.createElement("em"));
      }
    }
    cleanChildren(node, container);
  }

  // Word pastes bulleted lists as <p class="MsoListParagraph"> with a fake
  // bullet; turn runs of those into a real list.
  function groupWordLists(root) {
    Array.from(root.querySelectorAll("p[data-word-list]")).forEach((p) => {
      if (!p.parentNode || !p.dataset.wordList) return; // already moved into a list
      const ul = document.createElement("ul");
      p.before(ul);
      let cur = p;
      while (cur && cur.nodeType === Node.ELEMENT_NODE && cur.dataset && cur.dataset.wordList) {
        const next = cur.nextSibling && cur.nextSibling.nodeType === Node.TEXT_NODE && !cur.nextSibling.nodeValue.trim()
          ? cur.nextSibling.nextSibling : cur.nextSibling;
        const li = document.createElement("li");
        while (cur.firstChild) li.appendChild(cur.firstChild);
        ul.appendChild(li);
        cur.remove();
        cur = next;
      }
    });
    root.querySelectorAll("[data-word-list]").forEach((el) => el.removeAttribute("data-word-list"));
  }

  // Browsers nest blocks unpredictably (a list inside a <p>, <div>s inside
  // <div>s), so walk blocks recursively and only treat leaf content as text.
  function hasBlockChild(node) {
    return Array.from(node.children).some((c) => BLOCKS.has(c.tagName) || c.tagName === "IMG");
  }

  function collectBlocks(root, blocks) {
    let loose = "";
    const flushLoose = () => {
      if (loose.trim()) blocks.push(escapeLineStarts(loose.trim()));
      loose = "";
    };

    root.childNodes.forEach((node) => {
      const tag = node.nodeType === Node.ELEMENT_NODE ? node.tagName : "";
      if (tag === "UL" || tag === "OL") {
        flushLoose();
        const items = [];
        Array.from(node.querySelectorAll("li")).forEach((li) => {
          const text = inlineText(li).replace(/\s*\n\s*/g, " ").trim();
          if (text) items.push((tag === "UL" ? "- " : `${items.length + 1}. `) + text);
        });
        if (items.length) blocks.push(items.join("\n"));
      } else if (/^H[1-6]$/.test(tag)) {
        flushLoose();
        const text = inlineText(node).replace(/\s*\n\s*/g, " ").trim();
        if (text) blocks.push("# " + text);
      } else if (tag === "IMG") {
        flushLoose();
        if (node.dataset.mdSrc) blocks.push(`![image](${node.dataset.mdSrc})`);
      } else if (BLOCKS.has(tag)) {
        flushLoose();
        if (hasBlockChild(node)) {
          collectBlocks(node, blocks);
        } else {
          const text = inlineText(node).trim();
          if (text) blocks.push(escapeLineStarts(text));
        }
      } else {
        loose += inline(node);
      }
    });
    flushLoose();
  }

  function serialize(root) {
    const blocks = [];
    collectBlocks(root, blocks);
    return blocks.join("\n\n").replace(/\n{3,}/g, "\n\n").trim();
  }

  // ---------------------------------------------------------------------
  // Pictures
  // ---------------------------------------------------------------------
  // Photos/screenshots: downscale and re-encode (applies phone rotation, drops
  // location metadata). GIFs go up untouched so memes stay animated.
  async function prepare(file) {
    if (file.type === "image/gif") return file;
    let bitmap;
    try {
      bitmap = await createImageBitmap(file, { imageOrientation: "from-image" });
    } catch (e) {
      return file;
    }
    const scale = Math.min(1, MAX_DIMENSION / Math.max(bitmap.width, bitmap.height));
    if (file.type === "image/png" && scale === 1 && file.size <= 1024 * 1024) return file; // crisp small screenshots
    const canvas = document.createElement("canvas");
    canvas.width = Math.round(bitmap.width * scale);
    canvas.height = Math.round(bitmap.height * scale);
    const ctx = canvas.getContext("2d");
    ctx.fillStyle = "#fff"; // JPEG has no transparency
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(bitmap, 0, 0, canvas.width, canvas.height);
    const blob = await new Promise((resolve) => canvas.toBlob(resolve, "image/jpeg", 0.85));
    return blob || file;
  }

  function imageFiles(dataTransfer) {
    return dataTransfer ? Array.from(dataTransfer.files || []).filter((f) => f.type.startsWith("image/")) : [];
  }

  // ---------------------------------------------------------------------
  // Editor
  // ---------------------------------------------------------------------
  function attach(ta) {
    const form = ta.closest("form");
    const wrapper = document.createElement("div");
    wrapper.className = "pf-editor-wrap";

    const bar = document.createElement("div");
    bar.className = "pf-toolbar";
    bar.setAttribute("role", "toolbar");
    bar.setAttribute("aria-label", "Formatting");

    const editor = document.createElement("div");
    editor.className = "pf-editor post-formatted";
    editor.contentEditable = "true";
    editor.setAttribute("role", "textbox");
    editor.setAttribute("aria-multiline", "true");
    editor.setAttribute("aria-label", ta.getAttribute("aria-label") || ta.placeholder || "Message");
    editor.dataset.placeholder = ta.placeholder || "Write your message… you can paste pictures right in";
    editor.style.minHeight = `${Math.max(4, Number(ta.getAttribute("rows")) || 5) * 1.6}em`;

    const status = document.createElement("div");
    status.className = "pf-hint";
    status.setAttribute("aria-live", "polite");
    const defaultHint = "Tip: paste or drag pictures right into the box.";
    status.textContent = defaultHint;

    let uploads = 0;
    const buttons = {};

    function sync() {
      ta.value = serialize(editor);
      editor.classList.toggle("pf-empty", !ta.value && !editor.querySelector("img"));
    }

    function setBusy(delta) {
      uploads += delta;
      if (form) {
        form.querySelectorAll('button[type="submit"], input[type="submit"]').forEach((b) => {
          b.disabled = uploads > 0;
        });
      }
      status.textContent = uploads > 0 ? "Adding picture…" : defaultHint;
    }

    function updateButtons() {
      ["bold", "italic", "insertUnorderedList", "insertOrderedList"].forEach((cmd) => {
        let on = false;
        try { on = document.queryCommandState(cmd); } catch (e) { /* unsupported */ }
        buttons[cmd].setAttribute("aria-pressed", on ? "true" : "false");
      });
      let block = "";
      try { block = String(document.queryCommandValue("formatBlock")).toLowerCase(); } catch (e) { /* unsupported */ }
      buttons.heading.setAttribute("aria-pressed", /^h[1-6]$/.test(block) ? "true" : "false");
    }

    function insertNodeAtCursor(node) {
      editor.focus();
      const sel = window.getSelection();
      let range = sel.rangeCount ? sel.getRangeAt(0) : null;
      if (!range || !editor.contains(range.commonAncestorContainer)) {
        range = document.createRange();
        range.selectNodeContents(editor);
        range.collapse(false);
      }
      range.deleteContents();
      range.insertNode(node);
      range.setStartAfter(node);
      range.collapse(true);
      sel.removeAllRanges();
      sel.addRange(range);
    }

    async function addPicture(file) {
      if (!ALLOWED.includes(file.type)) {
        window.alert("Pictures need to be PNG, JPEG, GIF or WebP.");
        return;
      }
      const img = document.createElement("img");
      img.className = "post-img pf-uploading";
      img.alt = "";
      img.src = URL.createObjectURL(file); // instant preview while uploading
      const holder = document.createElement("div");
      holder.appendChild(img);
      insertNodeAtCursor(holder);
      const after = document.createElement("p");
      after.appendChild(document.createElement("br"));
      holder.after(after); // somewhere to keep typing below the picture
      setBusy(1);
      try {
        const blob = await prepare(file);
        if (blob.size > MAX_BYTES) throw new Error("That picture is too large (max 5 MB).");
        const body = new FormData();
        body.append("image", blob, file.name || "image");
        body.append("context", ta.dataset.uploadContext || "board");
        const token = form && form.querySelector('input[name="csrf_token"]');
        const res = await fetch("/board/images", {
          method: "POST",
          body,
          credentials: "same-origin",
          headers: token ? { "X-CSRFToken": token.value } : {},
        });
        let data = {};
        try { data = await res.json(); } catch (e) { /* non-JSON error page */ }
        if (!res.ok || !data.url) {
          throw new Error(data.error || (res.status === 413 ? "That picture is too large." : `Upload failed (${res.status}).`));
        }
        img.dataset.mdSrc = data.url;
        img.classList.remove("pf-uploading");
      } catch (e) {
        holder.remove();
        window.alert(e.message || "Sorry, that picture couldn't be added.");
      } finally {
        sync();
        setBusy(-1);
      }
    }

    function pickPictures() {
      const input = document.createElement("input");
      input.type = "file";
      input.accept = ALLOWED.join(",");
      input.multiple = true;
      input.addEventListener("change", () => Array.from(input.files).forEach(addPicture));
      input.click();
    }

    function addLink() {
      const sel = window.getSelection();
      const hasText = sel.rangeCount && !sel.isCollapsed && editor.contains(sel.anchorNode);
      const saved = sel.rangeCount ? sel.getRangeAt(0).cloneRange() : null;
      let url = window.prompt("Paste the web address for the link:", "https://");
      if (!url) return;
      url = url.trim();
      if (!/^https?:\/\//i.test(url)) url = "https://" + url.replace(/^\/+/, "");
      if (!/^https?:\/\/\S+$/i.test(url)) return;
      editor.focus();
      if (saved) {
        sel.removeAllRanges();
        sel.addRange(saved);
      }
      if (hasText) {
        document.execCommand("createLink", false, url);
      } else {
        const a = document.createElement("a");
        a.href = url;
        a.textContent = url;
        insertNodeAtCursor(a);
      }
      sync();
    }

    function run(cmd) {
      editor.focus();
      if (cmd === "image") return pickPictures();
      if (cmd === "link") return addLink();
      if (cmd === "heading") {
        const current = String(document.queryCommandValue("formatBlock")).toLowerCase();
        document.execCommand("formatBlock", false, /^h[1-6]$/.test(current) ? "p" : "h4");
      } else {
        document.execCommand(cmd, false, null);
      }
      sync();
      updateButtons();
    }

    BUTTONS.forEach((b) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "pf-btn";
      btn.textContent = b.label;
      btn.title = b.title;
      btn.setAttribute("aria-label", b.title);
      if (b.style) btn.style.cssText = b.style;
      btn.addEventListener("mousedown", (e) => e.preventDefault()); // keep the text selection
      btn.addEventListener("click", () => run(b.cmd));
      buttons[b.cmd] = btn;
      bar.appendChild(btn);
    });

    // Paste: pictures become pictures; formatted text keeps bold, italic,
    // headings, lists and links (but not fonts/colours); plain text as is.
    editor.addEventListener("paste", (e) => {
      const data = e.clipboardData;
      if (!data) return;
      e.preventDefault();
      const html = data.getData("text/html");
      const files = imageFiles(data);
      // A copied image usually comes with a one-<img> HTML wrapper; treat it as a picture.
      const htmlHasText = html && cleanPastedHtml(html).textContent.trim();
      if (files.length && !htmlHasText) {
        files.forEach(addPicture);
        return;
      }
      if (htmlHasText) {
        const cleaned = cleanPastedHtml(html);
        document.execCommand("insertHTML", false, cleaned.innerHTML);
      } else {
        const text = data.getData("text/plain");
        if (text) document.execCommand("insertText", false, text);
      }
      sync();
      updateButtons();
    });
    editor.addEventListener("dragover", (e) => {
      if (Array.from(e.dataTransfer.items || []).some((i) => i.kind === "file")) {
        e.preventDefault();
        editor.classList.add("pf-drop");
      }
    });
    editor.addEventListener("dragleave", () => editor.classList.remove("pf-drop"));
    editor.addEventListener("drop", (e) => {
      editor.classList.remove("pf-drop");
      const files = imageFiles(e.dataTransfer);
      if (!files.length) return;
      e.preventDefault();
      files.forEach(addPicture);
    });
    editor.addEventListener("input", sync);
    editor.addEventListener("keyup", updateButtons);
    editor.addEventListener("mouseup", updateButtons);

    // Swap the textarea for the editor. The textarea stays in the form (hidden)
    // and carries the converted text; "required" is enforced on submit instead.
    const required = ta.hasAttribute("required");
    ta.removeAttribute("required");
    ta.hidden = true;
    ta.parentNode.insertBefore(wrapper, ta);
    wrapper.append(bar, editor, status);
    if (ta.value.trim()) editor.textContent = ta.value; // e.g. browser-restored draft
    sync();

    if (form) {
      form.addEventListener("submit", (e) => {
        sync();
        if (uploads > 0 || (required && !ta.value.trim())) {
          e.preventDefault();
          status.textContent = uploads > 0 ? "Please wait for the picture to finish adding." : "Please write a message first.";
          editor.focus();
        }
      });
    }
  }

  function init() {
    try { document.execCommand("defaultParagraphSeparator", false, "p"); } catch (e) { /* older browsers */ }
    document.querySelectorAll("textarea[data-format-toolbar]").forEach(attach);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
