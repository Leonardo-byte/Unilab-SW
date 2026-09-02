import { useState, useEffect } from 'react'
import { Calendar, User, CheckCircle2, AlertTriangle, Eye, Trash2, FileText, Activity } from 'lucide-react'
import { api } from '../services/api'

function Historial() {
  const [sesiones, setSesiones] = useState([])
  const [loading, setLoading] = useState(true)
  const [sesionSeleccionada, setSesionSeleccionada] = useState(null)

  useEffect(() => {
    const fetchSesiones = async () => {
      try {
        const data = await api.getSessions(50)
        setSesiones(data)
      } catch (error) {
        console.error('Error:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchSesiones()
  }, [])

  const verDetalle = (sesion) => {
    setSesionSeleccionada(sesion)
  }

  const cerrarDetalle = () => {
    setSesionSeleccionada(null)
  }

  const estadoColor = (estado) => {
    if (estado === 'completada' || estado === 'activa') return 'text-green-400'
    if (estado === 'en curso') return 'text-cyan-400'
    return 'text-red-400'
  }

  const estadoIcon = (estado) => {
    if (estado === 'completada' || estado === 'activa') return <CheckCircle2 size={14} />
    if (estado === 'en curso') return <Activity size={14} />
    return <AlertTriangle size={14} />
  }

  return (
    <div className="space-y-8">

      <section>
        <h2 className="text-2xl font-bold text-cyan-400 mb-6 flex items-center gap-2 tracking-wider">
          <FileText size={24} />
          HISTORIAL Y REPORTES
        </h2>

        <div className="bg-[#14171e] border border-gray-800 rounded-lg overflow-hidden">
          <table className="w-full text-left">
            <thead className="bg-[#0f1115] text-gray-500 text-xs uppercase tracking-wider border-b border-gray-800">
              <tr>
                <th className="p-4 font-semibold">ID</th>
                <th className="p-4 font-semibold">PERFIL</th>
                <th className="p-4 font-semibold">TIPO</th>
                <th className="p-4 font-semibold">ESTUDIANTE</th>
                <th className="p-4 font-semibold">FECHA</th>
                <th className="p-4 font-semibold">ESTADO</th>
                <th className="p-4 text-right font-semibold">ACCIÓN</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800">
              {loading ? (
                <tr>
                  <td colSpan="7" className="p-4 text-center text-gray-500">
                    Cargando...
                  </td>
                </tr>
              ) : sesiones.length === 0 ? (
                <tr>
                  <td colSpan="7" className="p-4 text-center text-gray-500">
                    No hay sesiones registradas
                  </td>
                </tr>
              ) : (
                sesiones.map((sesion) => (
                  <tr key={sesion.id} className="hover:bg-[#1a1e26] transition-colors">
                    <td className="p-4 text-gray-300 font-mono text-sm">#{sesion.id}</td>
                    <td className="p-4 text-gray-300 text-sm">{sesion.nombre || sesion.tipo_prueba}</td>
                    <td className="p-4 text-gray-400 text-xs">{sesion.tipo_prueba || '-'}</td>
                    <td className="p-4 text-gray-300 text-sm">{sesion.alumno || sesion.operador}</td>
                    <td className="p-4 text-gray-500 text-xs">
                      {sesion.created_at ? new Date(sesion.created_at).toLocaleDateString('es-AR') : '-'}
                    </td>
                    <td className="p-4">
                      <span className={`flex items-center gap-1.5 text-sm font-medium ${estadoColor(sesion.estado)}`}>
                        {estadoIcon(sesion.estado)}
                        {sesion.estado || 'Completada'}
                      </span>
                    </td>
                    <td className="p-4 text-right">
                      <button
                        onClick={() => verDetalle(sesion)}
                        className="px-3 py-1 border border-cyan-400 text-cyan-400 rounded hover:bg-cyan-400 hover:text-black transition-all text-xs font-semibold"
                      >
                        <Eye size={12} className="inline mr-1" />
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

      {sesionSeleccionada && (
        <section>
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-xl font-bold text-gray-300 flex items-center gap-2">
              <Eye size={20} />
              Detalle de Sesión #{sesionSeleccionada.id}
            </h3>
            <button
              onClick={cerrarDetalle}
              className="text-gray-500 hover:text-gray-300 text-sm"
            >
              ✕ Cerrar
            </button>
          </div>

          <div className="bg-[#14171e] border border-gray-800 rounded-lg p-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              <div>
                <span className="text-gray-500 text-xs uppercase">Nombre</span>
                <p className="text-white font-mono text-sm mt-1">{sesionSeleccionada.nombre || '-'}</p>
              </div>
              <div>
                <span className="text-gray-500 text-xs uppercase">Tipo</span>
                <p className="text-white font-mono text-sm mt-1">{sesionSeleccionada.tipo_prueba || '-'}</p>
              </div>
              <div>
                <span className="text-gray-500 text-xs uppercase">Estudiante</span>
                <p className="text-white font-mono text-sm mt-1">{sesionSeleccionada.alumno || sesionSeleccionada.operador}</p>
              </div>
              <div>
                <span className="text-gray-500 text-xs uppercase">Estado</span>
                <p className={`font-mono text-sm mt-1 ${estadoColor(sesionSeleccionada.estado)}`}>
                  {sesionSeleccionada.estado || 'Completada'}
                </p>
              </div>
            </div>

            {sesionSeleccionada.descripcion && (
              <div>
                <span className="text-gray-500 text-xs uppercase">Descripción</span>
                <p className="text-gray-300 text-sm mt-1">{sesionSeleccionada.descripcion}</p>
              </div>
            )}
          </div>
        </section>
      )}

    </div>
  )
}

export default Historial
