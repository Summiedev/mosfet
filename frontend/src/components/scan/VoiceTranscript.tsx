import { MicOff } from 'lucide-react'

export function VoiceTranscript() {
  return (
    <div className="bg-[#0F172B] border border-[#1D293D] rounded-lg p-4">
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-2">
          <MicOff className="w-4 h-4 text-[#6B7280]" />
          <h3 className="font-semibold text-white text-sm">Live Voice Transcript</h3>
        </div>
        <button className="text-xs bg-[#1A2235] hover:bg-[#2A3042] px-3 py-1.5 rounded-md text-[#A5B4D3] transition-colors border border-[#2A3042]">
          Resume Listening
        </button>
      </div>
      
      <div className="flex flex-col items-center justify-center py-6 text-center">
        <MicOff className="w-8 h-8 text-[#3E4C69] mb-3 opacity-50" />
        <p className="text-sm text-[#6B7280]">Voice transcription is currently paused.</p>
      </div>
    </div>
  )
}
