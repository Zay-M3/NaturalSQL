type SidebarItem = {
  id: string
  label: string
}

type SidebarProps = {
  title: string
  items: SidebarItem[]
}

export const Sidebar = ({ title, items }: SidebarProps) => {
  return (
    <aside className="sticky top-6 h-fit rounded-2xl border border-emerald-100 bg-emerald-50/60 p-4">
      <p className="mb-3 text-xs font-semibold uppercase tracking-[0.18em] text-emerald-700">{title}</p>
      <nav aria-label="Documentation sections">
        <ul className="space-y-2">
          {items.map((item) => (
            <li key={item.id}>
              <a
                href={`#${item.id}`}
                className="block rounded-lg px-3 py-2 text-sm font-medium text-slate-700 transition-colors hover:bg-emerald-100 hover:text-emerald-900"
              >
                {item.label}
              </a>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  )
}
