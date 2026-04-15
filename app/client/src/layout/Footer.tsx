import { Link } from 'react-router-dom'
import { GitHubProjectBadge } from '../components/ui/GitHubProjectBadge'

export const Footer = () => {
	const year = new Date().getFullYear()

	return (
		<footer className="border-t border-emerald-100 bg-emerald-50/40 text-slate-900">
			<div className="mx-auto flex w-full max-w-6xl flex-col gap-6 px-6 py-8 sm:px-10 lg:flex-row lg:items-end lg:justify-between">
				<div className="space-y-3">
					<p className="font-serif text-2xl tracking-tight text-slate-900 sm:text-3xl">NaturalSQL</p>
					<p className="max-w-md text-sm leading-relaxed tracking-wide text-slate-600">
						Build SQL with natural language, keep your workflow fast, and stay focused on analysis.
					</p>
				</div>

				<div className="flex flex-col gap-4 text-sm tracking-wide sm:items-end">
					<nav aria-label="Footer" className="flex items-center gap-6">
						<Link to="/" className="transition-colors hover:text-emerald-700">
							Chat
						</Link>
						<Link to="/documentation" className="transition-colors hover:text-emerald-700">
							Documentation
						</Link>
						<Link to="/about" className="transition-colors hover:text-emerald-700">
							About
						</Link>
						<GitHubProjectBadge owner="Zay-M3" repo="NaturalSQL" variant="compact" />
					</nav>
					<p className="text-xs uppercase tracking-[0.18em] text-slate-500">Copyright {year} NaturalSQL</p>
				</div>
			</div>
		</footer>
	)
}
