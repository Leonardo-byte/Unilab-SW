import { useState, useEffect, useRef } from 'react'
import {LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine, Legend} from 'recharts'
import {Play, Square, AlertTriangle, CheckCircle2, Zap} from 'lucide-react'
import { api } from '../services/api'
import { useDevice } from '../context/DeviceContext.jsx'

function EnsayoMagnetico() {
  const { jaulaConectada } = useDevice()

  const [Bx, setBx] = useState(45.2)
  const [By, setBy] = useState(-12.8)
  const [Bz, setBz] = useState(22.1)

  const [magnitudTotal, setMagnitudTotal] = useState(0)
  const [ejeSeleccionado, setEjeSeleccionado] = useState('ALL')
  const [modoActivo, setModoActivo] = useState('manual')

  const [ensayoActivo, setEnsayoActivo] = useState(false)
  const [perfilValidado, setPerfilValidado] = useState(false)

  const [datosGrafica, setDatosGrafica] = useState([])
  const [telemetriaBobinas, setTelemetriaBobinas] = useState([
    { eje: 'X', corriente: 0, constante: 27.14, temperatura: 45 },
    { eje: 'Y', corriente: 0, constante: 31.32, temperatura: 42 },
    { eje: 'Z', corriente: 0, constante: 29.08, temperatura: 48 },
  ])

  const [funcionParams, setFuncionParams] = useState({
    offsetX: 0, offsetY: 0, offsetZ: 0,
    amplitudX: 20, amplitudY: 20, amplitudZ: 20,
    frecuencia: 1.0,
  })

  const [conectado, setConectado] = useState(false)
  const wsRef = useRef(null)

  useEffect(() => {
    const magnitud = Math.sqrt(Bx*Bx + By*By + Bz*Bz).toFixed(1)
    setMagnitudTotal(magnitud)
  }, [Bx, By, Bz])

  useEffect(() => {
    if (!jaulaConectada) {
      wsRef.current?.close()
      wsRef.current = null
      setConectado(false)
      return
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const ws = new WebSocket(`${protocol}//${window.location.host}/ws/telemetry`)
    let retryRef = { current: 0 }

    ws.onopen = () => setConectado(true)

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.type === 'telemetry' && data.jaula) {
        const j = data.jaula
        setTelemetriaBobinas([
          { eje: 'X', corriente: j.eje_x_corriente || 0, constante: 27.14, temperatura: 45 },
          { eje: 'Y', corriente: j.eje_y_corriente || 0, constante: 31.32, temperatura: 42 },
          { eje: 'Z', corriente: j.eje_z_corriente || 0, constante: 29.08, temperatura: 48 },
        ])

        if (ensayoActivo) {
          const now = Date.now()
          const deltaTime = ensayoStartTimeRef.current
            ? (now - ensayoStartTimeRef.current) / 1000
            : 0

          let objX = Bx
          let objY = By
          let objZ = Bz

          if (modoActivo === 'funcion') {
            const t = deltaTime
            const f = funcionParams.frecuencia
            const w = 2 * Math.PI * f
            objX = funcionParams.offsetX + funcionParams.amplitudX * Math.sin(w * t)
            objY = funcionParams.offsetY + funcionParams.amplitudY * Math.sin(w * t)
            objZ = funcionParams.offsetZ + funcionParams.amplitudZ * Math.sin(w * t)
          }

          setDatosGrafica(prev => {
            const nuevoTiempo = prev.length > 0 ? prev[prev.length - 1].tiempo + 1 : 0
            const nuevoDato = {
              tiempo: nuevoTiempo,
              tiempoReal: deltaTime.toFixed(2),
              objX: objX.toFixed(1),
              medX: (j.eje_x_campo || 0).toFixed(1),
              objY: objY.toFixed(1),
              medY: (j.eje_y_campo || 0).toFixed(1),
              objZ: objZ.toFixed(1),
              medZ: (j.eje_z_campo || 0).toFixed(1),
            }
            return [...prev, nuevoDato].slice(-120)
          })
        }
      }
    }

    ws.onclose = () => {
      setConectado(false)
      const delay = Math.min(1000 * Math.pow(1.5, retryRef.current), 10000)
      retryRef.current += 1
      setTimeout(connect, delay)
    }

    ws.onerror = () => {
      setConectado(false)
      ws.close()
    }

    wsRef.current = ws

    return () => wsRef.current?.close()
  }, [jaulaConectada, ensayoActivo, modoActivo, Bx, By, Bz, funcionParams])

  const ensayoStartTimeRef = useRef(null)

  useEffect(() => {
    if (ensayoActivo && modoActivo === 'funcion') {
      ensayoStartTimeRef.current = Date.now()
    }
  }, [ensayoActivo, modoActivo, funcionParams])

  const [logs, setLogs] = useState([
    { hora: '14:02:41', mensaje: 'Iniciando secuencia de prueba V-01...', tipo: 'info' },
    { hora: '14:02:42', mensaje: 'Verificación de hardware OK.', tipo: 'success' },
    { hora: '14:02:45', mensaje: 'Cargando perfil objetivo: MANUAL', tipo: 'info' },
    { hora: '14:03:06', mensaje: 'Consigna Bx enviada (45.2 μT).', tipo: 'info' },
    { hora: '14:03:09', mensaje: 'Corriente Eje X estabilizada.', tipo: 'success' },
    { hora: '14:03:10', mensaje: 'Consigna By enviada (-12.8 μT).', tipo: 'info' },
    { hora: '14:03:18', mensaje: 'Corriente Eje Y estabilizada.', tipo: 'success' },
    { hora: '14:04:20', mensaje: '>>> Telemetría en tiempo real activa.', tipo: 'info' },
  ])

  const validarPerfil = () => {
    if (magnitudTotal >= 35 && magnitudTotal <= 95) {
      setPerfilValidado(true)
      setLogs(prev => [...prev, {
        hora: new Date().toLocaleTimeString(),
        mensaje: `Perfil validado: ${magnitudTotal} μT (Dentro de rango)`,
        tipo: 'success'
      }])
    } else {
      setLogs(prev => [...prev, {
        hora: new Date().toLocaleTimeString(),
        mensaje: `Perfil fuera de rango: ${magnitudTotal} μT`,
        tipo: 'warning'
      }])
    }
  }

  const iniciarEnsayo = async () => {
    if (!jaulaConectada) {
      setLogs(prev => [...prev, {
        hora: new Date().toLocaleTimeString(),
        mensaje: 'La jaula debe estar conectada para iniciar',
        tipo: 'warning'
      }])
      return
    }
    if (!perfilValidado) {
      setLogs(prev => [...prev, {
        hora: new Date().toLocaleTimeString(),
        mensaje: 'Debe validar el perfil primero',
        tipo: 'warning'
      }])
      return
    }
    try {
      await api.iniciarEnsayo(Bx, By, Bz)
      setEnsayoActivo(true)
      setDatosGrafica([])
      setLogs(prev => [...prev, {
        hora: new Date().toLocaleTimeString(),
        mensaje: modoActivo === 'funcion'
          ? `▶ Ensayo iniciado (FUNCIÓN) — f=${funcionParams.frecuencia}Hz`
          : `▶ Ensayo iniciado — Bx:${Bx} By:${By} Bz:${Bz} μT`,
        tipo: 'success'
      }])
    } catch (error) {
      setLogs(prev => [...prev, {
        hora: new Date().toLocaleTimeString(),
        mensaje: `Error al iniciar ensayo: ${error.message}`,
        tipo: 'warning'
      }])
    }
  }

  const abortarSecuencia = async () => {
    try {
      await api.detenerEnsayo()
    } catch (error) {
      console.error(error)
    }
    setEnsayoActivo(false)
    setPerfilValidado(false)
    setLogs(prev => [...prev, {
      hora: new Date().toLocaleTimeString(),
      mensaje: '⏹ Secuencia detenida por usuario',
      tipo: 'warning'
    }])
  }

  const coloresEje = {
    X: { linea: '#EF4444', texto: 'text-red-400', borde: 'border-red-400' },
    Y: { linea: '#10B981', texto: 'text-green-400', borde: 'border-green-400' },
    Z: { linea: '#3B82F6', texto: 'text-blue-400', borde: 'border-blue-400' }
  }

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const p = payload[0].payload
      return (
        <div className="bg-gray-900 border border-gray-700 rounded p-3 shadow-xl">
          <p className="text-gray-300 text-xs mb-2">T-{p.tiempoReal}s</p>
          <p className="text-red-400 text-sm">OBJ X: {p.objX} μT</p>
          <p className="text-red-300 text-sm">MED X: {p.medX} μT</p>
          <p className="text-green-400 text-sm">OBJ Y: {p.objY} μT</p>
          <p className="text-green-300 text-sm">MED Y: {p.medY} μT</p>
          <p className="text-blue-400 text-sm">OBJ Z: {p.objZ} μT</p>
          <p className="text-blue-300 text-sm">MED Z: {p.medZ} μT</p>
        </div>
      )
    }
    return null
  }

  const renderLine = (label, dataKey, color, isDashed = false) => (
    <Line
      key={label}
      type="monotone"
      dataKey={dataKey}
      stroke={color}
      strokeWidth={isDashed ? 1.5 : 2.5}
      strokeDasharray={isDashed ? "5 5" : "0"}
      dot={false}
      name={label}
    />
  )

  return (
    <div className="space-y-6">

      <div className="grid grid-cols-12 gap-6">

        <div className="col-span-4 space-y-6">

          <div className="bg-[#14171e] border border-gray-800 rounded-lg p-1">
            <div className="flex space-x-1">
              <button
                onClick={() => setModoActivo('manual')}
                className={`flex-1 px-3 py-2 rounded text-xs font-semibold tracking-wider transition-all ${
                  modoActivo === 'manual'
                    ? 'bg-cyan-500 text-black'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                ENTRADA MANUAL
              </button>
              <button
                onClick={() => setModoActivo('funcion')}
                className={`flex-1 px-3 py-2 rounded text-xs font-semibold tracking-wider transition-all ${
                  modoActivo === 'funcion'
                    ? 'bg-cyan-500 text-black'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                FUNCIÓN
              </button>
            </div>
          </div>

          {modoActivo === 'manual' ? (
            <div className="bg-[#14171e] border border-gray-800 rounded-lg p-6 space-y-4">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <label className="text-gray-400 text-xs font-mono">Bx (μT)</label>
                  <input
                    type="number"
                    value={Bx}
                    onChange={(e) => setBx(parseFloat(e.target.value) || 0)}
                    className="bg-gray-900 border border-gray-700 rounded px-3 py-1 text-cyan-400 font-mono text-sm w-32 text-right"
                    step="0.1"
                  />
                </div>
                <div className="flex items-center justify-between">
                  <label className="text-gray-400 text-xs font-mono">By (μT)</label>
                  <input
                    type="number"
                    value={By}
                    onChange={(e) => setBy(parseFloat(e.target.value) || 0)}
                    className="bg-gray-900 border border-gray-700 rounded px-3 py-1 text-cyan-400 font-mono text-sm w-32 text-right"
                    step="0.1"
                  />
                </div>
                <div className="flex items-center justify-between">
                  <label className="text-gray-400 text-xs font-mono">Bz (μT)</label>
                  <input
                    type="number"
                    value={Bz}
                    onChange={(e) => setBz(parseFloat(e.target.value) || 0)}
                    className="bg-gray-900 border border-gray-700 rounded px-3 py-1 text-cyan-400 font-mono text-sm w-32 text-right"
                    step="0.1"
                  />
                </div>
              </div>

              <div className="border-t border-gray-800 pt-4 mt-4">
                <div className="flex items-center justify-between">
                  <span className="text-gray-400 text-xs font-mono">MAGNITUD TOTAL DEL CAMPO</span>
                  <span className="text-2xl font-bold text-cyan-400 font-mono">
                    {magnitudTotal} <span className="text-xs text-gray-500">μT</span>
                  </span>
                </div>
                <div className="mt-2 h-1 bg-gray-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-cyan-400 transition-all"
                    style={{ width: `${((magnitudTotal - 35) / (95 - 35)) * 100}%` }}
                  />
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-[#14171e] border border-gray-800 rounded-lg p-6 space-y-4">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-gray-400 text-xs font-mono">Offset X (μT)</label>
                  <input
                    type="number"
                    value={funcionParams.offsetX}
                    onChange={(e) => setFuncionParams(p => ({ ...p, offsetX: parseFloat(e.target.value) || 0 }))}
                    className="bg-gray-900 border border-gray-700 rounded px-2 py-1 text-cyan-400 font-mono text-sm w-24 text-right"
                    step="0.1"
                  />
                </div>
                <div className="flex items-center justify-between">
                  <label className="text-gray-400 text-xs font-mono">Offset Y (μT)</label>
                  <input
                    type="number"
                    value={funcionParams.offsetY}
                    onChange={(e) => setFuncionParams(p => ({ ...p, offsetY: parseFloat(e.target.value) || 0 }))}
                    className="bg-gray-900 border border-gray-700 rounded px-2 py-1 text-cyan-400 font-mono text-sm w-24 text-right"
                    step="0.1"
                  />
                </div>
                <div className="flex items-center justify-between">
                  <label className="text-gray-400 text-xs font-mono">Offset Z (μT)</label>
                  <input
                    type="number"
                    value={funcionParams.offsetZ}
                    onChange={(e) => setFuncionParams(p => ({ ...p, offsetZ: parseFloat(e.target.value) || 0 }))}
                    className="bg-gray-900 border border-gray-700 rounded px-2 py-1 text-cyan-400 font-mono text-sm w-24 text-right"
                    step="0.1"
                  />
                </div>
              </div>

              <div className="space-y-2 pt-2 border-t border-gray-800">
                <div className="flex items-center justify-between">
                  <label className="text-gray-400 text-xs font-mono">Amplitud X (μT)</label>
                  <input
                    type="number"
                    value={funcionParams.amplitudX}
                    onChange={(e) => setFuncionParams(p => ({ ...p, amplitudX: parseFloat(e.target.value) || 0 }))}
                    className="bg-gray-900 border border-gray-700 rounded px-2 py-1 text-cyan-400 font-mono text-sm w-24 text-right"
                    step="0.1"
                    max="50"
                  />
                </div>
                <div className="flex items-center justify-between">
                  <label className="text-gray-400 text-xs font-mono">Amplitud Y (μT)</label>
                  <input
                    type="number"
                    value={funcionParams.amplitudY}
                    onChange={(e) => setFuncionParams(p => ({ ...p, amplitudY: parseFloat(e.target.value) || 0 }))}
                    className="bg-gray-900 border border-gray-700 rounded px-2 py-1 text-cyan-400 font-mono text-sm w-24 text-right"
                    step="0.1"
                    max="50"
                  />
                </div>
                <div className="flex items-center justify-between">
                  <label className="text-gray-400 text-xs font-mono">Amplitud Z (μT)</label>
                  <input
                    type="number"
                    value={funcionParams.amplitudZ}
                    onChange={(e) => setFuncionParams(p => ({ ...p, amplitudZ: parseFloat(e.target.value) || 0 }))}
                    className="bg-gray-900 border border-gray-700 rounded px-2 py-1 text-cyan-400 font-mono text-sm w-24 text-right"
                    step="0.1"
                    max="50"
                  />
                </div>
              </div>

              <div className="pt-2 border-t border-gray-800">
                <label className="text-gray-400 text-xs font-mono block mb-1">Frecuencia (Hz)</label>
                <input
                  type="range"
                  min="0"
                  max="20"
                  step="0.1"
                  value={funcionParams.frecuencia}
                  onChange={(e) => setFuncionParams(p => ({ ...p, frecuencia: parseFloat(e.target.value) }))}
                  className="w-full h-1 bg-gray-700 rounded appearance-none"
                  style={{
                    background: `linear-gradient(to right, #06b6d4 0%, #06b6d4 ${(funcionParams.frecuencia/20)*100}%, #374151 ${(funcionParams.frecuencia/20)*100}%, #374151 100%)`
                  }}
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>0</span>
                  <span>{funcionParams.frecuencia.toFixed(1)} Hz</span>
                  <span>20</span>
                </div>
              </div>
            </div>
          )}

          <button
            onClick={validarPerfil}
            className="w-full mt-4 px-4 py-2 border border-cyan-400 text-cyan-400 rounded hover:bg-cyan-400 hover:text-black transition-all text-xs font-bold tracking-wider flex items-center justify-center gap-2"
          >
            <CheckCircle2 size={14} />
            VALIDAR PERFIL
          </button>

          <div className="grid grid-cols-2 gap-3 mt-4">
            <button
              onClick={iniciarEnsayo}
              disabled={!jaulaConectada || !perfilValidado || ensayoActivo}
              className={`px-4 py-3 rounded font-bold text-xs tracking-wider flex items-center justify-center gap-2 transition-all ${
                ensayoActivo
                  ? 'bg-green-500 text-white'
                  : jaulaConectada && perfilValidado
                  ? 'bg-green-500 hover:bg-green-600 text-white'
                  : 'bg-gray-800 text-gray-500 cursor-not-allowed'
              }`}
            >
              {ensayoActivo ? (
                <><CheckCircle2 size={14} /> EN CURSO</>
              ) : (
                <><Play size={14} /> INICIAR</>
              )}
            </button>
            <button
              onClick={abortarSecuencia}
              disabled={!ensayoActivo && !perfilValidado}
              className={`px-4 py-3 rounded font-bold text-xs tracking-wider flex items-center justify-center gap-2 transition-all ${
                !ensayoActivo && !perfilValidado
                  ? 'bg-gray-800 text-gray-600 cursor-not-allowed'
                  : 'bg-red-500 hover:bg-red-600 text-white'
              }`}
            >
              <Square size={14} />
              PARAR
            </button>
          </div>
        </div>

        <div className="col-span-8">
          <div className="bg-[#14171e] border border-gray-800 rounded-lg p-6 h-[500px]">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-gray-300 font-bold text-sm tracking-wider">
                Correlación del campo magnético
              </h3>

              <div className="flex items-center gap-2">
                {['ALL', 'X', 'Y', 'Z'].map((eje) => (
                  <button
                    key={eje}
                    onClick={() => setEjeSeleccionado(eje)}
                    className={`px-4 py-1.5 rounded text-xs font-bold tracking-wider transition-all ${
                      ejeSeleccionado === eje
                        ? 'bg-cyan-400 text-black'
                        : 'text-gray-500 hover:text-gray-300'
                    }`}
                  >
                    {eje === 'ALL' ? 'TODOS' : `EJE ${eje}`}
                  </button>
                ))}
              </div>

              <div className="flex items-center gap-4 text-xs">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-0.5 border-t-2 border-dashed border-cyan-400"></div>
                  <span className="text-gray-400">Objetivo</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-0.5 bg-green-400"></div>
                  <span className="text-gray-400">Medido</span>
                  {ensayoActivo && (
                    <span className="text-green-400 text-[10px] font-bold animate-pulse">LIVE</span>
                  )}
                </div>
              </div>
            </div>

            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={datosGrafica}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis
                  dataKey="tiempo"
                  stroke="#6B7280"
                  tick={{ fill: '#6B7280', fontSize: 10 }}
                  tickFormatter={(value) => `T-${value}s`}
                />
                <YAxis
                  stroke="#6B7280"
                  tick={{ fill: '#6B7280', fontSize: 10 }}
                  domain={[-60, 60]}
                  tickFormatter={(value) => `${value}`}
                />
                <Tooltip content={<CustomTooltip />} />
                <ReferenceLine x={0} stroke="#6B7280" strokeDasharray="3 3" />
                <ReferenceLine y={0} stroke="#6B7280" strokeDasharray="3 3" />

                {ejeSeleccionado === 'ALL' && (
                  <>
                    {renderLine('Obj X', 'objX', '#EF4444', true)}
                    {renderLine('Med X', 'medX', '#EF4444')}
                    {renderLine('Obj Y', 'objY', '#10B981', true)}
                    {renderLine('Med Y', 'medY', '#10B981')}
                    {renderLine('Obj Z', 'objZ', '#3B82F6', true)}
                    {renderLine('Med Z', 'medZ', '#3B82F6')}
                  </>
                )}
                {ejeSeleccionado === 'X' && (
                  <>
                    {renderLine('Obj X', 'objX', '#EF4444', true)}
                    {renderLine('Med X', 'medX', '#EF4444')}
                  </>
                )}
                {ejeSeleccionado === 'Y' && (
                  <>
                    {renderLine('Obj Y', 'objY', '#10B981', true)}
                    {renderLine('Med Y', 'medY', '#10B981')}
                  </>
                )}
                {ejeSeleccionado === 'Z' && (
                  <>
                    {renderLine('Obj Z', 'objZ', '#3B82F6', true)}
                    {renderLine('Med Z', 'medZ', '#3B82F6')}
                  </>
                )}
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">

        <div className="bg-[#14171e] border border-gray-800 rounded-lg p-6">
          <h3 className="text-cyan-400 font-bold text-xs tracking-wider mb-4 flex items-center gap-2">
            <Zap size={14} />
            TELEMETRÍA DE BOBINAS
          </h3>

          <div className="space-y-4">
            {telemetriaBobinas.map((bobina) => (
              <div key={bobina.eje} className="border-b border-gray-800 pb-3 last:border-0">
                <div className="flex items-center justify-between mb-2">
                  <span className={`text-sm font-semibold ${
                    bobina.eje === 'X' ? 'text-red-400' :
                    bobina.eje === 'Y' ? 'text-green-400' : 'text-cyan-400'
                  }`}>
                    Eje {bobina.eje}
                  </span>
                  <span className="text-white font-mono text-sm">
                    {bobina.corriente.toFixed(2)} A
                  </span>
                </div>

                <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden mb-2">
                  <div
                    className={`h-full transition-all ${
                      bobina.eje === 'X' ? 'bg-red-400' :
                      bobina.eje === 'Y' ? 'bg-green-400' : 'bg-cyan-400'
                    }`}
                    style={{ width: `${Math.min(100, (bobina.corriente / 3.5) * 100)}%` }}
                  />
                </div>

                <div className="flex items-center justify-between text-xs">
                  <span className="text-gray-500 font-mono">
                    K{bobina.eje}={bobina.constante} μT/A
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-[#14171e] border border-gray-800 rounded-lg p-6">
          <h3 className="text-gray-300 font-bold text-xs tracking-wider mb-4 flex items-center gap-2">
            <AlertTriangle size={14} />
            SYSTEM LOG
          </h3>

          <div className="h-[200px] overflow-y-auto font-mono text-xs space-y-1">
            {logs.map((log, index) => (
              <div key={index} className="flex items-start gap-2">
                <span className="text-gray-600">[{log.hora}]</span>
                <span className={`${
                  log.tipo === 'success' ? 'text-green-400' :
                  log.tipo === 'warning' ? 'text-yellow-400' :
                  'text-gray-400'
                }`}>
                  {log.mensaje}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

    </div>
  )
}

export default EnsayoMagnetico
