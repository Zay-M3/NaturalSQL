import { useEffect, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAuthStore } from '../storage/authStore'

type NavItem = {
  label: string
  path: string
  isActive: (pathname: string) => boolean
}

const navItems: NavItem[] = [
  {
    label: 'Chat',
    path: '/',
    isActive: (pathname) => pathname === '/' || pathname.startsWith('//'),
  },
  {
    label: 'Documentation',
    path: '/documentation',
    isActive: (pathname) => pathname === '/documentation' || pathname.startsWith('/documentation/'),
  },
  {
    label: 'About',
    path: '/about',
    isActive: (pathname) => pathname === '/about' || pathname.startsWith('/about/'),
  },
]

export const Header = () => {
  const { pathname } = useLocation()
  const [isCompact, setIsCompact] = useState(false)
  const user = useAuthStore((state) => state.user)
  const isLoading = useAuthStore((state) => state.isLoading)
  const loginWithGoogle = useAuthStore((state) => state.loginWithGoogle)
  const logout = useAuthStore((state) => state.logout)

  useEffect(() => {
    const onScroll = () => {
      setIsCompact(window.scrollY > 16)
    }

    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })

    return () => {
      window.removeEventListener('scroll', onScroll)
    }
  }, [])

  return (
    <header
      className={[
        'sticky top-0 z-50 border-b border-emerald-100/80 bg-emerald-50/60 backdrop-blur-md',
        'transition-[padding,background-color,backdrop-filter] duration-300 ease-out',
        isCompact ? 'py-2' : 'py-4',
      ].join(' ')}
    >
      <nav aria-label="Primary" className="mx-auto flex max-w-3xl items-center justify-center">
        <ul className="flex items-center justify-center gap-12">
          {navItems.map((item) => {
            const active = item.isActive(pathname)

            return (
              <li key={item.label}>
                <Link
                  to={item.path}
                  className={[
                    'relative inline-flex items-center py-1 text-sm font-medium tracking-wide text-slate-700 transition-colors duration-200',
                    active ? 'text-emerald-900' : 'hover:text-emerald-800',
                  ].join(' ')}
                >
                  <span>{item.label}</span>
                  <span
                    aria-hidden="true"
                    className={[
                      'absolute -bottom-1 left-0 h-0.5 w-full bg-emerald-700 transition-opacity duration-200',
                      active ? 'opacity-100' : 'opacity-0',
                    ].join(' ')}
                  />
                </Link>
              </li>
            )
          })}
          <li>
            {user ? (
              <button
                type="button"
                disabled={isLoading}
                onClick={logout}
                className="rounded-full border border-emerald-300 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-emerald-900 transition-colors hover:bg-emerald-100 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {isLoading ? 'Logging out...' : 'Logout'}
              </button>
            ) : (
              <button
                type="button"
                disabled={isLoading}
                onClick={loginWithGoogle}
                className="rounded-full bg-emerald-800 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-white transition-colors hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {isLoading ? 'Login in progress...' : 'Login'}
              </button>
            )}
          </li>
        </ul>
      </nav>
    </header>
  )
}
