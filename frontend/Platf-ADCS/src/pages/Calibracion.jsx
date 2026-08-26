import { useState, useEffect } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area} from 'recharts'
import { CheckCircle2, RotateCcw, Play, Pause, AlertCircle, TrendingUp} from 'lucide-react'

function Calibracion() {
  const [faseActual, setFaseActual] = useState(2) 
  const [barridoActivo, setBarridoActivo] = useState(true)
  const [faseEje, setFaseEje] = useState('EJE Y (3/6)')
  const [progresoBarrido, setProgresoBarrido] = useState(65)
  const [puntosRestantes, setPuntosRestantes] = useState(1240)
  const [puntosTotales, setPuntosTotales] = useState(1240)
  const [tempPromedio, setTempPromedio] = useState(42.5)

  const [coeficientes, setCoeficientes] = useState([
    { param: 'Kx', teorico: 27.1458, calibrado: 27.35, delta: 0.75, estado: 'validado' },
    { param: 'Ky', teorico: 31.3217, calibrado: 31.48, delta: 0.50, estado: 'validado' },
    { param: 'Kz', teorico: 29.0849, calibrado: 29.22, delta: 0.46, estado: 'validado' },
  ])

  const [r2Determinacion, setR2Determinacion] = useState(0.984)
  const [epoch, setEpoch] = useState(500)
  const [convergencia, setConvergencia] = useState(true)

  const [trainingLossData, setTrainingLossData] = useState([
    { epoch: 0, loss: 2.5 },
    { epoch: 100, loss: 1.8 },
    { epoch: 200, loss: 1.2 },
    { epoch: 300, loss: 0.8 },
    { epoch: 400, loss: 0.5 },
    { epoch: 500, loss: 0.3 },
  ])

  const [residualData, setResidualData] = useState(
    Array.from({ length: 50 }, (_, i) => ({
      punto: i,
      antes: (Math.random() - 0.5) * 10,
      despues: (Math.random() - 0.5) * 2,
    }))
  )

  useEffect(() => {
    if (!barridoActivo) return

    const intervalo = setInterval(() => {
      setPuntosRestantes(prev => Math.max(0, prev - 10))
      setProgresoBarrido(prev => Math.min(100, prev + 0.5))
      setTempPromedio(prev => 42.5 + (Math.random() - 0.5) * 0.5)
    }, 1000)

    return () => clearInterval(intervalo)
  }, [barridoActivo])

  const iniciarBarrido = () => {
    setBarridoActivo(true)
    setPuntosRestantes(1240)
    setProgresoBarrido(0)
  }

  const pausarBarrido = () => {
    setBarridoActivo(false)
  }

  const reiniciarCalibracion = () => {
    setFaseActual(1)
    setBarridoActivo(false)
    setPuntosRestantes(1240)
    setProgresoBarrido(0)
  }

  return (
    <div className="space-y-6">
      
      <div className="bg-[#14171e] border border-gray-800 rounded-lg p-6">
        <div className="flex items-center justify-between">
          {[
            { num: 1, label: 'VERIF', completado: true },
            { num: 2, label: 'VALIDAR', completado: false },
          ].map((fase, index) => (
            <div key={fase.num} className="flex items-center flex-1">
              <div className="flex items-center">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center border-2 font-bold text-sm ${
                  fase.completado
                    ? 'bg-cyan-500 border-cyan-500 text-black'
                    : fase.activo
                    ? 'border-cyan-400 text-cyan-400 bg-transparent'
                    : 'border-gray-600 text-gray-600'
                }`}>
                  {fase.completado ? <CheckCircle2 size={18} /> : fase.num}
                </div>
                <span className={`ml-3 text-xs font-bold tracking-wider ${
                  fase.activo || fase.completado ? 'text-cyan-400' : 'text-gray-600'
                }`}>
                  {fase.label}
                </span>
              </div>
              {index < 3 && (
                <div className={`flex-1 h-0.5 mx-4 ${
                  fase.completado ? 'bg-cyan-500' : 'bg-gray-700'
                }`} />
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-12 gap-6">
        
  
        <div className="col-span-4 space-y-6">
          <div className="bg-[#14171e] border border-gray-800 rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${barridoActivo ? 'bg-green-500 animate-pulse' : 'bg-yellow-500'}`}></div>
                <h3 className="text-gray-300 font-bold text-xs tracking-wider">
                  {barridoActivo ? 'BARRIDO EN CURSO' : 'BARRIDO PAUSADO'}
                </h3>
              </div>
              <RotateCcw size={16} className="text-gray-500 cursor-pointer hover:text-cyan-400" />
            </div>

            <div className="mb-4">
              <p className="text-gray-400 text-xs mb-2">FASE:</p>
              <p className="text-cyan-400 font-mono text-sm font-bold">{faseEje}</p>

              <div className="mt-2 h-2 bg-gray-800 rounded-full overflow-hidden">
                <div
                  className="h-full bg-cyan-400 transition-all"
                  style={{ width: `${progresoBarrido}%` }}
                />
              </div>
              <p className="text-right text-xs text-cyan-400 mt-1">{progresoBarrido.toFixed(0)}%</p>
            </div>

            <div className="grid grid-cols-2 gap-3 mb-4">
              <div className="bg-[#0a0c10] border border-gray-800 rounded p-3">
                <p className="text-gray-500 text-[10px] mb-1">RESTANTE</p>
                <p className="text-white font-mono text-lg font-bold">{puntosRestantes.toLocaleString()}</p>
              </div>
              <div className="bg-[#0a0c10] border border-gray-800 rounded p-3">
                <p className="text-gray-500 text-[10px] mb-1">PUNTOS</p>
                <p className="text-white font-mono text-lg font-bold">{puntosTotales.toLocaleString()}</p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3 mt-6">
              <button
                onClick={barridoActivo ? pausarBarrido : iniciarBarrido}
                className={`px-4 py-2 rounded font-bold text-xs tracking-wider flex items-center justify-center gap-2 transition-all ${
                  barridoActivo
                    ? 'bg-yellow-500 hover:bg-yellow-600 text-black'
                    : 'bg-green-500 hover:bg-green-600 text-black'
                }`}
              >
                {barridoActivo ? <Pause size={14} /> : <Play size={14} />}
                {barridoActivo ? 'PAUSAR' : 'CONTINUAR'}
              </button>
              <button
                onClick={reiniciarCalibracion}
                className="px-4 py-2 border border-gray-600 text-gray-400 rounded hover:bg-gray-700 hover:text-white transition-all text-xs font-bold tracking-wider flex items-center justify-center gap-2"
              >
                <RotateCcw size={14} />
                REINICIAR
              </button>
            </div>
          </div>
        </div>

        <div className="col-span-8 space-y-6">
          
          <div className="bg-[#14171e] border border-gray-800 rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-gray-300 font-bold text-xs tracking-wider">
                COEFICIENTES: TEÓRICO VS CALIBRADO
              </h3>
              <span className="text-gray-500 text-[10px] font-mono">MODEL: ML_REG_V4.2</span>
            </div>

            <table className="w-full">
              <thead className="border-b border-gray-800">
                <tr>
                  <th className="text-left text-gray-500 text-[10px] font-bold py-2">PARAM</th>
                  <th className="text-left text-gray-500 text-[10px] font-bold py-2">TEÓRICO</th>
                  <th className="text-left text-gray-500 text-[10px] font-bold py-2">CALIBRADO</th>
                  <th className="text-left text-gray-500 text-[10px] font-bold py-2">Δ%</th>
                  <th className="text-left text-gray-500 text-[10px] font-bold py-2">ESTADO</th>
                </tr>
              </thead>
              <tbody>
                {coeficientes.map((coef) => (
                  <tr key={coef.param} className="border-b border-gray-800 last:border-0">
                    <td className="py-3">
                      <span className="text-cyan-400 font-mono font-bold">{coef.param}</span>
                    </td>
                    <td className="py-3">
                      <span className="text-gray-400 font-mono text-sm">{coef.teorico.toFixed(4)}</span>
                    </td>
                    <td className="py-3">
                      <span className="text-cyan-400 font-mono font-bold">{coef.calibrado.toFixed(2)}</span>
                    </td>
                    <td className="py-3">
                      <span className="text-green-400 font-mono text-sm">+{coef.delta.toFixed(2)}%</span>
                    </td>
                    <td className="py-3">
                      <div className="flex items-center gap-2">
                        <CheckCircle2 size={14} className="text-green-500" />
                        <span className="text-green-400 text-xs font-bold">✓</span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

        </div>
      </div>

      <div className="flex items-center justify-end gap-4">
        <button className="px-6 py-3 border border-cyan-400 text-cyan-400 rounded hover:bg-cyan-400 hover:text-black transition-all text-xs font-bold tracking-wider flex items-center gap-2">
          <TrendingUp size={14} />
          EXPORTAR REPORTE DE CALIBRACIÓN
        </button>
        <button className="px-6 py-3 bg-green-500 hover:bg-green-600 text-black rounded font-bold text-xs tracking-wider flex items-center gap-2 transition-all">
          <CheckCircle2 size={14} />
          APLICAR MODELO DE COMPENSACIÓN
        </button>
      </div>

    </div>
  )
}

export default Calibracion
