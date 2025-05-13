import axios from 'axios'
import { jwtDecode } from 'jwt-decode'

export const API_BASE_URL = 'http://127.0.0.1:8000/api';

export const API_ENDPOINTS = {
  USERS: '/users',
} as const;

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true
})

interface JwtPayload {
  sub: string;  // email
  exp: number;
}

// Добавляем интерсептор для добавления токена к запросам
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Добавляем интерсептор для обработки ошибок
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      switch (error.response.status) {
        case 401:
          localStorage.removeItem('token')
          window.dispatchEvent(new CustomEvent('tokenExpired'))
          break
        case 403:
          throw new Error('Доступ запрещен')
        case 429:
          throw new Error('Слишком много запросов. Пожалуйста, подождите')
        case 500:
          throw new Error('Внутренняя ошибка сервера')
        default:
          throw new Error(error.response.data?.detail || 'Произошла ошибка')
      }
    } else if (error.request) {
      throw new Error('Нет ответа от сервера')
    } else {
      throw new Error('Ошибка при выполнении запроса')
    }
    return Promise.reject(error)
  }
)

export const auth = {
  login: async (email: string, password: string) => {
    try {
      const formData = new URLSearchParams()
      formData.append('username', email)
      formData.append('password', password)
      
      const response = await api.post('/auth/token', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Accept': 'application/json',
        },
        withCredentials: true
      })
      
      if (!response.data || !response.data.access_token) {
        throw new Error('Токен не получен')
      }
      
      return response.data
    } catch (error: any) {
      if (error.response?.status === 429) {
        throw new Error('Слишком много попыток входа. Пожалуйста, подождите.')
      }
      if (error.response?.status === 403) {
        throw new Error('Аккаунт заблокирован')
      }
      if (error.response?.status === 401) {
        throw new Error('Неверный email или пароль')
      }
      throw new Error(error.response?.data?.detail || 'Ошибка при входе в систему')
    }
  },
  
  loginWithGoogle: async () => {
    try {
      // Открываем окно авторизации Google
      const width = 500
      const height = 600
      const left = window.screenX + (window.outerWidth - width) / 2
      const top = window.screenY + (window.outerHeight - height) / 2
      
      const authWindow = window.open(
        'http://127.0.0.1:8000/api/auth/google/login',
        'Google Auth',
        `width=${width},height=${height},left=${left},top=${top}`
      )

      // Ждем ответа от окна авторизации
      return new Promise((resolve, reject) => {
        const checkWindow = setInterval(() => {
          if (authWindow?.closed) {
            clearInterval(checkWindow)
            reject(new Error('Окно авторизации было закрыто'))
          }
        }, 1000)

        window.addEventListener('message', async (event) => {
          if (event.origin === 'http://127.0.0.1:8000') {
            clearInterval(checkWindow)
            if (authWindow) {
              authWindow.close()
            }
            
            if (event.data.error) {
              reject(new Error(event.data.error))
            } else if (event.data.access_token) {
              resolve(event.data)
            }
          }
        })
      })
    } catch (error: any) {
      throw new Error(error.message || 'Ошибка при входе через Google')
    }
  },
  
  register: (name: string, surname: string, username: string, email: string, password: string) =>
    api.post('/users/', { name, surname, username, email, password }),
  
  getProfile: async () => {
    const token = localStorage.getItem('token')
    if (!token) {
      throw new Error('Токен не найден')
    }
    
    try {
      const decoded = jwtDecode<JwtPayload>(token)
      if (decoded.exp * 1000 < Date.now()) {
        localStorage.removeItem('token')
        throw new Error('Токен истек')
      }
      
      const response = await api.get('/users/me')
      return response.data
    } catch (error) {
      if (error instanceof Error) {
        throw error
      }
      throw new Error('Не удалось получить профиль пользователя')
    }
  },
  
  logout: () => {
    localStorage.removeItem('token')
    window.location.href = '/login'
  }
} 

export const users = {
  getUsers: async () => {
    const response = await api.get('/users/')
    return response.data
  }
}