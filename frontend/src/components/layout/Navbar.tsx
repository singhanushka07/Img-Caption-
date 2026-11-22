import { NavLink } from 'react-router-dom'
import { cn } from '@/lib/utils'

const links = [
  { to: '/', label: 'Home' },
  { to: '/caption', label: 'Caption Studio' },
  { to: '/vqa', label: 'Visual QA' },
  { to: '/analytics', label: 'Analytics' },
  { to: '/about', label: 'About' },
]

export default function Navbar() {
  return (
    <nav className="sticky top-0 z-50 h-14 backdrop-blur-md bg-white/[0.88] border-b border-slate-200/60">
      <div className="max-w-[1320px] mx-auto px-8 h-full flex items-center gap-8">
        <span className="font-[800] text-sm tracking-tight select-none">
          IMG Caption
        </span>

        <div className="flex items-center gap-1 h-full">
          {links.map(({ to, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                cn(
                  'relative px-3 h-full flex items-center text-[13px] transition-colors duration-200',
                  isActive
                    ? 'text-blue-600 font-semibold'
                    : 'text-slate-500 hover:text-slate-700',
                )
              }
            >
              {({ isActive }) => (
                <>
                  {label}
                  {isActive && (
                    <span className="absolute bottom-0 left-3 right-3 h-[2px] bg-blue-600 rounded-full" />
                  )}
                </>
              )}
            </NavLink>
          ))}
        </div>
      </div>
    </nav>
  )
}
