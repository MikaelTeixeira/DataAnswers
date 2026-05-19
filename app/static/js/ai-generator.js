const aiReplyForm = document.querySelector("#aiReplyForm");
const generatedReply = document.querySelector("#generatedReply");
const generationStatus = document.querySelector("#generationStatus");
const copyGeneratedReply = document.querySelector("#copyGeneratedReply");
const platformId = document.querySelector("#platformId");
const platformDataElement = document.querySelector("#platformData");
const useStructure = document.querySelector("#useStructure");
const structureField = document.querySelector("#structureField");
const structureId = document.querySelector("#structureId");
const situationField = document.querySelector("#situationField");
const situation = document.querySelector("#situation");

function getPlatformData() {
  try {
    return JSON.parse(platformDataElement.textContent);
  } catch {
    return [];
  }
}

function setStatus(message) {
  generationStatus.textContent = message;
}

function renderStructures() {
  const platforms = getPlatformData();
  const selectedPlatform = platforms.find((platform) => String(platform.id) === platformId.value);
  const structures = selectedPlatform ? selectedPlatform.structures : [];

  structureId.innerHTML = "";
  for (const structure of structures) {
    const option = document.createElement("option");
    option.value = structure.id;
    option.textContent = structure.title;
    structureId.append(option);
  }

  if (structures.length === 0) {
    const option = document.createElement("option");
    option.value = "";
    option.textContent = "Nenhuma estrutura cadastrada";
    structureId.append(option);
  }
}

function updateMode() {
  const shouldUseStructure = useStructure.checked;
  structureField.classList.toggle("hidden-field", !shouldUseStructure);
  situationField.classList.toggle("hidden-field", shouldUseStructure);
  structureId.required = shouldUseStructure;
  situation.required = !shouldUseStructure;
}

platformId.addEventListener("change", renderStructures);
useStructure.addEventListener("change", updateMode);

renderStructures();
updateMode();

aiReplyForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  setStatus("Gerando...");
  generatedReply.textContent = "";

  const formData = new FormData(aiReplyForm);

  try {
    const response = await fetch("/api/generate-reply", {
      method: "POST",
      body: formData,
    });
    const data = await response.json();

    if (!response.ok) {
      generatedReply.textContent = data.error || "Nao foi possivel gerar a resposta.";
      setStatus("Erro.");
      return;
    }

    generatedReply.textContent = data.reply;
    setStatus("Pronto.");
  } catch {
    generatedReply.textContent = "Nao foi possivel conectar ao servidor.";
    setStatus("Erro.");
  }
});

copyGeneratedReply.addEventListener("click", async () => {
  const text = generatedReply.textContent.trim();
  if (!text || text === "A resposta gerada aparecera aqui.") {
    return;
  }

  await navigator.clipboard.writeText(text);
  setStatus("Copiado.");
});
