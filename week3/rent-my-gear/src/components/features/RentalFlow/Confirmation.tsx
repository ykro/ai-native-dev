"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { CheckCircle, Calendar, ArrowRight } from "lucide-react";
import { GearItem } from "@/lib/validation";
import { formatDateRange } from "@/lib/date-utils";
import type { RentalDates } from "./index";

interface ConfirmationProps {
  item: GearItem;
  dates: RentalDates;
  confirmationId: string | null;
  onReset: () => void;
}

export function Confirmation({
  item,
  dates,
  confirmationId,
  onReset,
}: ConfirmationProps) {
  return (
    <Card className="overflow-hidden">
      {/* Success header */}
      <div className="bg-gradient-to-r from-emerald-500 to-green-600 text-white p-6 text-center">
        <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-white/20 flex items-center justify-center">
          <CheckCircle className="w-10 h-10" />
        </div>
        <h3 className="text-2xl font-bold mb-2">¡Renta Confirmada!</h3>
        <p className="text-white/90">
          Tu reservación ha sido procesada exitosamente
        </p>
      </div>

      <CardContent className="p-6 space-y-6">
        {/* Confirmation ID */}
        {confirmationId && (
          <div className="text-center py-4 bg-muted/50 rounded-lg">
            <p className="text-sm text-muted-foreground mb-1">
              Número de confirmación
            </p>
            <p className="text-lg font-mono font-bold tracking-wider">
              {confirmationId}
            </p>
          </div>
        )}

        {/* Rental details */}
        <div className="space-y-4">
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
              <Calendar className="w-5 h-5 text-primary" />
            </div>
            <div>
              <p className="font-medium">{item.name}</p>
              <p className="text-sm text-muted-foreground">
                {formatDateRange(dates.startDate, dates.endDate)}
              </p>
            </div>
          </div>
        </div>

        {/* Next steps */}
        <div className="bg-blue-50 dark:bg-blue-950/30 rounded-lg p-4 space-y-2">
          <h4 className="font-medium text-blue-900 dark:text-blue-100">
            Próximos pasos
          </h4>
          <ul className="text-sm text-blue-800 dark:text-blue-200 space-y-1">
            <li className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-500" />
              Recibirás un correo con los detalles de tu renta
            </li>
            <li className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-500" />
              Presenta tu confirmación al recoger el equipo
            </li>
            <li className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-500" />
              Revisa el equipo antes de retirarlo
            </li>
          </ul>
        </div>

        {/* Actions */}
        <div className="flex flex-col sm:flex-row gap-3">
          <Button
            variant="outline"
            className="flex-1"
            onClick={onReset}
          >
            Rentar Otro Equipo
          </Button>
          <Link href="/" className="flex-1">
            <Button className="w-full gap-2">
              Volver al Inicio
              <ArrowRight className="w-4 h-4" />
            </Button>
          </Link>
        </div>
      </CardContent>
    </Card>
  );
}
