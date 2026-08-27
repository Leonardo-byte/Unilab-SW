import { useEffect, useRef, useState } from 'react'

export function useTelemetryWebSocket(onMessage) {
  const [conectado, setConectado] = useState(false)
  const wsRef = useRef(null)
  const onMessageRef = useRef(onMessage)

  onMessageRef.current = onMessage

  useEffect(() => {
    const connect = () => {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const ws = new WebSocket(`${protocol}//${window.location.host}/ws/telemetry`)

      ws.onopen = () => {
        setConectado(true)
      }

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data)
        onMessageRef.current?.(data)
      }

      ws.onclose = () => {
        setConectado(false)
        setTimeout(connect, 3000)
      }

      ws.onerror = () => {
        ws.close()
      }

      wsRef.current = ws
    }

    connect()

    return () => {
      wsRef.current?.close()
    }
  }, [])

  return { conectado }
}
