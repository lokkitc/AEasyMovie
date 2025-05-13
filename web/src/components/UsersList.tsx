import { useState } from 'react';
import { useUsers } from '../hooks/useUsers';

export const UsersList = () => {
  const [page, setPage] = useState(1);
  const { users = [], loading, error, total } = useUsers(page);
  const limit = 10;
  const totalPages = Math.ceil(total / limit);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-white">Загрузка пользователей...</p>
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
          <h3 className="text-xl font-semibold text-white mb-2">Ошибка загрузки</h3>
          <p className="text-red-200">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
          >
            Попробовать снова
          </button>
        </div>
      </div>
    );
  }

  if (!users || users.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-white text-xl">Пользователи не найдены</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h2 className="text-2xl font-bold mb-6 text-white">Пользователи</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {users.map((user, index) => (
          <div
            key={user.id ? `user-${user.id}` : `user-${index}`}
            className="bg-gray-800 rounded-lg p-6 shadow-lg hover:shadow-xl transition-shadow"
          >
            <div className="flex items-center space-x-4">
              {user.photo ? (
                <img
                  key={user.id ? `photo-${user.id}` : `photo-${index}`}
                  src={user.photo}
                  alt={user.username}
                  className="w-12 h-12 rounded-full"
                />
              ) : (
                <div 
                  key={user.id ? `avatar-placeholder-${user.id}` : `avatar-placeholder-${index}`}
                  className="w-12 h-12 rounded-full bg-blue-500 flex items-center justify-center text-white text-xl"
                >
                  {user.username[0].toUpperCase()}
                </div>
              )}
              <div key={user.id ? `user-info-${user.id}` : `user-info-${index}`}>
                <h3 className="text-lg font-semibold text-white">{user.username}</h3>
                <p className="text-gray-400">{user.email}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {totalPages > 1 && (
        <div className="flex justify-center mt-8 space-x-2">
          <button
            key="prev-button"
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-4 py-2 bg-gray-700 text-white rounded disabled:opacity-50 hover:bg-gray-600 transition-colors"
          >
            Назад
          </button>
          <span key="page-info" className="px-4 py-2 text-white">
            Страница {page} из {totalPages}
          </span>
          <button
            key="next-button"
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
            className="px-4 py-2 bg-gray-700 text-white rounded disabled:opacity-50 hover:bg-gray-600 transition-colors"
          >
            Вперед
          </button>
        </div>
      )}
    </div>
  );
}; 