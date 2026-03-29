import { NextRequest, NextResponse } from "next/server"

const GROQ_API_KEY = process.env.GROQ_API_KEY
const GROQ_MODEL = process.env.GROQ_CHAT_MODEL ?? "llama-3.3-70b-versatile"

export async function POST(req: NextRequest) {
  const { message, contextType, contextData } = await req.json()

  // 컨텍스트 타입에 따른 시스템 프롬프트 구성
  let systemPrompt = "당신은 제조 현장 인텔리전스 플랫폼의 AI 코파일럿입니다. 철강/열연 공장 운영에 대한 전문적인 도움을 제공합니다."

  if (contextType === "scenario" && contextData) {
    systemPrompt = `현재 사용자는 [${contextData.scenarioName}] 분석을 수행 중입니다. 에이전트 타입은 [${contextData.agentType}]입니다. 관련 질문에 답변하세요.`
  } else if (contextType === "document" && contextData) {
    systemPrompt = `현재 사용자가 보고 있는 위키 문서:\n\n${contextData.content}`
  }

  if (!GROQ_API_KEY) {
    return NextResponse.json({ error: "GROQ_API_KEY가 설정되지 않았습니다." }, { status: 500 })
  }

  try {
    const response = await fetch("https://api.groq.com/openai/v1/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${GROQ_API_KEY}`,
      },
      body: JSON.stringify({
        model: GROQ_MODEL,
        messages: [
          { role: "system", content: systemPrompt },
          { role: "user", content: message },
        ],
        max_tokens: 1024,
      }),
    })

    const data = await response.json()
    if (!response.ok) {
      return NextResponse.json({ error: data.error?.message ?? "Groq API 오류" }, { status: 500 })
    }

    const text = data.choices?.[0]?.message?.content ?? ""
    return NextResponse.json({ content: text })
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : "알 수 없는 오류"
    return NextResponse.json({ error: msg }, { status: 500 })
  }
}
