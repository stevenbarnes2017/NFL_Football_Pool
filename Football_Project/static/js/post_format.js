// Formatting toolbar for message board and announcement textareas.
// Usage: <textarea data-format-toolbar [data-upload-context="announcement"]>.
// Inserts the plain-text markers that Football_Project/services/text_format.py
// renders (**bold**, *italic*, lists, links, ![image](/board/images/...)).
// Images can be added with the Image button, by pasting, or by drag and drop.
(function () {
  const BUTTONS = [
    { label: "B", title: "Bold (Ctrl+B)", style: "font-weight:700", action: "wrap", marker: "**", key: "b" },
    { label: "I", title: "Italic (Ctrl+I)", style: "font-style:italic", action: "wrap", marker: "*", key: "i" },
    { label: "H", title: "Heading", style: "font-weight:700", action: "prefix", prefix: () => "# " },
    { label: "• List", title: "Bulleted list", action: "prefix", prefix: () => "- " },
    { label: "1. List", title: "Numbered list", action: "prefix", prefix: (i) => `${i + 1}. ` },
    { label: "Link", title: "Insert link", action: "link" },
    { label: "Image", title: "Add image (or paste / drag one in)", action: "image" },
  ];

  const MAX_BYTES = 5 * 1024 * 1024;
  const MAX_DIMENSION = 1600;
  const ALLOWED = ["image/png", "image/jpeg", "image/gif", "image/webp"];

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
    else if (b.action === "image") pickImage(ta);
  }

  // ---- images ----
  function pickImage(ta) {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = ALLOWED.join(",");
    input.multiple = true;
    input.addEventListener("change", () => Array.from(input.files).forEach((f) => uploadImage(ta, f)));
    input.click();
  }

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

  function setBusy(ta, delta) {
    ta._pfUploads = (ta._pfUploads || 0) + delta;
    const form = ta.closest("form");
    if (!form) return;
    form.querySelectorAll('button[type="submit"], input[type="submit"]').forEach((btn) => {
      btn.disabled = ta._pfUploads > 0;
    });
    if (ta._pfStatus) ta._pfStatus.textContent = ta._pfUploads > 0 ? "Uploading image…" : "";
  }

  async function uploadImage(ta, file) {
    if (!ALLOWED.includes(file.type)) {
      window.alert("Only PNG, JPEG, GIF or WebP images can be added.");
      return;
    }
    const placeholder = `![Uploading ${file.name || "image"}…]()`;
    const atLineStart = ta.selectionStart === 0 || ta.value[ta.selectionStart - 1] === "\n";
    replaceSelection(ta, (atLineStart ? "" : "\n") + placeholder + "\n");
    setBusy(ta, 1);
    try {
      const blob = await prepare(file);
      if (blob.size > MAX_BYTES) throw new Error("Image is too large (max 5 MB).");
      const body = new FormData();
      body.append("image", blob, file.name || "image");
      body.append("context", ta.dataset.uploadContext || "board");
      const tokenInput = ta.closest("form") && ta.closest("form").querySelector('input[name="csrf_token"]');
      const res = await fetch("/board/images", {
        method: "POST",
        body,
        credentials: "same-origin",
        headers: tokenInput ? { "X-CSRFToken": tokenInput.value } : {},
      });
      let data = {};
      try { data = await res.json(); } catch (e) { /* non-JSON error page */ }
      if (!res.ok || !data.markdown) {
        throw new Error(data.error || (res.status === 413 ? "Image is too large." : `Upload failed (${res.status}).`));
      }
      ta.value = ta.value.replace(placeholder, data.markdown);
    } catch (e) {
      ta.value = ta.value.replace(placeholder + "\n", "").replace(placeholder, "");
      window.alert(e.message || "Image upload failed.");
    } finally {
      ta.dispatchEvent(new Event("input", { bubbles: true }));
      setBusy(ta, -1);
    }
  }

  function imageFiles(dataTransfer) {
    return dataTransfer ? Array.from(dataTransfer.files || []).filter((f) => f.type.startsWith("image/")) : [];
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

    ta.addEventListener("paste", (e) => {
      const files = imageFiles(e.clipboardData);
      if (!files.length) return;
      e.preventDefault();
      files.forEach((f) => uploadImage(ta, f));
    });
    ta.addEventListener("dragover", (e) => {
      if (Array.from(e.dataTransfer.items || []).some((i) => i.kind === "file")) {
        e.preventDefault();
        ta.classList.add("pf-drop");
      }
    });
    ta.addEventListener("dragleave", () => ta.classList.remove("pf-drop"));
    ta.addEventListener("drop", (e) => {
      ta.classList.remove("pf-drop");
      const files = imageFiles(e.dataTransfer);
      if (!files.length) return;
      e.preventDefault();
      files.forEach((f) => uploadImage(ta, f));
    });

    const hint = document.createElement("div");
    hint.className = "pf-hint";
    hint.textContent = "**bold**  *italic*  # heading  - list  1. list  [text](https://…)  ·  paste or drag in images";
    const status = document.createElement("span");
    status.className = "pf-status";
    status.setAttribute("aria-live", "polite");
    hint.appendChild(status);
    ta._pfStatus = status;
    ta.insertAdjacentElement("afterend", hint);
  }

  function init() {
    document.querySelectorAll("textarea[data-format-toolbar]").forEach(attach);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
