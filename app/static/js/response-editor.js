const tokenPattern = /(&lt;[a-zA-Z0-9_-]+&gt;)/g;

function escapeHtml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function renderPreview(textarea, preview) {
  const escapedText = escapeHtml(textarea.value || textarea.placeholder || "");
  preview.innerHTML = escapedText.replace(
    tokenPattern,
    '<span class="token-mark">$1</span>'
  );
}

for (const editor of document.querySelectorAll(".token-editor")) {
  const textarea = editor.querySelector(".token-textarea");
  const preview = editor.querySelector(".token-preview");

  renderPreview(textarea, preview);

  textarea.addEventListener("input", () => renderPreview(textarea, preview));
}
