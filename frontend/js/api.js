const API_BASE = (typeof window !== 'undefined' && window.API_BASE_URL) ? window.API_BASE_URL : '';

async function apiCall(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const opts = {
    headers: { 'Accept': 'application/json', ...options.headers },
    ...options,
  };
  if (opts.body && !(opts.body instanceof FormData)) {
    opts.headers['Content-Type'] = 'application/json';
    opts.body = typeof opts.body === 'string' ? opts.body : JSON.stringify(opts.body);
  }
  try {
    const res = await fetch(url, opts);
    const text = await res.text();
    if (!text) {
      throw new Error('Server returned no response. Make sure the backend server is running on port 8000.');
    }
    let data;
    try {
      data = JSON.parse(text);
    } catch {
      throw new Error('Server returned an invalid response. Check the backend server.');
    }
    if (!res.ok) {
      throw new Error(data.detail || 'Request failed');
    }
    return data;
  } catch (err) {
    if (err.message.includes('Failed to fetch')) {
      throw new Error('Cannot connect to server. Make sure the backend is running (port 8000).');
    }
    throw err;
  }
}

function getQueryParam(name) {
  const params = new URLSearchParams(window.location.search);
  return params.get(name);
}

function saveSession(key, value) {
  sessionStorage.setItem(key, JSON.stringify(value));
}

function getSession(key) {
  const val = sessionStorage.getItem(key);
  return val ? JSON.parse(val) : null;
}

function clearSession(key) {
  sessionStorage.removeItem(key);
}

function showLoading(btn) {
  if (!btn) return;
  btn.disabled = true;
  btn.dataset.originalText = btn.textContent;
  btn.innerHTML = '<span class="loading"></span> Processing...';
}

function hideLoading(btn) {
  if (!btn) return;
  btn.disabled = false;
  btn.textContent = btn.dataset.originalText || 'Submit';
}

function showError(elementId, message) {
  const el = document.getElementById(elementId);
  if (el) {
    el.className = 'alert alert-error';
    el.textContent = message;
    el.classList.remove('hidden');
  }
}

function showSuccess(elementId, message) {
  const el = document.getElementById(elementId);
  if (el) {
    el.className = 'alert alert-success';
    el.textContent = message;
    el.classList.remove('hidden');
  }
}

function getProgressColor(pct) {
  if (pct >= 80) return 'green';
  if (pct >= 60) return 'blue';
  if (pct >= 40) return 'amber';
  return 'red';
}

function getMatchClass(pct) {
  if (pct >= 75) return 'high';
  if (pct >= 50) return 'medium';
  return 'low';
}
