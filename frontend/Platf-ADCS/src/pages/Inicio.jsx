import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import StatusCard from '../components/StatusCard'
import ActionCard from '../components/ActionCard'
import {PlusCircle, Target, Radio, Activity, Zap, FileText, CheckCircle2, AlertTriangle} from 'lucide-react'
import { api } from '../services/api'
import { useDevice } from '../context/DeviceContext.jsx'

function Inicio() {
  const navigate = useNavigate()
  const { jaulaConectada, cubesatConectado } = useDevice()
  const [ensayoActivo, setEnsayoActivo] = useState(false)
  const [monitoreoActivo, setMonitoreoActivo] = useState(false)

  const [jaulaData, setJaulaData] = useState(null)
  const [cubesatData, setCubesatData] = useState(null)
  const [sesionesRecientes, setSesionesRecientes] = useState([])

  const wsRef = useRef(null)

  useEffect(() => {
    const fetchSesiones = async () => {
      try {
        const data = await api.getSessions(5)
        setSesionesRecientes(data)
      } catch (error) {
        console.error('Error fetching sessions:', error)
      }
    }
    fetchSesiones()
  }, [])

  useEffect(() => {
    if (!jaulaConectada && !cubesatConectado) {
      wsRef.current?.close()
      wsRef.current = null
      return
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const ws = new WebSocket(`${protocol}//${window.location.host}/ws/telemetry`)

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.type === 'telemetry') {
        if (data.jaula) setJaulaData(data.jaula)
        if (data.cubesat) setCubesatData(data.cubesat)
      }
    }

    ws.onclose = () => {
      setTimeout(() => {
        if (jaulaConectada || cubesatConectado) {
          wsRef.current = new WebSocket(`${protocol}//${window.location.host}/ws/telemetry`)
        }
      }, 3000)
    }

    wsRef.current = ws

    return () => wsRef.current?.close()
  }, [jaulaConectada, cubesatConectado])

  const handleNuevoEnsayo = async () => {
    if (!jaulaConectada) {
      return
    }
    try {
      if (!ensayoActivo) {
        await api.iniciarEnsayo(45.2, -12.8, 22.1)
      } else {
        await api.detenerEnsayo()
      }
      setEnsayoActivo(!ensayoActivo)
    } catch (error) {
      console.error('Error:', error)
    }
  }

  const handleCalibracion = () => {
    navigate('/calibracion')
  }

  const handleMonitoreoVivo = () => {
    if (!cubesatConectado) {
      return
    }
    setMonitoreoActivo(!monitoreoActivo)
    navigate('/telemetria')
  }

  return (
    <div className="space-y-10">
      <section>
        <h2 className="text-2xl font-bold text-cyan-400 mb-6 flex items-center gap-2 tracking-wider">
          <Activity size={24} />
          ESTADO DEL LABORATORIO
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

          <StatusCard
            title="JAULA"
            status={jaulaConectada ? (jaulaData?.estado || 'Conectada') : 'Desconectada'}
            statusColor={jaulaConectada
              ? "text-cyan-400 border-cyan-400/30 bg-cyan-400/10"
              : "text-red-400 border-red-400/30 bg-red-400/10"}
            metricLabel="CORRIENTE ACTUAL"
            metricValue={jaulaConectada ? `${((jaulaData?.eje_x_corriente || 0) + (jaulaData?.eje_y_corriente || 0) + (jaulaData?.eje_z_corriente || 0)) / 3}` : '0.0'}
            metricUnit="A"
          />

          <StatusCard
            title="CUBESAT"
            status={cubesatConectado ? 'Transmitiendo' : 'Sin Stream'}
            statusColor={cubesatConectado
              ? "text-green-400 border-green-400/30 bg-green-400/10"
              : "text-gray-400 border-gray-600 bg-gray-700/30"}
            metricLabel="VELOCIDAD ANGULAR"
            metricValue={cubesatConectado && cubesatData ? `${Math.sqrt(cubesatData.gyro_x**2 + cubesatData.gyro_y**2 + cubesatData.gyro_z**2).toFixed(3)}` : '--'}
            metricUnit="rad/s"
          />

        </div>
      </section>

      <section>
        <h2 className="text-2xl font-bold text-cyan-400 mb-6 flex items-center gap-2 tracking-wider">
          <Zap size={24} />
          ACCIONES RAPIDAS
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

          <ActionCard
            icon={PlusCircle}
            title={ensayoActivo ? 'DETENER ENSAYO' : 'NUEVO ENSAYO'}
            onClick={handleNuevoEnsayo}
          />

          <ActionCard
            icon={Target}
            title="CALIBRACIÓN"
            onClick={handleCalibracion}
          />

          <ActionCard
            icon={Radio}
            title={monitoreoActivo ? 'DETENER MONITOREO' : 'MONITOREO VIVO'}
            onClick={handleMonitoreoVivo}
          />

        </div>
      </section>

      <section>
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-lg font-bold text-gray-300 flex items-center gap-2 tracking-wider">
            <FileText size={20} />
            ACTIVIDAD RECIENTE
          </h2>
          <button className="text-cyan-400 hover:text-cyan-300 font-semibold text-sm tracking-wider flex items-center gap-1">
            VER TODO →
          </button>
        </div>

        <div className="bg-[#14171e] border border-gray-800 rounded-lg overflow-hidden">
          <table className="w-full text-left">
            <thead className="bg-[#0f1115] text-gray-500 text-xs uppercase tracking-wider border-b border-gray-800">
              <tr>
                <th className="p-4 font-semibold">ID</th>
                <th className="p-4 font-semibold">PERFIL</th>
                <th className="p-4 font-semibold">DURACIÓN</th>
                <th className="p-4 font-semibold">ESTADO</th>
                <th className="p-4 font-semibold">OPERADOR</th>
                <th className="p-4 text-right font-semibold">ACCIÓN</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800">
              {sesionesRecientes.length === 0 ? (
                <tr>
                  <td colSpan="6" className="p-4 text-center text-gray-500 text-sm">
                    No hay sesiones registradas
                  </td>
                </tr>
              ) : (
                sesionesRecientes.map((sesion, index) => (
                  <tr key={index} className="hover:bg-[#1a1e26] transition-colors">
                    <td className="p-4 text-gray-300 font-mono text-sm">#{sesion.id}</td>
                    <td className="p-4 text-gray-300 text-sm">{sesion.nombre || sesion.tipo_prueba}</td>
                    <td className="p-4 text-gray-300 text-sm">{sesion.duracion || '-'}</td>
                    <td className="p-4">
                      <span className={`flex items-center gap-1.5 text-sm font-medium ${
                        sesion.estado === 'completada' || sesion.estado === 'activa'
                          ? 'text-green-400'
                          : 'text-red-400'
                      }`}>
                        {sesion.estado === 'completada' || sesion.estado === 'activa' ? (
                          <CheckCircle2 size={14} />
                        ) : (
                          <AlertTriangle size={14} />
                        )}
                        {sesion.estado || 'Completada'}
                      </span>
                    </td>
                    <td className="p-4 text-gray-300 text-sm">{sesion.operador}</td>
                    <td className="p-4 text-right">
                      <button className="px-4 py-1.5 border border-cyan-400 text-cyan-400 rounded hover:bg-cyan-400 hover:text-black transition-all text-sm font-semibold tracking-wider">
                        Ver
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>

    </div>
  )
}

export default Inicio
