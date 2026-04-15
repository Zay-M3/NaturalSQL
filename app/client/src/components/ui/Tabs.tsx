import { useState } from 'react'
import { type ReactNode } from 'react'

type TabItem = {
  id: string
  label: string
  content: ReactNode
}

type TabsProps = {
  tabs: TabItem[]
}

export const Tabs = ({ tabs }: TabsProps) => {
  const [activeId, setActiveId] = useState(tabs[0]?.id)
  const activeTab = tabs.find((tab) => tab.id === activeId) ?? tabs[0]

  if (!tabs.length) return null

  return (
    <div className="rounded-xl border border-slate-200 bg-white">
      <div className="flex flex-wrap gap-2 border-b border-slate-200 p-2">
        {tabs.map((tab) => {
          const isActive = tab.id === activeTab.id
          return (
            <button
              key={tab.id}
              type="button"
              onClick={() => setActiveId(tab.id)}
              className={[
                'rounded-lg px-3 py-2 text-sm font-medium transition',
                isActive
                  ? 'bg-emerald-100 text-emerald-800'
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200',
              ].join(' ')}
            >
              {tab.label}
            </button>
          )
        })}
      </div>
      <div className="p-3">{activeTab.content}</div>
    </div>
  )
}
