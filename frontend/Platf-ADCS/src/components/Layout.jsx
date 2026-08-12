import { Outlet, useLocation, Link } from 'react-router-dom'
import {
  LayoutDashboard,
  SlidersHorizontal,
  Rocket,
  Wifi,
  Settings,
  History,
  Sun,
  User,
  Activity
} from 'lucide-react'

function Layout() {
  const location = useLocation()

  const menuItems = [
    { path: '/inicio', label: 'INICIO', icon: LayoutDashboard },
    { path: '/dispositivo', label: 'DISPOSITIVO', icon: SlidersHorizontal },
    { path: '/ensayo-magnetico', label: 'ENSAYO MAGNETICO', icon: Rocket },
    { path: '/telemetria', label: 'TELEMETRIA', icon: Wifi },
    { path: '/calibracion', label: 'CALIBRACIÓN', icon: SlidersHorizontal },
    { path: '/solar', label: 'SOLAR', icon: Sun },
    { path: '/historial', label: 'HISTORIAL Y REPORTES', icon: History },
    { path: '/configuracion', label: 'CONFIGURACIÓN', icon: Settings },
  ]

  return (
    <div className="flex h-screen bg-[#0a0c10] text-white font-mono">
      
      <aside className="w-64 bg-[#14171e] border-r border-gray-800 flex flex-col">
        <div className="p-6 border-b border-gray-800">
          <h1 className="text-3xl font-bold text-white tracking-wider">
            UNILAB
          </h1>
        </div>

        <nav className="flex-1 p-4 space-y-1">
          {menuItems.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.path
            
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-4 py-3 rounded-md transition-all text-sm tracking-wide ${
                  isActive
                    ? 'bg-[#1e2229] text-cyan-400 border-l-2 border-cyan-400'
                    : 'text-gray-400 hover:bg-[#1e2229] hover:text-white'
                }`}
              >
                <Icon size={18} />
                <span className="font-semibold">{item.label}</span>
              </Link>
            )
          })}
        </nav>
      </aside>

      <div className="flex-1 flex flex-col overflow-hidden">
        
        <header className="bg-[#0a0c10] border-b border-gray-800 px-6 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-6 text-sm">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-green-500"></span>
                <span className="text-gray-300 tracking-wider">JAULA: ACTIVADO</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-green-500"></span>
                <span className="text-gray-300 tracking-wider">CUBESAT: CONECTADO</span>
              </div>
            </div>

            <div className="flex items-center gap-2 text-gray-300 tracking-wider">
              <span className="font-semibold">MIGUEL</span>
              <User size={18} />
            </div>
          </div>
        </header>

        <main className="flex-1 p-8 overflow-auto">
          <Outlet />
        </main>

      </div>
    </div>
  )
}

export default Layout