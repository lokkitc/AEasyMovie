import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { users } from '../config/api';
import type { User } from '../types/user';

const UserProfile = () => {
  const { userId } = useParams();
  const navigate = useNavigate();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!userId) {
      setError('ID пользователя не указан');
      setLoading(false);
      return;
    }

    const fetchUser = async () => {
      try {
        const userData = await users.getUserById(parseInt(userId));
        setUser(userData);
      } catch (err) {
        console.error('Ошибка при загрузке профиля:', err);
        setError(err instanceof Error ? err.message : 'Ошибка при загрузке профиля пользователя');
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, [userId]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-white">Загрузка профиля...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center bg-red-900/50 p-6 rounded-lg">
          <svg className="w-12 h-12 text-red-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <h3 className="text-xl font-semibold text-white mb-2">Ошибка</h3>
          <p className="text-red-200">{error}</p>
          <button
            onClick={() => navigate('/users')}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
          >
            Вернуться к списку пользователей
          </button>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-white text-xl">Пользователь не найден</p>
          <button
            onClick={() => navigate('/users')}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
          >
            Вернуться к списку пользователей
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 py-8">
      <div className="container mx-auto px-4">
        <div className="bg-gray-800 rounded-lg shadow-xl overflow-hidden">
          {/* Шапка профиля */}
          <div className="relative h-48">
            {user.header_photo ? (
              <img
                src={user.header_photo}
                alt="Header"
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="w-full h-full bg-gradient-to-r from-blue-500 to-purple-500"></div>
            )}
            <div className="absolute bottom-0 left-0 right-0 p-6 bg-gradient-to-t from-gray-800 to-transparent">
              <div className="flex items-end space-x-4">
                {user.photo ? (
                  <img
                    src={user.photo}
                    alt={user.username}
                    className="w-24 h-24 rounded-full border-4 border-gray-800"
                  />
                ) : (
                  <div className="w-24 h-24 rounded-full bg-blue-500 flex items-center justify-center text-white text-4xl border-4 border-gray-800">
                    {user.username[0].toUpperCase()}
                  </div>
                )}
                <div>
                  <h1 className="text-2xl font-bold text-white">{user.username}</h1>
                  <p className="text-gray-300">{user.title}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Информация о пользователе */}
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h2 className="text-xl font-semibold text-white mb-4">Основная информация</h2>
                <div className="space-y-3">
                  <div>
                    <p className="text-gray-400">Имя</p>
                    <p className="text-white">{user.name} {user.surname}</p>
                  </div>
                  <div>
                    <p className="text-gray-400">Email</p>
                    <p className="text-white">{user.email}</p>
                  </div>
                  <div>
                    <p className="text-gray-400">Возраст</p>
                    <p className="text-white">{user.age || 'Не указан'}</p>
                  </div>
                  <div>
                    <p className="text-gray-400">Локация</p>
                    <p className="text-white">{user.location || 'Не указана'}</p>
                  </div>
                </div>
              </div>

              <div>
                <h2 className="text-xl font-semibold text-white mb-4">Статистика</h2>
                <div className="space-y-3">
                  <div>
                    <p className="text-gray-400">Уровень</p>
                    <p className="text-white">{user.level}</p>
                  </div>
                  <div>
                    <p className="text-gray-400">Статус</p>
                    <p className="text-white">
                      {user.is_premium ? (
                        <span className="text-yellow-400">Премиум</span>
                      ) : (
                        <span>Обычный</span>
                      )}
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-400">Дата регистрации</p>
                    <p className="text-white">
                      {new Date(user.created_at).toLocaleDateString('ru-RU')}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {user.about && (
              <div className="mt-6">
                <h2 className="text-xl font-semibold text-white mb-4">О себе</h2>
                <p className="text-gray-300">{user.about}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserProfile; 