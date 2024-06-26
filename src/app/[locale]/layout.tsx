import type { Metadata } from 'next'
import localFont from 'next/font/local'
import { ViewTransitions } from 'next-view-transitions'
import { Analytics } from '@vercel/analytics/react'
import { cn } from '@/lib/utils'
import { NextIntlClientProvider } from 'next-intl'
import { getMessages, unstable_setRequestLocale } from 'next-intl/server'
import ApolloWrapper from './apollo-wrapper'
import './globals.css'

const fontZpix = localFont({
  src: '../../../public/fonts/zpix.ttf',
  variable: '--font-zpix',
  display: 'swap'
})

export const metadata: Metadata = {
  title: 'Pokedex',
  description: '',
  keywords: ['pokemon', 'pokedex']
}

export default async function RootLayout({
  children,
  params: { locale }
}: {
  children: React.ReactNode
  params: { locale: string }
}) {
  unstable_setRequestLocale(locale)
  const messages = await getMessages()

  return (
    <ViewTransitions>
      <html lang={locale}>
        <body
          className={cn(fontZpix.variable, 'mx-aut min-h-screen bg-gray-100')}
        >
          <ApolloWrapper>
            <NextIntlClientProvider messages={messages}>
              {children}
            </NextIntlClientProvider>
          </ApolloWrapper>
          <Analytics />
        </body>
      </html>
    </ViewTransitions>
  )
}
