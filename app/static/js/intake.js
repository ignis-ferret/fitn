// app/static/js/intake.js
// Enhanced client-side intake wizard supporting grouped questions,
// conditional logic, and basic validation.

let questions = [];
let index = 0;
const answers = {};
let currentGroup = [];
let nextBtn;
let progressBar;

function updateProgress() {
  if (!progressBar) return;
  const pct = questions.length ? (index / questions.length) * 100 : 0;
  progressBar.style.width = pct + "%";
}

function showToast(msg) {
  const t = document.getElementById("toast");
  if (!t) return;
  t.textContent = msg;
  t.style.display = "block";
  setTimeout(() => {
    t.style.display = "none";
  }, 2000);
}

async function loadQuestions() {
  try {
    const res = await fetch("/api/intake/questions");
    if (!res.ok) throw new Error("Failed to load");
    const data = await res.json();
    questions = data.questions || [];
    const saved = localStorage.getItem("intake_progress");
    if (saved) {
      try {
        const state = JSON.parse(saved);
        if (state.answers && confirm("Resume where you left off?")) {
          index = state.index || 0;
          Object.assign(answers, state.answers);
        } else {
          localStorage.removeItem("intake_progress");
        }
      } catch {}
    }
    if (questions.length === 0) {
      document.getElementById("question").textContent =
        "No questions available.";
    } else {
      renderQuestion();
    }
  } catch (err) {
    document.getElementById("question").textContent =
      "Error loading questions.";
  }
}

function buildGroup() {
  currentGroup = [];
  const seen = new Set();
  let i = index;
  while (i < questions.length) {
    const q = questions[i];
    if (currentGroup.length === 0) {
      currentGroup.push(q);
      seen.add(q.variable_name);
      i += 1;
      continue;
    }
    const cond = q.conditional_on;
    if (cond && seen.has(cond.variable_name)) {
      currentGroup.push(q);
      seen.add(q.variable_name);
      i += 1;
      continue;
    }
    break;
  }
}

function renderQuestion() {
  buildGroup();
  const container = document.getElementById("question");
  container.innerHTML = "";
  container.oninput = () => {
    updateVisibility();
    updateNextButton();
  };

  currentGroup.forEach((q) => {
    const wrap = document.createElement("div");
    wrap.className = "question";
    wrap.dataset.var = q.variable_name;
    if (q.conditional_on) {
      wrap.dataset.dep = q.conditional_on.variable_name;
      wrap.dataset.depval = q.conditional_on.value;
      wrap.style.display = "none";
    }
    const label = document.createElement("p");
    label.textContent = q.text;
    wrap.appendChild(label);

    if (
      (q.type === "single-select" || q.type === "multi-select") &&
      q.options
    ) {
      const list = document.createElement("div");
      const saved = answers[q.variable_name];
      q.options.forEach((o) => {
        const l = document.createElement("label");
        l.className = "option";
        const input = document.createElement("input");
        input.type = q.type === "multi-select" ? "checkbox" : "radio";
        input.name = q.variable_name;
        input.value = o.value || o.text;
        if (saved) {
          if (Array.isArray(saved)) input.checked = saved.includes(input.value);
          else input.checked = saved === input.value;
        }
        l.appendChild(input);
        l.appendChild(document.createTextNode(o.text));
        list.appendChild(l);
      });
      wrap.appendChild(list);
    } else {
      const input = document.createElement("input");
      if (q.type === "number") {
        input.type = "range";
        const min =
          q.range && typeof q.range.min === "number" ? q.range.min : 0;
        const max =
          q.range && typeof q.range.max === "number" ? q.range.max : 100;
        input.min = min;
        input.max = max;
        input.value = answers[q.variable_name] ?? min;
        const out = document.createElement("span");
        out.className = "slider-value";
        out.textContent = input.value;
        input.addEventListener("input", () => {
          out.textContent = input.value;
        });
        wrap.appendChild(input);
        wrap.appendChild(out);
      } else {
        input.type = q.type === "time_24h" ? "time" : "text";
        if (answers[q.variable_name]) input.value = answers[q.variable_name];
        wrap.appendChild(input);
      }
      input.id = q.variable_name;
    }

    container.appendChild(wrap);
  });

  updateVisibility();
  updateNextButton();
  updateProgress();
}

function getValue(q) {
  const wrap = document.querySelector(
    `.question[data-var="${q.variable_name}"]`,
  );
  if (!wrap) return null;
  if (q.type === "multi-select") {
    return Array.from(wrap.querySelectorAll("input:checked")).map(
      (el) => el.value,
    );
  }
  if (q.type === "single-select") {
    const sel = wrap.querySelector("input:checked");
    return sel ? sel.value : null;
  }
  const inp = wrap.querySelector("input");
  return inp ? inp.value : null;
}

function updateVisibility() {
  currentGroup.forEach((q) => {
    if (!q.conditional_on) return;
    const wrap = document.querySelector(
      `.question[data-var="${q.variable_name}"]`,
    );
    let depVal = answers[q.conditional_on.variable_name];
    if (depVal === undefined) {
      const depQ = currentGroup.find(
        (qq) => qq.variable_name === q.conditional_on.variable_name,
      );
      if (depQ) depVal = getValue(depQ);
    }
    if (depVal === q.conditional_on.value) {
      wrap.style.display = "";
    } else {
      wrap.style.display = "none";
    }
  });
}

function updateNextButton() {
  if (!nextBtn) return;
  let enabled = true;
  for (const q of currentGroup) {
    if (q.optional) continue;
    const wrap = document.querySelector(
      `.question[data-var="${q.variable_name}"]`,
    );
    if (q.conditional_on && wrap.style.display === "none") continue;
    const val = getValue(q);
    if (
      val === null ||
      val === "" ||
      (Array.isArray(val) && val.length === 0)
    ) {
      enabled = false;
      break;
    }
  }
  nextBtn.classList.toggle("disabled", !enabled);
}

async function next() {
  if (nextBtn.classList.contains("disabled")) {
    showToast("Please complete the question.");
    return;
  }
  currentGroup.forEach((q) => {
    const val = getValue(q);
    if (
      val !== null &&
      val !== "" &&
      !(Array.isArray(val) && val.length === 0)
    ) {
      answers[q.variable_name] = val;
    }
  });
  index += currentGroup.length;
  while (index < questions.length) {
    const q = questions[index];
    const cond = q.conditional_on;
    if (cond && answers[cond.variable_name] !== cond.value) {
      index += 1;
    } else {
      break;
    }
  }

  if (index < questions.length) {
    localStorage.setItem("intake_progress", JSON.stringify({ index, answers }));
    renderQuestion();
  } else {
    localStorage.removeItem("intake_progress");
    await fetch("/api/intake/answers", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ answers }),
    });
    window.location.href = "/dashboard";
  }
}

document.addEventListener("DOMContentLoaded", () => {
  nextBtn = document.getElementById("nextBtn");
  progressBar = document.getElementById("progressBar");
  nextBtn.addEventListener("click", next);
  loadQuestions();
  updateProgress();
});
