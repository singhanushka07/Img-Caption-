import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Navbar from '@/components/layout/Navbar'
import HomePage from '@/pages/HomePage'
import CaptionStudioPage from '@/pages/CaptionStudioPage'
import VisualQAPage from '@/pages/VisualQAPage'
import AnalyticsPage from '@/pages/AnalyticsPage'
import AboutPage from '@/pages/AboutPage'

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-[#f8fafc] font-sans text-[#0f172a]">
        <Navbar />
        <main className="max-w-[1320px] mx-auto px-8 py-8">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/caption" element={<CaptionStudioPage />} />
            <Route path="/vqa" element={<VisualQAPage />} />
            <Route path="/analytics" element={<AnalyticsPage />} />
            <Route path="/about" element={<AboutPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
