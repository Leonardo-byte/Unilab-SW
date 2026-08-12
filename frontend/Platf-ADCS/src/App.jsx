import { useState } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Inicio from './pages/Inicio.jsx'
import Dispositivo from './pages/Dispositivo.jsx' 
import EnsayoMagnetico from './pages/EnsayoMagnetico.jsx'
import Telemetria from './pages/Telemetria.jsx'
import Calibracion from './pages/Calibracion.jsx'
import Solar from './pages/Solar.jsx'
import Historial from './pages/Historial.jsx'
import Configuracion from './pages/Configuracion.jsx'
import Layout from './components/Layout.jsx'


function App() {

  return (
    <>
      <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
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
    </>
  )
}

export default App    
