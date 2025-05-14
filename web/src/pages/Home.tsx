import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { users as usersApi } from '../config/api';
import { api } from '@/config/api';
import type { User } from '@/types/user';

interface Movie {
  movie_id: number;
  title: string;
  poster: string;
  rating: number;
  release_date: string;
  genres?: string[];
}

export default function Home() {
  const [topUsers, setTopUsers] = useState<User[]>([]);
  const [topMovies, setTopMovies] = useState<Movie[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const allUsers: User[] = await usersApi.getUsers();
        const sortedUsers = [...allUsers].sort((a, b) => b.level - a.level).slice(0, 10);
        setTopUsers(sortedUsers);

        const moviesResp = await api.get<Movie[]>('/movies/');
        const sortedMovies = [...moviesResp.data].sort((a, b) => b.rating - a.rating).slice(0, 12);
        setTopMovies(sortedMovies);
      } catch (e) {
        setTopUsers([]);
        setTopMovies([]);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  return (
    <div className="min-h-screen bg-black py-8">
      <div className="container mx-auto px-4">
        {/* Горячие новинки */}
        <h2 className="text-2xl font-bold text-white mb-2 mt-4 flex items-center gap-2">
          Горячие новинки
          <span className="h-1 w-24 bg-purple-600 rounded ml-2"></span>
        </h2>
        <div className="overflow-x-auto pb-4 scrollbar-thin scrollbar-thumb-gray-700 scrollbar-track-black">
          <div className="flex gap-6 min-w-max">
            {loading ? (
              <div className="text-gray-400">Загрузка...</div>
            ) : topMovies.length === 0 ? (
              <div className="text-gray-400">Нет фильмов</div>
            ) : (
              topMovies.map((movie) => (
                <Link
                  to={`/movies/${movie.movie_id}`}
                  key={movie.movie_id}
                  className="relative bg-gray-800 rounded-xl shadow-lg hover:shadow-2xl transition-shadow hover:scale-105 overflow-hidden flex-shrink-0 w-52"
                  style={{ minWidth: '208px' }}
                >
                  <img
                    src={movie.poster}
                    alt={movie.title}
                    className="w-full h-72 object-cover"
                  />
                  <div className="absolute top-2 right-2 bg-black bg-opacity-70 px-2 py-1 rounded text-yellow-400 font-bold text-xs flex items-center gap-1">
                    ★ {movie.rating.toFixed(1)}
                  </div>
                  <div className="p-3">
                    <div className="text-white font-semibold truncate" title={movie.title}>{movie.title}</div>
                    <div className="text-gray-400 text-xs mt-1 flex flex-wrap gap-1">
                      <span>{new Date(movie.release_date).getFullYear()}</span>
                      {movie.genres && movie.genres.length > 0 && (
                        <span>• {movie.genres[0]}</span>
                      )}
                    </div>
                  </div>
                </Link>
              ))
            )}
          </div>
        </div>

        {/* Лучшие пользователи */}
        <h2 className="text-2xl font-bold text-white mb-2 mt-10 flex items-center gap-2">
          Топ пользователи
          <span className="h-1 w-24 bg-purple-600 rounded ml-2"></span>
        </h2>
        <div className="overflow-x-auto pb-4 scrollbar-thin scrollbar-thumb-gray-700 scrollbar-track-black">
          <div className="flex gap-6 min-w-max">
            {loading ? (
              <div className="text-gray-400">Загрузка...</div>
            ) : topUsers.length === 0 ? (
              <div className="text-gray-400">Нет данных</div>
            ) : (
              topUsers.map((user, idx) => (
                <Link
                  to={`/users/${user.user_id}`}
                  key={user.user_id}
                  className="bg-gray-800 rounded-xl p-5 flex flex-col items-center w-52 shadow-lg hover:shadow-2xl transition-shadow hover:scale-105 flex-shrink-0"
                  style={{ minWidth: '208px' }}
                >
                  <div className="relative mb-3">
                    <img
                      src={user.photo || '/logo.png'}
                      alt={user.username}
                      className="w-20 h-20 rounded-full border-4 border-purple-600 object-cover bg-black"
                    />
                    {idx === 0 && (
                      <span className="absolute -top-2 -right-2 bg-yellow-400 text-black text-xs font-bold px-2 py-1 rounded-full shadow">TOP 1</span>
                    )}
                  </div>
                  <div className="text-white font-bold text-lg truncate mb-1">{user.username}</div>
                  <div className="text-purple-400 text-xs mb-1">{user.title}</div>
                  <div className="flex items-center gap-2 text-sm">
                    <span className="text-purple-400 font-bold">Уровень {user.level}</span>
                  </div>
                </Link>
              ))
            )}
          </div>
        </div>

        {/* Блок подписки/уведомления */}
        <div className="mt-12 flex justify-center">
          <div className="bg-gray-900/80 rounded-xl px-8 py-6 flex flex-col items-center shadow-lg max-w-xl w-full">
            <div className="text-white text-lg font-semibold mb-2">🎁 Получай редкие карты и молнии просто так!</div>
            <div className="text-gray-300 mb-4 text-center">Подпишись на наш <a href="https://t.me/yourchannel" target="_blank" rel="noopener noreferrer" className="text-purple-400 underline hover:text-purple-300">телеграм</a> и участвуй в розыгрышах карт, молний и билетов!</div>
            <a
              href="https://t.me/yourchannel"
              target="_blank"
              rel="noopener noreferrer"
              className="bg-purple-600 text-white px-6 py-2 rounded-lg hover:bg-purple-700 transition-colors font-semibold shadow"
            >
              Подписаться
            </a>
          </div>
        </div>
      </div>
    </div>
  );
} 