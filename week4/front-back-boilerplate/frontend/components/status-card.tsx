"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Loader2 } from "lucide-react"

interface StatusCardProps {
    initialStatus: string
    initialEnvironment?: string
}

export function StatusCard({ initialStatus }: StatusCardProps) {
    const [status, setStatus] = useState(initialStatus)
    const [loading, setLoading] = useState(false)

    const checkHealth = async () => {
        setLoading(true)
        try {
            // Use client-side fetch to revalidate
            const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/health`)
            if (res.ok) {
                const data = await res.json()
                setStatus(data.status === "active" ? "active" : "error")
            } else {
                setStatus("error")
            }
        } catch (e) {
            setStatus("error")
        } finally {
            setLoading(false)
        }
    }

    const isConnected = status === "active"

    return (
        <Card className="w-[350px] shadow-lg">
            <CardHeader>
                <CardTitle className="text-center">Estado del Sistema</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
                <div className="flex justify-between items-center p-4 bg-slate-100 rounded-lg">
                    <span className="font-medium">Backend:</span>
                    <Badge
                        variant={isConnected ? "default" : "destructive"}
                        className={isConnected ? "bg-green-600 hover:bg-green-700" : ""}
                    >
                        {isConnected ? "Activo" : "Inactivo"}
                    </Badge>
                </div>

                <Button
                    onClick={checkHealth}
                    disabled={loading}
                    className="w-full"
                    variant="outline"
                >
                    {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                    Reintentar Conexión
                </Button>
            </CardContent>
        </Card>
    )
}
