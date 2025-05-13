import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { auth } from '@/config/api'

export default function Login() {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  })
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    try {
      const response = await auth.login(formData.email, formData.password)
      if (response && response.access_token) {
        localStorage.setItem('token', response.access_token)
        navigate('/')
      } else {
        setError('Ошибка при получении токена')
      }
    } catch (err: any) {
      console.error(err)
      setError(err.message || 'Произошла ошибка при входе')
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
      <h1 className="text-3xl font-bold mb-8 text-center text-white">Вход</h1>
      {error && <div className="bg-red-100 text-red-600 p-3 rounded mb-4">{error}</div>}
      <form onSubmit={handleSubmit} className="space-y-6">
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
            placeholder="Введите ваш пароль"
          />
        </div>
        <button
          type="submit"
          className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all duration-200 font-medium"
        >
          Войти
        </button>
      </form>
      <p className="mt-4 text-center text-sm text-white">
        Нет аккаунта?{' '}
        <Link to="/register" className="text-blue-600 hover:text-blue-500">
          Зарегистрироваться
        </Link>
      </p>
    </div>
  )
} 