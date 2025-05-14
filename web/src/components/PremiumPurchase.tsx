import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'react-hot-toast'
import { FaCrown, FaCoins } from 'react-icons/fa'
import { api } from '@/config/api'

interface PremiumPurchaseProps {
  onClose: () => void
}

export default function PremiumPurchase({ onClose }: PremiumPurchaseProps) {
  const [months, setMonths] = useState(1)
  const queryClient = useQueryClient()

  const purchaseMutation = useMutation({
    mutationFn: async (data: { months: number; payment_method: string }) => {
      const response = await api.post('/premium/purchase', data)
      return response.data
    },
    onSuccess: (data) => {
      toast.success(data.message)
      queryClient.invalidateQueries({ queryKey: ['user'] })
      onClose()
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Ошибка при покупке премиум-подписки')
    }
  })

  const handlePurchase = () => {
    purchaseMutation.mutate({
      months,
      payment_method: 'card' // В будущем можно добавить выбор метода оплаты
    })
  }

  const prices = {
    RUB: 299,
    USD: 4.99,
    EUR: 4.49
  }

  return (
    <div className="bg-dark-secondary rounded-lg p-6 max-w-md w-full mx-4">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-bold text-white">Покупка премиум-подписки</h3>
        <FaCrown className="text-yellow-500 text-2xl" />
      </div>

      <div className="space-y-4">
        <div className="bg-dark-primary p-4 rounded-lg">
          <label className="block text-white mb-2">Выберите срок подписки</label>
          <select
            value={months}
            onChange={(e) => setMonths(Number(e.target.value))}
            className="w-full bg-dark-secondary text-white rounded p-2 border border-gray-600"
          >
            <option value={1}>1 месяц</option>
            <option value={3}>3 месяца</option>
            <option value={6}>6 месяцев</option>
            <option value={12}>12 месяцев</option>
          </select>
        </div>

        <div className="bg-dark-primary p-4 rounded-lg">
          <h4 className="text-white mb-2">Стоимость</h4>
          <div className="space-y-2">
            <div className="flex justify-between text-white">
              <span>1 месяц:</span>
              <span>{prices.RUB} ₽</span>
            </div>
            <div className="flex justify-between text-white">
              <span>Итого за {months} месяцев:</span>
              <span>{prices.RUB * months} ₽</span>
            </div>
          </div>
        </div>

        <div className="bg-yellow-500 bg-opacity-20 p-4 rounded-lg">
          <div className="flex items-center gap-2 text-yellow-500">
            <FaCrown />
            <span>Премиум-подписка включает:</span>
          </div>
          <ul className="text-gray-300 mt-2 space-y-1">
            <li>• Доступ ко всем эпизодам</li>
            <li>• Отсутствие рекламы</li>
            <li>• Приоритетная поддержка</li>
            <li>• Эксклюзивный контент</li>
          </ul>
        </div>

        <button
          onClick={handlePurchase}
          disabled={purchaseMutation.isPending}
          className="w-full px-4 py-2 bg-yellow-500 text-white rounded hover:bg-yellow-600 transition-colors disabled:opacity-50"
        >
          {purchaseMutation.isPending ? 'Обработка...' : 'Купить премиум'}
        </button>
      </div>
    </div>
  )
} 