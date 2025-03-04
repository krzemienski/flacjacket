import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import ThemeProvider from '@/components/ThemeProvider'
import Header from '@/components/Header'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'FlacJacket - Audio Track Analyzer',
  description: 'Analyze and extract tracks from audio files',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider>
          <div className="min-h-screen flex flex-col bg-background-light dark:bg-background-dark transition-colors duration-200">
            <Header />
            <main className="container mx-auto px-4 py-8 flex-grow">
              {children}
            </main>
            <footer className="py-4 text-center text-sm text-gray-500 dark:text-gray-400 border-t border-gray-200 dark:border-gray-800">
              <div className="container mx-auto">
                &copy; {new Date().getFullYear()} FlacJacket - A Shazam-like Audio Recognition Tool
              </div>
            </footer>
          </div>
        </ThemeProvider>
      </body>
    </html>
  )
}
