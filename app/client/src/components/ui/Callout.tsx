import { type ReactNode } from 'react'

type CalloutProps = {
  title: string
  children: ReactNode
}

export const Callout = ({ title, children }: CalloutProps) => {
  return (
    <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-4">
      <p className="text-sm font-semibold text-emerald-800">{title}</p>
      <div className="mt-1 text-sm leading-relaxed text-emerald-900/90">{children}</div>
    </div>
  )
}
