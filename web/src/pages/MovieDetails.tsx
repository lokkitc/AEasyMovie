import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/config/api'
import { useEffect, useRef, useState } from 'react'
import Player from '@vimeo/player'
import ReactPlayer from 'react-player'
import { auth } from '../config/api'
import { FaLock, FaCoins, FaCrown, FaStar } from 'react-icons/fa'
import { toast } from 'react-hot-toast'

interface Movie {
  movie_id: number
  title: string
  description: string
  release_date: string
  rating: number
  director: string
  genres: string[]
  poster: string
  backdrop: string
  movie_url: string
}

interface Episode {
  episode_id: number
  movie_id: number
  title: string
  episode_number: number
  cost: number
  created_at: string
  updated_at: string
  has_access: boolean
}

interface EpisodeDetail extends Episode {
  video_file: string
}

interface Comment {
  comment_id: number
  content: string
  user_id: number
  movie_id: number
  created_at: string
  rating: number
  user: {
    username: string
    photo: string
  }
}

export default function MovieDetails() {
  const { id } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const playerRef = useRef<YT.Player | null>(null)
  const vimeoPlayerRef = useRef<Player | null>(null)
  const [isYouTubeApiReady, setIsYouTubeApiReady] = useState(false)
  const [backdropType, setBackdropType] = useState<'image' | 'vimeo' | 'youtube' | 'dailymotion'>('image')
  const [selectedEpisode, setSelectedEpisode] = useState<Episode | null>(null)
  const [isWatching, setIsWatching] = useState(false)
  const [showPurchaseModal, setShowPurchaseModal] = useState(false)
  const [episodeToPurchase, setEpisodeToPurchase] = useState<Episode | null>(null)
  const [newComment, setNewComment] = useState('')
  const [rating, setRating] = useState(5)
  const [hoveredRating, setHoveredRating] = useState(0)

  const { data: movie, isLoading: movieLoading, error: movieError } = useQuery<Movie>({
    queryKey: ['movie', id],
    queryFn: async () => {
      try {
        const token = localStorage.getItem('token')
        if (!token) {
          navigate('/login')
          throw new Error('Требуется авторизация')
        }
        const response = await api.get(`/movies/${id}`)
        return response.data
      } catch (error: any) {
        if (error.response?.status === 401) {
          navigate('/login')
          throw new Error('Требуется авторизация')
        }
        if (error.response?.status === 403) {
          throw new Error('У вас нет доступа к этому фильму')
        }
        if (error.response?.status === 404) {
          throw new Error('Фильм не найден')
        }
        throw new Error('Ошибка при загрузке фильма')
      }
    },
  })

  const { data: episodes, isLoading: episodesLoading, error: episodesError } = useQuery<Episode[]>({
    queryKey: ['episodes', id],
    queryFn: async () => {
      try {
        const token = localStorage.getItem('token')
        if (!token) {
          navigate('/login')
          throw new Error('Требуется авторизация')
        }
        const response = await api.get(`/episodes/movie/${id}`)
        return response.data
      } catch (error: any) {
        if (error.response?.status === 401) {
          navigate('/login')
          throw new Error('Требуется авторизация')
        }
        throw new Error('Ошибка при загрузке эпизодов')
      }
    },
  })

  const { data: selectedEpisodeDetail, isLoading: selectedEpisodeLoading } = useQuery<EpisodeDetail>({
    queryKey: ['episode', selectedEpisode?.episode_id],
    queryFn: async () => {
      if (!selectedEpisode) return null
      try {
        const response = await api.get(`/episodes/${selectedEpisode.episode_id}`)
        console.log('Episode response:', response.data)
        return response.data
      } catch (error: any) {
        console.error('Error loading episode:', error)
        if (error.response?.status === 403) {
          toast.error('У вас нет доступа к этому эпизоду')
          setSelectedEpisode(null)
        }
        throw error
      }
    },
    enabled: !!selectedEpisode,
  })

  const { data: comments, isLoading: commentsLoading, error: commentsError } = useQuery<Comment[]>({
    queryKey: ['comments', id],
    queryFn: async () => {
      try {
        const token = localStorage.getItem('token')
        if (!token) {
          navigate('/login')
          throw new Error('Требуется авторизация')
        }
        const response = await api.get(`/comments/movie/${id}`)
        return response.data
      } catch (error: any) {
        if (error.response?.status === 401) {
          navigate('/login')
          throw new Error('Требуется авторизация')
        }
        throw new Error('Ошибка при загрузке комментариев')
      }
    },
  })

  const { data: user } = useQuery({
    queryKey: ['user'],
    queryFn: () => auth.getProfile(),
    retry: false
  });

  const purchaseMutation = useMutation({
    mutationFn: async (episodeId: number) => {
      const response = await api.post(`/episodes/${episodeId}/purchase`)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['episodes', id] })
      queryClient.invalidateQueries({ queryKey: ['user'] })
      toast.success('Эпизод успешно куплен!')
      setShowPurchaseModal(false)
      setEpisodeToPurchase(null)
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Ошибка при покупке эпизода')
    }
  })

  const createCommentMutation = useMutation({
    mutationFn: async () => {
      console.log('Отправка комментария:', {
        content: newComment,
        rating: rating,
        movie_id: Number(id),
        parent_comment_id: null
      })
      
      try {
        const response = await api.post('/comments', {
          content: newComment,
          rating: rating,
          movie_id: Number(id),
          parent_comment_id: null
        })
        console.log('Ответ сервера:', response.data)
        return response.data
      } catch (error: any) {
        console.error('Полная ошибка:', error)
        console.error('Детали ошибки:', {
          status: error.response?.status,
          data: error.response?.data,
          headers: error.response?.headers
        })
        throw error
      }
    },
    onSuccess: () => {
      console.log('Комментарий успешно добавлен')
      queryClient.invalidateQueries({ queryKey: ['comments', id] })
      setNewComment('')
      setRating(5)
      toast.success('Комментарий успешно добавлен')
    },
    onError: (error: any) => {
      console.error('Ошибка при создании комментария:', error)
      toast.error(error.response?.data?.detail || 'Ошибка при добавлении комментария')
    }
  })

  useEffect(() => {
    // Проверяем, не загружен ли уже API
    if (window.YT) {
      setIsYouTubeApiReady(true)
      return
    }

    // Загружаем YouTube Player API
    const tag = document.createElement('script')
    tag.src = 'https://www.youtube.com/iframe_api'
    const firstScriptTag = document.getElementsByTagName('script')[0]
    firstScriptTag.parentNode?.insertBefore(tag, firstScriptTag)

    // Инициализируем плеер, когда API готов
    window.onYouTubeIframeAPIReady = () => {
      setIsYouTubeApiReady(true)
    }

    return () => {
      if (playerRef.current) {
        playerRef.current.destroy()
      }
    }
  }, [])

  useEffect(() => {
    if (isYouTubeApiReady && movie?.movie_url) {
      const videoId = extractVideoId(movie.movie_url)
      if (videoId) {
        try {
          playerRef.current = new window.YT.Player('youtube-player', {
            height: '400',
            width: '100%',
            videoId: videoId,
            playerVars: {
              autoplay: 0,
              modestbranding: 1,
              rel: 0,
            },
            events: {
              onError: (event: any) => {
                console.error('YouTube Player Error:', event.data)
              }
            }
          })
        } catch (error) {
          console.error('Error initializing YouTube player:', error)
        }
      }
    }
  }, [isYouTubeApiReady, movie?.movie_url])

  useEffect(() => {
    if (movie?.backdrop) {
      if (movie.backdrop.includes('vimeo.com')) {
        setBackdropType('vimeo')
        const videoId = extractVimeoId(movie.backdrop)
        if (videoId) {
          const element = document.getElementById('vimeo-backdrop')
          if (element) {
            vimeoPlayerRef.current = new Player(element, {
              id: parseInt(videoId),
              background: true,
              responsive: true,
              dnt: true,
              autopause: false,
              autoplay: true,
              loop: true,
              muted: true,
              playsinline: true
            })
          }
        }
      } else if (movie.backdrop.includes('youtube.com') || movie.backdrop.includes('youtu.be')) {
        setBackdropType('youtube')
      } else if (movie.backdrop.includes('dailymotion.com')) {
        setBackdropType('dailymotion')
      } else {
        setBackdropType('image')
      }
    }

    return () => {
      if (vimeoPlayerRef.current) {
        vimeoPlayerRef.current.destroy()
      }
    }
  }, [movie?.backdrop])

  // Функция для извлечения ID видео из URL YouTube
  const extractVideoId = (url: string) => {
    try {
      const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/
      const match = url.match(regExp)
      return match && match[2].length === 11 ? match[2] : null
    } catch (error) {
      console.error('Error extracting video ID:', error)
      return null
    }
  }

  const extractVimeoId = (url: string) => {
    try {
      // Поддержка стандартного формата vimeo.com/ID
      let regExp = /vimeo\.com\/([0-9]+)/
      let match = url.match(regExp)

      if (!match) {
        // Поддержка формата player.vimeo.com/video/ID
        regExp = /player\.vimeo\.com\/video\/([0-9]+)/
        match = url.match(regExp)
      }

      if (match) {
        // Удаляем все параметры после ID
        const id = match[1].split(/[?#]/)[0]
        return id
      }

      return null
    } catch (error) {
      console.error('Error extracting Vimeo ID:', error)
      return null
    }
  }

  const extractDailymotionId = (url: string) => {
    try {
      const regExp = /dailymotion\.com\/video\/([a-zA-Z0-9]+)/
      const match = url.match(regExp)
      return match ? match[1] : null
    } catch (error) {
      console.error('Error extracting Dailymotion ID:', error)
      return null
    }
  }

    const handleEpisodeClick = (episode: Episode) => {
    if (episode.has_access || user?.is_premium) {
      setSelectedEpisode(episode)
            } else {
      toast.error('У вас нет доступа к этому эпизоду')
    }
  }

  const handleWatchClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    setIsWatching(true)
  }

  const handlePurchaseClick = (e: React.MouseEvent, episode: Episode) => {
    e.stopPropagation()
    setEpisodeToPurchase(episode)
    setShowPurchaseModal(true)
  }

  const handleConfirmPurchase = async () => {
    if (episodeToPurchase) {
      try {
        await purchaseMutation.mutateAsync(episodeToPurchase.episode_id)
      } catch (error) {
        console.error('Error purchasing episode:', error)
      }
    }
  }

  const handleSubmitComment = (e: React.FormEvent) => {
    e.preventDefault()
    if (!newComment.trim()) {
      toast.error('Комментарий не может быть пустым')
      return
    }
    createCommentMutation.mutate()
  }

  if (movieLoading || commentsLoading) {
    return <div className="text-center">Загрузка...</div>
  }

  if (movieError) {
    return <div className="text-center text-red-600">{movieError.message}</div>
  }

  if (!movie) {
    return <div className="text-center text-red-600">Фильм не найден</div>
  }

  return (
    <div className="mx-auto">
      <div className="bg-transparent dark:bg-dark-transparent rounded-lg shadow-md p-8">
        {movie.backdrop && (
          <div className="relative h-96 -mx-8 -mt-8 mb-8 overflow-hidden">
            {backdropType === 'vimeo' && (
              <div
                id="vimeo-backdrop"
                className="absolute inset-0 w-full h-full"
                style={{ minHeight: '384px' }}
              />
            )}
            {backdropType === 'youtube' && (
              <iframe
                src={`https://www.youtube-nocookie.com/embed/${extractVideoId(movie.backdrop)}?autoplay=1&mute=1&loop=1&playlist=${extractVideoId(movie.backdrop)}&controls=0&showinfo=0&rel=0&modestbranding=1&playsinline=1&background=1`}
                className="absolute inset-0 w-full h-full"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
                loading="lazy"
                referrerPolicy="no-referrer"
              />
            )}
            {backdropType === 'dailymotion' && (
              <iframe
                src={`https://www.dailymotion.com/embed/video/${extractDailymotionId(movie.backdrop)}?autoplay=1&mute=1&loop=1&controls=0&ui-logo=0&ui-start-screen-info=0&ui-end-screen-info=0&ui-highlight=0&ui-video-info=0`}
                className="absolute inset-0 w-full h-full"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
                loading="lazy"
                referrerPolicy="no-referrer"
              />
            )}
            {backdropType === 'image' && (
              <img
                src={movie.backdrop}
                alt={movie.title}
                className="w-full h-full object-cover rounded-t-lg"
              />
            )}
            <div className="absolute inset-0 bg-gradient-to-b from-black via-black/50 to-black" />
            <div className="absolute inset-0 bg-gradient-to-r from-black via-transparent to-black" />
          </div>
        )}
        <div className="flex gap-8 -mt-32 relative z-10">
          {movie.poster && (
            <img
              src={movie.poster}
              alt={movie.title}
              className="w-72 h-108 object-cover rounded-lg shadow-md"
            />
          )}
          <div className="flex-1">
            <h1 className="text-3xl font-bold mb-4 text-white">{movie.title}</h1>
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div>
                <p className="text-white">Год выпуска</p>
                <p className="font-semibold text-white">{new Date(movie.release_date).getFullYear()}</p>
              </div>
              <div>
                <p className="text-white">Режиссер</p>
                <p className="font-semibold text-white">{movie.director}</p>
              </div>
              <div>
                <p className="text-white">Жанры</p>
                <p className="font-semibold text-white">{movie.genres.join(', ')}</p>
              </div>
              <div>
                <p className="text-white">Рейтинг</p>
                <p className="font-semibold text-white">{movie.rating}</p>
              </div>
            </div>
            <p className="text-white whitespace-pre-line">{movie.description}</p>
          </div>
        </div>
        {movie.movie_url && (
          <div className="mt-4 max-w-72">
            <div className="relative aspect-video rounded-lg shadow-md overflow-hidden">
              <iframe
                src={`https://www.youtube-nocookie.com/embed/${extractVideoId(movie.movie_url)}?modestbranding=1&rel=0&origin=${window.location.origin}`}
                title={movie.title}
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
                className="absolute top-0 left-0 w-full h-full"
                loading="lazy"
                referrerPolicy="no-referrer"
              />
            </div>
          </div>
        )}
      </div>
          <div className="mt-8">
            <h2 className="text-2xl font-bold mb-6 text-white">Эпизоды</h2>
        {episodesLoading ? (
          <div className="text-center text-white">Загрузка эпизодов...</div>
        ) : episodesError ? (
          <div className="text-center text-red-600">Ошибка при загрузке эпизодов</div>
        ) : episodes?.length === 0 ? (
          <div className="text-center text-white">Эпизоды отсутствуют</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {episodes?.map((episode) => (
              <div
                key={episode.episode_id}
                className={`relative bg-dark-secondary rounded-lg p-4 cursor-pointer transition-transform hover:scale-105 ${
                  !episode.has_access && !user?.is_premium ? 'opacity-75' : ''
                }`}
                onClick={() => handleEpisodeClick(episode)}
              >
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-lg font-semibold text-white">Эпизод {episode.episode_number}</h3>
                  {!episode.has_access && !user?.is_premium && (
                    <div className="flex items-center gap-2">
                      <FaLock className="text-yellow-500" />
                      <span className="text-yellow-500">{episode.cost} монет</span>
                    </div>
                  )}
                  {user?.is_premium && (
                    <div className="flex items-center gap-2">
                      <FaCrown className="text-yellow-500" />
                      <span className="text-yellow-500">Премиум доступ</span>
          </div>
        )}
                </div>
                <p className="text-gray-300">{episode.title}</p>
                {!episode.has_access && !user?.is_premium && (
                  <div className="absolute inset-0 bg-black bg-opacity-50 rounded-lg flex items-center justify-center">
                    <button
                      className="px-4 py-2 bg-yellow-500 text-white rounded hover:bg-yellow-600 transition-colors"
                      onClick={(e) => handlePurchaseClick(e, episode)}
                      disabled={purchaseMutation.isPending}
                    >
                      {purchaseMutation.isPending ? 'Покупка...' : `Купить за ${episode.cost} монет`}
                    </button>
          </div>
        )}
              </div>
            ))}
          </div>
        )}
      </div>

      {selectedEpisode && selectedEpisodeDetail && (
        <div className="mt-8">
          <h3 className="text-xl font-bold mb-4 text-white">
            Эпизод {selectedEpisode.episode_number}: {selectedEpisode.title}
          </h3>
          <div className="aspect-video bg-black rounded-lg overflow-hidden">
            <video
              src={`http://127.0.0.1:8000${selectedEpisodeDetail.video_file}`}
              controls
              className="w-full h-full"
              onError={(e) => {
                console.error('Video error:', e)
                toast.error('Ошибка загрузки видео')
              }}
            />
          </div>
        </div>
      )}

      <div className="bg-dark-secondary rounded-lg shadow-md p-8 mt-8">
        <h2 className="text-2xl font-bold mb-6 text-white">Комментарии</h2>
        
        {/* Форма добавления комментария */}
        <form onSubmit={handleSubmitComment} className="mb-8">
          <div className="mb-4">
            <label className="block text-white mb-2">Ваша оценка</label>
            <div className="flex gap-1">
              {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((star) => (
                <button
                  key={star}
                  type="button"
                  className="text-2xl focus:outline-none"
                  onMouseEnter={() => setHoveredRating(star)}
                  onMouseLeave={() => setHoveredRating(0)}
                  onClick={() => setRating(star)}
                >
                  <FaStar
                    className={`${
                      star <= (hoveredRating || rating)
                        ? 'text-yellow-500'
                        : 'text-gray-400'
                    }`}
                  />
                </button>
              ))}
            </div>
          </div>
          <div className="mb-4">
            <label className="block text-white mb-2">Ваш комментарий</label>
            <textarea
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              className="w-full p-2 rounded bg-dark-primary text-white border border-gray-600 min-h-[100px]"
              placeholder="Напишите ваш комментарий..."
            />
          </div>
          <button
            type="submit"
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
            disabled={createCommentMutation.isPending}
          >
            {createCommentMutation.isPending ? 'Отправка...' : 'Отправить комментарий'}
          </button>
        </form>

        {commentsError ? (
          <div className="text-red-600">Ошибка при загрузке комментариев</div>
        ) : comments?.length === 0 ? (
          <p className="text-white">Пока нет комментариев</p>
        ) : (
          comments?.map((comment) => (
            <div key={comment.comment_id} className="border-b border-gray-700 pb-4 mb-4 last:border-b-0 last:pb-0 last:mb-0">
              <div className="flex justify-between items-center mb-2">
                <div className="flex items-center">
                  <img src={comment.user.photo} alt={comment.user.username} className="w-8 h-8 rounded-full mr-2" />
                  <span className="font-semibold text-white">{comment.user.username}</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="flex items-center">
                    {[...Array(10)].map((_, i) => (
                      <FaStar
                        key={i}
                        className={`text-sm ${
                          i < comment.rating ? 'text-yellow-500' : 'text-gray-400'
                        }`}
                      />
                    ))}
                  </div>
                  <span className="text-sm text-gray-400">
                  {new Date(comment.created_at).toLocaleDateString()}
                </span>
                </div>
              </div>
              <p className="text-white">{comment.content}</p>
            </div>
          ))
        )}
      </div>

      {/* Модальное окно подтверждения покупки */}
      {showPurchaseModal && episodeToPurchase && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-dark-secondary rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-xl font-bold text-white mb-4">Подтверждение покупки</h3>
            <div className="space-y-4">
              <p className="text-white">
                Вы собираетесь купить эпизод {episodeToPurchase.episode_number}: {episodeToPurchase.title}
              </p>
              {user?.is_premium && (
                <div className="bg-yellow-500 bg-opacity-20 p-4 rounded-lg">
                  <div className="flex items-center gap-2 text-yellow-500">
                    <FaCrown />
                    <span>У вас есть премиум-доступ! Вы можете смотреть этот эпизод бесплатно.</span>
                  </div>
                </div>
              )}
              <div className="flex items-center justify-between bg-dark-primary p-4 rounded-lg">
                <div className="flex items-center gap-2">
                  <FaCoins className="text-yellow-500" />
                  <span className="text-white">Ваш баланс:</span>
                </div>
                <span className="text-white font-semibold">{user?.money || 0} монет</span>
              </div>
              <div className="flex items-center justify-between bg-dark-primary p-4 rounded-lg">
                <div className="flex items-center gap-2">
                  <FaCoins className="text-yellow-500" />
                  <span className="text-white">Стоимость:</span>
                </div>
                <span className="text-white font-semibold">{episodeToPurchase.cost} монет</span>
              </div>
              <div className="flex items-center justify-between bg-dark-primary p-4 rounded-lg">
                <div className="flex items-center gap-2">
                  <FaCoins className="text-yellow-500" />
                  <span className="text-white">Останется после покупки:</span>
                </div>
                <span className="text-white font-semibold">
                  {((user?.money || 0) - episodeToPurchase.cost).toFixed(1)} монет
                </span>
              </div>
              <div className="flex gap-4 mt-6">
                <button
                  className="flex-1 px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors"
                  onClick={() => {
                    setShowPurchaseModal(false)
                    setEpisodeToPurchase(null)
                  }}
                >
                  Отмена
                </button>
                <button
                  className="flex-1 px-4 py-2 bg-yellow-500 text-white rounded hover:bg-yellow-600 transition-colors"
                  onClick={handleConfirmPurchase}
                  disabled={purchaseMutation.isPending || (user?.money || 0) < episodeToPurchase.cost}
                >
                  {purchaseMutation.isPending ? 'Покупка...' : 'Подтвердить покупку'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
} 