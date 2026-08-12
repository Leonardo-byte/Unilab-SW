import { useState } from 'react'
import StatusCard from '../components/StatusCard'
import ActionCard from '../components/ActionCard'
import {PlusCircle, Target, Radio, Activity, Zap, FileText, CheckCircle2, AlertTriangle} from 'lucide-react'

function Inicio() {
  
  // Estados para las acciones rápidas
  const [ensayoActivo, setEnsayoActivo] = useState(false)
  const [calibracionActiva, setCalibracionActiva] = useState(false)
  const [monitoreoActivo, setMonitoreoActivo] = useState(false)

  // Datos simulados de actividad reciente
  const sesionesRecientes = [
    { 
      id: '#042', 
      perfil: 'Órbita LEO', 
      duracion: '15m', 
      estado: 'Completada', 
      operador: 'Juan P.',
      tipo: 'success'
    },
    { 
      id: '#041', 
      perfil: 'Manual 50uT', 
      duracion: '5m', 
      estado: 'Abortada', 
      operador: 'Miguel I.',
      tipo: 'warning'
    },
  ]

  return (
    <div className="space-y-10">
      <section>
        <h2 className="text-2xl font-bold text-cyan-400 mb-6 flex items-center gap-2 tracking-wider">
          <Activity size={24} />
          ESTADO DEL LABORATORIO
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          
          {/* Tarjeta 1: Jaula */}
          <StatusCard 
            title="JAULA" 
            status="Reposo" 
            statusColor="text-cyan-400 border-cyan-400/30 bg-cyan-400/10" 
            metricLabel="CORRIENTE ACTUAL" 
            metricValue="0.0" 
            metricUnit="A" 
          />

          {/* Tarjeta 2: CubeSat */}
          <StatusCard 
            title="CUBESAT" 
            status="Trasmitiendo" 
            statusColor="text-gray-400 border-gray-600 bg-gray-700/30" 
            metricLabel="VOLTAJE PRINCIPAL" 
            metricValue="--" 
            metricUnit="V" 
          />

          {/* Tarjeta 3: Simulador Solar */}
          <StatusCard 
            title="SIM. SOLAR" 
            status="Apagado" 
            statusColor="text-gray-400 border-gray-600 bg-gray-700/30" 
            metricLabel="POTENCIA DE SALIDA" 
            metricValue="0" 
            metricUnit="W" 
          />

        </div>
      </section>

      {/* ============================================ */}
      {/* SECCIÓN 2: ACCIONES RÁPIDAS                  */}
      {/* ============================================ */}
      <section>
        <h2 className="text-2xl font-bold text-cyan-400 mb-6 flex items-center gap-2 tracking-wider">
          <Zap size={24} />
          ACCIONES RAPIDAS
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          
          {/* Acción 1: Nuevo Ensayo */}
          <ActionCard 
            icon={PlusCircle}
            title="NUEVO ENSAYO"
            onClick={() => {
              setEnsayoActivo(!ensayoActivo)
              console.log('Nuevo Ensayo:', !ensayoActivo ? 'ACTIVO' : 'DETENIDO')
            }}
          />

          {/* Acción 2: Calibración ML */}
          <ActionCard 
            icon={Target}
            title="CALIBRACIÓN ML"
            onClick={() => {
              setCalibracionActiva(!calibracionActiva)
              console.log('Calibración:', !calibracionActiva ? 'EJECUTANDO' : 'DETENIDA')
            }}
          />

          {/* Acción 3: Monitoreo Vivo */}
          <ActionCard 
            icon={Radio}
            title="MONITOREO VIVO"
            onClick={() => {
              setMonitoreoActivo(!monitoreoActivo)
              console.log('Monitoreo:', !monitoreoActivo ? 'EN VIVO' : 'PAUSADO')
            }}
          />

        </div>
      </section>

      {/* ============================================ */}
      {/* SECCIÓN 3: ACTIVIDAD RECIENTE                */}
      {/* ============================================ */}
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

        {/* Tabla de sesiones */}
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
              {sesionesRecientes.map((sesion, index) => (
                <tr key={index} className="hover:bg-[#1a1e26] transition-colors">
                  <td className="p-4 text-gray-300 font-mono text-sm">{sesion.id}</td>
                  <td className="p-4 text-gray-300 text-sm">{sesion.perfil}</td>
                  <td className="p-4 text-gray-300 text-sm">{sesion.duracion}</td>
                  <td className="p-4">
                    <span className={`flex items-center gap-1.5 text-sm font-medium ${
                      sesion.tipo === 'success' ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {sesion.tipo === 'success' ? (
                        <CheckCircle2 size={14} />
                      ) : (
                        <AlertTriangle size={14} />
                      )}
                      {sesion.estado}
                    </span>
                  </td>
                  <td className="p-4 text-gray-300 text-sm">{sesion.operador}</td>
                  <td className="p-4 text-right">
                    <button className="px-4 py-1.5 border border-cyan-400 text-cyan-400 rounded hover:bg-cyan-400 hover:text-black transition-all text-sm font-semibold tracking-wider">
                      Ver
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

    </div>
  )
}

export default Inicio