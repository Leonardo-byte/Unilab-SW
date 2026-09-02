import { useState, useEffect } from 'react'
import { Settings, Save, RefreshCw, ToggleLeft, ToggleRight, Monitor, Smartphone, Wifi, Database } from 'lucide-react'
import { api } from '../services/api'

function Configuracion() {
  const [config, setConfig] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const data = await api.getConfig()
        setConfig(data)
      } catch (error) {
        console.error('Error fetching config:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchConfig()
  }, [])

  const handleSave = async () => {
    setSaving(true)
    try {
      await new Promise(r => setTimeout(r, 500))
      console.log('Config guardada:', config)
    } catch (error) {
      console.error('Error saving config:', error)
    } finally {
      setSaving(false)
    }
  }

  const handleToggleSimulation = () => {
    if (config) {
      setConfig({ ...config, simulation_mode: !config.simulation_mode })
    }
  }

  if (loading || !config) {
    return (
      <div className="flex items-center justify-center h-[400px]">
        <RefreshCw size={24} className="text-cyan-400 animate-spin" />
      </div>
    )
  }

  return (
    <div className="space-y-8">

      <section>
        <h2 className="text-2xl font-bold text-cyan-400 mb-6 flex items-center gap-2 tracking-wider">
          <Settings size={24} />
          CONFIGURACIÓN DEL SISTEMA
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">

          <div className="bg-[#14171e] border border-gray-800 rounded-lg p-6 flex items-center gap-4">
            <Monitor size={32} className="text-gray-500" />
            <div>
              <p className="text-gray-500 text-xs font-bold tracking-wider">MODO</p>
              <p className="text-white font-bold text-sm mt-1">
                {config.simulation_mode ? 'SIMULACIÓN' : 'HARDWARE REAL'}
              </p>
            </div>
          </div>

          <div className="bg-[#14171e] border border-gray-800 rounded-lg p-6 flex items-center gap-4">
            <Database size={32} className="text-gray-500" />
            <div>
              <p className="text-gray-500 text-xs font-bold tracking-wider">BASE DE DATOS</p>
              <p className="text-white font-bold text-sm mt-1">SQLite</p>
            </div>
          </div>

          <div className="bg-[#14171e] border border-gray-800 rounded-lg p-6 flex items-center gap-4">
            <Wifi size={32} className="text-gray-500" />
            <div>
              <p className="text-gray-500 text-xs font-bold tracking-wider">CONEXIÓN</p>
              <p className="text-white font-bold text-sm mt-1">
                Backend:8000 → Frontend:5173
              </p>
            </div>
          </div>
        </div>
      </section>

      <section>
        <h3 className="text-lg font-bold text-gray-300 mb-4 flex items-center gap-2 tracking-wider">
          <Smartphone size={20} />
          HARDWARE
        </h3>

        <div className="bg-[#14171e] border border-gray-800 rounded-lg p-6 space-y-4">

          <div className="flex items-center justify-between">
            <div>
              <label className="text-gray-400 text-xs font-bold tracking-wider">
                Modo de Simulación
              </label>
              <p className="text-gray-500 text-xs mt-1">
                Cuando está activado, usa datos simulados en lugar de hardware real
              </p>
            </div>
            <button
              onClick={handleToggleSimulation}
              className={`relative inline-flex h-6 w-12 items-center rounded-full transition-colors ${
                config.simulation_mode ? 'bg-cyan-500' : 'bg-gray-600'
              }`}
            >
              <span className="sr-only">Toggle simulation</span>
              <span className={`inline-block h-5 w-5 transform rounded-full bg-white transition-transform ${
                config.simulation_mode ? 'translate-x-6' : 'translate-x-1'
              }`} />
            </button>
          </div>

          <div className="border-t border-gray-800 pt-4">
            <h4 className="text-xs font-bold text-gray-500 tracking-wider mb-3">CONEXIÓN JAULA</h4>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-gray-400 text-xs block mb-1">Puerto Serial</label>
                <input
                  type="text"
                  value={config.jaula_serial_port || ''}
                  onChange={(e) => setConfig({ ...config, jaula_serial_port: e.target.value })}
                  className="w-full bg-[#0a0c10] border border-gray-700 rounded px-3 py-2 text-cyan-400 font-mono text-sm focus:border-cyan-400 focus:outline-none"
                />
              </div>
              <div>
                <label className="text-gray-400 text-xs block mb-1">Baudios</label>
                <input
                  type="number"
                  value={config.jaula_baudrate || 0}
                  onChange={(e) => setConfig({ ...config, jaula_baudrate: parseInt(e.target.value) || 0 })}
                  className="w-full bg-[#0a0c10] border border-gray-700 rounded px-3 py-2 text-cyan-400 font-mono text-sm focus:border-cyan-400 focus:outline-none"
                />
              </div>
            </div>
          </div>

          <div className="border-t border-gray-800 pt-4">
            <h4 className="text-xs font-bold text-gray-500 tracking-wider mb-3">CONEXIÓN CUBESAT</h4>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-gray-400 text-xs block mb-1">IP Cubéats</label>
                <input
                  type="text"
                  value={config.cubesat_ip || ''}
                  onChange={(e) => setConfig({ ...config, cubesat_ip: e.target.value })}
                  className="w-full bg-[#0a0c10] border border-gray-700 rounded px-3 py-2 text-cyan-400 font-mono text-sm focus:border-cyan-400 focus:outline-none"
                />
              </div>
              <div>
                <label className="text-gray-400 text-xs block mb-1">Puerto UDP</label>
                <input
                  type="number"
                  value={config.cubesat_udp_port || 0}
                  onChange={(e) => setConfig({ ...config, cubesat_udp_port: parseInt(e.target.value) || 0 })}
                  className="w-full bg-[#0a0c10] border border-gray-700 rounded px-3 py-2 text-cyan-400 font-mono text-sm focus:border-cyan-400 focus:outline-none"
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      <section>
        <h3 className="text-lg font-bold text-gray-300 mb-4 flex items-center gap-2 tracking-wider">
          <Settings size={20} />
          PARÁMETROS DE CONTROL
        </h3>

        <div className="bg-[#14171e] border border-gray-800 rounded-lg p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

            <div className="space-y-4">
              <h4 className="text-xs font-bold text-gray-500 tracking-wider">RANGO DE CORRIENTE</h4>
              <div>
                <label className="text-gray-400 text-xs block mb-1">Mínimo (A)</label>
                <input
                  type="number"
                  value={config.min_current || 0}
                  onChange={(e) => setConfig({ ...config, min_current: parseFloat(e.target.value) || 0 })}
                  className="w-full bg-[#0a0c10] border border-gray-700 rounded px-3 py-2 text-cyan-400 font-mono text-sm focus:border-cyan-400 focus:outline-none"
                  step="0.1"
                />
              </div>
              <div>
                <label className="text-gray-400 text-xs block mb-1">Máximo (A)</label>
                <input
                  type="number"
                  value={config.max_current || 0}
                  onChange={(e) => setConfig({ ...config, max_current: parseFloat(e.target.value) || 0 })}
                  className="w-full bg-[#0a0c10] border border-gray-700 rounded px-3 py-2 text-cyan-400 font-mono text-sm focus:border-cyan-400 focus:outline-none"
                  step="0.1"
                />
              </div>
            </div>

            <div className="space-y-4">
              <h4 className="text-xs font-bold text-gray-500 tracking-wider">RANGO DE CAMPO MAGNÉTICO</h4>
              <div>
                <label className="text-gray-400 text-xs block mb-1">Mínimo (μT)</label>
                <input
                  type="number"
                  value={config.min_field || 0}
                  onChange={(e) => setConfig({ ...config, min_field: parseFloat(e.target.value) || 0 })}
                  className="w-full bg-[#0a0c10] border border-gray-700 rounded px-3 py-2 text-cyan-400 font-mono text-sm focus:border-cyan-400 focus:outline-none"
                  step="0.1"
                />
              </div>
              <div>
                <label className="text-gray-400 text-xs block mb-1">Máximo (μT)</label>
                <input
                  type="number"
                  value={config.max_field || 0}
                  onChange={(e) => setConfig({ ...config, max_field: parseFloat(e.target.value) || 0 })}
                  className="w-full bg-[#0a0c10] border border-gray-700 rounded px-3 py-2 text-cyan-400 font-mono text-sm focus:border-cyan-400 focus:outline-none"
                  step="0.1"
                />
              </div>
            </div>

          </div>

          <div className="border-t border-gray-800 pt-4 mt-4">
            <h4 className="text-xs font-bold text-gray-500 tracking-wider mb-3">CONSTANTES DE BOBINA (μT/A)</h4>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="text-gray-400 text-xs block mb-1">K_X</label>
                <input
                  type="number"
                  value={config.kx || 0}
                  onChange={(e) => setConfig({ ...config, kx: parseFloat(e.target.value) || 0 })}
                  className="w-full bg-[#0a0c10] border border-gray-700 rounded px-3 py-2 text-cyan-400 font-mono text-sm focus:border-cyan-400 focus:outline-none"
                  step="0.001"
                  readOnly
                />
              </div>
              <div>
                <label className="text-gray-400 text-xs block mb-1">K_Y</label>
                <input
                  type="number"
                  value={config.ky || 0}
                  onChange={(e) => setConfig({ ...config, ky: parseFloat(e.target.value) || 0 })}
                  className="w-full bg-[#0a0c10] border border-gray-700 rounded px-3 py-2 text-cyan-400 font-mono text-sm focus:border-cyan-400 focus:outline-none"
                  step="0.001"
                  readOnly
                />
              </div>
              <div>
                <label className="text-gray-400 text-xs block mb-1">K_Z</label>
                <input
                  type="number"
                  value={config.kz || 0}
                  onChange={(e) => setConfig({ ...config, kz: parseFloat(e.target.value) || 0 })}
                  className="w-full bg-[#0a0c10] border border-gray-700 rounded px-3 py-2 text-cyan-400 font-mono text-sm focus:border-cyan-400 focus:outline-none"
                  step="0.001"
                  readOnly
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      <div className="flex justify-end">
        <button
          onClick={handleSave}
          disabled={saving}
          className="px-6 py-3 bg-cyan-500 hover:bg-cyan-600 text-black rounded font-bold text-xs tracking-wider flex items-center justify-center gap-2 transition-all disabled:opacity-50"
        >
          {saving ? <RefreshCw size={14} className="animate-spin" /> : <Save size={14} />}
          {saving ? 'GUARDANDO...' : 'GUARDAR CONFIGURACIÓN'}
        </button>
      </div>

    </div>
  )
}

export default Configuracion
