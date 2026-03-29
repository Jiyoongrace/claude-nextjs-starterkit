"use client"

import { useState } from "react"
import { Play, Loader2 } from "lucide-react"
import { cn } from "@/lib/utils"
import { SCENARIOS, AGENT_BADGE_COLORS } from "@/lib/scenarios"
import { ScenarioId } from "@/lib/scenarios"
import { useWorkspace } from "@/lib/workspace-context"
import { AgentResponse } from "./RichRenderer"

interface Props {
  scenarioId: ScenarioId
}

export function ScenarioPanel({ scenarioId }: Props) {
  const { setMode } = useWorkspace()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const scenario = SCENARIOS.find(s => s.id === scenarioId)!

  // 각 시나리오별 폼 파라미터 상태
  const [params, setParams] = useState<Record<string, string>>({
    // S1
    error_code: "DG320", width: "1200", thickness: "8.5",
    // S2
    edging_value: "",
    // S3
    job_id: "JOB-2025-0325", date_from: "2025-03-20", date_to: "2025-03-26",
    // S4
    term: "",
    // S5
    factory_name: "HOT_MILL_3", systems: "",
    // S6
    requester: "", screen_id: "SCR_QUALITY_MGR", permission_level: "READ_WRITE",
    // S7
    service_a: "ORDER_DB", service_b: "PROD_DB",
  })

  function set(key: string, value: string) {
    setParams(p => ({ ...p, [key]: value }))
  }

  async function handleRun() {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch("/api/agent/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scenario_id: scenarioId, params }),
      })
      const data = await res.json()
      if (!res.ok) {
        setError(data.detail ?? `오류 발생 (${res.status})`)
        return
      }
      setMode({ type: "result", scenarioId, result: data as AgentResponse })
    } catch (e) {
      setError("서버에 연결할 수 없습니다.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* 헤더 */}
      <div className="shrink-0 border-b px-6 py-4">
        <div className="flex items-center gap-3">
          <span className="text-2xl">{scenario.agentEmoji}</span>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="font-semibold text-base">{scenario.title}</h2>
              <span className={cn("rounded-full px-2 py-0.5 text-xs font-medium", AGENT_BADGE_COLORS[scenario.agent])}>
                {scenario.agent}
              </span>
            </div>
            <p className="text-sm text-muted-foreground mt-0.5">{scenario.description}</p>
          </div>
        </div>
      </div>

      {/* 입력 폼 */}
      <div className="flex-1 overflow-y-auto px-6 py-6">
        <div className="max-w-lg space-y-5">
          {scenarioId === "S1" && (
            <>
              <Field label="에러 코드">
                <input value={params.error_code} onChange={e => set("error_code", e.target.value)}
                  className="input-field" placeholder="예: DG320" />
              </Field>
              <Field label={`폭 (width): ${params.width}mm`}>
                <input type="range" min={900} max={1300} value={params.width}
                  onChange={e => set("width", e.target.value)} className="w-full accent-primary" />
                <div className="flex justify-between text-xs text-muted-foreground mt-1">
                  <span>900mm</span><span>1300mm</span>
                </div>
              </Field>
              <Field label={`두께 (thickness): ${params.thickness}mm`}>
                <input type="range" min={6} max={12} step={0.5} value={params.thickness}
                  onChange={e => set("thickness", e.target.value)} className="w-full accent-primary" />
                <div className="flex justify-between text-xs text-muted-foreground mt-1">
                  <span>6mm</span><span>12mm</span>
                </div>
              </Field>
            </>
          )}

          {scenarioId === "S2" && (
            <Field label="변경된 Edging 기준값">
              <input value={params.edging_value} onChange={e => set("edging_value", e.target.value)}
                className="input-field" placeholder="예: 두께 허용 공차 ±0.3 → ±0.5mm" />
            </Field>
          )}

          {scenarioId === "S3" && (
            <>
              <Field label="Job ID">
                <input value={params.job_id} onChange={e => set("job_id", e.target.value)}
                  className="input-field" placeholder="예: JOB-2025-0325" />
              </Field>
              <div className="grid grid-cols-2 gap-4">
                <Field label="시작 날짜">
                  <input type="date" value={params.date_from} onChange={e => set("date_from", e.target.value)}
                    className="input-field" />
                </Field>
                <Field label="종료 날짜">
                  <input type="date" value={params.date_to} onChange={e => set("date_to", e.target.value)}
                    className="input-field" />
                </Field>
              </div>
            </>
          )}

          {scenarioId === "S4" && (
            <Field label="비즈니스 용어 검색">
              <input value={params.term} onChange={e => set("term", e.target.value)}
                className="input-field" placeholder="예: 단중, DG320, 타겟 단중" />
            </Field>
          )}

          {scenarioId === "S5" && (
            <>
              <Field label="신규 공장명">
                <input value={params.factory_name} onChange={e => set("factory_name", e.target.value)}
                  className="input-field" placeholder="예: HOT_MILL_3" />
              </Field>
              <Field label="연동 대상 시스템 (쉼표 구분)">
                <input value={params.systems} onChange={e => set("systems", e.target.value)}
                  className="input-field" placeholder="예: PlanningAPI, WeightCalc, ReportGen" />
              </Field>
            </>
          )}

          {scenarioId === "S6" && (
            <>
              <Field label="신청자 이름">
                <input value={params.requester} onChange={e => set("requester", e.target.value)}
                  className="input-field" placeholder="예: 홍길동" />
              </Field>
              <Field label="화면 ID">
                <input value={params.screen_id} onChange={e => set("screen_id", e.target.value)}
                  className="input-field" placeholder="예: SCR_QUALITY_MGR" />
              </Field>
              <Field label="권한 레벨">
                <select value={params.permission_level} onChange={e => set("permission_level", e.target.value)}
                  className="input-field">
                  <option value="READ">READ — 조회만</option>
                  <option value="READ_WRITE">READ_WRITE — 입력/수정</option>
                  <option value="ADMIN">ADMIN — 관리자</option>
                </select>
              </Field>
            </>
          )}

          {scenarioId === "S7" && (
            <>
              <Field label="서비스 A">
                <select value={params.service_a} onChange={e => set("service_a", e.target.value)}
                  className="input-field">
                  <option value="ORDER_DB">주문 서비스 (ORDER_DB)</option>
                  <option value="PROD_DB">생산 서비스 (PROD_DB)</option>
                </select>
              </Field>
              <Field label="서비스 B">
                <select value={params.service_b} onChange={e => set("service_b", e.target.value)}
                  className="input-field">
                  <option value="PROD_DB">생산 서비스 (PROD_DB)</option>
                  <option value="ORDER_DB">주문 서비스 (ORDER_DB)</option>
                </select>
              </Field>
            </>
          )}
        </div>
      </div>

      {/* 에러 메시지 */}
      {error && (
        <div className="shrink-0 mx-6 mb-2 rounded-md bg-destructive/10 px-4 py-2 text-sm text-destructive">
          {error}
        </div>
      )}

      {/* 실행 버튼 */}
      <div className="shrink-0 border-t px-6 py-4">
        <button
          onClick={handleRun}
          disabled={loading}
          className="flex items-center gap-2 rounded-lg bg-primary px-5 py-2.5 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-60 transition-colors"
        >
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
          {loading ? "분석 중..." : "분석 실행"}
        </button>
      </div>
    </div>
  )
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="space-y-1.5">
      <label className="text-sm font-medium">{label}</label>
      {children}
    </div>
  )
}
