import { useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { Dog, Heart, Loader2, PartyPopper } from 'lucide-react';
import { usePetStack } from './hooks/usePetStack';
import { PetCard } from './components/PetCard';
import { AdoptionConfirmation } from './components/AdoptionConfirmation';
import type { PetProfile } from './services/petProvider';

type AppScreen = 'browse' | 'adoption' | 'success';

function App() {
  const { currentPet, nextPet, advance, isLoading } = usePetStack();
  const [screen, setScreen] = useState<AppScreen>('browse');
  const [likedPet, setLikedPet] = useState<PetProfile | null>(null);

  const handleLike = () => {
    if (currentPet) {
      setLikedPet(currentPet);
      setScreen('adoption');
    }
  };

  const handlePass = () => {
    advance();
  };

  const handleBackToBrowse = () => {
    advance();
    setScreen('browse');
    setLikedPet(null);
  };

  const handleScheduleVisit = () => {
    setScreen('success');
  };

  const handleContinueBrowsing = () => {
    advance();
    setScreen('browse');
    setLikedPet(null);
  };

  return (
    <div className="min-h-dvh flex flex-col bg-gradient-to-br from-warm-50 via-primary-50/30 to-friendly-50/20 overflow-hidden">
      {/* Header */}
      <motion.header
        className="flex items-center justify-center gap-3 py-6 px-4 safe-top"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
      >
        <motion.div
          animate={{ rotate: [0, -10, 10, -10, 0] }}
          transition={{ duration: 0.5, delay: 1, repeat: Infinity, repeatDelay: 5 }}
        >
          <Dog className="w-8 h-8 text-warm-600" />
        </motion.div>
        <h1 className="text-3xl sm:text-4xl font-bold bg-gradient-to-r from-warm-700 via-warm-600 to-friendly-600 bg-clip-text text-transparent tracking-tight">
          PawsMatch
        </h1>
      </motion.header>

      {/* Main Content */}
      <main className="flex-1 flex flex-col items-center justify-center px-4 pb-6">
        <AnimatePresence mode="wait">
          {screen === 'browse' && (
            <motion.div
              key="browse-screen"
              className="relative w-full max-w-sm h-[600px] sm:h-[650px] flex items-center justify-center"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <AnimatePresence mode="popLayout">
                {currentPet ? (
                  <PetCard
                    key={currentPet.id + currentPet.imageUrl}
                    pet={currentPet}
                    onLike={handleLike}
                    onPass={handlePass}
                  />
                ) : (
                  <motion.div
                    key="loading-state"
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.9 }}
                    className="flex flex-col items-center justify-center text-center p-8"
                  >
                    {isLoading ? (
                      <>
                        <motion.div
                          animate={{ rotate: 360 }}
                          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                          className="mb-6"
                        >
                          <Loader2 className="w-12 h-12 text-warm-500" />
                        </motion.div>
                        <p className="text-warm-600 text-lg font-medium">
                          Buscando tu match perfecto...
                        </p>
                        <p className="text-warm-400 text-sm mt-2">
                          Cargando mascotas adorables
                        </p>
                      </>
                    ) : (
                      <>
                        <motion.div
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          transition={{ type: 'spring', stiffness: 200, delay: 0.2 }}
                          className="w-20 h-20 rounded-full bg-gradient-to-br from-friendly-100 to-friendly-200 flex items-center justify-center mb-6"
                        >
                          <Heart className="w-10 h-10 text-friendly-500" fill="currentColor" />
                        </motion.div>
                        <p className="text-warm-700 text-xl font-semibold">
                          ¡Ya viste todas!
                        </p>
                        <p className="text-warm-500 text-sm mt-2 max-w-xs">
                          Has visto todas las mascotas disponibles. ¡Vuelve pronto para conocer nuevos amigos peludos!
                        </p>
                      </>
                    )}
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Pre-fetch the next image invisibly */}
              {nextPet && (
                <img
                  src={nextPet.imageUrl}
                  alt="preload"
                  className="hidden"
                  aria-hidden="true"
                />
              )}
            </motion.div>
          )}

          {screen === 'adoption' && likedPet && (
            <motion.div
              key="adoption-screen"
              className="w-full px-4"
              initial={{ opacity: 0, x: 100 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -100 }}
            >
              <AdoptionConfirmation
                pet={likedPet}
                onBack={handleBackToBrowse}
                onConfirm={handleScheduleVisit}
              />
            </motion.div>
          )}

          {screen === 'success' && likedPet && (
            <motion.div
              key="success-screen"
              className="flex flex-col items-center justify-center text-center p-8 max-w-md"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
            >
              <motion.div
                initial={{ scale: 0, rotate: -180 }}
                animate={{ scale: 1, rotate: 0 }}
                transition={{ type: 'spring', stiffness: 200, delay: 0.2 }}
                className="w-24 h-24 rounded-full bg-gradient-to-br from-primary-400 to-warm-500 flex items-center justify-center mb-6 shadow-lg shadow-warm-500/30"
              >
                <PartyPopper className="w-12 h-12 text-white" />
              </motion.div>

              <motion.h2
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
                className="text-2xl font-bold text-warm-800 mb-2"
              >
                ¡Visita Agendada!
              </motion.h2>

              <motion.p
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
                className="text-warm-600 mb-2"
              >
                Te contactaremos pronto para confirmar tu visita con <span className="font-bold text-friendly-600">{likedPet.name}</span>.
              </motion.p>

              <motion.p
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 }}
                className="text-warm-500 text-sm mb-8"
              >
                Revisa tu correo para más detalles y próximos pasos.
              </motion.p>

              <motion.button
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.7 }}
                onClick={handleContinueBrowsing}
                className="px-8 py-4 bg-gradient-to-r from-friendly-500 to-friendly-600 text-white rounded-2xl font-bold shadow-lg shadow-friendly-500/30"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                Seguir Explorando
              </motion.button>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Footer */}
      <motion.footer
        className="py-4 px-4 text-center safe-bottom"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
      >
        <p className="text-warm-400 text-xs">
          Creado con PawsMatch & The Dog API
        </p>
      </motion.footer>
    </div>
  );
}

export default App;
