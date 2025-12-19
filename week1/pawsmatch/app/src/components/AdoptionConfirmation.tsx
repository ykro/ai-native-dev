import { motion } from 'framer-motion';
import { Heart, Phone, Mail, MapPin, Calendar, ArrowLeft, CheckCircle } from 'lucide-react';
import type { PetProfile } from '../services/petProvider';

interface AdoptionConfirmationProps {
    pet: PetProfile;
    onBack: () => void;
    onConfirm: () => void;
}

export function AdoptionConfirmation({ pet, onBack, onConfirm }: AdoptionConfirmationProps) {
    return (
        <motion.div
            className="w-full max-w-md mx-auto"
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -50 }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
        >
            {/* Success Header */}
            <motion.div
                className="text-center mb-6"
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: 'spring', stiffness: 200, delay: 0.2 }}
            >
                <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-gradient-to-br from-friendly-400 to-friendly-600 flex items-center justify-center shadow-lg shadow-friendly-500/30">
                    <Heart className="w-10 h-10 text-white" fill="white" />
                </div>
                <h2 className="text-2xl font-bold text-warm-800">¡Te gusta {pet.name}!</h2>
                <p className="text-warm-500 mt-1">¿Listo para conocer a tu nuevo mejor amigo?</p>
            </motion.div>

            {/* Pet Card Preview */}
            <motion.div
                className="bg-white/70 backdrop-blur-xl rounded-3xl border border-white/50 shadow-xl overflow-hidden mb-6"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
            >
                <div className="flex gap-4 p-4">
                    <img
                        src={pet.imageUrl}
                        alt={pet.name}
                        className="w-24 h-24 rounded-2xl object-cover"
                    />
                    <div className="flex-1 min-w-0">
                        <h3 className="text-xl font-bold text-warm-800">{pet.name}</h3>
                        <p className="text-warm-600 text-sm mt-1 line-clamp-3">
                            {pet.bio.split('\n')[0]}
                        </p>
                    </div>
                </div>
            </motion.div>

            {/* Adoption Info */}
            <motion.div
                className="bg-white/70 backdrop-blur-xl rounded-3xl border border-white/50 shadow-xl p-6 mb-6"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
            >
                <h3 className="text-lg font-bold text-warm-800 mb-4">Información de Adopción</h3>

                <div className="space-y-4">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-friendly-100 flex items-center justify-center">
                            <MapPin className="w-5 h-5 text-friendly-600" />
                        </div>
                        <div>
                            <p className="text-sm text-warm-500">Ubicación</p>
                            <p className="text-warm-800 font-medium">Refugio PawsMatch</p>
                        </div>
                    </div>

                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-friendly-100 flex items-center justify-center">
                            <Phone className="w-5 h-5 text-friendly-600" />
                        </div>
                        <div>
                            <p className="text-sm text-warm-500">Teléfono</p>
                            <p className="text-warm-800 font-medium">+502 1234-5678</p>
                        </div>
                    </div>

                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-friendly-100 flex items-center justify-center">
                            <Mail className="w-5 h-5 text-friendly-600" />
                        </div>
                        <div>
                            <p className="text-sm text-warm-500">Correo</p>
                            <p className="text-warm-800 font-medium">adopta@pawsmatch.com</p>
                        </div>
                    </div>

                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-friendly-100 flex items-center justify-center">
                            <Calendar className="w-5 h-5 text-friendly-600" />
                        </div>
                        <div>
                            <p className="text-sm text-warm-500">Horario de Visitas</p>
                            <p className="text-warm-800 font-medium">Lun-Sáb, 9AM - 6PM</p>
                        </div>
                    </div>
                </div>
            </motion.div>

            {/* Action Buttons */}
            <motion.div
                className="flex gap-4"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
            >
                <motion.button
                    onClick={onBack}
                    className="flex-1 flex items-center justify-center gap-2 px-6 py-4 bg-white/80 backdrop-blur-sm text-warm-600 rounded-2xl font-bold border border-warm-200 shadow-lg"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                >
                    <ArrowLeft className="w-5 h-5" />
                    <span>Seguir Viendo</span>
                </motion.button>

                <motion.button
                    onClick={onConfirm}
                    className="flex-1 flex items-center justify-center gap-2 px-6 py-4 bg-gradient-to-r from-friendly-500 to-friendly-600 text-white rounded-2xl font-bold shadow-lg shadow-friendly-500/30"
                    whileHover={{ scale: 1.02, boxShadow: '0 20px 40px -12px rgba(56, 161, 105, 0.5)' }}
                    whileTap={{ scale: 0.98 }}
                >
                    <CheckCircle className="w-5 h-5" />
                    <span>Agendar Visita</span>
                </motion.button>
            </motion.div>
        </motion.div>
    );
}
