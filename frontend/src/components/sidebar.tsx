import Link from "next/link"
import { Activity, LayoutDashboard, LogOut } from "lucide-react"

export function Sidebar() {
  return (
    <div className="fixed left-0 top-0 w-64 h-screen bg-[#0e1122] border-r border-[#1E2433] p-6 flex flex-col z-20">
      {/* Logo */}
      <div className="flex items-center gap-3 mb-10">
        <div className="rounded-lg flex items-center justify-center">
          <Activity className="w-8 h-8 text-[#4F39F6]" />
        </div>
        <span className="text-2xl font-bold text-white">RadFlow</span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-2">
        <Link 
          href="/dashboard"
          className="flex items-center gap-3 px-4 py-3 rounded-lg bg-[#615FFF1A] border border-[#0e1122] transition-colors"
        >
          <LayoutDashboard className="w-5 h-5 text-[#7C86FF]" />
          <span className="font-medium text-[#7C86FF]">Dashboard</span>
        </Link>
      </nav>

      {/* User Profile */}
      <div className="mt-auto space-y-4 pt-6 border-t border-[#1E2433]">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-[#1E2433] border border-[#2A3042] flex items-center justify-center text-white text-sm font-bold">
            DR
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-sm font-medium text-white truncate">Dr. Roberts</div>
            <div className="text-xs text-[#9CA3AF]">Hybrid Radiologist</div>
          </div>
        </div>
        <Link href="/login" className="w-full flex items-center gap-3 px-2 py-2 text-sm text-[#9CA3AF] hover:text-white transition-colors">
          <LogOut className="w-5 h-5" />
          <span>Log out</span>
        </Link>
      </div>
    </div>
  )
}
