'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Mail, Phone, Lock, Activity } from 'lucide-react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'

export default function LoginPage() {
    const router = useRouter()
    const [email, setEmail] = useState('')
    const [phone, setPhone] = useState('')
    const [password, setPassword] = useState('')

    const handleSignIn = (e: React.FormEvent) => {
        e.preventDefault()
        // Handle sign in logic
        router.push('/verify-otp')
    }

    return (
        <div className="min-h-screen bg-[#020618] flex items-center justify-center p-4">
            <div className="w-full max-w-md">
                <div className="bg-[#0F172B] backdrop-blur border border-slate-700/50 rounded-2xl p-8 space-y-8">
                    {/* Logo */}
                    <div className="flex items-center justify-center gap-2">
                        <div className="rounded-lg flex items-center justify-center">
                            <div />
                              <Activity className="w-12 h-12 text-[#615FFF]" />
                            
                        </div>
                        <span className="text-3xl font-bold text-white">RadFlow</span>
                    </div>

                    {/* Header */}
                    <div className="space-y-2 text-center">
                        <h1 className="text-2xl font-bold text-white">Welcome back, Doctor</h1>
                        <p className="text-sm text-[#90A1B9]">Enter your credentials to continue</p>
                    </div>

                    {/* Form */}
                    <form onSubmit={handleSignIn} className="space-y-4">
                        {/* Email */}
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-[#CAD5E2]">Email Address</label>
                            <div className="relative">
                                <Mail className="absolute left-3 top-4 w-5 h-5 text-slate-500 z-10" />
                                <Input
                                    type="email"
                                    placeholder="doctor@hospital.com"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    className="pl-10 pb-6 pt-7 bg-[#020618] border-[#314158] text-white placeholder-slate-500 focus:border-blue-500 focus:ring-1 focus:ring-blue-500/20"
                                />
                            </div>
                        </div>

                        {/* Phone */}
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-[#CAD5E2]">Phone Number</label>
                            <div className="relative">
                                <Phone className="absolute left-3 top-4 w-5 h-5 text-slate-500 z-10" />
                                <Input
                                    type="tel"
                                    placeholder="+234 XXX XXX XXXX"
                                    value={phone}
                                    onChange={(e) => setPhone(e.target.value)}
                                    className="pl-10 pb-6 pt-7 bg-[#020618] border-[#314158] text-white placeholder-slate-500 focus:border-blue-500 focus:ring-1 focus:ring-blue-500/20"
                                />
                            </div>
                        </div>

                        {/* Password */}
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-[#CAD5E2]">Password</label>
                            <div className="relative">
                                <Lock className="absolute left-3 top-4 w-5 h-5 text-slate-500 z-10" />
                                <Input
                                    type="password"
                                    placeholder="••••••••"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="pl-10 pb-6 pt-7 bg-[#020618] border-[#314158] text-white placeholder-slate-500 focus:border-blue-500 focus:ring-1 focus:ring-blue-500/20"
                                />
                            </div>
                        </div>

                        {/* Sign In Button */}
                        <Button
                            type="submit"
                            className="w-full bg-[#4F39F6] hover:from-blue-700 hover:to-purple-700 text-white font-medium py-2 rounded-lg transition-all"
                        >
                            Sign In →
                        </Button>
                    </form>

                    {/* Footer Links */}
                    <div className="flex items-center justify-center gap-2 text-sm">
                        <span className="text-slate-400">Don&apos;t have an account?</span>
                        <Link href="/" className="text-blue-400 hover:text-blue-300 font-medium">
                            Request access
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    )
}
