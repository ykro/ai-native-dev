import type { PetProfile } from '../services/petProvider';

interface PetCardProps {
    pet: PetProfile;
    onAdopt: () => void;
    onNext: () => void;
    isLoading?: boolean;
}

export function PetCard({ pet, onAdopt, onNext, isLoading = false }: PetCardProps) {
    return (
        <div className="bg-white rounded-3xl shadow-xl overflow-hidden border-4 border-warm-100 max-w-sm w-full mx-auto transition-all hover:shadow-2xl">
            <div className="relative aspect-square w-full overflow-hidden bg-warm-100">
                <img
                    src={pet.imageUrl}
                    alt={pet.name}
                    className={`w-full h-full object-cover transition-opacity duration-300 ${isLoading ? 'opacity-50 blur-sm' : 'opacity-100'
                        }`}
                    loading="lazy"
                />
                {isLoading && (
                    <div className="absolute inset-0 flex items-center justify-center">
                        <div className="animate-spin rounded-full h-12 w-12 border-4 border-warm-500 border-t-transparent"></div>
                    </div>
                )}
            </div>

            <div className="p-6 text-center">
                <h2 className="text-3xl font-bold text-warm-800 mb-2">{pet.name}</h2>

                <div className="space-y-2 mb-8">
                    {pet.bio.split('\n').map((line, i) => (
                        <p key={i} className="text-warm-600 text-sm leading-relaxed">
                            {line}
                        </p>
                    ))}
                </div>

                <div className="flex gap-4 justify-center">
                    <button
                        onClick={onNext}
                        disabled={isLoading}
                        className="flex-1 px-6 py-3 bg-red-100 text-red-600 rounded-full font-bold hover:bg-red-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        Pass
                    </button>
                    <button
                        onClick={onAdopt}
                        disabled={isLoading}
                        className="flex-1 px-6 py-3 bg-friendly-500 text-white rounded-full font-bold hover:bg-friendly-600 transition-colors shadow-lg hover:shadow-friendly-200 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        Adopt!
                    </button>
                </div>
            </div>
        </div>
    );
}
