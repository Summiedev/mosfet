import { AlertTriangle } from 'lucide-react'

export function AIDetectionWarning() {
  return (
    <div className="bg-[#1A0A10]/60 border border-[#4C1A24]/70 rounded-xl p-5 w-full max-w-4xl mx-auto mb-2 relative overflow-hidden">
        {/* Subtle glow / highlight effect inside */}
        <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-b from-[#4C1A24]/10 to-transparent pointer-events-none"></div>
        
        <div className="relative z-10 flex flex-col">
            <div className="flex items-center gap-2 mb-1.5">
                <AlertTriangle className="w-4 h-4 text-[#E11D48] opacity-80" />
                <span className="text-xs font-medium text-[#E11D48]/80 uppercase tracking-widest">AI Detection</span>
            </div>
            <p className="text-[13px] text-[#A5B4D3]/70 mb-5 ml-0">
                Irregular mass detected — Upper Outer Quadrant
            </p>

            <div className="flex items-center gap-4">
                <div className="flex-1 h-[3px] bg-[#2A1118] rounded-full overflow-hidden">
                    <div className="h-full bg-[#E11D48] w-[87%] rounded-full shadow-[0_0_10px_rgba(225,29,72,0.8)]"></div>
                </div>
                <span className="text-[10px] font-mono text-[#A5B4D3]/50">87%</span>
            </div>
        </div>
    </div>
  )
}
