import React from 'react'
import ReactDOM from 'react-dom/client'
import './index.css'

import App from './App'
import Sistema from './Sistema'

// ⭐ Importante: añadimos React Router
import { BrowserRouter, Routes, Route } from "react-router-dom";

ReactDOM.createRoot(document.getElementById('root')!).render(
  <BrowserRouter>
    <Routes>
      {/* Página principal */}
      <Route path="/" element={<App />} />

      {/* Nueva página para Información del Sistema */}
      <Route path="/sistema" element={<Sistema />} />
    </Routes>
  </BrowserRouter>
)

