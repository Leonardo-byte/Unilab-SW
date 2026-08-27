import { useState, useEffect } from 'react'
import { Wifi, Usb, Activity, Search, Save, Power, CheckCircle2, AlertCircle, RefreshCw} from 'lucide-react'
import { api } from '../services/api'

function Dispositivo() {
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const data = await api.getStatus()
        setStatus(data)
      } catch (error) {
        console.error('Error fetching status:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchStatus()
    const interval = setInterval(fetchStatus, 5000)
    return () => clearInterval(interval)
  }, [])
  const [jaulaConfig, setJaulaConfig] = useState({
    puerto: 'COM3',
    baudios: '115200',
    estado: 'Desconectada'
  })
  const [consolaJaula, setConsolaJaula] = useState('> Consola: Esperando conexión...')

  const [cubesatConfig, setCubesatConfig] = useState({
    ip: '192.168.1.100',
    puerto: '5005',
    estado: 'Sin Stream',
    tasaDatos: 0
  })

  const [simuladorConfig, setSimuladorConfig] = useState({
    controlVia: 'Jaula (I2C)',
    estado: 'Standby'
  })

  useEffect(() => {
    if (cubesatConfig.estado === 'Conectado') {
      const intervalo = setInterval(() => {
        setCubesatConfig(prev => ({
          ...prev,
          tasaDatos: Math.floor(45 + Math.random() * 10) 
        }))
      }, 2000)
      return () => clearInterval(intervalo)
    }
  }, [cubesatConfig.estado])

  const conectarJaula = () => {
    setJaulaConfig(prev => ({
      ...prev,
      estado: prev.estado === 'Desconectada' ? 'Conectada' : 'Desconectada'
    }))
    setConsolaJaula(jaulaConfig.estado === 'Desconectada'
      ? `> Conexión establecida en ${jaulaConfig.puerto} @ ${jaulaConfig.baudios} bps\n> Verificando hardware... OK\n> Sistema listo.`
      : '> Desconectando...\n> Conexión cerrada.'
    )
  }

  const iniciarEscuchaUDP = () => {
    setCubesatConfig(prev => ({
      ...prev,
      estado: prev.estado === 'Sin Stream' ? 'Conectado' : 'Sin Stream'
    }))
  }

  const enviarPingHTTP = () => {
    setConsolaJaula(`> Enviando ping HTTP a ${cubesatConfig.ip}...`)
    setTimeout(() => {
      setConsolaJaula(prev => prev + '\n> Ping recibido: 200 OK\n> Latencia: 12ms')
    }, 1000)
  }

  const escanearRedLocal = () => {
    setConsolaJaula('> Escaneando red local...')
    setTimeout(() => {
      setConsolaJaula(prev => prev + '\n> Dispositivos encontrados:\n  - 192.168.1.100 (CubeSat 1U)\n  - 192.168.1.1 (Gateway)')
    }, 1500)
  }

  const guardarConfiguracion = () => {
    setConsolaJaula('> Configuración guardada correctamente.')
    setTimeout(() => {
      setConsolaJaula('> Cambios aplicados al sistema.')
    }, 500)
  }

  return (
    <div className="space-y-6">

      <div className="grid grid-cols-2 gap-6">
        
        <div className="bg-[#14171e] border border-gray-800 rounded-lg p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-gray-300 font-bold text-xs tracking-wider">
                INFRAESTRUCTURA: JAULA DE HELMHOLTZ
              </h3>
              <p className="text-gray-500 text-[10px] mt-1">Serial / FTDI</p>
            </div>
            <div className="flex items-center gap-2">
              <span className={`text-xs font-bold ${
                jaulaConfig.estado === 'Conectada' ? 'text-green-400' : 'text-red-400'
              }`}>
                Estado: {jaulaConfig.estado}
              </span>
              <div className={`w-2 h-2 rounded-full ${
                jaulaConfig.estado === 'Conectada' ? 'bg-green-500 animate-pulse' : 'bg-red-500'
              }`}></div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label className="text-gray-500 text-[10px] block mb-2">Puerto COM</label>
              <select
                value={jaulaConfig.puerto}
                onChange={(e) => setJaulaConfig(prev => ({ ...prev, puerto: e.target.value }))}
                className="w-full bg-[#0a0c10] border border-gray-700 rounded px-3 py-2 text-cyan-400 font-mono text-sm focus:border-cyan-400 focus:outline-none"
              >
                <option>COM1</option>
                <option>COM2</option>
                <option>COM3</option>
                <option>COM4</option>
                <option>/dev/ttyUSB0</option>
                <option>/dev/ttyUSB1</option>
              </select>
            </div>
            <div>
              <label className="text-gray-500 text-[10px] block mb-2">Baudios</label>
              <select
                value={jaulaConfig.baudios}
                onChange={(e) => setJaulaConfig(prev => ({ ...prev, baudios: e.target.value }))}
                className="w-full bg-[#0a0c10] border border-gray-700 rounded px-3 py-2 text-cyan-400 font-mono text-sm focus:border-cyan-400 focus:outline-none"
              >
                <option>9600</option>
                <option>19200</option>
                <option>38400</option>
                <option>57600</option>
                <option>115200</option>
                <option>230400</option>
              </select>
            </div>
          </div>

          <button
            onClick={conectarJaula}
            className={`w-full px-4 py-3 rounded font-bold text-xs tracking-wider flex items-center justify-center gap-2 transition-all mb-4 ${
              jaulaConfig.estado === 'Conectada'
                ? 'bg-red-500 hover:bg-red-600 text-white'
                : 'bg-cyan-500 hover:bg-cyan-600 text-black'
            }`}
          >
            <Power size={14} />
            {jaulaConfig.estado === 'Conectada' ? 'DESCONECTAR JAULA' : 'CONECTAR JAULA'}
          </button>

          <div className="bg-[#0a0c10] border border-gray-800 rounded p-4 font-mono text-xs text-gray-400 h-32 overflow-y-auto">
            <pre className="whitespace-pre-wrap">{consolaJaula}</pre>
          </div>
        </div>

        <div className="bg-[#14171e] border border-gray-800 rounded-lg p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-gray-300 font-bold text-xs tracking-wider">
                DISPOSITIVO: CUBESAT 1U
              </h3>
              <p className="text-gray-500 text-[10px] mt-1">Wi-Fi/UDP</p>
            </div>
            <div className="flex items-center gap-2">
              <span className={`text-xs font-bold ${
                cubesatConfig.estado === 'Conectado' ? 'text-green-400' : 'text-red-400'
              }`}>
                {cubesatConfig.estado}
              </span>
              <div className={`w-2 h-2 rounded-full ${
                cubesatConfig.estado === 'Conectado' ? 'bg-green-500 animate-pulse' : 'bg-red-500'
              }`}></div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label className="text-gray-500 text-[10px] block mb-2">IP Objetivo</label>
              <input
                type="text"
                value={cubesatConfig.ip}
                onChange={(e) => setCubesatConfig(prev => ({ ...prev, ip: e.target.value }))}
                className="w-full bg-[#0a0c10] border border-gray-700 rounded px-3 py-2 text-cyan-400 font-mono text-sm focus:border-cyan-400 focus:outline-none"
                placeholder="192.168.1.100"
              />
            </div>
            <div>
              <label className="text-gray-500 text-[10px] block mb-2">Puerto UDP</label>
              <input
                type="text"
                value={cubesatConfig.puerto}
                onChange={(e) => setCubesatConfig(prev => ({ ...prev, puerto: e.target.value }))}
                className="w-full bg-[#0a0c10] border border-gray-700 rounded px-3 py-2 text-cyan-400 font-mono text-sm focus:border-cyan-400 focus:outline-none"
                placeholder="5005"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3 mb-4">
            <button
              onClick={iniciarEscuchaUDP}
              className={`px-4 py-2 rounded font-bold text-xs tracking-wider flex items-center justify-center gap-2 transition-all ${
                cubesatConfig.estado === 'Conectado'
                  ? 'bg-red-500 hover:bg-red-600 text-white'
                  : 'bg-cyan-500 hover:bg-cyan-600 text-black'
              }`}
            >
              <Wifi size={14} />
              {cubesatConfig.estado === 'Conectado' ? 'DETENER' : 'INICIAR ESCUCHA UDP'}
            </button>
            <button
              onClick={enviarPingHTTP}
              className="px-4 py-2 border border-cyan-400 text-cyan-400 rounded hover:bg-cyan-400 hover:text-black transition-all text-xs font-bold tracking-wider"
            >
              Enviar Ping HTTP
            </button>
          </div>

          <div className="flex items-center justify-between text-xs mb-6">
            <span className="text-gray-500">Tasa de Datos</span>
            <span className="text-cyan-400 font-mono font-bold">
              {cubesatConfig.tasaDatos} Hz
            </span>
          </div>

          <div className="border-t border-gray-800 pt-4">
            <div className="flex items-center justify-between mb-3">
              <h4 className="text-gray-400 text-xs font-bold">SIMULADOR SOLAR</h4>
              <div className="flex items-center gap-2">
                <span className="text-green-400 text-xs font-bold">{simuladorConfig.estado}</span>
                <div className="w-2 h-2 rounded-full bg-green-500"></div>
              </div>
            </div>
            <div>
              <label className="text-gray-500 text-[10px] block mb-2">Control Vía</label>
              <select
                value={simuladorConfig.controlVia}
                onChange={(e) => setSimuladorConfig(prev => ({ ...prev, controlVia: e.target.value }))}
                className="w-full bg-[#0a0c10] border border-gray-700 rounded px-3 py-2 text-cyan-400 font-mono text-sm focus:border-cyan-400 focus:outline-none"
              >
                <option>Jaula (I2C)</option>
                <option>Independiente (USB)</option>
                <option>Manual</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <div className="flex items-center justify-end gap-4 pt-6 border-t border-gray-800">
        <button
          onClick={escanearRedLocal}
          className="px-6 py-3 border border-gray-600 text-gray-400 rounded hover:bg-gray-800 hover:text-white transition-all text-xs font-bold tracking-wider flex items-center gap-2"
        >
          <Search size={14} />
          ESCANEAR RED LOCAL
        </button>
        <button
          onClick={guardarConfiguracion}
          className="px-6 py-3 bg-cyan-500 hover:bg-cyan-600 text-black rounded font-bold text-xs tracking-wider flex items-center gap-2 transition-all"
        >
          <Save size={14} />
          GUARDAR CONFIGURACIÓN
        </button>
      </div>

    </div>
  )
}

export default Dispositivo