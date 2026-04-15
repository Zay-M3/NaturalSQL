import { Link } from 'react-router-dom'

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
						<a
							href="https://github.com/Zay-M3/NaturalSQL"
							target="_blank"
							rel="noreferrer"
							aria-label="NaturalSQL GitHub repository"
							className="inline-flex items-center text-slate-700 transition-colors hover:text-emerald-700"
						>
							<svg
								xmlns="http://www.w3.org/2000/svg"
								viewBox="0 0 24 24"
								fill="currentColor"
								className="h-5 w-5"
							>
								<path d="M12 2A10 10 0 0 0 8.84 21.5c.5.08.68-.22.68-.48v-1.7c-2.78.6-3.37-1.34-3.37-1.34-.45-1.15-1.1-1.45-1.1-1.45-.9-.62.07-.6.07-.6 1 .07 1.53 1.02 1.53 1.02.88 1.5 2.31 1.07 2.87.82.09-.64.35-1.07.63-1.31-2.22-.25-4.56-1.1-4.56-4.93 0-1.1.4-2 1.03-2.72-.1-.25-.45-1.27.1-2.64 0 0 .84-.27 2.75 1.04a9.6 9.6 0 0 1 5 0c1.9-1.3 2.74-1.04 2.74-1.04.55 1.37.2 2.39.1 2.64.64.72 1.03 1.62 1.03 2.72 0 3.84-2.34 4.67-4.57 4.92.36.3.68.9.68 1.82v2.7c0 .27.18.57.69.47A10 10 0 0 0 12 2Z" />
							</svg>
						</a>
					</nav>
					<p className="text-xs uppercase tracking-[0.18em] text-slate-500">Copyright {year} NaturalSQL</p>
				</div>
			</div>
		</footer>
	)
}
