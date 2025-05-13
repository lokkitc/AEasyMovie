import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { api } from '@/config/api'
import { useState } from 'react'
import { FaSort, FaFilter, FaStar } from 'react-icons/fa'

interface Movie {
  movie_id: number
  title: string
  description: string
  release_date: string
  rating: number
  poster: string
  backdrop: string
  director: string
  genres: string[]
}

type SortOption = 'rating_desc' | 'rating_asc' | 'year_desc' | 'year_asc' | 'title_asc' | 'title_desc'

export default function Movies() {
  const [sortBy, setSortBy] = useState<SortOption>('rating_desc')
  const [selectedGenres, setSelectedGenres] = useState<string[]>([])
  const [minRating, setMinRating] = useState<number>(0)
  const [yearRange, setYearRange] = useState<[number, number]>([1900, new Date().getFullYear()])

  const { data: movies, isLoading, error } = useQuery<Movie[]>({
    queryKey: ['movies'],
    queryFn: async () => {
      const response = await api.get('/movies/')
      return response.data
    },
  })

  // Получаем уникальные жанры из всех фильмов
  const allGenres = Array.from(new Set(movies?.flatMap(movie => movie.genres) || []))

  // Фильтрация и сортировка фильмов
  const filteredAndSortedMovies = movies?.filter(movie => {
    const movieYear = new Date(movie.release_date).getFullYear()
    
    // Проверка жанров: фильм должен содержать ВСЕ выбранные жанры
    const matchesGenres = selectedGenres.length === 0 || 
      selectedGenres.every(genre => movie.genres.includes(genre))
    
    const matchesRating = movie.rating >= minRating
    const matchesYear = movieYear >= yearRange[0] && movieYear <= yearRange[1]
    
    return matchesGenres && matchesRating && matchesYear
  }).sort((a, b) => {
    switch (sortBy) {
      case 'rating_desc':
        return b.rating - a.rating
      case 'rating_asc':
        return a.rating - b.rating
      case 'year_desc':
        return new Date(b.release_date).getTime() - new Date(a.release_date).getTime()
      case 'year_asc':
        return new Date(a.release_date).getTime() - new Date(b.release_date).getTime()
      case 'title_asc':
        return a.title.localeCompare(b.title)
      case 'title_desc':
        return b.title.localeCompare(a.title)
      default:
        return 0
    }
  })

  if (isLoading) {
    return <div className="text-center">Загрузка...</div>
  }

  if (error) {
    return <div className="text-center text-red-600">Ошибка при загрузке фильмов</div>
  }

  return (
    <div className="flex gap-8">
      <div className="flex-1">
      <h1 className="text-3xl font-bold mb-8 text-white">Фильмы</h1>
        {filteredAndSortedMovies?.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-gray-400 text-lg">
              {selectedGenres.length > 0 
                ? 'Нет фильмов с выбранными жанрами'
                : 'Нет доступных фильмов'}
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredAndSortedMovies?.map((movie) => (
          <Link
            key={movie.movie_id}
            to={`/movies/${movie.movie_id}`}
                className="movie-card bg-dark-secondary rounded-lg overflow-hidden hover:scale-105 transition-transform"
          >
            {movie.poster && (
              <img
                src={movie.poster}
                alt={movie.title}
                    className="w-full h-64 object-cover"
              />
            )}
                <div className="p-4">
            <h2 className="text-xl font-semibold mb-2 text-white">{movie.title}</h2>
                  <p className="text-gray-400 mb-2 line-clamp-2">{movie.description}</p>
                  <div className="flex justify-between items-center text-sm text-gray-400">
              <span>{new Date(movie.release_date).getFullYear()}</span>
                    <div className="flex items-center gap-1">
                      <FaStar className="text-yellow-500" />
                      <span>{movie.rating.toFixed(1)}</span>
                    </div>
                  </div>
            </div>
          </Link>
        ))}
          </div>
        )}
      </div>

      {/* Панель фильтров */}
      <div className="w-80 bg-dark-secondary p-6 rounded-lg h-fit">
        <div className="space-y-6">
          {/* Сортировка */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
              <FaSort />
              Сортировка
            </h3>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as SortOption)}
              className="w-full p-2 rounded bg-dark-primary text-white border border-gray-600"
            >
              <option value="rating_desc">По рейтингу (убыв.)</option>
              <option value="rating_asc">По рейтингу (возр.)</option>
              <option value="year_desc">По году (убыв.)</option>
              <option value="year_asc">По году (возр.)</option>
              <option value="title_asc">По названию (А-Я)</option>
              <option value="title_desc">По названию (Я-А)</option>
            </select>
          </div>

          {/* Фильтр по жанрам */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
              <FaFilter />
              Жанры
            </h3>
            {allGenres.length === 0 ? (
              <p className="text-gray-400 text-sm">Нет доступных жанров</p>
            ) : (
              <div className="flex flex-wrap gap-2">
                {allGenres.map((genre) => (
                  <button
                    key={genre}
                    onClick={() => {
                      if (selectedGenres.includes(genre)) {
                        setSelectedGenres(selectedGenres.filter(g => g !== genre))
                      } else {
                        setSelectedGenres([...selectedGenres, genre])
                      }
                    }}
                    className={`px-3 py-1.5 rounded-full text-sm font-medium transition-all duration-200 ${
                      selectedGenres.includes(genre)
                        ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30'
                        : 'bg-dark-primary text-gray-300 hover:bg-gray-700'
                    }`}
                  >
                    {genre}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Фильтр по рейтингу */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
              <FaStar />
              Минимальный рейтинг
            </h3>
            <input
              type="range"
              min="0"
              max="10"
              step="0.1"
              value={minRating}
              onChange={(e) => setMinRating(parseFloat(e.target.value))}
              className="w-full"
            />
            <div className="text-white text-center mt-1">{minRating.toFixed(1)}</div>
          </div>

          {/* Фильтр по годам */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-3">Годы выпуска</h3>
            <div className="flex gap-4">
              <div>
                <label className="text-white text-sm">От</label>
                <input
                  type="number"
                  value={yearRange[0]}
                  onChange={(e) => setYearRange([parseInt(e.target.value), yearRange[1]])}
                  className="w-full p-2 rounded bg-dark-primary text-white border border-gray-600"
                />
              </div>
              <div>
                <label className="text-white text-sm">До</label>
                <input
                  type="number"
                  value={yearRange[1]}
                  onChange={(e) => setYearRange([yearRange[0], parseInt(e.target.value)])}
                  className="w-full p-2 rounded bg-dark-primary text-white border border-gray-600"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 