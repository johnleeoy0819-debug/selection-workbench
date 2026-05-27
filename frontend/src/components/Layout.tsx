import React from 'react'
import { Outlet, Link, useLocation } from 'react-router-dom'

function Layout() {
  const location = useLocation()
  
  const navItems = [
    { path: '/keywords', label: '关键词工作台' },
    { path: '/validator', label: '单品验证台' },
    { path: '/scoring', label: 'AI 评分台' },
    { path: '/pool', label: '选品池' },
  ]
  
  return (
    <div className="container">
      <div className="header">
        <div className="header-left">
          <h1>Maple Hollow Home</h1>
          <div className="subtitle">Etsy 选品决策工作台</div>
        </div>
        <div className="header-right">
          <div style={{ fontSize: '12px', color: 'var(--text-faint)' }}>v1.0</div>
        </div>
      </div>
      
      <nav style={{ 
        display: 'flex', 
        gap: '8px', 
        marginBottom: '32px',
        borderBottom: '1px solid var(--border)',
        paddingBottom: '16px'
      }}>
        {navItems.map(item => (
          <Link
            key={item.path}
            to={item.path}
            style={{
              padding: '8px 16px',
              textDecoration: 'none',
              color: location.pathname === item.path ? '#fff' : 'var(--text)',
              background: location.pathname === item.path ? 'var(--accent)' : 'transparent',
              borderRadius: 'var(--radius)',
              fontSize: '14px',
              fontWeight: 500,
              transition: 'all 0.15s'
            }}
          >
            {item.label}
          </Link>
        ))}
      </nav>
      
      <Outlet />
    </div>
  )
}

export default Layout
