import React, { useState } from 'react'

function KeywordLab() {
  const [file, setFile] = useState<File | null>(null)
  const [importing, setImporting] = useState(false)
  const [result, setResult] = useState<any>(null)

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
      setResult(data)
    } catch (err) {
      setResult({ error: true, message: '上传失败' })
    } finally {
      setImporting(false)
    }
  }

  return (
    <div>
      <div className="card" style={{ marginBottom: '24px' }}>
        <div className="card-label">数据导入</div>
        <div 
          style={{
            border: '2px dashed var(--border)',
            borderRadius: 'var(--radius)',
            padding: '48px 24px',
            textAlign: 'center',
            cursor: 'pointer'
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
        
        {result && (
          <div style={{ marginTop: '16px', fontSize: '14px' }}>
            <div>导入成功: {result.imported}</div>
            <div>跳过重复: {result.skipped}</div>
            {result.errors?.length > 0 && (
              <div style={{ color: 'var(--red)' }}>错误: {result.errors.length}</div>
            )}
          </div>
        )}
      </div>
      
      <div className="card">
        <div className="card-label">关键词列表</div>
        <div style={{ color: 'var(--text-muted)', fontSize: '14px', marginTop: '12px' }}>
          导入后将在此显示关键词数据
        </div>
      </div>
    </div>
  )
}

export default KeywordLab
