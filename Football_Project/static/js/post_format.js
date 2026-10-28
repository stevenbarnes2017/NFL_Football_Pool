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
    if (tag === "B" || tag === "STRONG") return wrapLines(inlineText(node), "**");
    if (tag === "I" || tag === "EM") return wrapLines(inlineText(node), "_");
    if (tag === "A") {
      const href = node.getAttribute("href") || "";
      const text = inlineText(node).trim();
      if (!/^https?:\/\//i.test(href)) return text;
      return text && text !== href ? `[${text}](${href})` : href;
    }
    if (BLOCKS.has(tag)) return "\n" + inlineText(node) + "\n";
    return inlineText(node); // span, font, u, etc.
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

    // Paste: pictures become pictures; everything else comes in as plain
    // text (no fonts/colours from Word or web pages).
    editor.addEventListener("paste", (e) => {
      const files = imageFiles(e.clipboardData);
      e.preventDefault();
      if (files.length) {
        files.forEach(addPicture);
        return;
      }
      const text = e.clipboardData ? e.clipboardData.getData("text/plain") : "";
      if (text) document.execCommand("insertText", false, text);
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
