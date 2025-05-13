import { Outlet } from 'react-router-dom'
import Navbar from './Navbar'
import Footer from './Footer'
import { maxWidth } from '@/config/values'

export default function Layout() {
  return (
    <div className="min-h-screen bg-gray-100 dark:bg-black max">
      <Navbar />
      <main className="container mx-auto" style={{ maxWidth: maxWidth }}>
        <Outlet />
      </main>
      <Footer />
    </div>
  )
} 