'use client'

import { ScanHeader } from '@/components/scan/ScanHeader'
import { LiveVideoFeed } from '@/components/scan/LiveVideoFeed'
import { VoiceTranscript } from '@/components/scan/VoiceTranscript'
import { AnatomicalMap } from '@/components/scan/AnatomicalMap'
import { ProtocolChecklist } from '@/components/scan/ProtocolChecklist'
import { CapturedEvidence } from '@/components/scan/CapturedEvidence'

export default function ScanViewPage() {
    return (
        <div className="min-h-screen bg-[#020618] lg:p-6 p-4">
            <ScanHeader />

            <div className="grid lg:grid-cols-3 grid-cols-1 gap-6">
                {/* Main Video & Transcript Area (Left) */}
                <div className="lg:col-span-2 flex flex-col gap-6">
                    <LiveVideoFeed />
                    <VoiceTranscript />
                </div>

                {/* Patient Context & Tools Area (Right) */}
                <div className="lg:col-span-1 flex flex-col gap-6">
                    <AnatomicalMap />
                    <ProtocolChecklist />
                    <CapturedEvidence />
                </div>
            </div>
        </div>
    )
}
