import { createApi } from 'unsplash-js';
import nodeFetch from 'node-fetch';

// Initialize Unsplash Client
// We use node-fetch polyfill if not in native environment (Next.js usually handles this, but good for safety)
const unsplash = createApi({
    accessKey: process.env.UNSPLASH_ACCESS_KEY || '',
    fetch: nodeFetch as never, // casting as never to avoid type conflict with standard fetch
});

export interface Destination {
    id: string;
    slug: string;
    title: string;
    description: string;
    urls: {
        regular: string;
        full: string;
        small: string;
    };
    user: {
        name: string;
        username: string;
    };
    tags: string[];
}

export const UnsplashService = {

    // 1. Fetch Popular Destinations (Editorial Feed/Travel Topic)
    fetchPopular: async (): Promise<Destination[]> => {
        try {
            // Trying to fetch from 'travel' topic
            const result = await unsplash.topics.getPhotos({
                topicIdOrSlug: 'travel',
                perPage: 12,
                orderBy: 'editorial',
            });

            if (result.errors) {
                console.error('Unsplash API Error:', result.errors);
                return [];
            }

            const photos = result.response?.results || [];
            return photos.map(mapPhotoToDestination);

        } catch (error) {
            console.error('Unsplash Service Exception:', error);
            return [];
        }
    },

    // 2. Search Destinations
    searchDestinations: async (query: string): Promise<Destination[]> => {
        try {
            const result = await unsplash.search.getPhotos({
                query: query + ' travel', // Append travel context
                page: 1,
                perPage: 12,
                orientation: 'portrait', // Better for masonry
            });

            if (result.errors) {
                console.error('Unsplash Search Error:', result.errors);
                return [];
            }

            const photos = result.response?.results || [];
            return photos.map(mapPhotoToDestination);

        } catch (error) {
            console.error('Unsplash Search Exception:', error);
            return [];
        }
    },

    // 3. Fetch Destination Details
    fetchById: async (id: string): Promise<Destination | null> => {
        try {
            const result = await unsplash.photos.get({ photoId: id });

            if (result.errors) {
                console.error('Unsplash GetId Error:', result.errors);
                return null;
            }

            return mapPhotoToDestination(result.response as any);

        } catch (error) {
            console.error("Unsplash GetId Exception", error);
            return null;
        }
    },

    // 4. Fetch Related (by tags or location)
    fetchRelated: async (query_tags: string): Promise<Destination[]> => {
        try {
            const result = await unsplash.search.getPhotos({
                query: query_tags + ' place',
                page: 1,
                perPage: 4,
            });

            if (result.errors) return [];
            return (result.response?.results || []).map(mapPhotoToDestination);

        } catch (error) {
            return [];
        }
    }
};

// Helper: Map Raw Unsplash Response to clean App Model
// eslint-disable-next-line @typescript-eslint/no-explicit-any
function mapPhotoToDestination(photo: any): Destination {
    return {
        id: photo.id,
        slug: photo.slug || photo.id,
        title: photo.alt_description || photo.description || 'Unknown Destination',
        description: photo.description || photo.alt_description || 'Explora este increíble lugar.',
        urls: {
            regular: photo.urls.regular,
            full: photo.urls.full,
            small: photo.urls.small,
        },
        user: {
            name: photo.user.name,
            username: photo.user.username,
        },
        // Extract first 3 tags if available
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        tags: (photo.tags || []).slice(0, 3).map((t: any) => t.title),
    };
}
