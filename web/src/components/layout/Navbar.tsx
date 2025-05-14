import { Link, useNavigate } from 'react-router-dom'
import { useState, useRef, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { auth } from '@/config/api'
import { maxWidth } from '@/config/values'


interface User {
  user_id: number
  username: string
  email: string
  name: string
  surname: string
  photo: string
}

export default function Navbar() {
  const navigate = useNavigate()
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)
  const token = localStorage.getItem('token')

  const { data: user } = useQuery<User>({
    queryKey: ['user'],
    queryFn: () => auth.getProfile(),
    enabled: !!token,
  })

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsMenuOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleLogout = () => {
    localStorage.removeItem('token')
    navigate('/login')
  }

  return (
    <nav className="bg-white dark:bg-dark-secondary shadow-lg">
      <div className="container mx-auto px-4" style={{ maxWidth: maxWidth }}>
        <div className="flex justify-between items-center h-16">
          <Link to="/" className="text-xl font-bold text-gray-800 dark:text-white flex items-center gap-2">
            <img src="/logo-transparent.png" alt="AEasyMovie" className="w-10 h-10" />
            AEasyMovie
          </Link>
          <div className="flex items-center space-x-4">
            <Link to="/movies" className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">
              Фильмы
            </Link>
            {token ? (
              <div className="relative" ref={menuRef}>
                <button
                  onClick={() => setIsMenuOpen(!isMenuOpen)}
                  className="flex items-center space-x-2 text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white focus:outline-none"
                >
                  <div className="w-8 h-8 rounded-full bg-gray-200 dark:bg-dark-accent flex items-center justify-center">
                    {user?.username ? (
                      <img 
                        src={user.photo} 
                        alt={user.username}
                        className="w-8 h-8 rounded-full object-cover border-2 border-white"
                      />
            
                    ) : (
                      <svg
                        className="w-5 h-5 text-gray-500 dark:text-gray-300"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                        />
                      </svg>
                    )}
                  </div>
                </button>
                {isMenuOpen && (
                  <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-dark-secondary rounded-md shadow-lg py-1 z-10">
                    <Link
                      to="/profile"
                      className="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-dark-accent"
                      onClick={() => setIsMenuOpen(false)}
                    >
                      Профиль
                    </Link>
                    <button
                      onClick={handleLogout}
                      className="block w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-dark-accent"
                    >
                      Выйти
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <>
                <Link to="/login" className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">
                  Войти
                </Link>
                <Link to="/register" className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">
                  Регистрация
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
} 