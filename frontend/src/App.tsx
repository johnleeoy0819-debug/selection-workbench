import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import KeywordLab from './pages/KeywordLab'
import ProductValidator from './pages/ProductValidator'
import AIScoring from './pages/AIScoring'
import ProductPool from './pages/ProductPool'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<KeywordLab />} />
          <Route path="keywords" element={<KeywordLab />} />
          <Route path="validator" element={<ProductValidator />} />
          <Route path="scoring" element={<AIScoring />} />
          <Route path="pool" element={<ProductPool />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
