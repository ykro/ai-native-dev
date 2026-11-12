import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "TraderPulse",
  description: "Panel de mercado con sentimiento generado por IA. Datos de ejemplo.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}
