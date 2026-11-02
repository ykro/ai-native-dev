import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { expect, test, vi, describe } from 'vitest'
import { StatusCard } from '@/components/status-card'
import React from 'react'

// Mock fetch globally
global.fetch = vi.fn()

describe('StatusCard Component', () => {
    test('renders active state correctly', () => {
        render(<StatusCard initialStatus="active" />)
        expect(screen.getByText('Backend:')).toBeDefined()
        expect(screen.getByText('Activo')).toBeDefined()
    })

    test('renders error state correctly', () => {
        render(<StatusCard initialStatus="error" />)
        expect(screen.getByText('Inactivo')).toBeDefined()
    })

    test('retry button triggers fetch and updates state', async () => {
        // Mock success response
        (global.fetch as any).mockResolvedValue({
            ok: true,
            json: async () => ({ status: 'active' })
        })

        render(<StatusCard initialStatus="error" />)

        const button = screen.getByText('Reintentar Conexión')
        fireEvent.click(button)

        // Check loading state implied by button disabled or just wait for update
        await waitFor(() => {
            expect(screen.getByText('Activo')).toBeDefined()
        })
    })
})
