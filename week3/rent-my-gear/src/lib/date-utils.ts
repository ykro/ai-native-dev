import {
  format,
  differenceInDays,
  addDays,
  isBefore,
  startOfDay,
  isValid,
  parseISO,
} from "date-fns";
import { es } from "date-fns/locale";

/**
 * Format a date for display in Spanish locale
 */
export function formatDate(date: Date, formatStr: string = "d 'de' MMMM, yyyy"): string {
  if (!isValid(date)) return "Fecha inválida";
  return format(date, formatStr, { locale: es });
}

/**
 * Format a date range for display
 */
export function formatDateRange(startDate: Date, endDate: Date): string {
  const start = formatDate(startDate, "d MMM");
  const end = formatDate(endDate, "d MMM yyyy");
  return `${start} - ${end}`;
}

/**
 * Calculate the number of rental days (inclusive)
 * Minimum 1 day rental
 */
export function calculateRentalDays(startDate: Date, endDate: Date): number {
  const days = differenceInDays(startDate, endDate);
  // Add 1 because rental is inclusive of both start and end dates
  return Math.abs(days) + 1;
}

/**
 * Calculate total rental price
 */
export function calculateTotalPrice(dailyRate: number, days: number): number {
  return dailyRate * days;
}

/**
 * Calculate rental price breakdown
 */
export function calculateRentalPrice(
  dailyRate: number,
  startDate: Date,
  endDate: Date
): {
  days: number;
  dailyRate: number;
  subtotal: number;
  total: number;
} {
  const days = calculateRentalDays(startDate, endDate);
  const subtotal = calculateTotalPrice(dailyRate, days);

  return {
    days,
    dailyRate,
    subtotal,
    total: subtotal, // Could add taxes/fees here in the future
  };
}

/**
 * Format price in Mexican Pesos
 */
export function formatPrice(amount: number): string {
  return new Intl.NumberFormat("es-MX", {
    style: "currency",
    currency: "MXN",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

/**
 * Check if a date is in the past
 */
export function isDateInPast(date: Date): boolean {
  const today = startOfDay(new Date());
  return isBefore(date, today);
}

/**
 * Check if a date range is valid for rental
 */
export function isValidRentalRange(startDate: Date, endDate: Date): boolean {
  const today = startOfDay(new Date());

  // Start date must be today or later
  if (isBefore(startDate, today)) return false;

  // End date must be same as or after start date
  if (isBefore(endDate, startDate)) return false;

  return true;
}

/**
 * Get the minimum selectable date (today)
 */
export function getMinSelectableDate(): Date {
  return startOfDay(new Date());
}

/**
 * Get a default end date (start date + 2 days)
 */
export function getDefaultEndDate(startDate: Date): Date {
  return addDays(startDate, 2);
}

/**
 * Parse an ISO date string safely
 */
export function parseDateSafe(dateString: string): Date | null {
  try {
    const date = parseISO(dateString);
    return isValid(date) ? date : null;
  } catch {
    return null;
  }
}

/**
 * Check if a date is available (mock implementation)
 * In a real app, this would check against a bookings database
 */
export function isDateAvailable(_date: Date, _gearId: string): boolean {
  // Mock: All dates are available
  // In production, check against reservations
  return true;
}

/**
 * Get unavailable dates for a gear item (mock implementation)
 * Returns an array of dates that are already booked
 */
export function getUnavailableDates(_gearId: string): Date[] {
  // Mock: No dates are unavailable
  // In production, fetch from database
  return [];
}
