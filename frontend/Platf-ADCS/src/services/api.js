const API_BASE = '/api'

async function fetchJSON(endpoint, options = {}) {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!response.ok) {
    throw new Error(`Error ${response.status}: ${response.statusText}`)
  }
  return response.json()
}

export const api = {
  login: (username, password) =>
    fetchJSON('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    }),

  logout: () =>
    fetchJSON('/auth/logout', { method: 'POST' }),

  verify: () => fetchJSON('/auth/verify'),

  getStatus: () => fetchJSON('/status'),

  getJaulaTelemetry: () => fetchJSON('/telemetry/jaula'),

  getCubesatTelemetry: () => fetchJSON('/telemetry/cubesat'),

  iniciarEnsayo: (bx, by, bz) =>
    fetchJSON('/telemetry/jaula/iniciar', {
      method: 'POST',
      body: JSON.stringify({ bx, by, bz }),
    }),

  detenerEnsayo: () =>
    fetchJSON('/telemetry/jaula/detener', { method: 'POST' }),

  conectarJaula: () =>
    fetchJSON('/control/jaula/conectar', { method: 'POST' }),

  desconectarJaula: () =>
    fetchJSON('/control/jaula/desconectar', { method: 'POST' }),

  conectarCubesat: () =>
    fetchJSON('/control/cubesat/conectar', { method: 'POST' }),

  desconectarCubesat: () =>
    fetchJSON('/control/cubesat/desconectar', { method: 'POST' }),

  estadoJaula: () => fetchJSON('/control/jaula/estado'),

  estadoCubesat: () => fetchJSON('/control/cubesat/estado'),

  getSessions: (limit = 10) => fetchJSON(`/control/sessions?limit=${limit}`),

  createSession: (nombre, alumno, tipo_prueba, descripcion) =>
    fetchJSON('/control/sessions', {
      method: 'POST',
      body: JSON.stringify({ nombre, alumno, tipo_prueba, descripcion }),
    }),

  cerrarSession: (id) =>
    fetchJSON(`/control/sessions/${id}/cerrar`, { method: 'POST' }),

  setCorriente: (eje, corriente) =>
    fetchJSON('/control/jaula/corriente', {
      method: 'POST',
      body: JSON.stringify({ eje, corriente }),
    }),

  setPerfilMagnetico: (bx, by, bz) =>
    fetchJSON('/control/jaula/perfil', {
      method: 'POST',
      body: JSON.stringify({ bx, by, bz }),
    }),
}
