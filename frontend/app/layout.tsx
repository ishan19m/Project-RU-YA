import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = { title: "RU'YA — See Beyond the Numbers", description: 'Retail intelligence and financial analytics for ElectroMart Chandigarh.' }
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) { return <html lang="en"><body>{children}</body></html> }
