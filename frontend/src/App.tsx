import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import LiuyaoPage from './pages/LiuyaoPage'
import DivinationPage from './pages/DivinationPage'
import AboutPage from './pages/AboutPage'
import HistoryPage from './pages/HistoryPage'
import './App.css'

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/liuyao" element={<LiuyaoPage />} />
          <Route path="/divination" element={<DivinationPage />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/about" element={<AboutPage />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App
