import { useState, useEffect } from 'react'
import {ChevronUp, ChevronDown, Radio, RotateCcw, Activity} from 'lucide-react'

function Telemetria() {
  const [telemetria, setTelemetria] = useState({
    roll: 14.2,
    pitch: -2.5,
    yaw: 89.1,
    q0: 0.707,
    q1: 0.000,
    q2: 0.707,
    q3: 0.000,
    acc: { x: 0.98, y: 0.12, z: -0.05 },
    gyro: { x: 0.01, y: -0.02, z: 0.00 },
    mag: { x: 24.1, y: -12.5, z: 45.2 },
    sun: { x: 84, negX: 12, y: 91, negY: 5, z: 22, negZ: 18 },
    adcsMode: 'SUN_ACQUISITION',
    mtq: { x: 45, y: 12, z: 0 },
    power: { voltage: 3.7, percentage: 85, watts: 0.56 },
    link: { frequency: 50, latency: 12 }
  })

  const [consolaExpandida, setConsolaExpandida] = useState(true)
  const [logsTelemetria, setLogsTelemetria] = useState([
    { timestamp: 1698765432, roll: 14.2, pitch: -2.5, yaw: 89.1, sun_1: 2847, sun_2: 412, sun_3: 3102, sun_4: 150, sun_5: 890, sun_6: 720 },
    { timestamp: 1698765433, roll: 14.2, pitch: -2.5, yaw: 89.1, sun_1: 2848, sun_2: 411, sun_3: 3105, sun_4: 150, sun_5: 889, sun_6: 721 },
    { timestamp: 1698765434, roll: 14.3, pitch: -2.4, yaw: 89.2, sun_1: 2850, sun_2: 410, sun_3: 3108, sun_4: 149, sun_5: 885, sun_6: 725 },
    { timestamp: 1698765435, roll: 14.3, pitch: -2.4, yaw: 89.2, sun_1: 2850, sun_2: 410, sun_3: 3108, sun_4: 149, sun_5: 885, sun_6: 725 },
  ])

  useEffect(() => {
    const intervalo = setInterval(() => {
      setTelemetria(prev => ({
        ...prev,
        roll: prev.roll + (Math.random() - 0.5) * 0.1,
        pitch: prev.pitch + (Math.random() - 0.5) * 0.1,
        yaw: prev.yaw + (Math.random() - 0.5) * 0.1,
      }))
    }, 1000)

    return () => clearInterval(intervalo)
  }, [])

  const formatNumber = (num, decimals = 1) => {
    return num.toFixed(decimals)
  }

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
                  +{formatNumber(telemetria.roll)}°
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
                  +{formatNumber(telemetria.yaw)}°
                </p>
              </div>
            </div>
          </div>

          <div className="bg-[#14171e] border border-gray-800 rounded-lg p-5">
            <h3 className="text-gray-400 text-xs font-bold tracking-wider mb-4">
              CUATERNIONES
            </h3>
            
            <div className="grid grid-cols-4 gap-2">
              {['q0', 'q1', 'q2', 'q3'].map((q, index) => (
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

      <div className="grid grid-cols-2 gap-6">
        
        <div className="bg-[#14171e] border border-gray-800 rounded-lg p-5">
          <h3 className="text-gray-400 text-xs font-bold tracking-wider mb-4">
            SENSORES SOLARES (LDR)
          </h3>
          
          <div className="grid grid-cols-3 gap-3">
            {[
              { label: '+X', value: telemetria.sun.x },
              { label: '-X', value: telemetria.sun.negX },
              { label: '+Y', value: telemetria.sun.y },
              { label: '-Y', value: telemetria.sun.negY },
              { label: '+Z', value: telemetria.sun.z },
              { label: '-Z', value: telemetria.sun.negZ },
            ].map((sensor) => (
              <div key={sensor.label} className="bg-[#0a0c10] border border-gray-800 rounded p-4 text-center">
                <p className="text-gray-500 text-xs mb-2">{sensor.label}</p>
                <p className={`font-mono text-2xl font-bold ${
                  sensor.value > 50 ? 'text-cyan-400' : 'text-gray-400'
                }`}>
                  {sensor.value.toString().padStart(2, '0')}%
                </p>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-[#14171e] border border-gray-800 rounded-lg p-5">
          <h3 className="text-gray-400 text-xs font-bold tracking-wider mb-4">
            SISTEMA Y CONTROL
          </h3>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-gray-400 text-xs font-bold">ADCS MODE</span>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                <span className="text-green-400 font-mono text-sm font-bold">
                  {telemetria.adcsMode}
                </span>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-gray-400 text-xs font-bold">MTQ STATUS</span>
              <span className="text-cyan-400 font-mono text-sm">
                X({telemetria.mtq.x}%) Y({telemetria.mtq.y}%) Z({telemetria.mtq.z}%)
              </span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-gray-400 text-xs font-bold">POWER</span>
              <span className="text-cyan-400 font-mono text-sm">
                {telemetria.power.voltage}V ({telemetria.power.percentage}%) | {telemetria.power.watts}W
              </span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-gray-400 text-xs font-bold">LINK</span>
              <span className="text-cyan-400 font-mono text-sm">
                UDP {telemetria.link.frequency}Hz | Latency {telemetria.link.latency}ms
              </span>
            </div>

            <div className="grid grid-cols-2 gap-3 pt-4">
              <button className="px-4 py-2 border border-cyan-400 text-cyan-400 rounded hover:bg-cyan-400 hover:text-black transition-all text-xs font-bold tracking-wider flex items-center justify-center gap-2">
                <Radio size={14} />
                GRABAR SESIÓN
              </button>
              <button className="px-4 py-2 border border-gray-600 text-gray-400 rounded hover:bg-gray-700 hover:text-white transition-all text-xs font-bold tracking-wider flex items-center justify-center gap-2">
                <RotateCcw size={14} />
                RECONECTAR
              </button>
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
            {logsTelemetria.map((log, index) => (
              <div key={index} className="text-gray-400 mb-2 leading-relaxed">
                <span className="text-gray-600">&gt; </span>
                <span className="text-cyan-400">
                  {JSON.stringify(log)}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

    </div>
  )
}

export default Telemetria