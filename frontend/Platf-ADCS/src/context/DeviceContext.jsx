import { createContext, useContext, useState } from 'react'

const DeviceContext = createContext(null)

export function DeviceProvider({ children }) {
  const [jaulaConectada, setJaulaConectada] = useState(false)
  const [cubesatConectado, setCubesatConectado] = useState(false)

  return (
    <DeviceContext.Provider value={{
      jaulaConectada,
      setJaulaConectada,
      cubesatConectado,
      setCubesatConectado,
    }}>
      {children}
    </DeviceContext.Provider>
  )
}

export function useDevice() {
  const context = useContext(DeviceContext)
  if (!context) {
    throw new Error('useDevice debe estar dentro de DeviceProvider')
  }
  return context
}
