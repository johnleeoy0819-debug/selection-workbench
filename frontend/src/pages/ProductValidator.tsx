import { useState, useEffect } from 'react'

function ProductValidator() {
  const [form, setForm] = useState({
    name: '',
    keyword_id: '',
    subcategory: 'hook',
    market_scope: 'us',
    unit_cost_cny: '',
    shipping_cny: '',
    custom_cny: '0',
    packaging_usd: '0.8',
    listing_price: '',
    annual_revenue: '0'
  })
  const [pricing, setPricing] = useState<any>(null)
  const [calculating, setCalculating] = useState(false)
  const [products, setProducts] = useState<any[]>([])

  const fetchProducts = async () => {
    try {
      const res = await fetch('/api/products')
      const data = await res.json()
      setProducts(data)
    } catch (err) {
      console.error('获取产品失败:', err)
    }
  }

  useEffect(() => {
    fetchProducts()
  }, [])

  const calculatePricing = async () => {
    if (!form.unit_cost_cny || !form.shipping_cny || !form.listing_price) return
    setCalculating(true)
    try {
      const res = await fetch('/api/pricing/calculate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          unit_cost_cny: parseFloat(form.unit_cost_cny),
          shipping_cny: parseFloat(form.shipping_cny),
          custom_cny: parseFloat(form.custom_cny || '0'),
          packaging_usd: parseFloat(form.packaging_usd || '0.8'),
          listing_price: parseFloat(form.listing_price),
          annual_revenue: parseFloat(form.annual_revenue || '0')
        })
      })
      const data = await res.json()
      setPricing(data)
    } catch (err) {
      console.error('计算失败:', err)
    } finally {
      setCalculating(false)
    }
  }

  const createProduct = async () => {
    try {
      const res = await fetch('/api/products', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: form.name,
          keyword_id: form.keyword_id ? parseInt(form.keyword_id) : null,
          subcategory: form.subcategory,
          market_scope: form.market_scope,
          source_type: 'manual'
        })
      })
      if (res.ok) {
        setForm({ ...form, name: '' })
        fetchProducts()
      }
    } catch (err) {
      console.error('创建产品失败:', err)
    }
  }

  const handleChange = (field: string, value: string) => {
    setForm(prev => ({ ...prev, [field]: value }))
  }

  return (
    <div>
      {/* 产品表单 */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div className="card-label">产品信息</div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginTop: '16px' }}>
          <div>
            <label style={{ fontSize: '12px', color: 'var(--text-faint)', textTransform: 'uppercase' }}>产品名称</label>
            <input
              type="text"
              value={form.name}
              onChange={(e) => handleChange('name', e.target.value)}
              style={{ width: '100%', padding: '8px 12px', border: '1px solid var(--border)', borderRadius: 'var(--radius)', marginTop: '4px' }}
              placeholder="输入产品名称"
            />
          </div>
          <div>
            <label style={{ fontSize: '12px', color: 'var(--text-faint)', textTransform: 'uppercase' }}>关键词ID</label>
            <input
              type="text"
              value={form.keyword_id}
              onChange={(e) => handleChange('keyword_id', e.target.value)}
              style={{ width: '100%', padding: '8px 12px', border: '1px solid var(--border)', borderRadius: 'var(--radius)', marginTop: '4px' }}
              placeholder="关联关键词ID"
            />
          </div>
          <div>
            <label style={{ fontSize: '12px', color: 'var(--text-faint)', textTransform: 'uppercase' }}>子类目</label>
            <select
              value={form.subcategory}
              onChange={(e) => handleChange('subcategory', e.target.value)}
              style={{ width: '100%', padding: '8px 12px', border: '1px solid var(--border)', borderRadius: 'var(--radius)', marginTop: '4px' }}
            >
              <option value="hook">挂钩</option>
              <option value="desk_decor">桌面装饰</option>
              <option value="wall_decor">墙面装饰</option>
            </select>
          </div>
          <div>
            <label style={{ fontSize: '12px', color: 'var(--text-faint)', textTransform: 'uppercase' }}>市场范围</label>
            <select
              value={form.market_scope}
              onChange={(e) => handleChange('market_scope', e.target.value)}
              style={{ width: '100%', padding: '8px 12px', border: '1px solid var(--border)', borderRadius: 'var(--radius)', marginTop: '4px' }}
            >
              <option value="us">美国</option>
              <option value="uk">英国</option>
              <option value="ca">加拿大</option>
              <option value="us_uk_ca">全部</option>
            </select>
          </div>
        </div>
      </div>

      {/* 成本表单 */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div className="card-label">成本与定价</div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px', marginTop: '16px' }}>
          <div>
            <label style={{ fontSize: '12px', color: 'var(--text-faint)', textTransform: 'uppercase' }}>单价 (CNY)</label>
            <input
              type="number"
              value={form.unit_cost_cny}
              onChange={(e) => handleChange('unit_cost_cny', e.target.value)}
              style={{ width: '100%', padding: '8px 12px', border: '1px solid var(--border)', borderRadius: 'var(--radius)', marginTop: '4px' }}
              placeholder="12.5"
            />
          </div>
          <div>
            <label style={{ fontSize: '12px', color: 'var(--text-faint)', textTransform: 'uppercase' }}>运费 (CNY)</label>
            <input
              type="number"
              value={form.shipping_cny}
              onChange={(e) => handleChange('shipping_cny', e.target.value)}
              style={{ width: '100%', padding: '8px 12px', border: '1px solid var(--border)', borderRadius: 'var(--radius)', marginTop: '4px' }}
              placeholder="8.0"
            />
          </div>
          <div>
            <label style={{ fontSize: '12px', color: 'var(--text-faint)', textTransform: 'uppercase' }}>定制费 (CNY)</label>
            <input
              type="number"
              value={form.custom_cny}
              onChange={(e) => handleChange('custom_cny', e.target.value)}
              style={{ width: '100%', padding: '8px 12px', border: '1px solid var(--border)', borderRadius: 'var(--radius)', marginTop: '4px' }}
              placeholder="0"
            />
          </div>
          <div>
            <label style={{ fontSize: '12px', color: 'var(--text-faint)', textTransform: 'uppercase' }}>包装费 (USD)</label>
            <input
              type="number"
              value={form.packaging_usd}
              onChange={(e) => handleChange('packaging_usd', e.target.value)}
              style={{ width: '100%', padding: '8px 12px', border: '1px solid var(--border)', borderRadius: 'var(--radius)', marginTop: '4px' }}
              placeholder="0.8"
            />
          </div>
          <div>
            <label style={{ fontSize: '12px', color: 'var(--text-faint)', textTransform: 'uppercase' }}>售价 (USD)</label>
            <input
              type="number"
              value={form.listing_price}
              onChange={(e) => handleChange('listing_price', e.target.value)}
              style={{ width: '100%', padding: '8px 12px', border: '1px solid var(--border)', borderRadius: 'var(--radius)', marginTop: '4px' }}
              placeholder="14.99"
            />
          </div>
          <div>
            <label style={{ fontSize: '12px', color: 'var(--text-faint)', textTransform: 'uppercase' }}>年销售额 (USD)</label>
            <input
              type="number"
              value={form.annual_revenue}
              onChange={(e) => handleChange('annual_revenue', e.target.value)}
              style={{ width: '100%', padding: '8px 12px', border: '1px solid var(--border)', borderRadius: 'var(--radius)', marginTop: '4px' }}
              placeholder="0"
            />
          </div>
        </div>
        <button
          className="btn btn-primary"
          style={{ marginTop: '16px', width: '100%' }}
          onClick={calculatePricing}
          disabled={calculating}
        >
          {calculating ? '计算中...' : '计算定价'}
        </button>
      </div>

      {/* 定价结果 */}
      {pricing && (
        <div className="card" style={{ marginBottom: '24px' }}>
          <div className="card-label">定价分析</div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: '16px', marginTop: '16px' }}>
            <div style={{ textAlign: 'center', padding: '16px', border: '1px solid var(--border)', borderRadius: 'var(--radius)' }}>
              <div style={{ fontSize: '28px', fontWeight: 700, color: 'var(--text)' }}>${pricing.cog}</div>
              <div style={{ fontSize: '12px', color: 'var(--text-faint)', marginTop: '4px' }}>总成本 (COG)</div>
            </div>
            <div style={{ textAlign: 'center', padding: '16px', border: '1px solid var(--border)', borderRadius: 'var(--radius)' }}>
              <div style={{ fontSize: '28px', fontWeight: 700, color: 'var(--text)' }}>${pricing.platform_fees}</div>
              <div style={{ fontSize: '12px', color: 'var(--text-faint)', marginTop: '4px' }}>平台费</div>
            </div>
            <div style={{ textAlign: 'center', padding: '16px', border: '1px solid var(--border)', borderRadius: 'var(--radius)' }}>
              <div style={{ fontSize: '28px', fontWeight: 700, color: 'var(--green)' }}>${pricing.net_profit}</div>
              <div style={{ fontSize: '12px', color: 'var(--text-faint)', marginTop: '4px' }}>净利润</div>
            </div>
            <div style={{ textAlign: 'center', padding: '16px', border: '1px solid var(--border)', borderRadius: 'var(--radius)' }}>
              <div style={{ fontSize: '28px', fontWeight: 700, color: pricing.net_margin_pct >= 50 ? 'var(--green)' : pricing.net_margin_pct >= 30 ? 'var(--amber)' : 'var(--red)' }}>
                {pricing.net_margin_pct}%
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-faint)', marginTop: '4px' }}>净利率</div>
            </div>
          </div>
          <button
            className="btn btn-primary"
            style={{ marginTop: '16px', width: '100%' }}
            onClick={createProduct}
          >
            保存产品
          </button>
        </div>
      )}

      {/* 产品列表 */}
      <div className="card">
        <div className="card-label">产品列表</div>
        {products.length === 0 ? (
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
                </tr>
              </thead>
              <tbody>
                {products.map((p: any) => (
                  <tr key={p.id}>
                    <td>{p.id}</td>
                    <td style={{ fontWeight: 500 }}>{p.name}</td>
                    <td><span className="tag">{p.subcategory}</span></td>
                    <td>{p.market_scope}</td>
                    <td><span className={`score-badge ${p.status === 'confirmed' ? 'high' : 'medium'}`}>{p.status}</span></td>
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

export default ProductValidator