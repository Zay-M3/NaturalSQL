import { GitHubProjectBadge } from '../components/ui/GitHubProjectBadge'

export default function About() {
    return (
        <main className="h-full min-h-0 overflow-y-auto bg-linear-to-b from-emerald-50 via-slate-50 to-white text-slate-900">
            <div className="mx-auto w-full max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
                <section className="rounded-3xl p-6 sm:p-8">
                    <div className="flex flex-col gap-6 sm:flex-row sm:items-start sm:justify-between">
                        <div className="space-y-4">
                            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-emerald-700">About NaturalSQL</p>
                            <h1 className="font-serif text-4xl tracking-tight text-slate-900 sm:text-5xl">Why <span className='text-emerald-700'>NaturalSQL</span> exists</h1>
                            <p className="max-w-2xl text-sm leading-relaxed tracking-wide text-slate-700 sm:text-base">
                                NaturalSQL started with a practical need: interacting with SQL databases through an LLM without adopting
                                a heavyweight framework full of unrelated features. The goal was to keep the workflow lightweight,
                                focused, and production-friendly.
                            </p>
                            <p className="max-w-2xl text-sm leading-relaxed tracking-wide text-slate-700 sm:text-base">
                                The project extracts real schema metadata, builds semantic vectors, and retrieves the most relevant
                                table and relationship context so your LLM can generate more accurate SQL grounded in your actual
                                database structure.
                            </p>

                            <img src="/img/naturalsql.png" alt="NaturalSQL logo" className="h-60 w-auto" />
                        </div>

                        <GitHubProjectBadge
                            owner="Zay-M3"
                            repo="NaturalSQL"
                            variant="detailed"
                            creatorName="Oscar David Estrada"
                            showCreator={true}
                            showBio={true}
                            className="w-full max-w-sm"
                        />
                    </div>

                    <div className="mt-8 grid gap-3 sm:grid-cols-3">
                        <div className="rounded-2xl border border-emerald-100 bg-white/80 p-4">
                            <p className="text-xs uppercase tracking-[0.14em] text-slate-500">Problem</p>
                            <p className="mt-2 text-sm leading-relaxed text-slate-700">
                                LLMs often miss real SQL details when they do not have accurate table, column, and relationship context.
                            </p>
                        </div>
                        <div className="rounded-2xl border border-emerald-100 bg-white/80 p-4">
                            <p className="text-xs uppercase tracking-[0.14em] text-slate-500">Solution</p>
                            <p className="mt-2 text-sm leading-relaxed text-slate-700">
                                NaturalSQL indexes schema metadata into vectors and retrieves grounded context for every natural-language request.
                            </p>
                        </div>
                        <div className="rounded-2xl border border-emerald-100 bg-white/80 p-4">
                            <p className="text-xs uppercase tracking-[0.14em] text-slate-500">Mission</p>
                            <p className="mt-2 text-sm leading-relaxed text-slate-700">
                                Make SQL generation accessible, fast, and reliable without sacrificing control over your data workflow.
                            </p>
                        </div>
                    </div>
                </section>
            </div>
        </main>
    )
}
