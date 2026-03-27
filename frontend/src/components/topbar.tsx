import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Plus } from "lucide-react"

interface TopbarProps {
  title?: string
  actionButton?: React.ReactNode
}

export function Topbar({ title = "Good morning, Dr. Roberts", actionButton }: TopbarProps) {
  return (
    <div className="sticky top-0 z-10 bg-[#020618] border-b border-[#1E2433] px-8 py-6 flex items-center justify-between">
      <div>
        <h1 className="text-2xl font-bold text-white">{title}</h1>
      </div>
      {actionButton ? actionButton : (
        <Link href="/start-scan">
          <Button className="bg-[#4F39F6] hover:bg-[#3D29D6] text-white gap-2 px-6">
            <Plus className="w-4 h-4" />
            Start New Scan
          </Button>
        </Link>
      )}
    </div>
  )
}

