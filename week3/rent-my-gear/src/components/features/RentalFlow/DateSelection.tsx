"use client";

import { useState } from "react";
import { Calendar } from "@/components/ui/calendar";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowLeft, CalendarDays } from "lucide-react";
import { validateRentalDates } from "@/lib/validation";
import {
  getMinSelectableDate,
  formatDate,
  calculateRentalDays,
} from "@/lib/date-utils";
import type { RentalDates } from "./index";
import type { DateRange } from "react-day-picker";

interface DateSelectionProps {
  initialDates: RentalDates | null;
  onSelect: (dates: RentalDates) => void;
  onBack: () => void;
}

export function DateSelection({
  initialDates,
  onSelect,
  onBack,
}: DateSelectionProps) {
  const minDate = getMinSelectableDate();

  const [dateRange, setDateRange] = useState<DateRange | undefined>(() => {
    if (initialDates) {
      return {
        from: initialDates.startDate,
        to: initialDates.endDate,
      };
    }
    return undefined;
  });

  const [error, setError] = useState<string | null>(null);

  const handleSelect = (range: DateRange | undefined) => {
    setDateRange(range);
    setError(null);
  };

  const handleContinue = () => {
    if (!dateRange?.from || !dateRange?.to) {
      setError("Por favor selecciona un rango de fechas");
      return;
    }

    const validation = validateRentalDates(dateRange.from, dateRange.to);

    if (!validation.success) {
      const firstError = validation.error.issues[0];
      setError(firstError.message);
      return;
    }

    onSelect({
      startDate: dateRange.from,
      endDate: dateRange.to,
    });
  };

  const days =
    dateRange?.from && dateRange?.to
      ? calculateRentalDays(dateRange.from, dateRange.to)
      : 0;

  return (
    <Card>
      <CardHeader className="pb-4">
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="icon" onClick={onBack}>
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <CardTitle className="text-lg flex items-center gap-2">
            <CalendarDays className="w-5 h-5" />
            Seleccionar Fechas
          </CardTitle>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        <div className="flex justify-center">
          <Calendar
            mode="range"
            selected={dateRange}
            onSelect={handleSelect}
            numberOfMonths={1}
            disabled={{ before: minDate }}
            className="rounded-md border"
          />
        </div>

        {dateRange?.from && dateRange?.to && (
          <div className="bg-muted/50 rounded-lg p-4 space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Fecha inicio:</span>
              <span className="font-medium">{formatDate(dateRange.from)}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Fecha fin:</span>
              <span className="font-medium">{formatDate(dateRange.to)}</span>
            </div>
            <div className="flex justify-between text-sm pt-2 border-t">
              <span className="text-muted-foreground">Total días:</span>
              <span className="font-semibold text-primary">
                {days} {days === 1 ? "día" : "días"}
              </span>
            </div>
          </div>
        )}

        {error && (
          <p className="text-sm text-destructive text-center">{error}</p>
        )}

        <Button
          onClick={handleContinue}
          className="w-full h-12"
          disabled={!dateRange?.from || !dateRange?.to}
        >
          Continuar al Resumen
        </Button>
      </CardContent>
    </Card>
  );
}
