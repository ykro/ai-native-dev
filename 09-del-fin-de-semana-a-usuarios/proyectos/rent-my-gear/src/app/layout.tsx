import type { Metadata } from "next";
import Link from "next/link";
import { Geist, Geist_Mono } from "next/font/google";
import { Toaster } from "@/components/ui/sonner";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Rent my Gear | Alquiler de Equipo Premium",
  description:
    "Marketplace de alquiler de equipo profesional para fotografía, montaña y deportes acuáticos.",
  keywords: [
    "alquiler equipo",
    "renta cámaras",
    "equipo fotografía",
    "camping",
    "deportes acuáticos",
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased min-h-screen bg-background`}
      >
        <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
          <div className="container mx-auto flex h-16 items-center px-4">
            <Link href="/" className="flex items-center gap-2">
              <span className="text-xl font-bold tracking-tight">
                Rent my Gear
              </span>
            </Link>
            <nav className="ml-auto flex items-center gap-6">
              <Link
                href="/category/fotografia-video"
                className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
              >
                Fotografía
              </Link>
              <Link
                href="/category/montana-camping"
                className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
              >
                Montaña
              </Link>
              <Link
                href="/category/deportes-acuaticos"
                className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
              >
                Acuáticos
              </Link>
            </nav>
          </div>
        </header>
        <main className="flex-1">{children}</main>
        <footer className="border-t py-8 mt-12">
          <div className="container mx-auto px-4 text-center text-sm text-muted-foreground">
            <p>&copy; {new Date().getFullYear()} Rent my Gear. Todos los derechos reservados.</p>
          </div>
        </footer>
        <Toaster position="top-center" richColors />
      </body>
    </html>
  );
}
