// Configuration
const API_BASE_URL = '';
const REFRESH_INTERVAL = 3000; // 3 seconds

// Global variables
let chart = null;
let selectedVariables = new Set();
let allVariables = [];
let realtimeTimer = null;

const MAX_CHART_POINTS = 30;
const chartSeries = {};
let lastChartTimestamp = null;


// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    console.log('Dashboard initialized');
    initializeDashboard();
});

async function initializeDashboard() {
    try {
        updateConnectionStatus('connecting');

        setupNavigation();

        await Promise.all([
            refreshStatus(),
            refreshLatestPacket(),
            loadVariableControls(),
            loadVisibleVariables(),
            loadRecentEvents(),
            loadRecentPackets(),
            refreshDevices()
        ]);

        initializeChart();

        startRealtimeUpdates();

        updateConnectionStatus('connected');
    } catch (error) {
        console.error('Error initializing dashboard:', error);
        updateConnectionStatus('disconnected');
        showErrorMessage('Error al inicializar el dashboard');
    }
}

function setupNavigation() {
    const buttons = document.querySelectorAll('.nav-button');
    const views = document.querySelectorAll('.view');

    buttons.forEach((button) => {
        button.addEventListener('click', () => {
            const targetView = button.dataset.view;

            buttons.forEach((item) => item.classList.remove('active'));
            button.classList.add('active');

            views.forEach((view) => {
                view.classList.remove('active-view');
            });

            const selectedView = document.getElementById(targetView);
            if (selectedView) {
                selectedView.classList.add('active-view');
            }

            if (targetView === 'charts-view') {
                updateChartData();
            }
        });
    });
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

function startRealtimeUpdates() {
    if (realtimeTimer !== null) {
        clearInterval(realtimeTimer);
    }

    realtimeTimer = setInterval(async () => {
        try {
            await refreshDashboardData();
            updateConnectionStatus('connected');
            updateLastUpdate();
        } catch (error) {
            console.error('Realtime refresh error:', error);
            updateConnectionStatus('disconnected');
        }
    }, 1000);
}

// API Calls
async function apiCall(endpoint, options = {}) {
    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    const fetchOptions = { ...defaultOptions, ...options };
    const url = `${API_BASE_URL}${endpoint}`;
    
    try {
        const response = await fetch(url, fetchOptions);
        
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
    
    lastChartTimestamp = null;

    Object.keys(chartSeries).forEach((key) => {
        delete chartSeries[key];
    });

    updateChartData();
}

async function updateChartData() {
    if (!chart) return;

    try {
        const data = await apiCall('/api/latest-packet');

        if (!data.available || !data.packet) {
            return;
        }

        const packet = data.packet;
        const timestamp = packet.timestamp || new Date().toISOString();

        if (timestamp === lastChartTimestamp) {
            return;
        }

        lastChartTimestamp = timestamp;

        const timeLabel = new Date(timestamp).toLocaleTimeString();

        chart.data.labels.push(timeLabel);

        if (chart.data.labels.length > MAX_CHART_POINTS) {
            chart.data.labels.shift();
        }

        const measurements = packet.measurements || [];

        measurements.forEach((measurement) => {
            const variable = measurement.variable;
            const value = Number(measurement.value);

            if (!Number.isFinite(value)) {
                return;
            }

            if (!chartSeries[variable]) {
                chartSeries[variable] = {
                    label: variable,
                    data: Array(Math.max(chart.data.labels.length - 1, 0)).fill(null),
                    borderColor: getChartColor(Object.keys(chartSeries).length),
                    backgroundColor: getChartColor(Object.keys(chartSeries).length) + '20',
                    tension: 0.25,
                    fill: false
                };

                chart.data.datasets.push(chartSeries[variable]);
            }

            chartSeries[variable].data.push(value);

            if (chartSeries[variable].data.length > MAX_CHART_POINTS) {
                chartSeries[variable].data.shift();
            }
        });

        chart.data.datasets.forEach((dataset) => {
            if (!measurements.some((measurement) => measurement.variable === dataset.label)) {
                dataset.data.push(null);

                if (dataset.data.length > MAX_CHART_POINTS) {
                    dataset.data.shift();
                }
            }
        });

        chart.update('none');
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

function getChartColor(index) {
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

    return colors[index % colors.length];
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


async function refreshDashboardData() {
    await Promise.all([
        refreshStatus(),
        refreshLatestPacket(),
        loadRecentEvents(),
        updateChartData(),
        refreshDevices()
    ]);
}


async function refreshDevices() {
    const panel = document.getElementById('devices-panel');

    if (!panel) {
        return;
    }

    try {
        const data = await apiCall('/api/devices');
        renderDevices(data.devices || [], data.protocols || []);
    } catch (error) {
        panel.innerHTML = '<span class="error-message">Error al cargar dispositivos</span>';
    }
}

function renderDevices(devices, protocols) {
    const panel = document.getElementById('devices-panel');

    if (!panel) {
        return;
    }

    if (!devices || devices.length === 0) {
        panel.innerHTML = `
            <p style="color: var(--text-secondary);">No hay dispositivos detectados.</p>
            <p><strong>Protocolos disponibles:</strong> ${protocols.join(', ') || 'Ninguno'}</p>
        `;
        return;
    }

    panel.innerHTML = devices
        .map((device) => {
            const deviceId = escapeHtml(device.device_id);
            const protocol = escapeHtml(device.protocol);
            const status = escapeHtml(device.status);
            const connectedText = device.connected ? 'Sí' : 'No';

            const actionButton = device.connected
                ? `<button class="btn btn-danger" onclick="disconnectDevice('${deviceId}')">Desconectar</button>`
                : `<button class="btn btn-success" onclick="connectDevice('${deviceId}')">Conectar</button>`;

            return `
                <div class="device-card">
                    <h3>${deviceId}</h3>
                    <p><strong>Protocolo:</strong> ${protocol}</p>
                    <p><strong>Estado:</strong> ${status}</p>
                    <p><strong>Conectado:</strong> ${connectedText}</p>
                    <p><strong>Paquetes recibidos:</strong> ${device.packets_received ?? 0}</p>
                    <p><strong>Última detección:</strong> ${formatDateTime(device.last_seen)}</p>
                    ${actionButton}
                </div>
            `;
        })
        .join('');
}

async function connectDevice(deviceId) {
    try {
        await apiCall(`/api/devices/${encodeURIComponent(deviceId)}/connect`, {
            method: 'POST'
        });

        showSuccessMessage(`Dispositivo ${deviceId} conectado`);
        await refreshDevices();
        await refreshLatestPacket();
        await updateChartData();
    } catch (error) {
        console.error('Error connecting device:', error);
        showErrorMessage(`Error al conectar ${deviceId}`);
    }
}

async function disconnectDevice(deviceId) {
    try {
        await apiCall(`/api/devices/${encodeURIComponent(deviceId)}/disconnect`, {
            method: 'POST'
        });

        showSuccessMessage(`Dispositivo ${deviceId} desconectado`);
        await refreshDevices();
    } catch (error) {
        console.error('Error disconnecting device:', error);
        showErrorMessage(`Error al desconectar ${deviceId}`);
    }
}


function formatDateTime(value) {
    if (!value) {
        return 'N/A';
    }

    try {
        return new Date(value).toLocaleString('es-ES');
    } catch (error) {
        return value;
    }
}



// Handle page unload
window.addEventListener('beforeunload', () => {
    if (realtimeTimer !== null) {
        clearInterval(realtimeTimer);
    }
});
