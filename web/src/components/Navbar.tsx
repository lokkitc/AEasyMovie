import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { auth } from '@/config/api'

export default function Navbar() {
  const { data: user } = useQuery({
    queryKey: ['user'],
    queryFn: () => auth.getProfile(),
    retry: false
  })

  return (
    <nav className="bg-dark-primary shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-20">
          <div className="flex items-center">
            <Link to="/" className="text-white text-xl font-bold">
              NubeMovie
            </Link>
          </div>

          <div className="flex items-center gap-4">
            {user && (
              <>
                {user.is_premium && (
                  <div className="flex items-center gap-2 bg-gradient-to-r from-purple-500 to-pink-500 px-3 py-1 rounded-full">
                    <span className="text-white text-sm">Премиум</span>
                  </div>
                )}
                <div className="flex items-center gap-2 bg-dark-secondary px-3 py-1 rounded-full">
                  <span className="text-yellow-400">💰</span>
                  <span className="text-white text-sm">{user.money}</span>
                </div>
                <div className="flex items-center gap-2">
                  <img
                    src={user.photo}
                    alt={user.username}
                    className="w-8 h-8 rounded-full"
                  />
                  <Link to="/profile" className="text-white hover:text-gray-300">
                    {user.username}
                  </Link>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
} 