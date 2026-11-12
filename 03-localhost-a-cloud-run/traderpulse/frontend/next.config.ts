import type { NextConfig } from "next";

const config: NextConfig = {
  // Salida autocontenida para la imagen de Cloud Run.
  output: "standalone",
};

export default config;
