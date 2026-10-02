document.addEventListener('DOMContentLoaded', () => {
  const uploadArea = document.getElementById('uploadArea');
  const fileInput = document.getElementById('fileInput');
  const resultDiv = document.getElementById('uploadResult');
  const errorDiv = document.getElementById('uploadError');

  if (uploadArea && fileInput) {
    uploadArea.addEventListener('click', () => fileInput.click());
    uploadArea.addEventListener('dragover', (e) => { e.preventDefault(); uploadArea.classList.add('dragover'); });
    uploadArea.addEventListener('dragleave', () => uploadArea.classList.remove('dragover'));
    uploadArea.addEventListener('drop', (e) => {
      e.preventDefault();
      uploadArea.classList.remove('dragover');
      if (e.dataTransfer.files.length) {
        fileInput.files = e.dataTransfer.files;
        handleUpload(e.dataTransfer.files[0]);
      }
    });
    fileInput.addEventListener('change', () => {
      if (fileInput.files.length) handleUpload(fileInput.files[0]);
    });
  }

  async function handleUpload(file) {
    errorDiv.classList.add('hidden');
    resultDiv.innerHTML = '<div class="alert alert-info"><span class="loading"></span> Analyzing resume...</div>';

    const formData = new FormData();
    formData.append('file', file);

    try {
      const data = await apiCall('/api/resume/upload', { method: 'POST', body: formData });
      saveSession('currentCandidate', data.candidate);
      saveSession('currentSkills', data.skills);
      saveSession('currentAssessmentId', data.assessment_id);
      window.location.href = `/resume-analysis.html?candidate_id=${data.candidate.id}`;
    } catch (err) {
      resultDiv.innerHTML = '';
      showError('uploadError', err.message || 'Failed to analyze resume');
    }
  }
});
