import { useState, useEffect, useCallback } from 'react'

function KeywordLab() {
  const [file, setFile] = useState<File | null>(null)
  const [importing, setImporting] = useState(false)
  const [importResult, setImportResult] = useState<any>(null)
  const [keywords, setKeywords] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [sortBy, setSortBy] = useState('avg_searches')
  const [sortOrder, setSortOrder] = useState('desc')
  const [kdFilter, setKdFilter] = useState('')

  const fetchKeywords = useCallback(async () => {
    setLoading(true)
    try {
      const res = await fetch(`/api/keywords?sort=${sortBy}&order=${sortOrder}`)
      const data = await res.json()
      setKeywords(data)
    } catch (err: any) {
      console.error('获取关键词失败:', err)
    } finally {
      setLoading(false)
    }
  }, [sortBy, sortOrder])

  useEffect(() => {
    fetchKeywords()
  }, [fetchKeywords])

  const handleUpload = async () => {
    if (!file) return
    setImporting(true)
    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await fetch('/api/keywords/import', {
        method: 'POST',
        body: formData
      })
      const data = await res.json()
      setImportResult(data)
      if (data.imported > 0) fetchKeywords()
    } catch (err: any) {
      setImportResult({ error: true, message: '上传失败' })
    } finally {
      setImporting(false)
      setFile(null)
    }
  }

  const toggleSelect = async (id: number) => {
    try {
      await fetch(`/api/keywords/${id}/select`, { method: 'PUT' })
      fetchKeywords()
    } catch (err: any) {
      console.error('切换选中状态失败:', err)
    }
  }

  const filteredKeywords = keywords.filter((kw: any) => {
    if (!kdFilter) return true
    const [min, max] = kdFilter.split('-').map(Number)
    if (max) return kw.kd >= min && kw.kd <= max
    return kw.kd >= min
  })

  return (
    <div>
      {/* 上传区域 */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div className="card-label">数据导入</div>
        <div
          style={{
            border: '2px dashed var(--border)',
            borderRadius: 'var(--radius)',
            padding: '48px 24px',
            textAlign: 'center',
            cursor: 'pointer',
            transition: 'border-color 0.15s'
          }}
          onClick={() => document.getElementById('csv-input')?.click()}
        >
          <input
            id="csv-input"
            type="file"
            accept=".csv"
            style={{ display: 'none' }}
            onChange={(e) => setFile(e.target.files?.[0] || null)}
          />
          <div style={{ fontSize: '14px', color: 'var(--text-muted)', marginBottom: '4px' }}>
            {file ? file.name : '拖拽 eRank CSV 文件到此处'}
          </div>
          <div style={{ fontSize: '12px', color: 'var(--text-faint)' }}>
            或点击上传
          </div>
        </div>

        {file && (
          <button
            className="btn btn-primary"
            style={{ marginTop: '16px', width: '100%' }}
            onClick={handleUpload}
            disabled={importing}
          >
            {importing ? '导入中...' : '开始导入'}
          </button>
        )}

        {importResult && (
          <div style={{ marginTop: '16px', fontSize: '14px' }}>
            <div>导入成功: {importResult.imported}</div>
            <div>跳过重复: {importResult.skipped}</div>
            {importResult.errors?.length > 0 && (
              <div style={{ color: 'var(--red)' }}>错误: {importResult.errors.length}</div>
            )}
          </div>
        )}
      </div>

      {/* 筛选和排序 */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', gap: '16px', alignItems: 'center', flexWrap: 'wrap' }}>
          <div>
            <span style={{ fontSize: '12px', color: 'var(--text-faint)', marginRight: '8px' }}>排序</span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              style={{ padding: '6px 12px', border: '1px solid var(--border)', borderRadius: 'var(--radius)' }}
            >
              <option value="avg_searches">搜索量</option>
              <option value="kd">KD</option>
              <option value="competition">竞争数</option>
            </select>
            <select
              value={sortOrder}
              onChange={(e) => setSortOrder(e.target.value)}
              style={{ padding: '6px 12px', border: '1px solid var(--border)', borderRadius: 'var(--radius)', marginLeft: '8px' }}
            >
              <option value="desc">降序</option>
              <option value="asc">升序</option>
            </select>
          </div>
          <div>
            <span style={{ fontSize: '12px', color: 'var(--text-faint)', marginRight: '8px' }}>KD 筛选</span>
            <input
              type="text"
              placeholder="0-20"
              value={kdFilter}
              onChange={(e) => setKdFilter(e.target.value)}
              style={{ padding: '6px 12px', border: '1px solid var(--border)', borderRadius: 'var(--radius)', width: '80px' }}
            />
          </div>
          <div style={{ marginLeft: 'auto', fontSize: '14px', color: 'var(--text-muted)' }}>
            共 {filteredKeywords.length} 个关键词
          </div>
        </div>
      </div>

      {/* 关键词列表 */}
      <div className="card">
        <div className="card-label">关键词列表</div>
        {loading ? (
          <div style={{ textAlign: 'center', padding: '48px', color: 'var(--text-muted)' }}>加载中...</div>
        ) : filteredKeywords.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '48px', color: 'var(--text-muted)' }}>暂无数据</div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table>
              <thead>
                <tr>
                  <th>选择</th>
                  <th>关键词</th>
                  <th>搜索量</th>
                  <th>点击</th>
                  <th>CTR</th>
                  <th>竞争</th>
                  <th>KD</th>
                </tr>
              </thead>
              <tbody>
                {filteredKeywords.map((kw: any) => (
                  <tr key={kw.id}>
                    <td>
                      <input
                        type="checkbox"
                        checked={kw.is_selected}
                        onChange={() => toggleSelect(kw.id)}
                      />
                    </td>
                    <td style={{ fontWeight: 500 }}>{kw.keyword}</td>
                    <td>{kw.avg_searches?.toLocaleString()}</td>
                    <td>{kw.avg_clicks?.toLocaleString()}</td>
                    <td>{kw.ctr}%</td>
                    <td>{kw.competition?.toLocaleString()}</td>
                    <td>
                      <span className={`score-badge ${kw.kd < 20 ? 'high' : kw.kd < 60 ? 'medium' : 'low'}`}>
                        {kw.kd}
                      </span>
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

export default KeywordLab