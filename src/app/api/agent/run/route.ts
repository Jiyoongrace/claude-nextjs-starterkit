import { NextRequest, NextResponse } from "next/server"
import { mockAgent } from "@/lib/mock-agents"

const FASTAPI_URL = process.env.FASTAPI_URL ?? "http://localhost:8000"
const USE_MOCK = process.env.USE_MOCK_AGENT === "true"

export async function POST(req: NextRequest) {
  const body = await req.json()
  const { scenario_id, params } = body

  // USE_MOCK_AGENT=true가 아니면 FastAPI 호출 시도
  if (!USE_MOCK) {
    try {
      const response = await fetch(`${FASTAPI_URL}/agent/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scenario_id, params: params ?? {} }),
        signal: AbortSignal.timeout(30_000),
      })

      if (response.ok) {
        const data = await response.json()
        return NextResponse.json(data)
      }

      // FastAPI 500 에러는 그대로 전파 (Mock 폴백 없음)
      const error = await response.json().catch(() => ({ detail: "FastAPI 오류" }))
      return NextResponse.json(error, { status: response.status })

    } catch {
      // ECONNREFUSED(서버 미실행) 또는 타임아웃 → Mock 폴백
      console.warn("[agent/run] FastAPI 연결 실패 → Mock 폴백 (FASTAPI_URL:", FASTAPI_URL, ")")
    }
  }

  // Mock 폴백: mock-agents.ts 직접 호출
  const result = await mockAgent(scenario_id, params ?? {})
  return NextResponse.json(result)
}
