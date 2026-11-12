"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowLeft, Receipt, Loader2 } from "lucide-react";
import { GearItem } from "@/lib/validation";
import {
  formatDate,
  formatPrice,
  calculateRentalPrice,
} from "@/lib/date-utils";
import type { RentalDates } from "./index";

interface PriceSummaryProps {
  item: GearItem;
  dates: RentalDates;
  onConfirm: () => Promise<void>;
  onBack: () => void;
}

export function PriceSummary({
  item,
  dates,
  onConfirm,
  onBack,
}: PriceSummaryProps) {
  const [isLoading, setIsLoading] = useState(false);

  const pricing = calculateRentalPrice(
    item.dailyRate,
    dates.startDate,
    dates.endDate
  );

  const handleConfirm = async () => {
    setIsLoading(true);
    try {
      await onConfirm();
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader className="pb-4">
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="icon" onClick={onBack} disabled={isLoading}>
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <CardTitle className="text-lg flex items-center gap-2">
            <Receipt className="w-5 h-5" />
            Resumen de Renta
          </CardTitle>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Item details */}
        <div className="bg-muted/50 rounded-lg p-4">
          <h4 className="font-semibold mb-2">{item.name}</h4>
          <p className="text-sm text-muted-foreground">{item.description}</p>
        </div>

        {/* Dates */}
        <div className="space-y-2">
          <h4 className="font-medium text-sm text-muted-foreground uppercase tracking-wide">
            Período de Renta
          </h4>
          <div className="flex justify-between items-center py-2 border-b">
            <span className="text-muted-foreground">Fecha inicio</span>
            <span className="font-medium">{formatDate(dates.startDate)}</span>
          </div>
          <div className="flex justify-between items-center py-2 border-b">
            <span className="text-muted-foreground">Fecha fin</span>
            <span className="font-medium">{formatDate(dates.endDate)}</span>
          </div>
          <div className="flex justify-between items-center py-2">
            <span className="text-muted-foreground">Duración</span>
            <span className="font-medium">
              {pricing.days} {pricing.days === 1 ? "día" : "días"}
            </span>
          </div>
        </div>

        {/* Pricing breakdown */}
        <div className="space-y-2">
          <h4 className="font-medium text-sm text-muted-foreground uppercase tracking-wide">
            Desglose de Precio
          </h4>
          <div className="flex justify-between items-center py-2 border-b">
            <span className="text-muted-foreground">
              Tarifa diaria
            </span>
            <span className="font-medium">{formatPrice(pricing.dailyRate)}</span>
          </div>
          <div className="flex justify-between items-center py-2 border-b">
            <span className="text-muted-foreground">
              {formatPrice(pricing.dailyRate)} x {pricing.days} días
            </span>
            <span className="font-medium">{formatPrice(pricing.subtotal)}</span>
          </div>
          <div className="flex justify-between items-center py-3 bg-primary/5 rounded-lg px-3 -mx-3">
            <span className="font-semibold text-lg">Total</span>
            <span className="font-bold text-xl text-primary">
              {formatPrice(pricing.total)}
            </span>
          </div>
        </div>

        {/* Confirm button */}
        <Button
          onClick={handleConfirm}
          className="w-full h-12"
          disabled={isLoading}
        >
          {isLoading ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Procesando...
            </>
          ) : (
            "Confirmar Renta"
          )}
        </Button>

        <p className="text-xs text-center text-muted-foreground">
          Al confirmar, aceptas los términos y condiciones del servicio de renta.
        </p>
      </CardContent>
    </Card>
  );
}
