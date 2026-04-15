import { type ReactNode } from 'react'

type SectionProps = {
  id: string
  eyebrow?: string
  title: string
  description?: string
  children: ReactNode
}

export const Section = ({ id, eyebrow, title, description, children }: SectionProps) => {
  return (
    <section id={id} className="scroll-mt-24 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      {eyebrow ? (
        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-emerald-700">{eyebrow}</p>
      ) : null}
      <h3 className="mt-1 text-2xl font-semibold tracking-tight text-slate-900">{title}</h3>
      {description ? <p className="mt-2 text-sm leading-relaxed text-slate-600">{description}</p> : null}
      <div className="mt-4 space-y-4">{children}</div>
    </section>
  )
}
