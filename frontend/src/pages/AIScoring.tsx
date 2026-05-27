import { useState, useEffect } from 'react'

function AIScoring() {
  const [products, setProducts] = useState<any[]>([])
  const [selectedProduct, setSelectedProduct] = useState<any>(null)
  const [scores, setScores] = useState({
    demand_score: 5,
    profit_score: 5,
    competition_score: 5,
    seasonal_score: 5
  })
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetch('/api/products')
      .then(res => res.json())
      .then(data => setProducts(data))
  }, [])

  const handleScore = async () => {
    if (!selectedProduct) return
    setLoading(true)
    try {
      const res = await fetch(`/api/scoring/${selectedProduct.id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(scores)
      })
      const data = await res.json()
      setResult(data)
    } catch (err) {
      console.error('评分失败:', err)
    } finally {
      setLoading(false)
    }
  }

  const getDecisionColor = (decision: string) => {
    switch (decision) {
      case 'execute': return 'var(--green)'
      case 'observe': return 'var(--amber)'
      case 'abandon': return 'var(--red)'
      default: return 'var(--text)'
    }
  }

  const getDecisionText = (decision: string) => {
    switch (decision) {
      case 'execute': return '立即执行'
      case 'observe': return '观察测试'
      case 'abandon': return '放弃'
      default: return decision
    }
  }

  return (
    <div>
      {/* 产品选择 */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div className="card-label">选择产品</div>
        <select
          value={selectedProduct?.id || ''}
          onChange={(e) => {
            const product = products.find((p: any) => p.id === parseInt(e.target.value))
            setSelectedProduct(product || null)
            setResult(null)
          }}
          style={{ width: '100%', padding: '8px 12px', border: '1px solid var(--border)', borderRadius: 'var(--radius)', marginTop: '12px' }}
        >
          <option value="">选择要评分的产品</option>
          {products.map((p: any) => (
            <option key={p.id} value={p.id}>{p.name}</option>
          ))}
        </select>
      </div>

      {/* 五维评分 */}
      {selectedProduct && (
        <div className="card" style={{ marginBottom: '24px' }}>
          <div className="card-label">五维评分 (1-10)</div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginTop: '16px' }}>
            {[
              { key: 'demand_score', label: '需求评分', weight: '35%', desc: '搜索量、趋势' },
              { key: 'profit_score', label: '利润评分', weight: '30%', desc: '毛利率、净利' },
              { key: 'competition_score', label: '竞争评分', weight: '25%', desc: '竞品数量、差异化' },
              { key: 'seasonal_score', label: '节日评分', weight: '10%', desc: '季节性需求' }
            ].map((item: any) => (
              <div key={item.key} style={{ padding: '16px', border: '1px solid var(--border)', borderRadius: 'var(--radius)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontWeight: 600 }}>{item.label}</span>
                  <span style={{ fontSize: '12px', color: 'var(--text-faint)' }}>权重 {item.weight}</span>
                </div>
                <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>{item.desc}</div>
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={(scores as any)[item.key]}
                  onChange={(e) => setScores({ ...scores, [item.key]: parseInt(e.target.value) })}
                  style={{ width: '100%', marginTop: '12px' }}
                />
                <div style={{ textAlign: 'center', fontSize: '24px', fontWeight: 700, marginTop: '8px' }}>
                  {(scores as any)[item.key]}
                </div>
              </div>
            ))}
          </div>
          <button
            className="btn btn-primary"
            style={{ marginTop: '16px', width: '100%' }}
            onClick={handleScore}
            disabled={loading}
          >
            {loading ? '评分中...' : '开始评分'}
          </button>
        </div>
      )}

      {/* 评分结果 */}
      {result && (
        <div className="card" style={{ marginBottom: '24px' }}>
          <div className="card-label">评分结果</div>
          <div style={{ textAlign: 'center', padding: '32px', border: '1px solid var(--border)', borderRadius: 'var(--radius)', marginTop: '16px' }}>
            <div style={{ fontSize: '56px', fontWeight: 700, color: getDecisionColor(result.decision) }}>
              {result.composite_score}
            </div>
            <div style={{ fontSize: '14px', color: 'var(--text-muted)', marginTop: '8px' }}>综合评分</div>
            <div style={{
              display: 'inline-block',
              marginTop: '16px',
              padding: '8px 24px',
              background: getDecisionColor(result.decision) + '20',
              color: getDecisionColor(result.decision),
              borderRadius: 'var(--radius)',
              fontWeight: 600,
              fontSize: '18px'
            }}>
              {getDecisionText(result.decision)}
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-faint)', marginTop: '8px' }}>
              置信度: {result.confidence === 'high' ? '高' : result.confidence === 'medium' ? '中' : '低'}
            </div>
          </div>

          {/* 评分明细 */}
          <div style={{ marginTop: '24px' }}>
            <div className="card-label">评分明细</div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginTop: '12px' }}>
              {Object.entries(result.breakdown).map(([key, value]: [string, any]) => (
                <div key={key} style={{ padding: '12px', border: '1px solid var(--border)', borderRadius: 'var(--radius)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ fontSize: '14px', textTransform: 'capitalize' }}>
                      {key === 'demand' ? '需求' : key === 'profit' ? '利润' : key === 'competition' ? '竞争' : '节日'}
                    </span>
                    <span style={{ fontWeight: 600 }}>{value.score}/10</span>
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--text-faint)', marginTop: '4px' }}>
                    权重 {value.weight} · 加权 {value.weighted_score}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default AIScoring