import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { auth, api } from '@/config/api'
import { useState, useRef } from 'react'
import { toast } from 'react-hot-toast'
import { User } from '@/types'
import PremiumPurchase from '@/components/PremiumPurchase'

interface UserResponse {
  user: User;
  path: string;
}

interface Comment {
  comment_id: number
  content: string
  movie_id: number
  created_at: string
  movie: {
    title: string
  }
}

export default function Profile() {
  const [isEditing, setIsEditing] = useState(false)
  const [formData, setFormData] = useState<Partial<User>>({})
  const [isUploading, setIsUploading] = useState(false)
  const avatarInputRef = useRef<HTMLInputElement>(null)
  const headerInputRef = useRef<HTMLInputElement>(null)
  const queryClient = useQueryClient()
  const [showPremiumModal, setShowPremiumModal] = useState(false)

  const { data: user, isLoading: userLoading, error: userError } = useQuery<User>({
    queryKey: ['user'],
    queryFn: () => auth.getProfile(),
    retry: false
  })

  const updateProfileMutation = useMutation({
    mutationFn: async (data: Partial<User>) => {
      const changedFields: Record<string, any> = {};
      
      Object.entries(data).forEach(([key, value]) => {
        const typedKey = key as keyof User;
        if (user && user[typedKey] !== value && value !== null && value !== undefined) {
          changedFields[key] = value;
        }
      });

      if (Object.keys(changedFields).length === 0) {
        throw new Error('Нет изменений для сохранения');
      }

      const response = await api.patch(`/users/${user?.user_id}`, changedFields);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user'] });
      setIsEditing(false);
      toast.success('Профиль успешно обновлен');
    },
    onError: (error: any) => {
      if (error.response?.status === 403) {
        toast.error('У вас нет прав для редактирования этого профиля');
      } else {
        toast.error(error.response?.data?.detail || 'Ошибка при обновлении профиля');
      }
    }
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData((prev: Partial<User>) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    updateProfileMutation.mutate(formData)
  }

  const handleFileUpload = async (file: File, type: 'photo' | 'header_photo') => {
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      setIsUploading(true);
      const response = await api.post<UserResponse>(`/users/upload/${type}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      if (response.data) {
        queryClient.invalidateQueries({ queryKey: ['user'] });
        toast.success('Изображение успешно загружено');
      }
    } catch (error) {
      console.error('Ошибка при загрузке файла:', error);
      toast.error('Ошибка при загрузке изображения');
    } finally {
      setIsUploading(false);
    }
  };

  const handleAvatarClick = () => {
    avatarInputRef.current?.click()
  }

  const handleHeaderClick = () => {
    headerInputRef.current?.click()
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>, type: 'photo' | 'header_photo') => {
    const file = e.target.files?.[0]
    if (file) {
      handleFileUpload(file, type)
    }
  }

  if (userLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-white">Загрузка профиля...</p>
        </div>
      </div>
    );
  }

  if (userError) {
    if (userError instanceof Error && userError.message === 'Токен не найден') {
      window.location.href = '/login'
      return null
    }
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center bg-red-900/50 p-6 rounded-lg">
          <svg className="w-12 h-12 text-red-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <h3 className="text-xl font-semibold text-white mb-2">Ошибка</h3>
          <p className="text-red-200">{userError instanceof Error ? userError.message : 'Неизвестная ошибка'}</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-white text-xl">Профиль не найден</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black py-8">
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
            <div className="absolute inset-0 bg-black bg-opacity-50 opacity-0 hover:opacity-100 transition-opacity flex items-center justify-center cursor-pointer"
                 onClick={handleHeaderClick}>
              <span className="text-white">Изменить заголовок</span>
            </div>
            <div className="absolute bottom-0 left-0 right-0 p-6 bg-gradient-to-t from-gray-800 to-transparent">
              <div className="flex items-end space-x-4">
                {user.photo ? (
            <div className="relative group">
            <img
              src={user.photo}
              alt={user.username}
                      className="w-24 h-24 rounded-full border-4 border-gray-800 cursor-pointer"
                onClick={handleAvatarClick}
              />
                    <div className="absolute inset-0 bg-black bg-opacity-50 opacity-0 group-hover:opacity-100 transition-opacity rounded-full flex items-center justify-center cursor-pointer"
                         onClick={handleAvatarClick}>
                      <span className="text-white text-sm">Изменить фото</span>
                    </div>
                  </div>
                ) : (
                  <div className="w-24 h-24 rounded-full bg-blue-500 flex items-center justify-center text-white text-4xl border-4 border-gray-800 cursor-pointer"
                       onClick={handleAvatarClick}>
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
            <div className="flex justify-end mb-4">
              <button
                onClick={() => setIsEditing(!isEditing)}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
              >
                {isEditing ? 'Отмена' : 'Редактировать'}
              </button>
            </div>

            {isEditing ? (
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                    <label className="block text-gray-400 mb-1">Имя</label>
                  <input
                    type="text"
                    name="name"
                    defaultValue={user.name}
                    onChange={handleInputChange}
                    className="w-full p-2 rounded bg-dark-primary text-white border border-gray-600"
                  />
                </div>
                <div>
                    <label className="block text-gray-400 mb-1">Фамилия</label>
                  <input
                    type="text"
                    name="surname"
                    defaultValue={user.surname}
                    onChange={handleInputChange}
                    className="w-full p-2 rounded bg-dark-primary text-white border border-gray-600"
                  />
                </div>
                <div>
                    <label className="block text-gray-400 mb-1">Имя пользователя</label>
                  <input
                    type="text"
                    name="username"
                    defaultValue={user.username}
                    onChange={handleInputChange}
                    className="w-full p-2 rounded bg-dark-primary text-white border border-gray-600"
                  />
                </div>
                <div>
                    <label className="block text-gray-400 mb-1">Email</label>
                  <input
                    type="email"
                    name="email"
                    defaultValue={user.email}
                    onChange={handleInputChange}
                    className="w-full p-2 rounded bg-dark-primary text-white border border-gray-600"
                  />
                </div>
                <div>
                    <label className="block text-gray-400 mb-1">Местоположение</label>
                  <input
                    type="text"
                    name="location"
                    defaultValue={user.location}
                    onChange={handleInputChange}
                    className="w-full p-2 rounded bg-dark-primary text-white border border-gray-600"
                  />
                </div>
                <div>
                    <label className="block text-gray-400 mb-1">Возраст</label>
                  <input
                    type="number"
                    name="age"
                    defaultValue={user.age}
                    onChange={handleInputChange}
                    className="w-full p-2 rounded bg-dark-primary text-white border border-gray-600"
                  />
                  </div>
                </div>
                <div>
                  <label className="block text-gray-400 mb-1">О себе</label>
                  <textarea
                    name="about"
                    defaultValue={user.about}
                    onChange={handleInputChange}
                    className="w-full p-2 rounded bg-dark-primary text-white border border-gray-600"
                    rows={4}
                  />
                </div>
                <button
                  type="submit"
                  className="w-full px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
                  disabled={updateProfileMutation.isPending}
                >
                  {updateProfileMutation.isPending ? 'Сохранение...' : 'Сохранить'}
                </button>
              </form>
            ) : (
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
                    {user.is_premium && user.premium_until && (
                      <p className="text-gray-400 text-sm mt-1">
                        До {new Date(user.premium_until).toLocaleDateString()}
                      </p>
                    )}
                    </div>
                    <div>
                      <p className="text-gray-400">Баланс</p>
                      <p className="text-white">{user.money} монет</p>
                    </div>
                    <div>
                      <p className="text-gray-400">Дата регистрации</p>
                      <p className="text-white">
                        {new Date(user.created_at).toLocaleDateString('ru-RU')}
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-400">Титул</p>
                      <p className="text-white">{user.title}</p>
                    </div>
                    {!user.is_premium && (
                      <button
                        onClick={() => setShowPremiumModal(true)}
                        className="mt-2 px-4 py-2 bg-yellow-500 text-white rounded hover:bg-yellow-600 transition-colors"
                      >
                        Купить премиум
                      </button>
                    )}
                  </div>
                </div>
                  </div>
                )}

                {user.about && (
              <div className="mt-6">
                <h2 className="text-xl font-semibold text-white mb-4">О себе</h2>
                <p className="text-gray-300">{user.about}</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Модальное окно покупки премиум-подписки */}
      {showPremiumModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <PremiumPurchase onClose={() => setShowPremiumModal(false)} />
        </div>
      )}

      <input
        type="file"
        ref={avatarInputRef}
        className="hidden"
        accept="image/*"
        onChange={(e) => handleFileChange(e, 'photo')}
      />
      <input
        type="file"
        ref={headerInputRef}
        className="hidden"
        accept="image/*"
        onChange={(e) => handleFileChange(e, 'header_photo')}
      />
    </div>
  )
} 