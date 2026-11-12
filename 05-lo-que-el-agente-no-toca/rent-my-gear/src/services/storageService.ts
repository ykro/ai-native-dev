import { Storage } from "@google-cloud/storage";
import { getEnv } from "@/config/env";

// Lazy-initialized storage client
let storageClient: Storage | null = null;

/**
 * Get the GCS storage client
 * Initializes on first use to defer env validation
 */
function getStorageClient(): Storage {
  if (storageClient === null) {
    const env = getEnv();
    storageClient = new Storage({
      projectId: env.GCS_PROJECT_ID,
      keyFilename: env.GOOGLE_APPLICATION_CREDENTIALS,
    });
  }
  return storageClient;
}

/**
 * Get the bucket instance
 */
function getBucket() {
  const env = getEnv();
  return getStorageClient().bucket(env.GCS_BUCKET_NAME);
}

/**
 * Generate a unique filename for uploaded images
 */
function generateFilename(gearId: string, extension: string = "png"): string {
  const timestamp = Date.now();
  const random = Math.random().toString(36).substring(2, 8);
  return `gear-images/${gearId}-${timestamp}-${random}.${extension}`;
}

/**
 * Upload an image buffer to GCS
 * Returns the public URL of the uploaded file
 */
export async function uploadImage(
  buffer: Buffer,
  gearId: string,
  contentType: string = "image/png"
): Promise<string> {
  const env = getEnv();
  const bucket = getBucket();
  const extension = contentType.split("/")[1] || "png";
  const filename = generateFilename(gearId, extension);

  const file = bucket.file(filename);

  await file.save(buffer, {
    contentType,
    metadata: {
      cacheControl: "public, max-age=31536000", // 1 year cache
      metadata: {
        gearId,
        generatedBy: "nano-banana",
        generatedAt: new Date().toISOString(),
      },
    },
  });

  // Make the file publicly accessible
  await file.makePublic();

  // Return the public URL
  const publicUrl = `https://storage.googleapis.com/${env.GCS_BUCKET_NAME}/${filename}`;
  return publicUrl;
}

/**
 * Upload an image from base64 string
 */
export async function uploadImageFromBase64(
  base64Data: string,
  gearId: string,
  contentType: string = "image/png"
): Promise<string> {
  // Remove data URL prefix if present
  const base64Clean = base64Data.replace(/^data:image\/\w+;base64,/, "");
  const buffer = Buffer.from(base64Clean, "base64");

  return uploadImage(buffer, gearId, contentType);
}

/**
 * Delete an image from GCS
 */
export async function deleteImage(filename: string): Promise<void> {
  const bucket = getBucket();
  const file = bucket.file(filename);

  try {
    await file.delete();
  } catch (error) {
    console.error(`Failed to delete file ${filename}:`, error);
    throw new Error(`Could not delete image: ${filename}`);
  }
}

/**
 * Check if a file exists in the bucket
 */
export async function fileExists(filename: string): Promise<boolean> {
  const bucket = getBucket();
  const file = bucket.file(filename);

  try {
    const [exists] = await file.exists();
    return exists;
  } catch {
    return false;
  }
}

/**
 * List all gear images in the bucket
 */
export async function listGearImages(): Promise<string[]> {
  const bucket = getBucket();

  try {
    const [files] = await bucket.getFiles({ prefix: "gear-images/" });
    return files.map((file) => file.name);
  } catch (error) {
    console.error("Failed to list gear images:", error);
    return [];
  }
}

/**
 * Get the public URL for a file in the bucket
 */
export function getPublicUrl(filename: string): string {
  const env = getEnv();
  return `https://storage.googleapis.com/${env.GCS_BUCKET_NAME}/${filename}`;
}

/**
 * Extract filename from a GCS public URL
 */
export function extractFilenameFromUrl(url: string): string | null {
  const env = getEnv();
  const prefix = `https://storage.googleapis.com/${env.GCS_BUCKET_NAME}/`;

  if (url.startsWith(prefix)) {
    return url.slice(prefix.length);
  }

  return null;
}
