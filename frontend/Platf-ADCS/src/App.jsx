import { useState } from 'react'
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import Inicio from './pages/Inicio.jsx'
import Dispositivo from './pages/Dispositivo.jsx'
import EnsayoMagnetico from './pages/EnsayoMagnetico.jsx'
import Telemetria from './pages/Telemetria.jsx'
import Calibracion from './pages/Calibracion.jsx'
import Solar from './pages/Solar.jsx'
import Historial from './pages/Historial.jsx'
import Configuracion from './pages/Configuracion.jsx'
import Login from './pages/Login.jsx'
import Layout from './components/Layout.jsx'
import { DeviceProvider } from './context/DeviceContext.jsx'
import { AuthProvider, useAuth } from './context/AuthContext.jsx'

function RequireAuth({ children }) {
  const { usuario, loading } = useAuth()
  const location = useLocation()

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0a0c10] flex items-center justify-center">
        <div className="text-cyan-400 font-mono">CARGANDO...</div>
      </div>
    )
  }

  if (!usuario) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  return children
}

function App() {

  return (
    <>
      <AuthProvider>
        <DeviceProvider>
        <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={
            <RequireAuth>
              <Layout />
            </RequireAuth>
          }>
            <Route index element={<Inicio />} />
            <Route path="inicio" element={<Inicio />} />
            <Route path="dispositivo" element={<Dispositivo />} />
            <Route path="ensayo-magnetico" element={<EnsayoMagnetico />} />
            <Route path="telemetria" element={<Telemetria />} />
            <Route path="calibracion" element={<Calibracion />} />
            <Route path="solar" element={<Solar />} />
            <Route path="historial" element={<Historial />} />
            <Route path="configuracion" element={<Configuracion />} />
          </Route>
        </Routes>
        </BrowserRouter>
        </DeviceProvider>
        </AuthProvider>
    </>
  )
}

export default App
