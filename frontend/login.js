// Configuration (igual que en app.js: vacío porque Nginx hace de proxy a /api)
const API_BASE_URL = '';

document.addEventListener('DOMContentLoaded', () => {
    // Si ya hay una sesión guardada, no mostrar el login de nuevo.
    const existingToken = localStorage.getItem('unilab_token');

    if (existingToken) {
        window.location.href = 'index.html';
        return;
    }

    const form = document.getElementById('login-form');
    form.addEventListener('submit', handleLogin);
});

async function handleLogin(event) {
    event.preventDefault();

    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    const submitBtn = document.getElementById('login-submit');

    hideLoginError();

    if (!username || !password) {
        showLoginError('Completa usuario y contraseña.');
        return;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = 'Ingresando...';

    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || 'Usuario o contraseña incorrectos.');
        }

        const data = await response.json();

        localStorage.setItem('unilab_token', data.token);
        localStorage.setItem('unilab_user', JSON.stringify(data.user));

        window.location.href = 'index.html';
    } catch (error) {
        showLoginError(error.message || 'No se pudo iniciar sesión.');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Ingresar';
    }
}

function showLoginError(message) {
    const errorEl = document.getElementById('login-error');
    errorEl.textContent = message;
    errorEl.style.display = 'block';
}

function hideLoginError() {
    const errorEl = document.getElementById('login-error');
    errorEl.textContent = '';
    errorEl.style.display = 'none';
}