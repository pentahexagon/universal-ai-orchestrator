import { NextRequest, NextResponse } from 'next/server'
import { spawn } from 'child_process'
import path from 'path'

// Simulate AI responses (for development without API keys)
const DEVELOPMENT_MODE = process.env.NODE_ENV === 'development' && !process.env.OPENAI_API_KEY

async function simulateAIResponse(question: string, agent: string, delay: number) {
  await new Promise(resolve => setTimeout(resolve, delay))

  const responses: Record<string, string> = {
    gemini: `[Gemini 분석]\n\n"${question}"에 대한 정보를 수집했습니다.\n\n관련 데이터와 최신 트렌드를 바탕으로 분석하면, 이는 중요한 주제입니다. 시장에서는 이에 대한 관심이 증가하고 있으며, 여러 전문가들이 다양한 관점을 제시하고 있습니다.`,
    chatgpt: `[ChatGPT 전략 분석]\n\n앞선 정보를 토대로 전략적 관점에서 분석하겠습니다.\n\n**핵심 인사이트:**\n1. 시장 기회가 존재합니다\n2. 경쟁 우위 확보가 필요합니다\n3. 리스크 관리가 중요합니다\n\n**SWOT 분석:**\n- 강점: 혁신적 접근 가능\n- 약점: 초기 투자 필요\n- 기회: 성장 잠재력 높음\n- 위협: 시장 변화 대응 필요`,
    claude: `[Claude 실행 계획]\n\n종합적인 분석을 바탕으로 실행 계획을 제시합니다.\n\n**단계별 액션 플랜:**\n1. 1단계 (1-2개월): 기반 구축\n2. 2단계 (3-6개월): 시범 운영\n3. 3단계 (6-12개월): 본격 확장\n\n**리스크 관리:**\n- 법적 검토 필수\n- 예산 계획 수립\n- 모니터링 체계 구축\n\n**최종 권고:**\n단계적 접근을 통해 리스크를 최소화하면서 추진하는 것을 권장합니다.`
  }

  return responses[agent] || `${agent} 응답`
}

async function callPythonOrchestrator(question: string): Promise<any> {
  return new Promise((resolve, reject) => {
    const pythonPath = path.join(process.cwd(), '..', 'main.py')
    const python = spawn('python3', [pythonPath, '--question', question])

    let stdout = ''
    let stderr = ''

    python.stdout.on('data', (data) => {
      stdout += data.toString()
    })

    python.stderr.on('data', (data) => {
      stderr += data.toString()
    })

    python.on('close', (code) => {
      if (code === 0) {
        try {
          resolve(JSON.parse(stdout))
        } catch (e) {
          reject(new Error('Failed to parse Python output'))
        }
      } else {
        reject(new Error(stderr || 'Python script failed'))
      }
    })

    setTimeout(() => {
      python.kill()
      reject(new Error('Python script timeout'))
    }, 60000) // 60 second timeout
  })
}

export async function POST(request: NextRequest) {
  try {
    const { question } = await request.json()

    if (!question || typeof question !== 'string') {
      return NextResponse.json(
        { success: false, error: '질문을 입력해주세요' },
        { status: 400 }
      )
    }

    // Development mode: use simulated responses
    if (DEVELOPMENT_MODE) {
      const [geminiResponse, chatgptResponse, claudeResponse] = await Promise.all([
        simulateAIResponse(question, 'gemini', 1000),
        simulateAIResponse(question, 'chatgpt', 1500),
        simulateAIResponse(question, 'claude', 2000),
      ])

      const synthesis = `# 통합 분석\n\n세 AI 에이전트의 분석을 종합한 결과입니다.\n\n${question}에 대해 다음과 같은 결론을 도출했습니다:\n\n1. **정보 수집 (Gemini)**: 관련 데이터와 트렌드 파악\n2. **전략 분석 (ChatGPT)**: SWOT 분석 및 인사이트 도출\n3. **실행 계획 (Claude)**: 구체적인 액션 플랜 수립\n\n**최종 권장사항:**\n단계적이고 체계적인 접근을 통해 목표를 달성하시기 바랍니다.`

      return NextResponse.json({
        success: true,
        question,
        responses: {
          gemini: { success: true, content: geminiResponse },
          chatgpt: { success: true, content: chatgptResponse },
          claude: { success: true, content: claudeResponse },
        },
        synthesis,
        metadata: {
          mode: 'development',
          total_duration: 2.5,
        }
      })
    }

    // Production mode: call Python orchestrator
    try {
      const result = await callPythonOrchestrator(question)
      return NextResponse.json(result)
    } catch (error) {
      console.error('Python orchestrator error:', error)
      return NextResponse.json(
        {
          success: false,
          error: 'AI 처리 중 오류가 발생했습니다. API 키를 확인해주세요.',
        },
        { status: 500 }
      )
    }

  } catch (error) {
    console.error('API error:', error)
    return NextResponse.json(
      { success: false, error: '서버 오류가 발생했습니다' },
      { status: 500 }
    )
  }
}
