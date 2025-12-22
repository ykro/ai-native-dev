import { z } from "zod";

/**
 * Category IDs used in the application
 */
export const CATEGORY_IDS = [
  "fotografia-video",
  "montana-camping",
  "deportes-acuaticos",
] as const;

export type CategoryId = (typeof CATEGORY_IDS)[number];

/**
 * Category display information (Spanish UI)
 */
export const CATEGORIES: Record<CategoryId, { name: string; description: string }> = {
  "fotografia-video": {
    name: "Fotografía y Video",
    description: "Cámaras, lentes, iluminación y equipo audiovisual profesional",
  },
  "montana-camping": {
    name: "Montaña y Camping",
    description: "Tiendas, mochilas, equipo técnico de montaña y accesorios de camping",
  },
  "deportes-acuaticos": {
    name: "Deportes Acuáticos",
    description: "Kayaks, SUP, equipo de buceo, surf y deportes náuticos",
  },
};

/**
 * Schema for gear item specifications
 */
export const gearSpecsSchema = z.record(z.string(), z.union([z.string(), z.number()]));

/**
 * Schema for a gear item from inventory
 */
export const gearItemSchema = z.object({
  id: z.string().min(1, "ID is required"),
  name: z.string().min(1, "Name is required"),
  category: z.enum(CATEGORY_IDS),
  description: z.string(),
  specs: gearSpecsSchema,
  dailyRate: z.number().positive("Daily rate must be positive"),
  imageURL: z.string().url().nullable(),
});

export type GearItem = z.infer<typeof gearItemSchema>;

/**
 * Schema for rental date selection
 * Validates that dates are not in the past and end date is after start date
 */
export const rentalDatesSchema = z
  .object({
    startDate: z.date(),
    endDate: z.date(),
  })
  .refine(
    (data) => {
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      return data.startDate >= today;
    },
    {
      message: "La fecha de inicio no puede ser en el pasado",
      path: ["startDate"],
    }
  )
  .refine(
    (data) => {
      return data.endDate >= data.startDate;
    },
    {
      message: "La fecha de fin debe ser igual o posterior a la fecha de inicio",
      path: ["endDate"],
    }
  );

export type RentalDates = z.infer<typeof rentalDatesSchema>;

/**
 * Schema for a complete rental request
 */
export const rentalRequestSchema = z.object({
  gearId: z.string().min(1, "Gear ID is required"),
  startDate: z.string().datetime(),
  endDate: z.string().datetime(),
  customerName: z.string().min(2, "El nombre debe tener al menos 2 caracteres"),
  customerEmail: z.string().email("Email inválido"),
});

export type RentalRequest = z.infer<typeof rentalRequestSchema>;

/**
 * Schema for rental confirmation response
 */
export const rentalConfirmationSchema = z.object({
  id: z.string(),
  gearId: z.string(),
  gearName: z.string(),
  startDate: z.string(),
  endDate: z.string(),
  totalDays: z.number(),
  dailyRate: z.number(),
  totalPrice: z.number(),
  status: z.enum(["confirmed", "pending", "cancelled"]),
  createdAt: z.string(),
});

export type RentalConfirmation = z.infer<typeof rentalConfirmationSchema>;

/**
 * Validate a gear item from inventory
 */
export function validateGearItem(data: unknown): GearItem {
  return gearItemSchema.parse(data);
}

/**
 * Validate rental dates (returns result object instead of throwing)
 */
export function validateRentalDates(startDate: Date, endDate: Date) {
  return rentalDatesSchema.safeParse({ startDate, endDate });
}

/**
 * Check if a category ID is valid
 */
export function isValidCategory(id: string): id is CategoryId {
  return CATEGORY_IDS.includes(id as CategoryId);
}
