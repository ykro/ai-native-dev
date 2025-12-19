import { useState, useEffect, useCallback, useRef } from 'react';
import { fetchRandomPetProfile, type PetProfile } from '../services/petProvider';

const BUFFER_SIZE = 3;

export function usePetStack() {
    const [stack, setStack] = useState<PetProfile[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const initialized = useRef(false);

    // Initialize the stack
    useEffect(() => {
        // Prevent double initialization in StrictMode
        if (initialized.current) return;
        initialized.current = true;

        const initStack = async () => {
            setIsLoading(true);
            try {
                // Fetch initial buffer parallelly
                const promises = Array.from({ length: BUFFER_SIZE }, () => fetchRandomPetProfile());
                const newPets = await Promise.all(promises);
                setStack(newPets);
            } catch (error) {
                console.error("Failed to init stack:", error);
            } finally {
                setIsLoading(false);
            }
        };
        initStack();
    }, []);

    // Remove current pet and fetch a new one in background
    const advance = useCallback(() => {
        setStack((prev) => {
            if (prev.length === 0) return prev;
            // Remove the first item (FIFO)
            const [, ...rest] = prev;
            return rest;
        });

        // Background fetch to replenish
        fetchRandomPetProfile().then((newPet) => {
            setStack((prev) => [...prev, newPet]);
        });
    }, []);

    return {
        currentPet: stack[0] || null,
        nextPet: stack[1] || null,
        advance,
        isLoading: isLoading && stack.length === 0,
    };
}
