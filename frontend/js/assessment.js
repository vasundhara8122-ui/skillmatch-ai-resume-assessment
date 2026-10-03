let assessmentData = null;
let currentQuestionIndex = 0;
let answers = {};
let isSubmitting = false;

document.addEventListener('DOMContentLoaded', async () => {
  const session = checkStudentAuth();
  if (!session) return;

  const assessmentId = getQueryParam('assessment_id') || getSession('pendingAssessmentId') || getSession('currentAssessmentId');
  if (!assessmentId) {
    document.getElementById('assessmentContainer').innerHTML = '<div class="alert alert-error">No assessment found. Please log in from your assessment invitation.</div>';
    return;
  }

  try {
    assessmentData = await apiCall(`/api/assessment/${assessmentId}`);
    if (assessmentData.status === 'completed') {
      window.location.href = `/result.html?assessment_id=${assessmentId}`;
      return;
    }
    renderAssessment();
  } catch (err) {
    document.getElementById('assessmentContainer').innerHTML = `<div class="alert alert-error">${err.message}</div>`;
  }
});

function renderAssessment() {
  const container = document.getElementById('assessmentContainer');
  const questions = assessmentData.questions;
  const total = questions.length;

  container.innerHTML = `
    <div class="card mb-4">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <div>
          <h3>Technical Assessment</h3>
          <p style="color:var(--text-muted)">${assessmentData.level} - ${assessmentData.level === 'Level 1' ? 'Medium' : 'Hard'} | ${total} Questions</p>
        </div>
        <div style="text-align:center">
          <div style="font-size:2rem;font-weight:800;color:var(--primary)" id="progressCount">1 / ${total}</div>
          <div style="color:var(--text-muted);font-size:0.85rem">Progress</div>
        </div>
      </div>
      <div class="progress-bar mt-2"><div class="fill blue" id="progressBar" style="width:0%"></div></div>
    </div>
    <div id="questionArea"></div>
    <div id="navArea" style="display:flex;justify-content:space-between;margin-top:24px;"></div>
  `;

  showQuestion(0);
}

function showQuestion(index) {
  const questions = assessmentData.questions;
  if (index >= questions.length) return;
  currentQuestionIndex = index;
  const q = questions[index];

  document.getElementById('progressCount').textContent = `${index + 1} / ${questions.length}`;
  document.getElementById('progressBar').style.width = `${((index) / questions.length) * 100}%`;

  const area = document.getElementById('questionArea');
  let html = `
    <div class="question-card fade-in">
      <span class="q-type q-type-${q.type}">${q.type.replace('_', ' ')} - ${q.skill}</span>
      <div class="q-text">${q.question}</div>
  `;

  if (q.type === 'mcq') {
    const options = [
      { key: 'A', text: q.option_a },
      { key: 'B', text: q.option_b },
      { key: 'C', text: q.option_c },
      { key: 'D', text: q.option_d },
    ];
    const saved = answers[q.id];
    html += '<div class="options">';
    options.forEach(opt => {
      if (!opt.text) return;
      const checked = saved === opt.key ? 'checked' : '';
      html += `<label><input type="radio" name="q${q.id}" value="${opt.key}" ${checked} onchange="saveAnswer(${q.id}, this.value)"> ${opt.key}. ${opt.text}</label>`;
    });
    html += '</div>';
  } else if (q.type === 'coding' || q.type === 'sql') {
    const saved = answers[q.id] || '';
    html += `<textarea class="code-editor" id="code_${q.id}" placeholder="Write your ${q.type === 'sql' ? 'SQL query' : 'code'} here..." oninput="saveAnswer(${q.id}, this.value)">${saved}</textarea>`;
    html += `<div class="mt-2"><button class="btn btn-secondary" onclick="runCode(${q.id})">Run Code</button> <span id="runResult_${q.id}"></span></div>`;
  } else {
    const saved = answers[q.id] || '';
    html += `<textarea class="code-editor" id="text_${q.id}" style="min-height:100px;background:#f8fafc;color:var(--text);border-color:var(--border);" placeholder="Type your answer here..." oninput="saveAnswer(${q.id}, this.value)">${saved}</textarea>`;
  }

  html += '</div>';
  area.innerHTML = html;

  const nav = document.getElementById('navArea');
  let navHtml = '';
  if (index > 0) navHtml += `<button class="btn btn-secondary" onclick="showQuestion(${index - 1})">Previous</button>`;
  else navHtml += '<div></div>';
  if (index < questions.length - 1) {
    navHtml += `<button class="btn btn-primary" onclick="showQuestion(${index + 1})">Next Question</button>`;
  } else {
    navHtml += `<button class="btn btn-success" onclick="submitAssessment()">Submit Assessment</button>`;
  }
  nav.innerHTML = navHtml;
}

function saveAnswer(questionId, value) {
  answers[questionId] = value;
}

function runCode(questionId) {
  const code = document.getElementById(`code_${questionId}`).value;
  const resultSpan = document.getElementById(`runResult_${questionId}`);
  if (!code.trim()) {
    resultSpan.innerHTML = '<span style="color:var(--error)">Editor is empty. Write your code first.</span>';
    return;
  }
  resultSpan.innerHTML = '<span class="loading"></span> Running...';
  setTimeout(() => {
    resultSpan.innerHTML = '<span style="color:var(--success)">Code recorded. You can continue to the next question.</span>';
  }, 1000);
}

async function submitAssessment() {
  if (isSubmitting) return;
  isSubmitting = true;

  const questions = assessmentData.questions;
  const unanswered = questions.filter(q => !answers[q.id] || !answers[q.id].trim());
  if (unanswered.length > 0) {
    if (!confirm(`You have ${unanswered.length} unanswered question(s). Submit anyway?`)) {
      isSubmitting = false;
      return;
    }
  }

  const payload = {
    answers: questions.map(q => ({
      question_id: q.id,
      candidate_answer: answers[q.id] || '',
    })),
  };

  const navArea = document.getElementById('navArea');
  navArea.innerHTML = '<div class="alert alert-info"><span class="loading"></span> Submitting your answers and calculating scores. Please do not close this page...</div>';

  try {
    const result = await apiCall(`/api/assessment/${assessmentData.assessment_id}/submit`, { method: 'POST', body: payload });
    saveSession('lastResult', result);
    window.location.href = `/result.html?assessment_id=${assessmentData.assessment_id}`;
  } catch (err) {
    isSubmitting = false;
    navArea.innerHTML = `<div class="alert alert-error">${err.message}</div><div style="margin-top:16px;display:flex;justify-content:space-between;"><button class="btn btn-secondary" onclick="showQuestion(${currentQuestionIndex})">Back to Assessment</button><button class="btn btn-success" onclick="submitAssessment()">Try Again</button></div>`;
  }
}
