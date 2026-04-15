type HeroProps = {
  title: string
  description: string
  badge?: string
}

export const Hero = ({ title, description, badge }: HeroProps) => {
  return (
    <section className="rounded-2xl border border-emerald-100 bg-gradient-to-br from-emerald-50 via-white to-lime-50 p-6">
      {badge ? (
        <span className="inline-flex rounded-full border border-emerald-200 bg-white px-3 py-1 text-xs font-semibold uppercase tracking-[0.14em] text-emerald-700">
          {badge}
        </span>
      ) : null}
      <h2 className="mt-3 text-3xl font-semibold tracking-tight text-slate-900 sm:text-4xl">{title}</h2>
      <p className="mt-3 max-w-3xl text-base leading-relaxed text-slate-700">{description}</p>
    </section>
  )
}
