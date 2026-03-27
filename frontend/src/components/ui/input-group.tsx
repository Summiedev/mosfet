import * as React from "react"

export function InputGroup({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex items-center border rounded-md overflow-hidden">
      {children}
    </div>
  )
}

export function InputGroupAddon({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="px-3 bg-muted text-muted-foreground flex items-center">
      {children}
    </div>
  )
}

export function InputGroupInput(
  props: React.InputHTMLAttributes<HTMLInputElement>
) {
  return (
    <input
      {...props}
      className="flex-1 px-3 py-2 outline-none bg-transparent"
    />
  )
}