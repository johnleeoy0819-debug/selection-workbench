import { useState, useEffect } from 'react'

function ProductPool() {
  const [products, setProducts] = useState<any[]>([])
  const [statusFilter, setStatusFilter] = useState('')
  const [sortBy, setSortBy] = useState('created_at')
  const [loading, setLoading] = useState(false)

  const fetchProducts = async () => {
    setLoading(true)
    try {
      let url = '/api/products'
      if (statusFilter) url += `?status=${statusFilter}`
      const res = await fetch(url)
      const data = await res.json()
      // 排序
      const sorted = [...data].sort((a: any, b: any) => {
        if (sortBy === 'created_at') return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        return 0
      })
      setProducts(sorted)
    } catch (err) {
      console.error('获取产品失败:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchProducts()
  }, [statusFilter, sortBy])

  const updateStatus = async (id: number, status: string) => {
    try {
      await fetch(`/api/products/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status })
      })
      fetchProducts()
    } catch (err) {
      console.error('更新状态失败:', err)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'confirmed': return 'high'
      case 'listed': return 'high'
      case 'observing': return 'medium'
      case 'abandoned': return 'low'
      default: return 'medium'
    }
  }

  const getStatusText = (status: string) => {
    const map: Record<string, string> = {
      'pending_analysis': '待分析',
      'analyzing': '分析中',
      'pending_decision': '待决策',
      'confirmed': '已确认',
      'listed': '已上架',
      'observing': '观察中',
      'abandoned': '已放弃',
      'archived': '已归档'
    }
    return map[status] || status
  }

  return (
    <div>
      {/* 筛选和排序 */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', gap: '16px', alignItems: 'center', flexWrap: 'wrap' }}>
          <div>
            <span style={{ fontSize: '12px', color: 'var(--text-faint)', marginRight: '8px' }}>状态筛选</span>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              style={{ padding: '6px 12px', border: '1px solid var(--border)', borderRadius: 'var(--radius)' }}
            >
              <option value="">全部</option>
              <option value="pending_analysis">待分析</option>
              <option value="pending_decision">待决策</option>
              <option value="confirmed">已确认</option>
              <option value="listed">已上架</option>
              <option value="observing">观察中</option>
              <option value="abandoned">已放弃</option>
            </select>
          </div>
          <div style={{ marginLeft: 'auto', fontSize: '14px', color: 'var(--text-muted)' }}>
            共 {products.length} 个产品
          </div>
        </div>
      </div>

      {/* 产品列表 */}
      <div className="card">
        <div className="card-label">选品池</div>
        {loading ? (
          <div style={{ textAlign: 'center', padding: '48px', color: 'var(--text-muted)' }}>加载中...</div>
        ) : products.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '48px', color: 'var(--text-muted)' }}>暂无产品</div>
        ) : (
          <div style={{ overflowX: 'auto', marginTop: '16px' }}>
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>名称</th>
                  <th>子类目</th>
                  <th>市场</th>
                  <th>状态</th>
                  <th>创建时间</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                {products.map((p: any) => (
                  <tr key={p.id}>
                    <td>{p.id}</td>
                    <td style={{ fontWeight: 500 }}>{p.name}</td>
                    <td><span className="tag">{p.subcategory}</span></td>
                    <td>{p.market_scope}</td>
                    <td><span className={`score-badge ${getStatusColor(p.status)}`}>{getStatusText(p.status)}</span></td>
                    <td style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{new Date(p.created_at).toLocaleDateString()}</td>
                    <td>
                      <select
                        value={p.status}
                        onChange={(e) => updateStatus(p.id, e.target.value)}
                        style={{ padding: '4px 8px', border: '1px solid var(--border)', borderRadius: 'var(--radius)', fontSize: '12px' }}
                      >
                        <option value="pending_analysis">待分析</option>
                        <option value="analyzing">分析中</option>
                        <option value="pending_decision">待决策</option>
                        <option value="confirmed">已确认</option>
                        <option value="listed">已上架</option>
                        <option value="observing">观察中</option>
                        <option value="abandoned">已放弃</option>
                        <option value="archived">已归档</option>
                      </select>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}

export default ProductPool