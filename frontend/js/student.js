document.addEventListener('DOMContentLoaded', () => {
  const assessmentId = getQueryParam('assessment');
  if (assessmentId) {
    saveSession('pendingAssessmentId', assessmentId);
  }
});
