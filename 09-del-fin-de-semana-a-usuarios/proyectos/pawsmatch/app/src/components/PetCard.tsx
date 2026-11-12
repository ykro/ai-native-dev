import { useState } from 'react';
import { motion, useMotionValue, useTransform, type PanInfo } from 'framer-motion';
import { Heart, X, Sparkles } from 'lucide-react';
import type { PetProfile } from '../services/petProvider';

interface PetCardProps {
    pet: PetProfile;
    onLike: () => void;
    onPass: () => void;
    isLoading?: boolean;
}

const SWIPE_THRESHOLD = 100;

export function PetCard({ pet, onLike, onPass, isLoading = false }: PetCardProps) {
    const [exitDirection, setExitDirection] = useState<'left' | 'right' | null>(null);
    const [imageLoaded, setImageLoaded] = useState(false);

    const x = useMotionValue(0);
    const rotate = useTransform(x, [-200, 200], [-25, 25]);
    const likeOpacity = useTransform(x, [0, 100], [0, 1]);
    const passOpacity = useTransform(x, [-100, 0], [1, 0]);

    const handleDragEnd = (_: MouseEvent | TouchEvent | PointerEvent, info: PanInfo) => {
        const offset = info.offset.x;
        const velocity = info.velocity.x;

        if (offset > SWIPE_THRESHOLD || velocity > 500) {
            setExitDirection('right');
            onLike();
        } else if (offset < -SWIPE_THRESHOLD || velocity < -500) {
            setExitDirection('left');
            onPass();
        }
    };

    return (
        <motion.div
            className="absolute w-full max-w-sm cursor-grab active:cursor-grabbing touch-none"
            style={{ x, rotate }}
            drag="x"
            dragConstraints={{ left: 0, right: 0 }}
            dragElastic={0.9}
            onDragEnd={handleDragEnd}
            initial={{ scale: 0.95, opacity: 0, y: 20 }}
            animate={{
                scale: 1,
                opacity: 1,
                y: 0,
                x: exitDirection === 'right' ? 500 : exitDirection === 'left' ? -500 : 0
            }}
            exit={{
                x: exitDirection === 'right' ? 500 : exitDirection === 'left' ? -500 : 0,
                opacity: 0,
                scale: exitDirection ? 0.8 : 0.95,
                transition: { duration: 0.3 }
            }}
            transition={{
                type: 'spring',
                stiffness: 300,
                damping: 25,
                opacity: { duration: 0.2 }
            }}
            whileTap={{ scale: 1.02 }}
        >
            {/* Glassmorphism Card */}
            <div className="relative overflow-hidden rounded-3xl bg-white/70 backdrop-blur-xl border border-white/50 shadow-2xl shadow-warm-900/10">

                {/* Swipe Indicators */}
                <motion.div
                    className="absolute top-8 left-8 z-20 flex items-center gap-2 px-4 py-2 bg-red-500/90 backdrop-blur-sm rounded-full border-2 border-red-400 shadow-lg"
                    style={{ opacity: passOpacity }}
                >
                    <X className="w-6 h-6 text-white" strokeWidth={3} />
                    <span className="text-white font-bold text-lg tracking-wide">NOPE</span>
                </motion.div>

                <motion.div
                    className="absolute top-8 right-8 z-20 flex items-center gap-2 px-4 py-2 bg-friendly-500/90 backdrop-blur-sm rounded-full border-2 border-friendly-400 shadow-lg"
                    style={{ opacity: likeOpacity }}
                >
                    <Heart className="w-6 h-6 text-white" fill="white" strokeWidth={3} />
                    <span className="text-white font-bold text-lg tracking-wide">ME GUSTA</span>
                </motion.div>

                {/* Pet Image */}
                <div className="relative aspect-[4/5] w-full overflow-hidden bg-gradient-to-br from-warm-100 to-warm-200">
                    {!imageLoaded && (
                        <div className="absolute inset-0 flex items-center justify-center">
                            <motion.div
                                animate={{ rotate: 360 }}
                                transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                                className="w-12 h-12 border-4 border-warm-300 border-t-warm-600 rounded-full"
                            />
                        </div>
                    )}
                    <motion.img
                        src={pet.imageUrl}
                        alt={pet.name}
                        className={`w-full h-full object-cover transition-opacity duration-500 ${
                            imageLoaded ? 'opacity-100' : 'opacity-0'
                        }`}
                        onLoad={() => setImageLoaded(true)}
                        draggable={false}
                    />

                    {/* Gradient Overlay */}
                    <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />

                    {/* Pet Name Overlay */}
                    <div className="absolute bottom-0 left-0 right-0 p-6">
                        <div className="flex items-center gap-2">
                            <h2 className="text-3xl font-bold text-white drop-shadow-lg">
                                {pet.name}
                            </h2>
                            <Sparkles className="w-6 h-6 text-primary-400" />
                        </div>
                    </div>
                </div>

                {/* Bio Section with Glassmorphism */}
                <div className="p-6 bg-gradient-to-b from-white/80 to-white/60 backdrop-blur-md">
                    <div className="space-y-2 mb-6">
                        {pet.bio.split('\n').map((line, i) => (
                            <p key={i} className="text-warm-700 text-sm leading-relaxed">
                                {line}
                            </p>
                        ))}
                    </div>

                    {/* Action Buttons */}
                    <div className="flex gap-4 justify-center">
                        <motion.button
                            onClick={onPass}
                            disabled={isLoading}
                            className="flex-1 flex items-center justify-center gap-2 px-6 py-4 bg-white/80 backdrop-blur-sm text-red-500 rounded-2xl font-bold border border-red-100 shadow-lg shadow-red-100/50 disabled:opacity-50 disabled:cursor-not-allowed"
                            whileHover={{ scale: 1.02, backgroundColor: 'rgba(254, 226, 226, 0.9)' }}
                            whileTap={{ scale: 0.98 }}
                        >
                            <X className="w-5 h-5" strokeWidth={2.5} />
                            <span>Pasar</span>
                        </motion.button>

                        <motion.button
                            onClick={onLike}
                            disabled={isLoading}
                            className="flex-1 flex items-center justify-center gap-2 px-6 py-4 bg-gradient-to-r from-friendly-500 to-friendly-600 text-white rounded-2xl font-bold shadow-lg shadow-friendly-500/30 disabled:opacity-50 disabled:cursor-not-allowed"
                            whileHover={{ scale: 1.02, boxShadow: '0 20px 40px -12px rgba(56, 161, 105, 0.5)' }}
                            whileTap={{ scale: 0.98 }}
                        >
                            <Heart className="w-5 h-5" fill="currentColor" />
                            <span>Adoptar</span>
                        </motion.button>
                    </div>
                </div>
            </div>
        </motion.div>
    );
}
