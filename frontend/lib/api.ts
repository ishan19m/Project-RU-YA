export type DatasetRow = Record<string, string | number>
export type DatasetSummary = { filename: string; size: number; rows: DatasetRow[]; columns: string[]; dateColumn?: string; revenueColumn?: string; unitsColumn?: string; productColumn?: string; categoryColumn?: string; profitColumn?: string; dateRange?: { from: string; to: string } }
export type Analysis = {
  kpis: { total_revenue:number; realized_revenue:number; total_profit:number; profit_margin_pct:number; total_orders:number; units_sold:number; average_order_value:number; return_rate_pct:number }
  monthly: { month:string; realized_revenue:number; total_profit:number; total_orders:number }[]
  categories: { name:string; revenue:number; share_pct:number }[]
  products: { name:string; category:string; revenue:number; units:number }[]
  forecast: { available:boolean; message?:string; best_model?:string; models:{ model:string; MAE:number; RMSE:number; MAPE:number }[]; future:{ month:string; forecasted_revenue:number }[] }
}

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? ''
export async function uploadDataset(file: File) {
  const form = new FormData(); form.append('file', file)
  const response = await fetch(`${API_BASE_URL}/datasets/upload`, { method: 'POST', body: form })
  if (!response.ok) throw new Error(`Dataset upload failed (${response.status})`)
  return response.json()
}
