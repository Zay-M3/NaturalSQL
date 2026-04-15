type TopbarProps = {
  title: string
  subtitle: string
}

export const Topbar = ({ title, subtitle }: TopbarProps) => {
  return (
    <header className="rounded-2xl border border-emerald-100 bg-white p-4 shadow-sm">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-emerald-700">NaturalSQL Docs</p>
          <h1 className="text-2xl font-serif tracking-tight text-slate-900">{title}</h1>
          <p className="text-sm text-slate-600">{subtitle}</p>
        </div>
        <div className="w-full max-w-xs rounded-xl border border-emerald-100 bg-emerald-50/70 px-3 py-2 text-sm text-slate-500">
          Search docs (soon)
        </div>
      </div>
    </header>
  )
}
