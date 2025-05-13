import { maxWidth } from '@/config/values'

export default function Footer() {
  return (
    <footer className="bg-white dark:bg-dark-secondary shadow-lg mt-8">
      <div className="container mx-auto px-4 py-6" style={{ maxWidth: maxWidth }}>
        <div className="text-center text-gray-600 dark:text-gray-300">
          <p>&copy; 2024 NubeMovie. Все права защищены.</p>
        </div>
      </div>
    </footer>
  )
} 