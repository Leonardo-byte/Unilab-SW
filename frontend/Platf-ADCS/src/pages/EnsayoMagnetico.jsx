import { useState, useEffect } from 'react'
import {LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine} from 'recharts'
import {Play,Square, AlertTriangle, CheckCircle2, Thermometer, Zap} from 'lucide-react'

function EnsayoMagnetico() {
  const [Bx, setBx] = useState(45.2)
  const [By, setBy] = useState(-12.8)
  const [Bz, setBz] = useState(22.1)
  
  const [magnitudTotal, setMagnitudTotal] = useState(0)
  
  const [modoActivo, setModoActivo] = useState('manual') 
  
  const [ensayoActivo, setEnsayoActivo] = useState(false)
  const [perfilValidado, setPerfilValidado] = useState(false)
  
  const [datosGrafica, setDatosGrafica] = useState([])
  
  const [telemetriaBobinas, setTelemetriaBobinas] = useState([
    { eje: 'X', corriente: 1.66, constante: 27.14, temperatura: 45 },
    { eje: 'Y', corriente: 0.82, constante: 31.32, temperatura: 42 },
    { eje: 'Z', corriente: 1.12, constante: 29.08, temperatura: 48 },
  ])
  
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

  useEffect(() => {
    const magnitud = Math.sqrt(Bx*Bx + By*By + Bz*Bz).toFixed(1)
    setMagnitudTotal(magnitud)
  }, [Bx, By, Bz])

  useEffect(() => {
    if (!ensayoActivo) return

    const intervalo = setInterval(() => {
      setDatosGrafica(prev => {
        const ultimoTiempo = prev.length > 0 ? prev[prev.length - 1].tiempo : 0
        const nuevoTiempo = ultimoTiempo + 1
        
        const campoObjetivo = 50 * Math.sin(nuevoTiempo * 0.1) + 20
        const campoMedido = campoObjetivo + (Math.random() - 0.5) * 5
        
        const nuevoDato = {
          tiempo: nuevoTiempo,
          objetivo: campoObjetivo.toFixed(1),
          medido: campoMedido.toFixed(1),
          timestamp: new Date().toLocaleTimeString()
        }
        
        const nuevosDatos = [...prev, nuevoDato].slice(-60)
        return nuevosDatos
      })
    }, 1000)

    return () => clearInterval(intervalo)
  }, [ensayoActivo])

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

  const iniciarEnsayo = () => {
    if (!perfilValidado) {
      setLogs(prev => [...prev, {
        hora: new Date().toLocaleTimeString(),
        mensaje: 'Debe validar el perfil primero',
        tipo: 'warning'
      }])
      return
    }
    setEnsayoActivo(true)
    setDatosGrafica([])
    setLogs(prev => [...prev, {
      hora: new Date().toLocaleTimeString(),
      mensaje: '▶ Ensayo iniciado',
      tipo: 'success'
    }])
  }

  const abortarSecuencia = () => {
    setEnsayoActivo(false)
    setPerfilValidado(false)
    setLogs(prev => [...prev, {
      hora: new Date().toLocaleTimeString(),
      mensaje: '⏹ Secuencia abortada por usuario',
      tipo: 'warning'
    }])
  }

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-gray-900 border border-gray-700 rounded p-3 shadow-xl">
          <p className="text-gray-300 text-xs mb-2">T-{payload[0].payload.tiempo}s</p>
          <p className="text-cyan-400 text-sm">
            OBJ: {payload[0].value} nT
          </p>
          <p className="text-green-400 text-sm">
            REAL: {payload[1].value} nT
          </p>
        </div>
      )
    }
    return null
  }

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
                onClick={() => setModoActivo('igrf')}
                className={`flex-1 px-3 py-2 rounded text-xs font-semibold tracking-wider transition-all ${
                  modoActivo === 'igrf'
                    ? 'bg-cyan-500 text-black'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                IMPORT IGRF
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
                disabled={!perfilValidado || ensayoActivo}
                className={`px-4 py-3 rounded font-bold text-xs tracking-wider flex items-center justify-center gap-2 transition-all ${
                  ensayoActivo
                    ? 'bg-green-500 text-white'
                    : perfilValidado
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
                PARAR.
              </button>
            </div>
          </div>
        </div>

        <div className="col-span-8">
          <div className="bg-[#14171e] border border-gray-800 rounded-lg p-6 h-[500px]">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-gray-300 font-bold text-sm tracking-wider">
                Correlación del campo magnético
              </h3>
              <div className="flex items-center gap-4 text-xs">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-0.5 border-t-2 border-dashed border-cyan-400"></div>
                  <span className="text-gray-400">Campo Magnético Objetivo</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-0.5 bg-green-400"></div>
                  <span className="text-gray-400">Campo Medido</span>
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
                  domain={[-50, 50]}
                  tickFormatter={(value) => `${value}`}
                />
                <Tooltip content={<CustomTooltip />} />
                <ReferenceLine x={0} stroke="#6B7280" strokeDasharray="3 3" />
                <ReferenceLine y={0} stroke="#6B7280" strokeDasharray="3 3" />
                
                <Line
                  type="monotone"
                  dataKey="objetivo"
                  stroke="#06B6D4"
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  dot={false}
                  name="OBJ"
                />
                
                <Line
                  type="monotone"
                  dataKey="medido"
                  stroke="#10B981"
                  strokeWidth={3}
                  dot={false}
                  name="REAL"
                />
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
                    {bobina.corriente} A
                  </span>
                </div>
                
                <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden mb-2">
                  <div
                    className={`h-full transition-all ${
                      bobina.eje === 'X' ? 'bg-red-400' :
                      bobina.eje === 'Y' ? 'bg-green-400' : 'bg-cyan-400'
                    }`}
                    style={{ width: `${(bobina.corriente / 3.5) * 100}%` }}
                  />
                </div>
                
                <div className="flex items-center justify-between text-xs">
                  <span className="text-gray-500 font-mono">
                    K{bobina.eje}={bobina.constante} μT/A
                  </span>
                  <div className="flex items-center gap-1">
                    <Thermometer size={10} className="text-gray-500" />
                    <span className={`font-mono ${
                      bobina.temperatura > 45 ? 'text-yellow-400' : 'text-green-400'
                    }`}>
                      {bobina.temperatura}°C
                    </span>
                  </div>
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