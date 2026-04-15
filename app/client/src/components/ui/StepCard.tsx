import { type ReactNode } from 'react'

type StepCardProps = {
  step: string
  title: string
  children: ReactNode
}

export const StepCard = ({ step, title, children }: StepCardProps) => {
  return (
    <article className="rounded-xl border border-slate-200 bg-slate-50 p-4">
      <div className="mb-2 flex items-center gap-3">
        <span className="inline-flex h-8 w-8 items-center justify-center rounded-full border border-emerald-200 bg-white text-xs font-semibold text-emerald-700">
          {step}
        </span>
        <h4 className="text-lg font-semibold tracking-tight text-slate-900">{title}</h4>
      </div>
      <div className="space-y-3 text-sm text-slate-700">{children}</div>
    </article>
  )
}
