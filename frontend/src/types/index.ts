export interface Keyword {
  id: number
  keyword: string
  avg_searches: number
  avg_clicks: number
  ctr: number
  competition: number
  kd: number
  is_selected: boolean
  created_at: string
}

export interface Product {
  id: number
  name: string
  status: string
  subcategory: string
  created_at: string
}

export interface ScoreResult {
  composite_score: number
  decision: string
  confidence: string
  breakdown: Record<string, {
    score: number
    weight: number
    weighted_score: number
  }>
}
