import { useRef, useState, useEffect, useMemo } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, ContactShadows, Edges, Html, Line, Stars, Sparkles } from '@react-three/drei'
import { Square, Hand, RotateCcw, Move3D, Eye, EyeOff } from 'lucide-react'
import * as THREE from 'three'

const SIZE = 1
const PANEL_SIZE = 0.6

function deg2rad(d) { return (d * Math.PI) / 180 }

function CubeBody({ autoOrient, manualEuler, telemetria, showAxes }) {
  const groupRef = useRef()
  const targetRef = useRef({ roll: 0, pitch: 0, yaw: 0 })
  const currentRef = useRef({ roll: 0, pitch: 0, yaw: 0 })

  useEffect(() => {
    if (autoOrient) {
      targetRef.current = {
        roll: deg2rad(telemetria.roll || 0),
        pitch: deg2rad(telemetria.pitch || 0),
        yaw: deg2rad(telemetria.yaw || 0),
      }
    } else {
      targetRef.current = {
        roll: deg2rad(manualEuler.roll),
        pitch: deg2rad(manualEuler.pitch),
        yaw: deg2rad(manualEuler.yaw),
      }
    }
  }, [autoOrient, manualEuler.roll, manualEuler.pitch, manualEuler.yaw, telemetria.roll, telemetria.pitch, telemetria.yaw])

  useFrame((_, dt) => {
    const c = currentRef.current
    const t = targetRef.current

    const step = 1 - Math.exp(-6 * dt)
    const maxRadPerSec = 3.0

    function approach(current, target) {
      let d = target - current
      if (d > Math.PI) d -= Math.PI * 2
      else if (d < -Math.PI) d += Math.PI * 2
      const maxStep = maxRadPerSec * dt
      if (d > maxStep) d = maxStep
      else if (d < -maxStep) d = -maxStep
      return current + d
    }

    c.roll = approach(c.roll, t.roll)
    c.pitch += (t.pitch - c.pitch) * step
    c.yaw = approach(c.yaw, t.yaw)

    if (groupRef.current) {
      groupRef.current.rotation.set(c.pitch, c.yaw, c.roll, 'YZX')
    }
  })

  return (
    <group ref={groupRef}>
      <mesh castShadow receiveShadow>
        <boxGeometry args={[SIZE, SIZE, SIZE]} />
        <meshStandardMaterial
          color="#1f2937"
          metalness={0.85}
          roughness={0.35}
        />
        <Edges color="#06b6d4" threshold={1} />
      </mesh>

      <mesh position={[0, SIZE / 2 + 0.001, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[SIZE * 0.9, SIZE * 0.9]} />
        <meshStandardMaterial color="#0e7490" metalness={0.4} roughness={0.6} emissive="#06b6d4" emissiveIntensity={0.15} />
      </mesh>

      <Html position={[0, SIZE / 2 + 0.01, 0]} center distanceFactor={1.5} occlude>
        <div className="px-1.5 py-0.5 text-[9px] font-mono font-bold text-cyan-300 bg-black/70 border border-cyan-400/40 rounded">+Y</div>
      </Html>
      <Html position={[0, -SIZE / 2 - 0.01, 0]} center distanceFactor={1.5} rotation={[Math.PI, 0, 0]}>
        <div className="px-1.5 py-0.5 text-[9px] font-mono font-bold text-green-300 bg-black/70 border border-green-400/40 rounded">-Y</div>
      </Html>
      <Html position={[SIZE / 2 + 0.01, 0, 0]} center distanceFactor={1.5} rotation={[0, Math.PI / 2, 0]}>
        <div className="px-1.5 py-0.5 text-[9px] font-mono font-bold text-red-300 bg-black/70 border border-red-400/40 rounded">+X</div>
      </Html>
      <Html position={[-SIZE / 2 - 0.01, 0, 0]} center distanceFactor={1.5} rotation={[0, -Math.PI / 2, 0]}>
        <div className="px-1.5 py-0.5 text-[9px] font-mono font-bold text-red-300 bg-black/70 border border-red-400/40 rounded">-X</div>
      </Html>
      <Html position={[0, 0, SIZE / 2 + 0.01]} center distanceFactor={1.5}>
        <div className="px-1.5 py-0.5 text-[9px] font-mono font-bold text-cyan-300 bg-black/70 border border-cyan-400/40 rounded">+Z</div>
      </Html>
      <Html position={[0, 0, -SIZE / 2 - 0.01]} center distanceFactor={1.5} rotation={[0, Math.PI, 0]}>
        <div className="px-1.5 py-0.5 text-[9px] font-mono font-bold text-cyan-300 bg-black/70 border border-cyan-400/40 rounded">-Z</div>
      </Html>

      <SolarPanel position={[SIZE / 2 + PANEL_SIZE / 2 + 0.02, 0, 0]} />
      <SolarPanel position={[-SIZE / 2 - PANEL_SIZE / 2 - 0.02, 0, 0]} rotation={[0, Math.PI, 0]} />

      <mesh position={[0, 0, SIZE / 2 + 0.005]}>
        <cylinderGeometry args={[0.06, 0.06, 0.04, 16]} />
        <meshStandardMaterial color="#fbbf24" emissive="#facc15" emissiveIntensity={0.8} />
      </mesh>
      <mesh position={[0, 0, -SIZE / 2 - 0.005]}>
        <cylinderGeometry args={[0.04, 0.04, 0.03, 16]} />
        <meshStandardMaterial color="#9ca3af" />
      </mesh>

      {showAxes && <GimbalAxes />}
    </group>
  )
}

function SolarPanel({ position, rotation = [0, 0, 0] }) {
  return (
    <group position={position} rotation={rotation}>
      <mesh castShadow>
        <boxGeometry args={[PANEL_SIZE, PANEL_SIZE * 0.95, 0.02]} />
        <meshStandardMaterial color="#1e3a8a" metalness={0.6} roughness={0.3} />
        <Edges color="#3b82f6" threshold={1} />
      </mesh>
      {Array.from({ length: 4 }).map((_, i) =>
        Array.from({ length: 4 }).map((_, j) => (
          <mesh
            key={`${i}-${j}`}
            position={[
              -PANEL_SIZE / 2 + (i + 0.5) * (PANEL_SIZE / 4),
              -PANEL_SIZE / 2 + (j + 0.5) * (PANEL_SIZE / 4),
              0.012,
            ]}
          >
            <planeGeometry args={[PANEL_SIZE / 4.4, PANEL_SIZE / 4.4]} />
            <meshStandardMaterial color="#1e40af" metalness={0.5} roughness={0.25} />
          </mesh>
        ))
      )}
    </group>
  )
}

function GimbalAxes() {
  const xPts = useMemo(() => [new THREE.Vector3(0, 0, 0), new THREE.Vector3(1.4, 0, 0)], [])
  const yPts = useMemo(() => [new THREE.Vector3(0, 0, 0), new THREE.Vector3(0, 1.4, 0)], [])
  const zPts = useMemo(() => [new THREE.Vector3(0, 0, 0), new THREE.Vector3(0, 0, 1.4)], [])

  return (
    <group>
      <Line points={xPts} color="#ef4444" lineWidth={2} />
      <Line points={yPts} color="#22c55e" lineWidth={2} />
      <Line points={zPts} color="#3b82f6" lineWidth={2} />
      <mesh>
        <sphereGeometry args={[0.04, 12, 12]} />
        <meshStandardMaterial color="#fde047" emissive="#facc15" emissiveIntensity={1} />
      </mesh>
    </group>
  )
}

function Earth() {
  return (
    <group position={[6, -3, -8]}>
      <mesh>
        <sphereGeometry args={[2.5, 48, 48]} />
        <meshStandardMaterial
          color="#1e40af"
          emissive="#0c1e3d"
          emissiveIntensity={0.4}
          roughness={0.85}
          metalness={0.1}
        />
      </mesh>
      <mesh>
        <sphereGeometry args={[2.52, 48, 48]} />
        <meshStandardMaterial
          color="#10b981"
          transparent
          opacity={0.35}
          roughness={1}
        />
      </mesh>
      <mesh position={[0, 0, 0]}>
        <sphereGeometry args={[2.55, 48, 48]} />
        <meshBasicMaterial color="#60a5fa" transparent opacity={0.18} side={THREE.BackSide} />
      </mesh>
      <Html position={[0, 2.8, 0]} center distanceFactor={6}>
        <div className="text-[10px] font-mono font-bold text-cyan-300 bg-black/60 border border-cyan-400/30 rounded px-1.5 py-0.5 whitespace-nowrap">
          🌍 EARTH
        </div>
      </Html>
    </group>
  )
}

function OrbitRing() {
  const points = useMemo(() => {
    const pts = []
    const segments = 128
    const radius = 3.2
    for (let i = 0; i <= segments; i++) {
      const a = (i / segments) * Math.PI * 2
      pts.push(new THREE.Vector3(Math.cos(a) * radius, 0, Math.sin(a) * radius))
    }
    return pts
  }, [])

  return (
    <group rotation={[Math.PI * 0.08, 0, Math.PI * 0.05]}>
      <Line points={points} color="#06b6d4" lineWidth={1} transparent opacity={0.35} />
      <Html position={[3.2, 0, 0]} center distanceFactor={4}>
        <div className="text-[8px] font-mono text-cyan-400/70 whitespace-nowrap">LEO ORBIT</div>
      </Html>
    </group>
  )
}

function SunLight() {
  const ref = useRef()
  useFrame((state) => {
    if (ref.current) {
      ref.current.position.x = Math.cos(state.clock.elapsedTime * 0.05) * 8
      ref.current.position.z = Math.sin(state.clock.elapsedTime * 0.05) * 8
    }
  })
  return (
    <pointLight
      ref={ref}
      position={[6, 4, 4]}
      intensity={0.6}
      color="#fde68a"
      distance={20}
    />
  )
}

function Scene({ autoOrient, manualEuler, telemetria, showAxes, setOrbitEnabled }) {
  return (
    <Canvas
      shadows
      dpr={[1, 2]}
      camera={{ position: [2.4, 1.8, 2.4], fov: 45 }}
      gl={{ antialias: true, alpha: true }}
      onCreated={({ gl, scene }) => {
        gl.setClearColor('#02030a', 1)
        scene.fog = new THREE.FogExp2('#02030a', 0.04)
      }}
    >
      <ambientLight intensity={0.25} color="#1e3a8a" />
      <directionalLight
        position={[3, 4, 2]}
        intensity={1.1}
        castShadow
        shadow-mapSize-width={1024}
        shadow-mapSize-height={1024}
        shadow-camera-left={-3}
        shadow-camera-right={3}
        shadow-camera-top={3}
        shadow-camera-bottom={-3}
      />
      <directionalLight position={[-3, 1, -2]} intensity={0.4} color="#3b82f6" />
      <pointLight position={[0, 2, 2]} intensity={0.4} color="#06b6d4" />
      <SunLight />

      <Stars radius={80} depth={40} count={4500} factor={4} saturation={0.2} fade speed={0.6} />
      <Sparkles count={60} scale={[6, 3, 6]} size={2} speed={0.2} color="#06b6d4" />
      <Sparkles count={30} scale={[10, 2, 10]} size={1.2} speed={0.1} color="#a78bfa" />

      <Earth />
      <OrbitRing />

      <CubeBody
        autoOrient={autoOrient}
        manualEuler={manualEuler}
        telemetria={telemetria}
        showAxes={showAxes}
      />

      <ContactShadows
        position={[0, -1.05, 0]}
        opacity={0.35}
        scale={4}
        blur={2.4}
        far={2}
        color="#000000"
      />

      <gridHelper args={[6, 12, '#0e7490', '#0c4a6e']} position={[0, -1.05, 0]} />

      <OrbitControls
        enabled={true}
        enablePan={false}
        minDistance={1.6}
        maxDistance={8}
        onStart={() => setOrbitEnabled(false)}
        onEnd={() => setOrbitEnabled(true)}
        makeDefault
      />
    </Canvas>
  )
}

function CubeSat3D({ roll = 0, pitch = 0, yaw = 0 }) {
  const [autoOrient, setAutoOrient] = useState(true)
  const [manualEuler, setManualEuler] = useState({ roll: 0, pitch: 0, yaw: 0 })
  const [showAxes, setShowAxes] = useState(true)
  const [orbitEnabled, setOrbitEnabled] = useState(true)
  const [dragging, setDragging] = useState(false)
  const dragRef = useRef({ startX: 0, startY: 0, startRoll: 0, startPitch: 0 })
  const containerRef = useRef(null)
  const prevAutoOrient = useRef(autoOrient)

  const telemetria = { roll, pitch, yaw }

  const onPointerDown = (e) => {
    if (autoOrient || orbitEnabled === false) return
    e.currentTarget.setPointerCapture(e.pointerId)
    setDragging(true)
    dragRef.current = {
      startX: e.clientX,
      startY: e.clientY,
      startRoll: manualEuler.roll,
      startPitch: manualEuler.pitch,
    }
  }

  const onPointerMove = (e) => {
    if (!dragging || autoOrient) return
    const dx = e.clientX - dragRef.current.startX
    const dy = e.clientY - dragRef.current.startY
    setManualEuler((prev) => ({
      roll: dragRef.current.startRoll + dx * 0.5,
      pitch: Math.max(-90, Math.min(90, dragRef.current.startPitch - dy * 0.5)),
      yaw: prev.yaw,
    }))
  }

  const onPointerUp = (e) => {
    if (e.currentTarget.hasPointerCapture?.(e.pointerId)) {
      e.currentTarget.releasePointerCapture(e.pointerId)
    }
    setDragging(false)
  }

  const reset = () => setManualEuler({ roll: 0, pitch: 0, yaw: 0 })

  useEffect(() => {
    if (prevAutoOrient.current === false && autoOrient) {
      setManualEuler({ roll: 0, pitch: 0, yaw: 0 })
    }
    prevAutoOrient.current = autoOrient
  }, [autoOrient])

  return (
    <div className="w-full h-full flex flex-col">
      <div
        ref={containerRef}
        className="flex-1 relative rounded overflow-hidden"
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={onPointerUp}
        onPointerCancel={onPointerUp}
        style={{ touchAction: 'none', cursor: autoOrient ? 'grab' : (dragging ? 'grabbing' : 'grab') }}
      >
        <Scene
          autoOrient={autoOrient}
          manualEuler={manualEuler}
          telemetria={telemetria}
          showAxes={showAxes}
          setOrbitEnabled={setOrbitEnabled}
        />

        <div className="absolute top-2 left-2 text-[9px] font-mono text-cyan-300 bg-black/70 border border-cyan-400/30 rounded px-2 py-1 pointer-events-none">
          <div>R: {(autoOrient ? roll : manualEuler.roll).toFixed(1)}°</div>
          <div>P: {(autoOrient ? pitch : manualEuler.pitch).toFixed(1)}°</div>
          <div>Y: {(autoOrient ? yaw : manualEuler.yaw).toFixed(1)}°</div>
        </div>
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-2 text-[10px] font-mono">
        <button
          onClick={() => setAutoOrient(true)}
          className={`flex items-center gap-1 px-2 py-1 border rounded transition-colors ${
            autoOrient
              ? 'border-cyan-400 text-cyan-400 bg-cyan-400/10'
              : 'border-gray-700 text-gray-500 hover:text-white'
          }`}
        >
          <Square size={10} /> AUTO
        </button>
        <button
          onClick={() => setAutoOrient(false)}
          className={`flex items-center gap-1 px-2 py-1 border rounded transition-colors ${
            !autoOrient
              ? 'border-cyan-400 text-cyan-400 bg-cyan-400/10'
              : 'border-gray-700 text-gray-500 hover:text-white'
          }`}
        >
          <Hand size={10} /> MANUAL
        </button>
        <button
          onClick={reset}
          disabled={autoOrient}
          className="flex items-center gap-1 px-2 py-1 border border-gray-700 rounded text-gray-500 hover:text-white disabled:opacity-30"
        >
          <RotateCcw size={10} /> RESET
        </button>
        <button
          onClick={() => setShowAxes((v) => !v)}
          className={`flex items-center gap-1 px-2 py-1 border rounded transition-colors ${
            showAxes
              ? 'border-cyan-400 text-cyan-400 bg-cyan-400/10'
              : 'border-gray-700 text-gray-500 hover:text-white'
          }`}
        >
          {showAxes ? <Eye size={10} /> : <EyeOff size={10} />} EJES
        </button>
      </div>

      <div className="mt-1.5 text-[9px] text-gray-500 font-mono flex items-center gap-1">
        <Move3D size={10} />
        {autoOrient
          ? 'Orientación sincronizada con telemetría · arrastra para orbitar la cámara'
          : dragging
            ? 'Rotando satélite · suelta para terminar'
            : 'Arrastra para rotar el satélite · scroll para zoom'}
      </div>
    </div>
  )
}

export default CubeSat3D
