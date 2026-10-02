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

function renderResult(data) {
  const { result, skill_scores, skill_matches, candidate, assessment } = data;
  const container = document.getElementById('resultContainer');

  const scoreColor = getProgressColor(result.percentage);

  let html = `
    <div class="dashboard-header">
      <div class="container">
        <h1>Assessment Completed</h1>
        <p>Hello, ${candidate.name}</p>
      </div>
    </div>
  `;

  html += `<div class="container" style="padding-top:32px;">`;

  html += `
    <div class="card text-center mb-4 fade-in">
      <h3>Overall Score</h3>
      <div style="font-size:4rem;font-weight:800;color:var(--primary);margin:16px 0;">${result.percentage}%</div>
      <p style="color:var(--text-muted)">${result.correct_count} / ${result.total_questions} Questions Correct</p>
      <div class="progress-bar mt-2" style="max-width:400px;margin:16px auto;"><div class="fill ${scoreColor}" style="width:${result.percentage}%"></div></div>
    </div>
  `;

  html += `
    <div class="grid grid-4 mb-4">
      <div class="stat-card"><div class="stat-value">${result.theory_score}</div><div class="stat-label">Theory Score</div></div>
      <div class="stat-card"><div class="stat-value">${result.mcq_score}</div><div class="stat-label">MCQ Score</div></div>
      <div class="stat-card"><div class="stat-value">${result.coding_score}</div><div class="stat-label">Coding Score</div></div>
      <div class="stat-card"><div class="stat-value">${result.sql_score}</div><div class="stat-label">SQL Score</div></div>
    </div>
  `;

  html += `<div class="card mb-4"><h3 class="mb-2">Skill Performance</h3>`;
  skill_scores.forEach(s => {
    const color = getProgressColor(s.percentage);
    html += `
      <div class="skill-bar">
        <div class="skill-label"><span>${s.skill}</span><span class="pct">${s.percentage}%</span></div>
        <div class="progress-bar"><div class="fill ${color}" style="width:${s.percentage}%"></div></div>
      </div>
    `;
  });
  html += `</div>`;

  html += `<div class="card mb-4"><h3 class="mb-2">AI Skill Match</h3>`;
  skill_matches.forEach(m => {
    const cls = getMatchClass(m.match_percentage);
    html += `
      <div class="match-card ${cls}">
        <div class="role-name">${m.role_name}</div>
        <div class="match-pct">${m.match_percentage}%</div>
      </div>
    `;
  });
  html += `
    <div class="report-note">
      Skill-match percentages are based on resume information and assessment performance.
      Final employment decisions are made by the company/HR.
    </div>
  </div>`;

  html += `<div class="text-center mb-4"><a href="/student-dashboard.html" class="btn btn-secondary">Back to Dashboard</a></div>`;
  html += `</div>`;

  container.innerHTML = html;
}
