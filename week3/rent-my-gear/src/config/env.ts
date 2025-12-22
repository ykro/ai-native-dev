import { z } from "zod";

/**
 * Environment variables schema for server-side validation.
 * Validates all required GCS and AI API configuration at runtime.
 */
const envSchema = z.object({
  // Google Cloud Storage configuration
  GCS_BUCKET_NAME: z
    .string()
    .min(3, "GCS_BUCKET_NAME must be at least 3 characters")
    .max(63, "GCS_BUCKET_NAME must be at most 63 characters")
    .regex(
      /^[a-z0-9][a-z0-9-_.]*[a-z0-9]$/,
      "GCS_BUCKET_NAME must start and end with a letter or number, and can only contain lowercase letters, numbers, hyphens, underscores, and dots"
    ),

  GCS_PROJECT_ID: z
    .string()
    .min(6, "GCS_PROJECT_ID must be at least 6 characters")
    .max(30, "GCS_PROJECT_ID must be at most 30 characters"),

  GOOGLE_APPLICATION_CREDENTIALS: z
    .string()
    .min(1, "GOOGLE_APPLICATION_CREDENTIALS cannot be empty"),

  // Nano Banana (Gemini) API configuration
  NANO_BANANA_API_KEY: z
    .string()
    .min(1, "NANO_BANANA_API_KEY cannot be empty"),
});

export type Env = z.infer<typeof envSchema>;

/**
 * Validates environment variables and returns the typed config.
 * Throws a descriptive error if validation fails.
 */
function validateEnv(): Env {
  const result = envSchema.safeParse({
    GCS_BUCKET_NAME: process.env.GCS_BUCKET_NAME,
    GCS_PROJECT_ID: process.env.GCS_PROJECT_ID,
    GOOGLE_APPLICATION_CREDENTIALS: process.env.GOOGLE_APPLICATION_CREDENTIALS,
    NANO_BANANA_API_KEY: process.env.NANO_BANANA_API_KEY,
  });

  if (!result.success) {
    const errors = result.error.issues
      .map((issue) => `  - ${issue.path.join(".")}: ${issue.message}`)
      .join("\n");

    throw new Error(
      `\n\n❌ Environment validation failed:\n${errors}\n\n` +
        `Please check your .env.local file and ensure all required variables are set.\n` +
        `See .env.example for reference.\n`
    );
  }

  return result.data;
}

/**
 * Lazy-loaded environment configuration.
 * Only validates when first accessed, allowing for graceful error handling.
 */
let _env: Env | null = null;

export function getEnv(): Env {
  if (_env === null) {
    _env = validateEnv();
  }
  return _env;
}

/**
 * Check if environment is configured (without throwing).
 * Useful for conditional rendering or feature flags.
 */
export function isEnvConfigured(): boolean {
  try {
    getEnv();
    return true;
  } catch {
    return false;
  }
}
