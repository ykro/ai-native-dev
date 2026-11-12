import { createApi } from 'unsplash-js';
import nodeFetch, { Response as NodeFetchResponse, RequestInit as NodeFetchInit } from 'node-fetch';

// Custom Fetch Wrapper
const fetchWithLogging = async (url: string, init: NodeFetchInit) => {
    try {
        const response = await nodeFetch(url, init);
        if (!response.ok) {
            const text = await response.text();
            console.error(`[Unsplash] API Error (${response.status}): ${text}`);
            return new NodeFetchResponse(text, {
                status: response.status,
                statusText: response.statusText,
                headers: response.headers
            });
        }
        return response;
    } catch (error) {
        console.error('[Unsplash] Network Failure:', error);
        throw error;
    }
};

const unsplash = createApi({
    accessKey: process.env.UNSPLASH_ACCESS_KEY || '',
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    fetch: fetchWithLogging as any,
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
        thumb: string; // ADDED
    };
    user: {
        name: string;
        username: string;
    };
    tags: string[];
    location?: string;
    cityName?: string; // ADDED

    // Custom fields for Grid Display customization
    gridTitle?: string;
    gridSubtitle?: string;
}

export const UnsplashService = {

    // 1. Fetch Popular (HOMEPAGE Mode)
    fetchPopular: async (): Promise<Destination[]> => {
        try {
            const TOP_CITIES = [
                'Paris', 'Rome', 'London', 'New York', 'Tokyo', 'Barcelona', 'Dubai', 'Singapore', 'Amsterdam', 'Bangkok',
                'Istanbul', 'Seoul', 'Prague', 'Berlin', 'Sydney', 'Hong Kong', 'Rio de Janeiro', 'Cape Town', 'Kyoto', 'Venice',
                'Florence', 'Vienna', 'Lisbon', 'San Francisco', 'Los Angeles', 'Chicago', 'Budapest', 'Dublin', 'Edinburgh', 'Madrid',
                'Milan', 'Munich', 'Toronto', 'Vancouver', 'Montreal', 'Mexico City', 'Cancun', 'Buenos Aires', 'Cusco', 'Cairo',
                'Marrakech', 'Petra', 'Bali', 'Phuket', 'Santorini', 'Mykonos', 'Dubrovnik', 'Reykjavik', 'Queenstown', 'Bora Bora'
            ];

            const shuffled = TOP_CITIES.sort(() => 0.5 - Math.random());
            const selected = shuffled.slice(0, 3);

            // console.log(`[Unsplash] Fetching popular for: ${selected.join(', ')}`);

            const promises = selected.map(city => {
                const query = `${city} travel`;
                return unsplash.search.getPhotos({
                    query: query,
                    page: 1,
                    perPage: 4,
                    orientation: 'portrait',
                    orderBy: 'relevant'
                }).then(result => ({ city, result }));
            });

            const results = await Promise.all(promises);
            let combinedDestinations: Destination[] = [];

            results.forEach(({ city, result }) => {
                if (result.response?.results) {
                    // MODE: HOMEPAGE
                    const mapped = result.response.results.map(photo => mapPhotoToDestination(photo, city, 'home'));
                    combinedDestinations = [...combinedDestinations, ...mapped];
                }
            });

            return combinedDestinations.sort(() => 0.5 - Math.random());

        } catch (error) {
            console.error('Unsplash Service Exception (fetchPopular):', error);
            return [];
        }
    },

    // 2. Search Destinations (SEARCH Mode)
    searchDestinations: async (query: string): Promise<Destination[]> => {
        try {
            const finalQuery = query + ' travel';
            // console.log(`[Unsplash] Search Query: "${finalQuery}"`);

            const result = await unsplash.search.getPhotos({
                query: finalQuery,
                page: 1,
                perPage: 12,
                orientation: 'portrait',
            });

            if (result.errors) return [];

            const photos = result.response?.results || [];
            // MODE: SEARCH
            return photos.map(photo => mapPhotoToDestination(photo, query, 'search'));

        } catch (error) {
            console.error('Unsplash Search Exception:', error);
            return [];
        }
    },

    // 3. Details
    fetchById: async (id: string): Promise<Destination | null> => {
        try {
            const controller = new AbortController();
            const timeout = setTimeout(() => controller.abort(), 8000);

            const result = await unsplash.photos.get({ photoId: id }, { signal: controller.signal });
            clearTimeout(timeout);

            if (result.errors) return null;

            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            return mapPhotoToDestination(result.response as any, undefined, 'detail');

        } catch { // Removed error
            return null;
        }
    },

    // 4. Fetch Related
    fetchRelated: async (locationBase: string, tags: string[] = [], excludedId?: string, fallbackCity?: string): Promise<Destination[]> => {
        try {
            // console.log(`[Unsplash] fetchRelated called with: locationBase="${locationBase}", tags=${tags.length}, fallbackCity="${fallbackCity}"`);
            // USER REQUEST: "en la primera query no veo todos los tags" -> Increase tag slice
            const tagString = tags.slice(0, 3).join(' ');
            const finalQuery = `${locationBase} ${tagString} travel`;
            console.log(`[Unsplash] Related Query (Primary): "${finalQuery}"`);

            const result = await unsplash.search.getPhotos({
                query: finalQuery,
                page: 1,
                perPage: 12, // Fetch a bit more to filter
                orientation: 'portrait'
            });

            if (result.errors) return [];
            let rawPhotos = result.response?.results || [];

            if (excludedId) {
                rawPhotos = rawPhotos.filter(p => p.id !== excludedId);
            }

            // Priority 2: Secondary Query (User Request: "landmark travel" if < 8)
            // USER REQUEST: "no quiero usar el location de la foto sino el fallback de la ciudad"
            if (rawPhotos.length < 8) {
                // Use passed fallbackCity OR locationBase if city not available
                const cityContext = fallbackCity || locationBase;
                const landmarkQuery = `${cityContext} landmark travel`;
                console.log(`[Unsplash] Related Query (Secondary - Filler): "${landmarkQuery}"`);

                const landmarkResult = await unsplash.search.getPhotos({
                    query: landmarkQuery,
                    page: 1,
                    perPage: 12
                });

                if (landmarkResult.response?.results) {
                    const newPhotos = landmarkResult.response.results.filter(p =>
                        p.id !== excludedId && !rawPhotos.some(existing => existing.id === p.id)
                    );
                    rawPhotos = [...rawPhotos, ...newPhotos];
                }
            }

            // Limit to 8 (Bento Grid)
            const finalResults = rawPhotos.slice(0, 8).map(p => mapPhotoToDestination(p, fallbackCity || locationBase, 'search'));
            return finalResults;

        } catch {
            return [];
        }
    }
};

// Mapper: Updated for ID Cleanup and Duplicates
// eslint-disable-next-line @typescript-eslint/no-explicit-any
function mapPhotoToDestination(photo: any, contextLocation?: string, mode: 'home' | 'search' | 'detail' = 'detail'): Destination {

    // --- DESCRIPTION / SLUG CLEANING ---
    let descText = photo.description;

    // If no desc, or desc is just the ID (common Unsplash issue), try Fallbacks
    if (!descText || descText === photo.id) {
        if (photo.alternative_slugs?.es) {
            descText = photo.alternative_slugs.es.replace(/-/g, ' ');
        } else if (photo.alt_description) {
            descText = photo.alt_description;
        }
    }

    // Double Check: If descText STILL contains the ID or looks like a file name
    if (descText && (descText.includes(photo.id) || descText.includes('_'))) {
        // Last ditch try with alt desc or just generic
        if (photo.alt_description && photo.alt_description !== descText) {
            descText = photo.alt_description;
        } else {
            descText = undefined; // Will trigger "Destino Turístico" below
        }
    }

    // Capitalize
    if (descText) {
        descText = descText.charAt(0).toUpperCase() + descText.slice(1);
    } else {
        descText = "Destino turístico";
    }

    // --- STANDARD TITLE LOGIC (Detail) ---
    let primaryTitle: string;
    const photoLocationName = photo.location?.name;
    if (photoLocationName) primaryTitle = photoLocationName;
    else if (photo.location?.city && photo.location?.country) primaryTitle = `${photo.location.city}, ${photo.location.country}`;
    else if (contextLocation && mode !== 'home') primaryTitle = contextLocation.charAt(0).toUpperCase() + contextLocation.slice(1);
    else primaryTitle = descText.length < 50 ? descText : descText.slice(0, 50) + '...';

    // DEDUPLICATION: "Sydney, Sydney" or "Paris, Paris"
    // Safe case-insensitive check
    const parts = primaryTitle.split(',').map(s => s.trim());
    if (parts.length > 1) {
        if (parts[0].toLowerCase() === parts[1].toLowerCase()) {
            // It is duplicate on start (e.g. Sydney, Sydney, Australia)
            // Remove first part
            primaryTitle = parts.slice(1).join(', ');
            // Check again if we reduced to "Sydney":
            const newParts = primaryTitle.split(',').map(s => s.trim());
            if (newParts.length === 1 && newParts[0].toLowerCase() === parts[0].toLowerCase()) {
                // It essentially became "Sydney" (which is fine)
            }
        }
    }

    // --- GRID CUSTOMIZATION ---
    let gridTitle = primaryTitle;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    let gridSubtitle = (photo.tags || []).slice(0, 3).map((t: any) => t.title).join(' • ');

    // Override Subtitle if it contains ID (rare but happens if tags fail?)
    if (gridSubtitle && gridSubtitle.includes(photo.id)) gridSubtitle = "";

    if (mode === 'home') {
        if (contextLocation) {
            gridTitle = contextLocation.charAt(0).toUpperCase() + contextLocation.slice(1);
        }
        gridSubtitle = descText;
    }
    else if (mode === 'search') {
        gridTitle = descText;
    }

    const finalLocation = photoLocationName || ((photo.location?.city && photo.location?.country) ? `${photo.location.city}, ${photo.location.country}` : undefined);

    // EXTRACT CITY NAME FOR FALLBACKS
    let cityName = photo.location?.city || photo.location?.country || contextLocation;

    // Fallback: If no location metadata, try to extract from Tags
    if (!cityName && photo.tags && photo.tags.length > 0) {
        // Filter out generic tags like 'travel', 'outdoor', etc. if possible, or just take the first few meaningful ones
        // Assuming tags are objects with title.
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const usefulTags = photo.tags.map((t: any) => t.title)
            .filter((t: string) => !['travel', 'nature', 'city', 'building', 'architecture'].includes(t.toLowerCase()))
            .slice(0, 1);

        if (usefulTags.length > 0) {
            cityName = usefulTags[0]; // e.g., "Prague"
        }
    }

    // Improve Title if it defaulted to description and we found a city name
    if (primaryTitle === descText && cityName) {
        // If the description doesn't already start with the city
        if (!descText.toLowerCase().includes(cityName.toLowerCase())) {
            primaryTitle = `${cityName} - ${descText}`; // e.g. "Prague - A woman walking..."
            // If description is super long, maybe just use City?
            // Let's keep it descriptive but anchored.
        }
    }

    return {
        id: photo.id,
        slug: photo.slug || photo.id,
        title: primaryTitle,
        description: photo.description || photo.alt_description || 'Explora este increíble lugar.',
        urls: {
            regular: photo.urls.regular, // Main Image = Regular (good per user check)
            full: photo.urls.full,
            small: photo.urls.small,
            thumb: photo.urls.thumb,
        },
        user: {
            name: photo.user.name,
            username: photo.user.username,
        },
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        tags: (photo.tags || []).slice(0, 3).map((t: any) => t.title),
        location: finalLocation,
        cityName: cityName, // ADDED

        gridTitle,
        gridSubtitle
    };
}
