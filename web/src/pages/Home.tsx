import { Link } from 'react-router-dom'

export default function Home() {
  return (
    <div className="text-center">
      <h1 className="text-4xl font-bold text-white mb-8">
        Добро пожаловать в NubeMovie
      </h1>
      <p className="text-xl text-white mb-8">
        Ваш путеводитель по миру кино
      </p>
      <div className="flex flex-col sm:flex-row gap-4 justify-center">
        <Link
          to="/movies"
          className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
        >
          Смотреть фильмы
        </Link>
        <Link
          to="/profile"
          className="bg-gray-600 text-white px-6 py-3 rounded-lg hover:bg-gray-700 transition-colors"
        >
          Мой профиль
        </Link>
        <Link
          to="/users"
          className="bg-gray-600 text-white px-6 py-3 rounded-lg hover:bg-gray-700 transition-colors"
        >
          Пользователи
        </Link>
      </div>
    </div>
  )
} 