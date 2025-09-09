// app/static/js/intake.js
// Simple client-side wizard for answering intake questions sequentially.
let questions = [];
let index = 0;
const answers = {};

async function loadQuestions() {
  try {
    const res = await fetch('/api/intake/questions');
    if (!res.ok) throw new Error('Failed to load');
    const data = await res.json();
    questions = data.questions || [];
    if (questions.length === 0) {
      document.getElementById('question').textContent = 'No questions available.';
    } else {
      renderQuestion();
    }
  } catch (err) {
    document.getElementById('question').textContent = 'Error loading questions.';
  }
}

function renderQuestion() {
  const q = questions[index];
  const container = document.getElementById('question');
  container.innerHTML = '';
  const label = document.createElement('p');
  label.textContent = q.text;
  container.appendChild(label);
  let input;
  if (q.type === 'single-select' && q.options) {
    input = document.createElement('select');
    q.options.forEach((o) => {
      const opt = document.createElement('option');
      opt.value = o.value || o.text;
      opt.textContent = o.text;
      input.appendChild(opt);
    });
  } else {
    input = document.createElement('input');
    input.type = q.type === 'number' ? 'number' : 'text';
  }
  input.id = 'answer';
  container.appendChild(input);
}

async function next() {
  const q = questions[index];
  const val = document.getElementById('answer').value;
  answers[q.variable_name] = val;
  index += 1;
  if (index < questions.length) {
    renderQuestion();
  } else {
    await fetch('/api/intake/answers', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ answers }),
    });
    window.location.href = '/dashboard';
  }
}

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('nextBtn').addEventListener('click', next);
  loadQuestions();
});
