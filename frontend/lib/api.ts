export type DatasetRow = Record<string, string | number>
export type DatasetSummary = { filename: string; size: number; rows: DatasetRow[]; columns: string[]; dateColumn?: string; revenueColumn?: string; unitsColumn?: string; productColumn?: string; categoryColumn?: string; profitColumn?: string; dateRange?: { from: string; to: string } }

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? ''
export async function uploadDataset(file: File) {
  const form = new FormData(); form.append('file', file)
  const response = await fetch(`${API_BASE_URL}/datasets/upload`, { method: 'POST', body: form })
  if (!response.ok) throw new Error(`Dataset upload failed (${response.status})`)
  return response.json()
}
