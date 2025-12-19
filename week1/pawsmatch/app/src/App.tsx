import { useState, useEffect } from 'react';
import { fetchRandomPetProfile, type PetProfile } from './services/petProvider';
import { PetCard } from './components/PetCard';

function App() {
  const [currentPet, setCurrentPet] = useState<PetProfile | null>(null);
  const [loading, setLoading] = useState(true);

  const loadNewPet = async () => {
    setLoading(true);
    try {
      const pet = await fetchRandomPetProfile();
      setCurrentPet(pet);
    } catch (error) {
      console.error("Failed to load pet:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Initial load
    loadNewPet();
  }, []);

  const handleAdopt = () => {
    if (currentPet) {
      alert(`Yay! You adopted ${currentPet.name}! 🎉`);
      loadNewPet();
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-8 bg-warm-50">
      <header className="mb-8 text-center">
        <h1 className="text-6xl font-bold text-warm-800 mb-4 tracking-tight">
          PawsMatch
        </h1>
        <p className="text-xl text-warm-600 italic">
          Finding the perfect companion for every home.
        </p>
      </header>

      <main className="w-full max-w-4xl flex justify-center">
        {currentPet ? (
          <PetCard
            pet={currentPet}
            onAdopt={handleAdopt}
            onNext={loadNewPet}
            isLoading={loading}
          />
        ) : (
          <div className="text-warm-600 text-lg animate-pulse flex flex-col items-center">
            <div className="animate-spin rounded-full h-12 w-12 border-4 border-warm-500 border-t-transparent mb-4"></div>
            Finding a furry friend for you...
          </div>
        )}
      </main>

      <footer className="mt-12 text-center text-warm-400 text-sm">
        Powered by PawsMatch & The Dog API
      </footer>
    </div>
  )
}

export default App
