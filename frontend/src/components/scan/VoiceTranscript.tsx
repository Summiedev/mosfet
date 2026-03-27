import { Mic, MicOff } from 'lucide-react'
import { useState } from 'react'

export function VoiceTranscript() {
  const [isListening, setIsListening] = useState(true)

  return (
    <div className="bg-[#0F172B] border border-[#1D293D] rounded-lg p-4">
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-2">
          {isListening ? (
             <Mic className="w-5 h-5 text-[#657AF0]" />
          ) : (
            <MicOff className="w-5 h-5 text-[#6B7280]" />
          )}
          <h3 className="font-semibold text-white text-sm">Live Voice Transcript</h3>
        </div>
        <button 
          onClick={() => setIsListening(!isListening)}
          className="text-xs bg-[#1A2235] hover:bg-[#2A3042] px-3 py-1.5 rounded-md text-[#A5B4D3] transition-colors border border-[#2A3042]"
        >
          {isListening ? 'Pause Listening' : 'Resume Listening'}
        </button>
      </div>
      
      {isListening ? (
        <div className="flex flex-col gap-4 text-sm px-1">
          <div className="flex gap-4 items-start">
            <span className="text-[#3E4C69] font-mono text-xs pt-0.5 min-w-[40px]">00:15</span>
            <p className="text-[#9CA3AF]">Scanning right breast...</p>
          </div>
          <div className="flex gap-4 items-start">
            <span className="text-[#3E4C69] font-mono text-xs pt-0.5 min-w-[40px]">00:45</span>
            <p className="text-[#9CA3AF]">There is a hypoechoic mass in the upper outer quadrant, measuring approximately 1.5 cm.</p>
          </div>
          <div className="flex gap-4 items-start">
            <span className="text-[#3E4C69] font-mono text-xs pt-0.5 min-w-[40px]">00:45</span>
            <p className="text-[#D1D5DB]">There is a hypoechoic mass in the upper outer quadrant, measuring approximately 1.5 cm.</p>
          </div>
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center py-6 text-center">
          <MicOff className="w-8 h-8 text-[#3E4C69] mb-3 opacity-50" />
          <p className="text-sm text-[#6B7280]">Voice transcription is currently paused.</p>
        </div>
      )}
    </div>
  )
}
