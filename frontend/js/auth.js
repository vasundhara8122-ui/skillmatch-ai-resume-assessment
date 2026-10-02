function checkCompanyAuth() {
  const session = getSession('companySession');
  if (!session) {
    window.location.href = '/company-login.html';
    return null;
  }
  return session;
}

function checkStudentAuth() {
  const session = getSession('studentSession');
  if (!session) {
    window.location.href = '/student-login.html';
    return null;
  }
  return session;
}

function logout(role) {
  clearSession(`${role}Session`);
  window.location.href = '/index.html';
}
