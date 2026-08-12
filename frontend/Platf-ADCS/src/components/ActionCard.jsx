function ActionCard({ icon: Icon, title, onClick }) {
  return (
    <button
      onClick={onClick}
      className="bg-[#14171e] border border-gray-800 rounded-lg p-8 flex flex-col items-center justify-center hover:border-cyan-400 hover:bg-[#1a1e26] transition-all duration-300 group cursor-pointer"
    >
      <div className="text-cyan-400 mb-4 group-hover:scale-110 transition-transform">
        <Icon size={40} strokeWidth={1.5} />
      </div>

      <h3 className="text-white font-bold text-sm tracking-wider">
        {title}
      </h3>
    </button>
  )
}

export default ActionCard