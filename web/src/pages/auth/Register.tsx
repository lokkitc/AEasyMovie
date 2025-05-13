import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { auth } from '@/config/api'
import { FcGoogle } from 'react-icons/fc'

export default function Register() {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    name: '',
    surname: '',
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
  })
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (formData.password !== formData.confirmPassword) {
      setError('Пароли не совпадают')
      return
    }

    // Проверка на наличие только букв в имени и фамилии
    const letterOnly = /^[a-zA-Zа-яА-Я]+$/
    if (!letterOnly.test(formData.name) || !letterOnly.test(formData.surname)) {
      setError('Имя и фамилия должны содержать только буквы')
      return
    }

    try {
      await auth.register(formData.name, formData.surname, formData.username, formData.email, formData.password)
      navigate('/login')
    } catch (err: any) {
      setError(err.message || 'Ошибка при регистрации')
    }
  }

  const handleGoogleLogin = async () => {
    try {
      const response = await auth.loginWithGoogle()
      if (response && response.access_token) {
        localStorage.setItem('token', response.access_token)
        navigate('/')
      }
    } catch (err: any) {
      setError(err.message || 'Ошибка при входе через Google')
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
  }

  return (
    <div className="max-w-md mx-auto">
      <h1 className="text-3xl font-bold mb-8 text-center text-white">Регистрация</h1>
      {error && <div className="bg-red-100 text-red-600 p-3 rounded mb-4">{error}</div>}
      
      <button
        onClick={handleGoogleLogin}
        className="w-full flex items-center justify-center gap-2 bg-white text-gray-700 py-3 px-4 rounded-lg hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-all duration-200 font-medium mb-6"
      >
        <FcGoogle className="text-xl" />
        Продолжить с Google
      </button>

      <div className="relative mb-6">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-gray-600"></div>
        </div>
        <div className="relative flex justify-center text-sm">
          <span className="px-2 bg-dark-primary text-gray-400">или</span>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-white">
            Имя
          </label>
          <input
            type="text"
            id="name"
            name="name"
            value={formData.name}
            onChange={handleChange}
            required
            className="mt-1 block w-full px-4 py-3 rounded-lg bg-dark-primary text-white border border-gray-600 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 focus:outline-none transition-all duration-200 placeholder-gray-400"
            placeholder="Введите ваше имя"
          />
        </div>
        <div>
          <label htmlFor="surname" className="block text-sm font-medium text-white">
            Фамилия
          </label>
          <input
            type="text"
            id="surname"
            name="surname"
            value={formData.surname}
            onChange={handleChange}
            required
            className="mt-1 block w-full px-4 py-3 rounded-lg bg-dark-primary text-white border border-gray-600 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 focus:outline-none transition-all duration-200 placeholder-gray-400"
            placeholder="Введите вашу фамилию"
          />
        </div>
        <div>
          <label htmlFor="username" className="block text-sm font-medium text-white">
            Имя пользователя
          </label>
          <input
            type="text"
            id="username"
            name="username"
            value={formData.username}
            onChange={handleChange}
            required
            className="mt-1 block w-full px-4 py-3 rounded-lg bg-dark-primary text-white border border-gray-600 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 focus:outline-none transition-all duration-200 placeholder-gray-400"
            placeholder="Введите имя пользователя"
          />
        </div>
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-white">
            Email
          </label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            required
            className="mt-1 block w-full px-4 py-3 rounded-lg bg-dark-primary text-white border border-gray-600 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 focus:outline-none transition-all duration-200 placeholder-gray-400"
            placeholder="Введите ваш email"
          />
        </div>
        <div>
          <label htmlFor="password" className="block text-sm font-medium text-white">
            Пароль
          </label>
          <input
            type="password"
            id="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            required
            className="mt-1 block w-full px-4 py-3 rounded-lg bg-dark-primary text-white border border-gray-600 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 focus:outline-none transition-all duration-200 placeholder-gray-400"
            placeholder="Введите пароль"
          />
        </div>
        <div>
          <label htmlFor="confirmPassword" className="block text-sm font-medium text-white">
            Подтвердите пароль
          </label>
          <input
            type="password"
            id="confirmPassword"
            name="confirmPassword"
            value={formData.confirmPassword}
            onChange={handleChange}
            required
            className="mt-1 block w-full px-4 py-3 rounded-lg bg-dark-primary text-white border border-gray-600 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 focus:outline-none transition-all duration-200 placeholder-gray-400"
            placeholder="Подтвердите пароль"
          />
        </div>
        <button
          type="submit"
          className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all duration-200 font-medium"
        >
          Зарегистрироваться
        </button>
      </form>
      <p className="mt-4 text-center text-sm text-white">
        Уже есть аккаунт?{' '}
        <Link to="/login" className="text-blue-600 hover:text-blue-500">
          Войти
        </Link>
      </p>
    </div>
  )
} 