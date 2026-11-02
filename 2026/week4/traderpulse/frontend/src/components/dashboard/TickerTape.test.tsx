import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import TickerTape from '@/components/dashboard/TickerTape'

describe('TickerTape', () => {
    it('renders ticker items', () => {
        render(<TickerTape />)

        // Check for some symbols from the mock data
        expect(screen.getAllByText('AAPL').length).toBeGreaterThan(0)
        expect(screen.getAllByText('BTC').length).toBeGreaterThan(0)
    })

    it('displays prices formatted correctly', () => {
        render(<TickerTape />)
        // Check for dollar sign
        const prices = screen.getAllByText(/^\$/)
        expect(prices.length).toBeGreaterThan(0)
    })
})
