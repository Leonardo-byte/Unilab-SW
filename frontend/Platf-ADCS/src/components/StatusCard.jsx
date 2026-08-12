function StatusCard({ title, status, statusColor, metricLabel, metricValue, metricUnit }) {
  return (
    <div className="bg-[#14171e] border border-gray-800 rounded-lg p-5 flex flex-col justify-between h-44">
      
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-gray-400 text-xs font-bold tracking-wider flex items-center gap-2">
          <span className="text-cyan-400">⚙</span>
          {title}
        </h3>
        
        <span className={`flex items-center gap-1.5 text-[10px] px-2 py-1 rounded border tracking-wider ${statusColor}`}>
          <span className="w-1.5 h-1.5 rounded-full bg-current"></span>
          {status}
        </span>
      </div>

      <div className="flex-1 flex flex-col justify-end">
        <p className="text-gray-500 text-[10px] uppercase tracking-wider mb-1">
          {metricLabel}
        </p>
        <p className="text-4xl font-bold text-white font-mono">
          {metricValue} <span className="text-sm text-gray-400 font-sans">{metricUnit}</span>
        </p>
        
        <div className="mt-3 h-8 w-full">
          <svg viewBox="0 0 100 30" className="w-full h-full" preserveAspectRatio="none">
            <polyline
              points="0,25 10,22 20,24 30,20 40,22 50,18 60,20 70,15 80,18 90,12 100,15"
              fill="none"
              stroke={metricValue === '0.0' ? '#06b6d4' : '#4b5563'}
              strokeWidth="1.5"
            />
          </svg>
        </div>
      </div>

    </div>
  )
}

export default StatusCard