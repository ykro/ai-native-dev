import type { Pet } from '../types/pet';
import { pets } from '../data/mockData';

export interface PetProfile extends Pet {
    imageUrl: string;
}

interface DogApiResponse {
    message: string;
    status: string;
}

const DOG_API_URL = 'https://dog.ceo/api/breeds/image/random';
// Reliable fallback image (Golden Retriever)
const FALLBACK_IMAGE = 'https://images.dog.ceo/breeds/retriever-golden/n02099601_3004.jpg';

/**
 * Fetches a random pet profile by combining local bio data with a remote dog image.
 * Provides a fallback image in case of API failure to ensure UI resilience.
 */
export const fetchRandomPetProfile = async (): Promise<PetProfile> => {
    // 1. Select a random pet from local data
    const randomPet = pets[Math.floor(Math.random() * pets.length)];

    let imageUrl = FALLBACK_IMAGE;

    try {
        // 2. Fetch random image from Dog API
        const response = await fetch(DOG_API_URL);

        if (!response.ok) {
            throw new Error(`API Error: ${response.status} ${response.statusText}`);
        }

        const data: DogApiResponse = await response.json();

        // Validate response structure
        if (data.status === 'success' && data.message) {
            imageUrl = data.message;
        } else {
            console.warn('Unexpected API response format:', data);
        }

    } catch (error) {
        // 3. Graceful Error Handling
        console.error('Failed to fetch dog image, using fallback:', error);
        // Keep using FALLBACK_IMAGE
    }

    // 4. Merge and return
    return {
        ...randomPet,
        //imageUrl,
        photo: imageUrl,
    };
};

/**
 * Fetches a list of pet profiles.
 * Use this if we want to load multiple pets at once.
 */
export const fetchPetProfiles = async (count: number = 1): Promise<PetProfile[]> => {
    const promises = Array.from({ length: count }, () => fetchRandomPetProfile());
    return Promise.all(promises);
}
