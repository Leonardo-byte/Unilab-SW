// Configuration
const API_BASE_URL = '';
const REFRESH_INTERVAL = 3000; // 3 seconds

// Configuración para el almacenamiento de credenciales y sesión en el navegador
const AUTH_TOKEN_KEY = 'unilab_token';
const AUTH_USER_KEY = 'unilab_user';

// Global variables
let chart = null;
let selectedVariables = new Set();
let allVariables = [];
let refreshIntervalId = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    // Detiene la carga del dashboard y redirige al login si el usuario no está autenticado
    if (!requireAuth()) return;

    console.log('Dashboard initialized');

    // Muestra el nombre del usuario logueado en la interfaz
    displayCurrentUser();

    initializeDashboard();
});

async function initializeDashboard() {
    try {
        updateConnectionStatus('connecting');
        
        // Initial data load
        await Promise.all([
            refreshStatus(),
            refreshLatestPacket(),
            loadVariableControls(),
            loadVisibleVariables(),
            loadRecentEvents(),
            loadRecentPackets()
        ]);
        
        // Initialize chart
        initializeChart();
        
        // Set up auto-refresh
        startAutoRefresh();
        
        updateConnectionStatus('connected');
    } catch (error) {
        console.error('Error initializing dashboard:', error);
        updateConnectionStatus('disconnected');
        showErrorMessage('Error al inicializar el dashboard');
    }
}

// Connection status
function updateConnectionStatus(status) {
    const badge = document.getElementById('connection-status');
    badge.classList.remove('connected', 'connecting', 'disconnected');
    
    const statusTexts = {
        connected: 'Conectado',
        connecting: 'Conectando...',
        disconnected: 'Desconectado'
    };
    
    badge.classList.add(status);
    badge.textContent = statusTexts[status] || status;
}

// Auto-refresh setup
function startAutoRefresh() {
    if (refreshIntervalId) clearInterval(refreshIntervalId);
    
    refreshIntervalId = setInterval(() => {
        Promise.all([
            refreshLatestPacket(),
            loadRecentEvents(),
            loadRecentPackets()
        ]).catch(error => console.error('Auto-refresh error:', error));
    }, REFRESH_INTERVAL);
}

// API Calls
async function apiCall(endpoint, options = {}) {
    const token = getAuthToken();

    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        }
    };
    
    const fetchOptions = { ...defaultOptions, ...options };
    const url = `${API_BASE_URL}${endpoint}`;
    
    try {
        const response = await fetch(url, fetchOptions);

        if (response.status === 401) {
            localStorage.removeItem(AUTH_TOKEN_KEY);
            localStorage.removeItem(AUTH_USER_KEY);
            window.location.replace('/login.html');
            throw new Error('Sesión expirada');
        }

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error(`API Error [${endpoint}]:`, error);
        updateConnectionStatus('disconnected');
        throw error;
    }
}

// Status
async function refreshStatus() {
    try {
        const data = await apiCall('/api/status');
        
        const apiStatusEl = document.getElementById('api-status');
        const storageStatusEl = document.getElementById('storage-status');
        
        apiStatusEl.innerHTML = `<span class="status-ok">✓ ${data.api}</span>`;
        
        if (data.storage) {
            const { packets_count, events_count } = data.storage;
            const statusText = `Paquetes: ${packets_count} | Eventos: ${events_count}`;
            storageStatusEl.innerHTML = `<span class="status-ok">${statusText}</span>`;
        }
        
        updateConnectionStatus('connected');
        updateLastUpdate();
    } catch (error) {
        document.getElementById('api-status').innerHTML = '<span class="status-error">✗ Error</span>';
        document.getElementById('storage-status').innerHTML = '<span class="status-error">✗ Error</span>';
    }
}

// Latest Packet
async function refreshLatestPacket() {
    try {
        const data = await apiCall('/api/latest-packet');
        const latestPacketEl = document.getElementById('latest-packet');
        
        if (data.available && data.packet) {
            const json = JSON.stringify(data.packet, null, 2);
            latestPacketEl.innerHTML = `<pre>${escapeHtml(json)}</pre>`;
        } else {
            latestPacketEl.innerHTML = '<p style="color: var(--text-secondary);">Sin datos disponibles</p>';
        }
    } catch (error) {
        document.getElementById('latest-packet').innerHTML = '<span class="error-message">Error al cargar el paquete</span>';
    }
}

// Variables
async function loadVariableControls() {
    try {
        const data = await apiCall('/api/variables');
        allVariables = data.variables || [];
        
        const variablesListEl = document.getElementById('variables-list');
        const limitVariableEl = document.getElementById('limit-variable');
        
        // Clear existing options
        limitVariableEl.innerHTML = '<option value="">-- Selecciona una variable --</option>';
        
        variablesListEl.innerHTML = '';
        
        if (allVariables.length === 0) {
            variablesListEl.innerHTML = '<p style="color: var(--text-secondary);">No hay variables disponibles</p>';
            return;
        }
        
        allVariables.forEach(variable => {
            // Add to limit selector
            const option = document.createElement('option');
            option.value = variable;
            option.textContent = variable;
            limitVariableEl.appendChild(option);
            
            // Add checkbox
            const checkbox = document.createElement('label');
            checkbox.className = 'checkbox-item';
            checkbox.innerHTML = `
                <input type="checkbox" value="${escapeHtml(variable)}" />
                <span>${escapeHtml(variable)}</span>
            `;
            variablesListEl.appendChild(checkbox);
        });
    } catch (error) {
        document.getElementById('variables-list').innerHTML = '<span class="error-message">Error al cargar variables</span>';
    }
}

async function loadVisibleVariables() {
    try {
        const data = await apiCall('/api/visible-variables');
        const configuredVariablesEl = document.getElementById('configured-variables');
        
        if (data.configured && data.variables && data.variables.length > 0) {
            const list = data.variables
                .map(v => `<div class="checkbox-item" style="background-color: var(--bg-secondary); cursor: default;"><span>${escapeHtml(v)}</span></div>`)
                .join('');
            configuredVariablesEl.innerHTML = list;
        } else {
            configuredVariablesEl.innerHTML = '<p style="color: var(--text-secondary);">No hay variables configuradas</p>';
        }
    } catch (error) {
        document.getElementById('configured-variables').innerHTML = '<span class="error-message">Error al cargar variables visibles</span>';
    }
}

function saveVisibleVariables() {
    const checkboxes = document.querySelectorAll('#variables-list input[type="checkbox"]');
    selectedVariables.clear();
    
    checkboxes.forEach(checkbox => {
        if (checkbox.checked) {
            selectedVariables.add(checkbox.value);
        }
    });
    
    if (selectedVariables.size === 0) {
        showErrorMessage('Selecciona al menos una variable');
        return;
    }
    
    // In a real app, this would send to backend
    console.log('Selected variables:', Array.from(selectedVariables));
    showSuccessMessage(`${selectedVariables.size} variable(s) guardada(s)`);
    loadVisibleVariables();
}

// Safety Limits
function setSafetyLimits() {
    const variable = document.getElementById('limit-variable').value;
    const min = parseFloat(document.getElementById('limit-min').value);
    const max = parseFloat(document.getElementById('limit-max').value);
    
    if (!variable) {
        showErrorMessage('Selecciona una variable');
        return;
    }
    
    if (isNaN(min) || isNaN(max)) {
        showErrorMessage('Ingresa valores numéricos válidos');
        return;
    }
    
    if (min >= max) {
        showErrorMessage('El mínimo debe ser menor que el máximo');
        return;
    }
    
    console.log(`Safety limits for ${variable}: ${min} - ${max}`);
    showSuccessMessage('Límites de seguridad establecidos');
    
    // Clear inputs
    document.getElementById('limit-variable').value = '';
    document.getElementById('limit-min').value = '';
    document.getElementById('limit-max').value = '';
}

// Events
async function loadRecentEvents() {
    try {
        const data = await apiCall('/api/recent-events?limit=20');
        const eventsContainerEl = document.getElementById('events-container');
        
        if (!data.events || data.events.length === 0) {
            eventsContainerEl.innerHTML = '<p style="color: var(--text-secondary);">No hay eventos disponibles</p>';
            return;
        }
        
        const eventsHtml = data.events
            .map(event => formatEventItem(event))
            .join('');
        
        eventsContainerEl.innerHTML = eventsHtml;
    } catch (error) {
        document.getElementById('events-container').innerHTML = '<span class="error-message">Error al cargar eventos</span>';
    }
}

function formatEventItem(event) {
    const timestamp = event.timestamp ? new Date(event.timestamp).toLocaleString('es-ES') : 'N/A';
    const eventClass = event.type === 'error' ? 'error' : event.type === 'warning' ? 'warning' : '';
    
    return `
        <div class="event-item ${eventClass}">
            <div class="event-time">${escapeHtml(timestamp)}</div>
            <div class="event-message">${escapeHtml(event.message || 'Sin mensaje')}</div>
        </div>
    `;
}

// Recent Packets
async function loadRecentPackets() {
    try {
        const limit = parseInt(document.getElementById('packet-limit').value) || 10;
        const data = await apiCall(`/api/recent-packets?limit=${limit}`);
        const packetsContainerEl = document.getElementById('packets-container');
        
        if (!data.packets || data.packets.length === 0) {
            packetsContainerEl.innerHTML = '<p style="color: var(--text-secondary);">No hay paquetes disponibles</p>';
            return;
        }
        
        const tableHtml = `
            <table>
                <thead>
                    <tr>
                        <th>Timestamp</th>
                        <th>Sensor</th>
                        <th>Variables</th>
                        <th>Detalles</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.packets.map(packet => formatPacketRow(packet)).join('')}
                </tbody>
            </table>
        `;
        
        packetsContainerEl.innerHTML = tableHtml;
    } catch (error) {
        document.getElementById('packets-container').innerHTML = '<span class="error-message">Error al cargar paquetes</span>';
    }
}

function formatPacketRow(packet) {
    const timestamp = packet.timestamp ? new Date(packet.timestamp).toLocaleString('es-ES') : 'N/A';
    const sensor = packet.sensor || 'N/A';
    const variableCount = packet.measurements ? packet.measurements.length : 0;
    
    return `
        <tr>
            <td>${escapeHtml(timestamp)}</td>
            <td>${escapeHtml(sensor)}</td>
            <td>${variableCount}</td>
            <td><button class="btn btn-primary" onclick="console.log(this)">Ver</button></td>
        </tr>
    `;
}

// Chart
function initializeChart() {
    const ctx = document.getElementById('telemetry-chart');
    if (!ctx) return;
    
    if (chart) chart.destroy();
    
    chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: []
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                title: {
                    display: true,
                    text: 'Telemetría en Tiempo Real'
                }
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left'
                },
                x: {
                    display: true
                }
            }
        }
    });
    
    updateChartData();
}

async function updateChartData() {
    if (!chart) return;
    
    try {
        const data = await apiCall('/api/recent-packets?limit=30');
        
        if (!data.packets || data.packets.length === 0) return;
        
        // Prepare data
        const timestamps = data.packets.map(p => 
            p.timestamp ? new Date(p.timestamp).toLocaleTimeString() : 'N/A'
        );
        
        const variablesData = {};
        
        data.packets.forEach(packet => {
            if (packet.measurements) {
                packet.measurements.forEach(m => {
                    if (!variablesData[m.variable]) {
                        variablesData[m.variable] = [];
                    }
                    variablesData[m.variable].push(m.value);
                });
            }
        });
        
        // Generate colors
        const colors = generateChartColors(Object.keys(variablesData).length);
        
        chart.data.labels = timestamps;
        chart.data.datasets = Object.entries(variablesData).map((entry, idx) => ({
            label: entry[0],
            data: entry[1],
            borderColor: colors[idx],
            backgroundColor: colors[idx] + '20',
            tension: 0.1,
            fill: false
        }));
        
        chart.update();
    } catch (error) {
        console.error('Error updating chart:', error);
    }
}

function generateChartColors(count) {
    const colors = [
        '#2563eb',
        '#ef4444',
        '#10b981',
        '#f59e0b',
        '#8b5cf6',
        '#ec4899',
        '#06b6d4',
        '#f97316'
    ];
    
    const result = [];
    for (let i = 0; i < count; i++) {
        result.push(colors[i % colors.length]);
    }
    return result;
}

// Storage Operations
function clearStorageConfirm() {
    if (confirm('¿Estás seguro de que quieres limpiar todos los datos?')) {
        clearStorage();
    }
}

async function clearStorage() {
    try {
        const data = await apiCall('/api/clear', { method: 'POST' });
        showSuccessMessage('Almacenamiento limpiado');
        
        // Refresh all data
        await initializeDashboard();
    } catch (error) {
        showErrorMessage('Error al limpiar el almacenamiento');
    }
}


// Utility Functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function updateLastUpdate() {
    const now = new Date().toLocaleTimeString('es-ES');
    document.getElementById('last-update').textContent = now;
}

function showErrorMessage(message) {
    const container = document.createElement('div');
    container.className = 'error-message';
    container.textContent = message;
    
    showNotification(container);
}

function showSuccessMessage(message) {
    const container = document.createElement('div');
    container.className = 'success-message';
    container.textContent = message;
    
    showNotification(container);
}

function showNotification(element) {
    const card = document.querySelector('.card');
    if (card) {
        card.parentNode.insertBefore(element, card);
        
        setTimeout(() => {
            element.remove();
        }, 5000);
    }
}

// Handle page unload
window.addEventListener('beforeunload', () => {
    if (refreshIntervalId) clearInterval(refreshIntervalId);
});

// --- Funciones de Gestión de Autenticación ---

/**
 * Recupera el token Bearer almacenado en la sesión local.
 */
function getAuthToken() {
    return localStorage.getItem(AUTH_TOKEN_KEY);
}

/**
 * Valida la existencia del token. Si no existe, redirige al usuario a la vista de login.
 * Retorna true si está autenticado, false en caso contrario.
 */
function requireAuth() {
    const token = getAuthToken();

    if (!token) {
        window.location.href = 'login.html';
        return false;
    }

    return true;
}

/**
 * Intenta leer los datos del usuario logueado e inyectar su nombre en el elemento HTML id="current-user".
 */
function displayCurrentUser() {
    const userEl = document.getElementById('current-user');
    const stored = localStorage.getItem(AUTH_USER_KEY);

    if (!userEl || !stored) return;

    try {
        const user = JSON.parse(stored);
        userEl.textContent = user.username;
    } catch (error) {
        // Si el dato guardado en localStorage está corrupto o inválido, no hace nada
        console.error('Error al procesar el usuario actual:', error);
    }
}


/**
 * Cierra la sesión del usuario: invalida el token en el backend,
 * limpia el localStorage y redirige al login.
 */
function logout() {
    const token = getAuthToken();

    fetch(`${API_BASE_URL}/api/auth/logout`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token })
    }).catch(() => {});

    localStorage.removeItem(AUTH_TOKEN_KEY);
    localStorage.removeItem(AUTH_USER_KEY);
    window.location.replace('/login.html');
}
