import { NextResponse } from 'next/server';
import { UnsplashService } from '@/services/unsplash';

export async function GET(request: Request) {
    const { searchParams } = new URL(request.url);
    const query = searchParams.get('q');

    // Cache Control Headers
    const headers = {
        'Cache-Control': 'public, s-maxage=3600, stale-while-revalidate=59',
    };

    if (!query) {
        // If no query, return popular destinations
        const popular = await UnsplashService.fetchPopular();
        return NextResponse.json(popular, { headers });
    }

    // If query exists, perform search
    const results = await UnsplashService.searchDestinations(query);
    return NextResponse.json(results, { headers });
}
