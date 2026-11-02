import { StatusCard } from "@/components/status-card"
import { env } from "@/lib/env"

async function getHealth() {
  try {
    const res = await fetch(`${env.NEXT_PUBLIC_API_URL}/api/v1/health`, { cache: "no-store" })
    if (!res.ok) return { status: "error" }
    return await res.json()
  } catch (e) {
    return { status: "error" }
  }
}

export default async function Page() {
  const health = await getHealth()

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8 bg-slate-50">
      <div className="z-10 max-w-5xl w-full flex flex-col items-center justify-between font-mono text-sm">
        <h1 className="text-4xl font-bold mb-12 text-slate-900 tracking-tight">Dashboard de Control</h1>

        <StatusCard
          initialStatus={health.status}
        />

        <p className="mt-8 text-slate-500">
          Frontend: Next.js 16 | Backend: FastAPI (Python 3.14)
        </p>
      </div>
    </main>
  )
}
