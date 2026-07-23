function normalizeSearchText(value) {
  return value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .trim();
}

function searchableItemText(item) {
  const formValues = [...item.querySelectorAll("input, textarea, select")]
    .map((field) => field.value)
    .join(" ");
  return `${item.textContent} ${formValues}`;
}

for (const input of document.querySelectorAll("[data-list-search]")) {
  const list = document.querySelector(`#${input.dataset.listSearch}`);
  if (!list) {
    continue;
  }

  const items = [...list.querySelectorAll("[data-search-item]")];
  const emptyResult = list.querySelector("[data-empty-search]");

  input.addEventListener("input", () => {
    const query = normalizeSearchText(input.value);
    let visibleItems = 0;

    for (const item of items) {
      const matches = !query || normalizeSearchText(searchableItemText(item)).includes(query);
      item.hidden = !matches;
      if (matches) {
        visibleItems += 1;
      }
    }

    if (emptyResult) {
      emptyResult.hidden = !query || visibleItems > 0;
    }
  });
}
