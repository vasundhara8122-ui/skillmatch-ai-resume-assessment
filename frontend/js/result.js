document.addEventListener('DOMContentLoaded', async () => {
  const assessmentId = getQueryParam('assessment_id');
  if (!assessmentId) {
    document.getElementById('resultContainer').innerHTML = '<div class="alert alert-error">No assessment result found.</div>';
    return;
  }

  try {
    const data = await apiCall(`/api/assessment/${assessmentId}/result`);
    renderResult(data);
  } catch (err) {
    document.getElementById('resultContainer').innerHTML = `<div class="alert alert-error">${err.message}</div>`;
  }
});

function safeNum(val) {
  if (val === null || val === undefined || val === '' || isNaN(val)) return 0;
  return Number(val);
}

function safeStr(val, fallback) {
  if (val === null || val === undefined || val === '' || val === 'Not Found') return fallback || 'N/A';
  return String(val);
}

function renderResult(data) {
  const { result, skill_scores, skill_matches, candidate, assessment } = data;
  const container = document.getElementById('resultContainer');

  if (!result) {
    container.innerHTML = `
      <div class="dashboard-header"><div class="container">
        <h1>Assessment Results</h1>
        <p>Results are not available yet.</p>
      </div></div>
      <div class="container" style="padding-top:32px;">
        <div class="alert alert-error">Your assessment results could not be found. This may happen if the assessment was not submitted properly. Please contact your HR representative.</div>
        <div class="text-center mt-4"><a href="/student-dashboard.html" class="btn btn-secondary">Back to Dashboard</a></div>
      </div>`;
    return;
  }

  const percentage = safeNum(result.percentage);
  const correctCount = safeNum(result.correct_count);
  const totalQuestions = safeNum(result.total_questions);
  const scoreColor = getProgressColor(percentage);

  const theoryScore = safeNum(result.theory_score);
  const mcqScore = safeNum(result.mcq_score);
  const codingScore = safeNum(result.coding_score);
  const sqlScore = safeNum(result.sql_score);
  const codeOutputScore = safeNum(result.code_output_score);
  const debuggingScore = safeNum(result.debugging_score);

  const candidateName = candidate ? safeStr(candidate.name, 'Candidate') : 'Candidate';
  const assessmentStatus = assessment ? safeStr(assessment.status, 'completed') : 'completed';
  const assessmentLevel = assessment ? safeStr(assessment.level, '') : '';

  let html = `
    <div class="dashboard-header">
      <div class="container">
        <h1>Assessment Completed</h1>
        <p>Hello, ${candidateName}</p>
      </div>
    </div>
  `;

  html += `<div class="container" style="padding-top:32px;">`;

  html += `
    <div class="card text-center mb-4 fade-in">
      <h3>Overall Score</h3>
      <div style="font-size:4rem;font-weight:800;color:var(--primary);margin:16px 0;">${percentage}%</div>
      <p style="color:var(--text-muted)">${correctCount} / ${totalQuestions} Questions Correct</p>
      <p style="color:var(--text-muted);font-size:0.9rem;">Status: <span class="badge badge-success">${assessmentStatus}</span>${assessmentLevel ? ' | Level: ' + assessmentLevel : ''}</p>
      <div class="progress-bar mt-2" style="max-width:400px;margin:16px auto;"><div class="fill ${scoreColor}" style="width:${Math.min(percentage, 100)}%"></div></div>
    </div>
  `;

  html += `
    <div class="stat-grid mb-4">
      <div class="stat-card"><div class="stat-value">${theoryScore}</div><div class="stat-label">Theory Score</div></div>
      <div class="stat-card"><div class="stat-value">${mcqScore}</div><div class="stat-label">MCQ Score</div></div>
      <div class="stat-card"><div class="stat-value">${codeOutputScore}</div><div class="stat-label">Code Output Score</div></div>
      <div class="stat-card"><div class="stat-value">${debuggingScore}</div><div class="stat-label">Debugging Score</div></div>
      <div class="stat-card"><div class="stat-value">${codingScore}</div><div class="stat-label">Coding Score</div></div>
      <div class="stat-card"><div class="stat-value">${sqlScore}</div><div class="stat-label">SQL Score</div></div>
      <div class="stat-card"><div class="stat-value">${correctCount}</div><div class="stat-label">Total Correct</div></div>
      <div class="stat-card"><div class="stat-value">${totalQuestions}</div><div class="stat-label">Total Questions</div></div>
    </div>
  `;

  if (skill_scores && skill_scores.length > 0) {
    html += `<div class="card mb-4"><h3 class="mb-2">Skill Performance</h3>`;
    skill_scores.forEach(s => {
      const pct = safeNum(s.percentage);
      const color = getProgressColor(pct);
      html += `
        <div class="skill-bar">
          <div class="skill-label"><span>${safeStr(s.skill, 'Unknown')}</span><span class="pct">${pct}%</span></div>
          <div class="progress-bar"><div class="fill ${color}" style="width:${Math.min(pct, 100)}%"></div></div>
        </div>
      `;
    });
    html += `</div>`;
  }

  if (skill_matches && skill_matches.length > 0) {
    html += `<div class="card mb-4"><h3 class="mb-2">AI Skill Match</h3>`;
    skill_matches.forEach(m => {
      const pct = safeNum(m.match_percentage);
      const cls = getMatchClass(pct);
      html += `
        <div class="match-card ${cls}">
          <div class="role-name">${safeStr(m.role_name, 'Unknown Role')}</div>
          <div class="match-pct">${pct}%</div>
        </div>
      `;
    });
    html += `
      <div class="report-note">
        Skill-match percentages are based on resume information and assessment performance.
        Final employment decisions are made by the company/HR.
      </div>
    </div>`;
  }

  html += `<div class="text-center mb-4"><a href="/student-dashboard.html" class="btn btn-secondary">Back to Dashboard</a></div>`;
  html += `</div>`;

  container.innerHTML = html;
}
