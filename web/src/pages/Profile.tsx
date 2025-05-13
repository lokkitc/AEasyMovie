import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { auth, api } from '@/config/api'
import { useState, useRef } from 'react'
import { toast } from 'react-hot-toast'
import { User } from '@/types'

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
    return <div className="text-center">Загрузка...</div>
  }

  if (userError) {
    if (userError instanceof Error && userError.message === 'Токен не найден') {
      window.location.href = '/login'
      return null
    }
    return <div className="text-center text-red-600">Ошибка загрузки профиля: {userError instanceof Error ? userError.message : 'Неизвестная ошибка'}</div>
  }

  if (!user) {
    return <div className="text-center text-red-600">Ошибка загрузки профиля</div>
  }

  return (
    <div className="mx-auto">
      <div className="bg-transparent rounded-lg shadow-md p-8 mb-8">
        {user.header_photo && (
          <div className="relative h-48 -mx-8 -mt-8 mb-8 group">
            <img
              src={user.header_photo}
              alt="Header"
              className="w-full h-full object-cover rounded-t-lg"
            />
            <div 
              className="absolute inset-0 bg-black bg-opacity-50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center cursor-pointer"
              onClick={handleHeaderClick}
            >
              <span className="text-white pointer-events-none">Изменить заголовок</span>
            </div>
            <input
              type="file"
              ref={headerInputRef}
              className="hidden"
              accept="image/*"
              onChange={(e) => handleFileChange(e, 'header_photo')}
            />
          </div>
        )}
        <div className="flex items-start gap-8">
          {user.photo && (
            <div className="relative group">
            <img
              src={user.photo}
              alt={user.username}
                className="w-32 h-32 rounded-full object-cover border-4 border-white shadow-md cursor-pointer"
                onClick={handleAvatarClick}
              />
              <div 
                className="absolute inset-0 bg-black bg-opacity-50 opacity-0 group-hover:opacity-100 transition-opacity rounded-full flex items-center justify-center cursor-pointer"
                onClick={handleAvatarClick}
              >
                <span className="text-white text-sm pointer-events-none">Изменить фото</span>
              </div>
              <input
                type="file"
                ref={avatarInputRef}
                className="hidden"
                accept="image/*"
                onChange={(e) => handleFileChange(e, 'photo')}
              />
            </div>
          )}
          <div className="flex-1">
            <div className="flex justify-between items-center mb-4">
              <h1 className="text-3xl font-bold text-white">{user.name} {user.surname}</h1>
              <button
                onClick={() => setIsEditing(!isEditing)}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
              >
                {isEditing ? 'Отмена' : 'Редактировать'}
              </button>
            </div>

            {isEditing ? (
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-white mb-1">Имя</label>
                  <input
                    type="text"
                    name="name"
                    defaultValue={user.name}
                    onChange={handleInputChange}
                    className="w-full p-2 rounded bg-dark-primary text-white border border-gray-600"
                  />
                </div>
                <div>
                  <label className="block text-white mb-1">Фамилия</label>
                  <input
                    type="text"
                    name="surname"
                    defaultValue={user.surname}
                    onChange={handleInputChange}
                    className="w-full p-2 rounded bg-dark-primary text-white border border-gray-600"
                  />
                </div>
                <div>
                  <label className="block text-white mb-1">Имя пользователя</label>
                  <input
                    type="text"
                    name="username"
                    defaultValue={user.username}
                    onChange={handleInputChange}
                    className="w-full p-2 rounded bg-dark-primary text-white border border-gray-600"
                  />
                </div>
                <div>
                  <label className="block text-white mb-1">Email</label>
                  <input
                    type="email"
                    name="email"
                    defaultValue={user.email}
                    onChange={handleInputChange}
                    className="w-full p-2 rounded bg-dark-primary text-white border border-gray-600"
                  />
                </div>
                <div>
                  <label className="block text-white mb-1">Местоположение</label>
                  <input
                    type="text"
                    name="location"
                    defaultValue={user.location}
                    onChange={handleInputChange}
                    className="w-full p-2 rounded bg-dark-primary text-white border border-gray-600"
                  />
                </div>
                <div>
                  <label className="block text-white mb-1">Возраст</label>
                  <input
                    type="number"
                    name="age"
                    defaultValue={user.age}
                    onChange={handleInputChange}
                    className="w-full p-2 rounded bg-dark-primary text-white border border-gray-600"
                  />
                </div>
                <div>
                  <label className="block text-white mb-1">О себе</label>
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
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4 mb-6">
                  <div className="bg-dark-secondary p-4 rounded-lg">
                    <p className="text-white mb-2">Премиум статус</p>
                    <div className="flex items-center gap-2">
                      <span className={`w-3 h-3 rounded-full ${user.is_premium ? 'bg-green-500' : 'bg-red-500'}`}></span>
                      <p className="text-xl font-semibold text-white">
                        {user.is_premium ? 'Активен' : 'Неактивен'}
                      </p>
                    </div>
                    {user.is_premium && user.premium_until && (
                      <p className="text-gray-400 text-sm mt-1">
                        До {new Date(user.premium_until).toLocaleDateString()}
                      </p>
                    )}
                  </div>
                  
                  <div className="bg-dark-secondary p-4 rounded-lg">
                    <p className="text-white mb-2">Баланс</p>
                    <p className="text-xl font-semibold text-white">{user.money} монет</p>
                  </div>
                  
                  <div className="bg-dark-secondary p-4 rounded-lg">
                    <p className="text-white mb-2">Уровень</p>
                    <p className="text-xl font-semibold text-white">{user.level}</p>
                  </div>
                  
                  <div className="bg-dark-secondary p-4 rounded-lg">
                    <p className="text-white mb-2">Титул</p>
                    <p className="text-xl font-semibold text-white">{user.title}</p>
                  </div>
                </div>

                <div>
                  <p className="text-white">Имя пользователя</p>
                  <p className="text-xl font-semibold text-white">{user.username}</p>
                </div>
                <div>
                  <p className="text-white">Email</p>
                  <p className="text-xl font-semibold text-white">{user.email}</p>
                </div>
                {user.location && (
                  <div>
                    <p className="text-white">Местоположение</p>
                    <p className="text-xl font-semibold text-white">{user.location}</p>
                  </div>
                )}
                {user.age && (
                  <div>
                    <p className="text-white">Возраст</p>
                    <p className="text-xl font-semibold text-white">{user.age}</p>
                  </div>
                )}
                {user.about && (
                  <div>
                    <p className="text-white">О себе</p>
                    <p className="text-xl font-semibold text-white">{user.about}</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
} 