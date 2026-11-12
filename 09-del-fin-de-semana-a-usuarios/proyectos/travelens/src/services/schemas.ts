import { z } from "zod";

export const ItineraryDaySchema = z.object({
  day: z.number().int().positive(),
  title: z.string().trim().min(1),
  activities: z.array(z.string().trim().min(1)).min(1),
});

export const ItineraryResponseSchema = z.object({
  intro: z.string().trim().min(1),
  days: z.array(ItineraryDaySchema).length(3),
  hiddenGem: z.object({
    title: z.string().trim().min(1),
    description: z.string().trim().min(1),
  }),
  localFood: z.object({
    dish: z.string().trim().min(1),
    description: z.string().trim().min(1),
  }),
});

export type TravelPlan = z.infer<typeof ItineraryResponseSchema>;
