import { useState, useEffect, useRef } from 'react'
import { ChevronUp, ChevronDown, Radio, RotateCcw, Activity, Wifi, WifiOff } from 'lucide-react'
import { useDevice } from '../context/DeviceContext.jsx'

function Telemetria() {
  const { cubesatConectado } = useDevice()
  const [telemetria, setTelemetria] = useState({
    roll: 0,
    pitch: 0,
    yaw: 0,
    q0: 0,
    q1: 0,
    q2: 0,
    q3: 0,
    acc: { x: 0, y: 0, z: 0 },
    gyro: { x: 0, y: 0, z: 0 },
    mag: { x: 0, y: 0, z: 0 },
    sun: { x: 0, negX: 0, y: 0, negY: 0, z: 0, negZ: 0 },
    adcsMode: '---',
    sunSensors: { sun_1: 0, sun_2: 0, sun_3: 0, sun_4: 0, sun_5: 0, sun_6: 0 }
  })

  const [consolaExpandida, setConsolaExpandida] = useState(true)
  const [logsTelemetria, setLogsTelemetria] = useState([])
  const [conectado, setConectado] = useState(false)
  const wsRef = useRef(null)

  useEffect(() => {
    if (!cubesatConectado) {
      wsRef.current?.close()
      wsRef.current = null
      setConectado(false)
      return
    }

    const connect = () => {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const ws = new WebSocket(`${protocol}//${window.location.host}/ws/telemetry`)

      ws.onopen = () => setConectado(true)

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data)
        if (data.type === 'telemetry' && data.cubesat) {
          const c = data.cubesat
          setTelemetria({
            roll: c.roll || 0,
            pitch: c.pitch || 0,
            yaw: c.yaw || 0,
            q0: c.q0 || 0,
            q1: c.q1 || 0,
            q2: c.q2 || 0,
            q3: c.q3 || 0,
            acc: { x: c.acc_x || 0, y: c.acc_y || 0, z: c.acc_z || 0 },
            gyro: { x: c.gyro_x || 0, y: c.gyro_y || 0, z: c.gyro_z || 0 },
            mag: { x: c.mag_x || 0, y: c.mag_y || 0, z: c.mag_z || 0 },
            sun: {
              x: c.sun_1 || 0,
              negX: c.sun_2 || 0,
              y: c.sun_3 || 0,
              negY: c.sun_4 || 0,
              z: c.sun_5 || 0,
              negZ: c.sun_6 || 0
            },
            adcsMode: c.adcs_mode || '---',
            sunSensors: {
              sun_1: c.sun_1 || 0,
              sun_2: c.sun_2 || 0,
              sun_3: c.sun_3 || 0,
              sun_4: c.sun_4 || 0,
              sun_5: c.sun_5 || 0,
              sun_6: c.sun_6 || 0
            }
          })

          setLogsTelemetria(prev => {
            const nuevo = {
              timestamp: Math.floor(Date.now() / 1000),
              roll: c.roll,
              pitch: c.pitch,
              yaw: c.yaw,
              sun_1: c.sun_1,
              sun_2: c.sun_2,
              sun_3: c.sun_3,
              sun_4: c.sun_4,
              sun_5: c.sun_5,
              sun_6: c.sun_6
            }
            return [...prev, nuevo].slice(-50)
          })
        }
      }

      ws.onclose = () => {
        setConectado(false)
        const delay = Math.min(1000 * Math.pow(1.5, retryCount.current), 10000)
        retryCount.current += 1
        setTimeout(connect, delay)
      }

      ws.onerror = () => {
        setConectado(false)
        ws.close()
      }

      wsRef.current = ws
    }
    let retryCount = { current: 0 }

    connect()

    return () => wsRef.current?.close()
  }, [cubesatConectado])

  const formatNumber = (num, decimals = 1) => num.toFixed(decimals)

  return (
    <div className="space-y-6">

      <div className="grid grid-cols-12 gap-6">

        <div className="col-span-4 space-y-6">

          <div className="bg-[#14171e] border border-gray-800 rounded-lg p-5">
            <h3 className="text-gray-400 text-xs font-bold tracking-wider mb-4">
              ESTADOS CINEMÁTICOS
            </h3>

            <div className="grid grid-cols-3 gap-3">
              <div className="bg-[#0a0c10] border border-gray-800 rounded p-3 text-center">
                <p className="text-gray-500 text-[10px] mb-1">ROLL</p>
                <p className="text-cyan-400 font-mono text-xl font-bold">
                  {telemetria.roll >= 0 ? '+' : ''}{formatNumber(telemetria.roll)}°
                </p>
              </div>
              <div className="bg-[#0a0c10] border border-gray-800 rounded p-3 text-center">
                <p className="text-gray-500 text-[10px] mb-1">PITCH</p>
                <p className="text-cyan-400 font-mono text-xl font-bold">
                  {formatNumber(telemetria.pitch)}°
                </p>
              </div>
              <div className="bg-[#0a0c10] border border-gray-800 rounded p-3 text-center">
                <p className="text-gray-500 text-[10px] mb-1">YAW</p>
                <p className="text-cyan-400 font-mono text-xl font-bold">
                  {telemetria.yaw >= 0 ? '+' : ''}{formatNumber(telemetria.yaw)}°
                </p>
              </div>
            </div>
          </div>

          <div className="bg-[#14171e] border border-gray-800 rounded-lg p-5">
            <h3 className="text-gray-400 text-xs font-bold tracking-wider mb-4">
              CUATERNIONES
            </h3>

            <div className="grid grid-cols-4 gap-2">
              {['q0', 'q1', 'q2', 'q3'].map((q) => (
                <div key={q} className="text-center">
                  <p className="text-gray-500 text-[10px] mb-1">{q}:</p>
                  <p className="text-cyan-400 font-mono text-sm font-bold">
                    {telemetria[q].toFixed(3)}
                  </p>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-[#14171e] border border-gray-800 rounded-lg p-5">
            <h3 className="text-gray-400 text-xs font-bold tracking-wider mb-4">
              DATOS
            </h3>

            <div className="space-y-3">
              <div className="flex items-center justify-between text-xs">
                <span className="text-gray-400 font-mono w-16">ACC (g)</span>
                <div className="flex gap-3 font-mono">
                  <span className="text-cyan-400">X:{telemetria.acc.x.toFixed(2)}</span>
                  <span className="text-cyan-400">Y:{telemetria.acc.y.toFixed(2)}</span>
                  <span className="text-cyan-400">Z:{telemetria.acc.z.toFixed(2)}</span>
                </div>
              </div>

              <div className="flex items-center justify-between text-xs">
                <span className="text-gray-400 font-mono w-16">GYRO (°/s)</span>
                <div className="flex gap-3 font-mono">
                  <span className="text-cyan-400">X:{telemetria.gyro.x.toFixed(2)}</span>
                  <span className="text-cyan-400">Y:{telemetria.gyro.y.toFixed(2)}</span>
                  <span className="text-cyan-400">Z:{telemetria.gyro.z.toFixed(2)}</span>
                </div>
              </div>

              <div className="flex items-center justify-between text-xs">
                <span className="text-gray-400 font-mono w-16">MAG (μT)</span>
                <div className="flex gap-3 font-mono">
                  <span className="text-cyan-400">X:{telemetria.mag.x.toFixed(1)}</span>
                  <span className="text-cyan-400">Y:{telemetria.mag.y.toFixed(1)}</span>
                  <span className="text-cyan-400">Z:{telemetria.mag.z.toFixed(1)}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="col-span-8">
          <div className="bg-[#14171e] border border-gray-800 rounded-lg p-5 h-[500px] relative">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-gray-300 font-bold text-xs tracking-wider">
                VISUALIZACIÓN ALTITUDINAL (CUBESAT 1U)
              </h3>
              <div className="flex items-center gap-3 text-xs">
                <div className="flex items-center gap-1">
                  <div className="w-2 h-2 bg-red-500 rounded-sm"></div>
                  <span className="text-red-500 font-bold">X</span>
                </div>
                <div className="flex items-center gap-1">
                  <div className="w-2 h-2 bg-green-500 rounded-sm"></div>
                  <span className="text-green-500 font-bold">Y</span>
                </div>
                <div className="flex items-center gap-1">
                  <div className="w-2 h-2 bg-blue-500 rounded-sm"></div>
                  <span className="text-blue-500 font-bold">Z</span>
                </div>
              </div>
            </div>

            <div className="w-full h-[calc(100%-3rem)] bg-[#0a0c10] rounded border border-gray-800 relative overflow-hidden flex items-center justify-center">

              <div className="absolute inset-0 opacity-10" style={{
                backgroundImage: 'linear-gradient(rgba(6, 182, 212, 0.3) 1px, transparent 1px), linear-gradient(90deg, rgba(6, 182, 212, 0.3) 1px, transparent 1px)',
                backgroundSize: '40px 40px'
              }}></div>

              <div className="relative" style={{ transform: 'perspective(1000px) rotateX(20deg) rotateY(-30deg)' }}>
                <div className="w-48 h-48 border-2 border-cyan-400 relative" style={{
                  transformStyle: 'preserve-3d',
                  boxShadow: '0 0 30px rgba(6, 182, 212, 0.3)'
                }}>
                  <div className="absolute inset-0 border border-cyan-400/30 bg-cyan-400/5"></div>
                  <div className="absolute inset-0 border border-cyan-400/30 bg-cyan-400/5" style={{ transform: 'translateZ(192px)' }}></div>
                  <div className="absolute inset-0 border border-cyan-400/30 bg-cyan-400/5" style={{ transform: 'rotateY(90deg) translateZ(96px)' }}></div>
                  <div className="absolute inset-0 border border-cyan-400/30 bg-cyan-400/5" style={{ transform: 'rotateY(-90deg) translateZ(96px)' }}></div>
                  <div className="absolute inset-0 border border-cyan-400/30 bg-cyan-400/5" style={{ transform: 'rotateX(90deg) translateZ(96px)' }}></div>
                  <div className="absolute inset-0 border border-cyan-400/30 bg-cyan-400/5" style={{ transform: 'rotateX(-90deg) translateZ(96px)' }}></div>

                  <div className="absolute top-1/2 left-1/2 w-32 h-1 bg-red-500 origin-left" style={{ transform: 'translate(-50%, -50%)' }}>
                    <div className="absolute right-0 top-1/2 -translate-y-1/2 text-red-500 font-bold text-lg">X</div>
                  </div>
                  <div className="absolute top-1/2 left-1/2 w-32 h-1 bg-green-500 origin-left" style={{ transform: 'translate(-50%, -50%) rotate(90deg)' }}>
                    <div className="absolute right-0 top-1/2 -translate-y-1/2 text-green-500 font-bold text-lg">Y</div>
                  </div>
                  <div className="absolute top-1/2 left-1/2 w-32 h-1 bg-blue-500 origin-left" style={{ transform: 'translate(-50%, -50%) rotate(-90deg)' }}>
                    <div className="absolute right-0 top-1/2 -translate-y-1/2 text-blue-500 font-bold text-lg">Z</div>
                  </div>
                </div>
              </div>

              <div className="absolute top-4 right-4 w-16 h-16">
                <svg viewBox="0 0 100 100" className="w-full h-full">
                  <line x1="50" y1="50" x2="80" y2="50" stroke="#EF4444" strokeWidth="3" />
                  <line x1="50" y1="50" x2="50" y2="20" stroke="#10B981" strokeWidth="3" />
                  <line x1="50" y1="50" x2="30" y2="70" stroke="#3B82F6" strokeWidth="3" />
                  <text x="85" y="55" fill="#EF4444" fontSize="12" fontWeight="bold">X</text>
                  <text x="50" y="15" fill="#10B981" fontSize="12" fontWeight="bold">Y</text>
                  <text x="20" y="75" fill="#3B82F6" fontSize="12" fontWeight="bold">Z</text>
                </svg>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-[#14171e] border border-gray-800 rounded-lg overflow-hidden">

        <button
          onClick={() => setConsolaExpandida(!consolaExpandida)}
          className="w-full px-5 py-3 flex items-center justify-between hover:bg-[#1a1e26] transition-colors"
        >
          <div className="flex items-center gap-2">
            <Activity size={14} className="text-gray-400" />
            <span className="text-gray-400 text-xs font-bold tracking-wider">
              TRASMISIÓN DE TELEMETRÍA
            </span>
          </div>
          {consolaExpandida ? (
            <ChevronUp size={16} className="text-gray-400" />
          ) : (
            <ChevronDown size={16} className="text-gray-400" />
          )}
        </button>

        {consolaExpandida && (
          <div className="border-t border-gray-800 p-5 bg-[#0a0c10] font-mono text-xs max-h-64 overflow-y-auto">
            {logsTelemetria.length === 0 ? (
              <div className="text-gray-500">Esperando datos de telemetría...</div>
            ) : (
              logsTelemetria.map((log, index) => (
                <div key={index} className="text-gray-400 mb-2 leading-relaxed">
                  <span className="text-gray-600">&gt; </span>
                  <span className="text-cyan-400">
                    {JSON.stringify(log)}
                  </span>
                </div>
              ))
            )}
          </div>
        )}
      </div>

    </div>
  )
}

export default Telemetria
