const tokenPattern = /(@responsible_name|@student_name)/g;

function escapeHtml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function renderHighlight(textarea, highlight) {
  const escapedText = escapeHtml(textarea.value || textarea.placeholder || "");
  highlight.innerHTML = escapedText.replace(
    tokenPattern,
    '<span class="token-mark">$1</span>'
  );
}

for (const editor of document.querySelectorAll(".token-editor")) {
  const textarea = editor.querySelector(".token-textarea");
  const highlight = editor.querySelector(".token-highlight");

  renderHighlight(textarea, highlight);

  textarea.addEventListener("input", () => renderHighlight(textarea, highlight));
  textarea.addEventListener("scroll", () => {
    highlight.scrollTop = textarea.scrollTop;
    highlight.scrollLeft = textarea.scrollLeft;
  });
}
