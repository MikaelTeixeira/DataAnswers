const tokenPattern = /(&lt;responsible&gt;|&lt;student&gt;|@responsible_formal|@responsible_name|@responsible_title|@responsible_article|@responsible_subject|@responsible_object|@responsible_possessive|@responsible|@student_name|@student_pronoun|@student_article|@student_subject|@student_object|@student_possessive|@student)/g;

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
