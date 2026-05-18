const studentNameInput = document.querySelector("#studentName");
const guardianNameInput = document.querySelector("#guardianName");
const studentMaleGenderInput = document.querySelector("#studentMaleGender");
const studentFemaleGenderInput = document.querySelector("#studentFemaleGender");
const guardianMaleGenderInput = document.querySelector("#guardianMaleGender");
const guardianFemaleGenderInput = document.querySelector("#guardianFemaleGender");
const platformSelector = document.querySelector("#platformSelector");
const messageList = document.querySelector("#messageList");
const copyStatus = document.querySelector("#copyStatus");
const platformTemplatesElement = document.querySelector("#platformTemplates");
let selectedPlatformId = null;

function getTemplates() {
  if (!platformTemplatesElement) {
    return [];
  }

  try {
    return JSON.parse(platformTemplatesElement.textContent);
  } catch {
    return [];
  }
}

function formatName(value, fallback) {
  const trimmedValue = value.trim();
  if (!trimmedValue) {
    return fallback;
  }

  const firstName = trimmedValue.split(/\s+/)[0];
  return firstName
    .toLocaleLowerCase("pt-BR")
    .replace(/(^|\s|-)(\p{L})/gu, (match) => match.toLocaleUpperCase("pt-BR"));
}

function getPersonGenderData(maleInput, femaleInput, fallbackLabel) {
  if (femaleInput.checked) {
    return {
      genero: "Feminino",
      ele_ela: "ela",
      o_a: "a",
      dele_dela: "dela",
      do_da: "da",
      senhor_senhora: "Sra.",
    };
  }

  if (maleInput.checked) {
    return {
      genero: "Masculino",
      ele_ela: "ele",
      o_a: "o",
      dele_dela: "dele",
      do_da: "do",
      senhor_senhora: "Sr.",
    };
  }

  return {
    genero: "Nao informado",
    ele_ela: fallbackLabel,
    o_a: "o(a)",
    dele_dela: "dele(a)",
    do_da: "do(a)",
    senhor_senhora: "Sr(a).",
  };
}

function renderText(templateText) {
  const studentName = formatName(studentNameInput.value, "[nome do aluno]");
  const guardianName = formatName(guardianNameInput.value, "[nome do responsavel]");
  const studentGender = getPersonGenderData(
    studentMaleGenderInput,
    studentFemaleGenderInput,
    "aluno(a)"
  );
  const guardianGender = getPersonGenderData(
    guardianMaleGenderInput,
    guardianFemaleGenderInput,
    "responsavel"
  );
  const responsibleName = `${guardianGender.senhor_senhora} ${guardianName}`;

  return templateText
    .replaceAll("{aluno}", studentName)
    .replaceAll("{aluno_nome}", studentName)
    .replaceAll("@student_name", studentName)
    .replaceAll("{responsavel}", guardianName)
    .replaceAll("{responsavel_nome}", guardianName)
    .replaceAll("@responsible_name", responsibleName)
    .replaceAll("{pronome_aluno}", studentGender.do_da)
    .replaceAll("{aluno_pronome}", studentGender.do_da)
    .replaceAll("{aluno_ele_ela}", studentGender.ele_ela)
    .replaceAll("{aluno_o_a}", studentGender.o_a)
    .replaceAll("{aluno_dele_dela}", studentGender.dele_dela)
    .replaceAll("{responsavel_pronome}", guardianGender.senhor_senhora)
    .replaceAll("{responsavel_tratamento}", guardianGender.senhor_senhora)
    .replaceAll("{responsavel_ele_ela}", guardianGender.ele_ela)
    .replaceAll("{responsavel_o_a}", guardianGender.o_a)
    .replaceAll("{responsavel_dele_dela}", guardianGender.dele_dela)
    .replaceAll("{genero}", studentGender.genero)
    .replaceAll("{ele_ela}", studentGender.ele_ela)
    .replaceAll("{o_a}", studentGender.o_a)
    .replaceAll("{dele_dela}", studentGender.dele_dela)
    .replaceAll("<aluno>", studentName)
    .replaceAll("<aluno_nome>", studentName)
    .replaceAll("<responsavel>", guardianName)
    .replaceAll("<responsavel_nome>", guardianName)
    .replaceAll("<pronome_aluno>", studentGender.do_da)
    .replaceAll("<aluno_pronome>", studentGender.do_da)
    .replaceAll("<aluno_ele_ela>", studentGender.ele_ela)
    .replaceAll("<aluno_o_a>", studentGender.o_a)
    .replaceAll("<aluno_dele_dela>", studentGender.dele_dela)
    .replaceAll("<responsavel_pronome>", guardianGender.senhor_senhora)
    .replaceAll("<responsavel_tratamento>", guardianGender.senhor_senhora)
    .replaceAll("<responsavel_ele_ela>", guardianGender.ele_ela)
    .replaceAll("<responsavel_o_a>", guardianGender.o_a)
    .replaceAll("<responsavel_dele_dela>", guardianGender.dele_dela)
    .replaceAll("<genero>", studentGender.genero)
    .replaceAll("<ele_ela>", studentGender.ele_ela)
    .replaceAll("<o_a>", studentGender.o_a)
    .replaceAll("<dele_dela>", studentGender.dele_dela);
}

function showCopyStatus(message) {
  copyStatus.textContent = message;
  window.setTimeout(() => {
    copyStatus.textContent = "";
  }, 1800);
}

async function copyMessage(text) {
  await navigator.clipboard.writeText(text);
  showCopyStatus("Copiado.");
}

function renderMessages() {
  messageList.innerHTML = "";
  const platforms = getTemplates();
  if (!selectedPlatformId && platforms.length > 0) {
    selectedPlatformId = String(platforms[0].id);
  }

  const selectedPlatform = platforms.find((platform) => String(platform.id) === selectedPlatformId);
  if (!selectedPlatform) {
    return;
  }

  if (selectedPlatform.responses.length === 0) {
    const emptyMessage = document.createElement("p");
    emptyMessage.className = "alert";
    emptyMessage.textContent = "Nenhuma resposta ativa cadastrada para esta plataforma.";
    messageList.append(emptyMessage);
    return;
  }

  for (const response of selectedPlatform.responses) {
    const renderedText = renderText(response.text);
    const card = document.createElement("article");
    card.className = "message-card";

    const title = document.createElement("h3");
    title.textContent = response.title;

    const header = document.createElement("header");
    header.append(title);

    const output = document.createElement("div");
    output.className = "message-output";
    output.textContent = renderedText;

    const actions = document.createElement("div");
    actions.className = "card-actions";

    const copyButton = document.createElement("button");
    copyButton.className = "copy-button";
    copyButton.type = "button";
    copyButton.textContent = "Copiar";
    copyButton.addEventListener("click", () => copyMessage(renderedText));
    actions.append(copyButton);

    card.append(header, output, actions);
    messageList.append(card);
  }
}

function renderPlatformSelector() {
  platformSelector.innerHTML = "";
  const platforms = getTemplates();
  if (platforms.length === 0) {
    return;
  }

  if (!selectedPlatformId) {
    selectedPlatformId = String(platforms[0].id);
  }

  for (const platform of platforms) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = String(platform.id) === selectedPlatformId ? "platform-tab active" : "platform-tab";
    button.textContent = platform.name;
    button.addEventListener("click", () => {
      selectedPlatformId = String(platform.id);
      renderPlatformSelector();
      renderMessages();
    });
    platformSelector.append(button);
  }
}

function enforceSingleGenderSelection(selectedInput, otherInput) {
  selectedInput.addEventListener("change", () => {
    if (selectedInput.checked) {
      otherInput.checked = false;
    }
    renderMessages();
  });
}

studentNameInput.addEventListener("input", renderMessages);
guardianNameInput.addEventListener("input", renderMessages);
enforceSingleGenderSelection(studentMaleGenderInput, studentFemaleGenderInput);
enforceSingleGenderSelection(studentFemaleGenderInput, studentMaleGenderInput);
enforceSingleGenderSelection(guardianMaleGenderInput, guardianFemaleGenderInput);
enforceSingleGenderSelection(guardianFemaleGenderInput, guardianMaleGenderInput);

renderPlatformSelector();
renderMessages();
