import { NextResponse } from 'next/server';
import { GeminiService } from '@/services/gemini';

export async function POST(request: Request) {
    try {
        const body = await request.json();
        const { destination, context } = body;

        if (!destination) {
            return NextResponse.json({ error: 'Destination is required' }, { status: 400 });
        }

        const plan = await GeminiService.generateTravelPlan(destination, context);
        return NextResponse.json({ plan });

    } catch (error) {
        console.error('API Plan Error:', error);
        return NextResponse.json({ error: 'Failed to generate plan' }, { status: 500 });
    }
}
