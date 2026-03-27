'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Checkbox } from '@/components/ui/checkbox'
import { ArrowLeft, Play, Pause, MapPin, Volume2, Zap, AlertCircle } from 'lucide-react'
import Link from 'next/link'

export default function ScanViewPage() {
    const [isLive, setIsLive] = useState(true)
    const [checkedItems, setCheckedItems] = useState([false, false, false])
    const [selectedRegion, setSelectedRegion] = useState('Upper Outer')

    const CHECKLIST_ITEMS = [
        'Relevant anatomical regions',
        'Margins (Circumscribed, etc.)',
        'Review all anatomical planes'
    ]

    const toggleChecklistItem = (index: number) => {
        const newChecked = [...checkedItems]
        newChecked[index] = !newChecked[index]
        setCheckedItems(newChecked)
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 p-8">
            {/* Header */}
            <div className="mb-6 flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <Link href="/dashboard">
                        <Button variant="ghost" size="icon" className="text-slate-400 hover:text-slate-300">
                            <ArrowLeft className="w-5 h-5" />
                        </Button>
                    </Link>
                    <div>
                        <div className="flex items-center gap-2">
                            <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
                            <span className="text-sm text-slate-400">LIVE</span>
                            <span className="text-xs text-slate-400">83:57</span>
                            <Badge variant="outline" className="border-slate-600/50 text-slate-300">1 captures</Badge>
                        </div>
                        <h1 className="text-xl font-bold text-white mt-1">Amaka Johnson</h1>
                        <p className="text-xs text-slate-400">PT-2024-001 · Breast Ultrasound</p>
                    </div>
                </div>
                <div>
                    <p className="text-sm text-slate-400 mb-2">Context: Palpable lump in left breast</p>
                    <Button className="bg-green-600 hover:bg-green-700 text-white gap-2">
                        ✓ Complete Scan
                    </Button>
                </div>
            </div>

            {/* Main Content Grid */}
            <div className="grid grid-cols-3 gap-6">
                {/* Video Player */}
                <div className="col-span-2 space-y-6">
                    {/* Video Area */}
                    <div className="relative bg-slate-900/50 border border-slate-700/50 rounded-lg overflow-hidden aspect-video">
                        <div className="w-full h-full bg-gradient-to-br from-slate-800 to-slate-900 flex items-center justify-center">
                            <div className="text-center">
                                <div className="w-16 h-16 rounded-full bg-slate-700/50 flex items-center justify-center mx-auto mb-4">
                                    <Play className="w-6 h-6 text-slate-400" />
                                </div>
                                <p className="text-slate-400">Ultrasound Stream</p>
                            </div>
                        </div>

                        {/* Overlay Info */}
                        <div className="absolute top-4 right-4 flex gap-2">
                            <Badge className="bg-amber-500/20 text-amber-400 border-amber-500/30">
                                GAIN 📊 65%
                            </Badge>
                            <Badge className="bg-slate-700/50 text-slate-300">DEPTH 📏 4.5cm</Badge>
                        </div>

                        {/* Bottom Controls */}
                        <div className="absolute bottom-4 left-4 right-4 flex gap-3">
                            <Button
                                size="sm"
                                variant="outline"
                                className="border-slate-600/50 text-slate-400 hover:text-slate-300"
                            >
                                🧊 Freeze
                            </Button>
                            <Button
                                size="sm"
                                variant="outline"
                                className="border-slate-600/50 text-slate-400 hover:text-slate-300"
                            >
                                📷 Capture
                            </Button>
                            <Button
                                size="sm"
                                variant="outline"
                                className="border-slate-600/50 text-slate-400 hover:text-slate-300"
                            >
                                🎬 Cine Loop
                            </Button>
                            <Button
                                size="sm"
                                className="bg-blue-600 hover:bg-blue-700 text-white ml-auto"
                            >
                                📏 Measure
                            </Button>
                        </div>
                    </div>

                    {/* Alerts and Insights */}
                    <div className="grid grid-cols-2 gap-4">
                        <div className="bg-amber-500/20 border border-amber-500/30 rounded-lg p-4">
                            <div className="flex items-start gap-3">
                                <AlertCircle className="w-4 h-4 text-amber-400 flex-shrink-0 mt-1" />
                                <div>
                                    <p className="font-semibold text-amber-400 text-sm">Possible hypoechoic area detected</p>
                                </div>
                            </div>
                        </div>
                        <div className="bg-slate-700/20 border border-slate-600/50 rounded-lg p-4">
                            <div className="flex items-start gap-3">
                                <Zap className="w-4 h-4 text-slate-400 flex-shrink-0 mt-1" />
                                <div>
                                    <p className="font-semibold text-slate-300 text-sm">Consider capturing this frame</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Voice Transcript */}
                    <div className="space-y-3">
                        <div className="flex items-center gap-2">
                            <Volume2 className="w-4 h-4 text-slate-400" />
                            <h3 className="font-semibold text-white">Live Voice Transcript</h3>
                            <button className="ml-auto text-sm text-blue-400 hover:text-blue-300">Resume Listening</button>
                        </div>
                        <div className="bg-slate-900/30 border border-slate-700/50 rounded-lg p-4 text-center">
                            <p className="text-slate-400 text-sm">Voice transcription is currently paused.</p>
                        </div>
                    </div>
                </div>

                {/* Right Sidebar */}
                <div className="space-y-6">
                    {/* Anatomical Map */}
                    <div className="bg-slate-800/40 border border-slate-700/50 rounded-lg p-4 space-y-3">
                        <h3 className="font-semibold text-white flex items-center gap-2">
                            <MapPin className="w-4 h-4" />
                            Anatomical Capture Map
                        </h3>
                        <Badge className="bg-blue-600 text-white">Right Breast</Badge>
                        <div className="bg-slate-900/50 rounded-lg p-4 text-center">
                            <p className="text-xs text-slate-400">Anatomical diagram placeholder</p>
                        </div>
                        <p className="text-xs text-slate-400">Selected: {selectedRegion}</p>
                    </div>

                    {/* Protocol Checklist */}
                    <div className="bg-slate-800/40 border border-slate-700/50 rounded-lg p-4 space-y-3">
                        <h3 className="font-semibold text-white flex items-center gap-2">
                            ✓ Protocol Checklist
                            <span className="text-xs text-slate-400 ml-auto">{checkedItems.filter(Boolean).length} / {CHECKLIST_ITEMS.length}</span>
                        </h3>
                        <div className="space-y-2">
                            {CHECKLIST_ITEMS.map((item, index) => (
                                <div key={index} className="flex items-center gap-3">
                                    <Checkbox
                                        checked={checkedItems[index]}
                                        onCheckedChange={() => toggleChecklistItem(index)}
                                    />
                                    <label className="text-sm text-slate-300 cursor-pointer flex-1">
                                        {item}
                                    </label>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Captured Evidence */}
                    <div className="bg-slate-800/40 border border-slate-700/50 rounded-lg p-4 space-y-3">
                        <h3 className="font-semibold text-white">Captured Evidence (0)</h3>
                        <div className="bg-slate-900/50 rounded-lg p-6 text-center">
                            <p className="text-xs text-slate-400">No images captured.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
