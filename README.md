# VS-ME

## 🚀 프로젝트 소개

VS-ME는 정체기를 극복하고 자신의 수행능력을 키워가고 싶은 개인을 위한 플랫폼입니다.
운동·식단뿐만 아니라 수면, 영양제 등 사용자가 원하는 데이터를 자유롭게 기록할 수 있으며, AI는 이를 바탕으로 신뢰성 있는 성장 피드백을 제공합니다.


핵심 가치 (MECE 정리)

데이터 기록 유연성

운동, 식단뿐만 아니라 개인이 원하는 모든 항목(예: 수면, 영양제, 컨디션)을 jsonb 형식으로 저장 가능

개인화된 데이터 스키마를 강제하지 않고, 사용자가 원하는 만큼 확장 가능

AI 기반 분석과 조언

LangGraph 기반 에이전트가 자연어 요청(NLQ)을 이해하고 적절한 Tool을 호출

GPT 모델이 단순 요약이 아니라, 개인의 누적 데이터를 바탕으로 신뢰성 높은 전략적 피드백 제공

시각화와 성장 추적

"승리의 연대기" 차트를 통해 운동·기록 데이터의 변화를 직관적으로 확인

Chart.js 기반의 시각화와 분석 리포트를 통해 단기적인 성과와 장기적인 성장을 동시에 관리

데이터 저장 및 보안

Supabase(PostgreSQL)를 기반으로, 사용자의 데이터를 안전하게 관리

API 키 및 권한은 환경 변수를 통해 안전하게 보호

📊 우리의 Positioning

우리 서비스의 포지션은 **“즉각성보다 타당성, 기록 편의성보다 콘텐츠 다양성”**입니다.

```mermaid
quadrantChart
    title Service Positioning Matrix
    x-axis Immediacy --> Analytical_Rigor
    y-axis Recording_Convenience --> Content_Diversity
    
    "우리 서비스": [0.9, 0.8]
    "GPT": [0.25, 0.9]
    "메모 앱": [0.15, 0.2]
    "노션": [0.35, 0.4]
    "헬스장 PT": [0.75, 0.25]
```


즉,

GPT는 빠르고 즉각적인 응답에 강점이 있는 반면,

우리 서비스는 충분한 데이터를 모으고 분석하여 개인의 성장에 타당한 인사이트를 제공하는 데 집중합니다.

⚠️ UX 관점

우리 서비스의 UI는 직관적이거나 단순하지 않습니다.

그러나 이는 단순 기록 도구가 아니라, 성장 지향적 분석 플랫폼이라는 포지션을 강화합니다.

👉 요약하자면, **“내가 넣고 싶은 모든 데이터를 기반으로, GPT가 주지 못하는 타당성 있는 성장 피드백을 주는 서비스”**입니다.

## 🏛️ 아키텍처 (Architecture)

본 프로젝트는 **이중 백엔드(Dual Backend)** 구조를 채택하여 웹 서비스와 AI 에이전트 기능을 분리하고 확장성을 확보했습니다.

-   **Express.js (Node.js) 백엔드**: 프론트엔드의 메인 API 서버 역할을 합니다. AI 코칭, 전략 브리핑, 데이터베이스 프록시 기능을 수행합니다.
-   **FastAPI (Python) 백엔드**: LangGraph 기반의 ReAct 에이전트를 API로 제공합니다. 복잡한 Tool-Calling 로직을 처리하여 사용자의 자연어 요청(예: "내 운동 기록 보여줘")을 수행합니다.

```mermaid
flowchart LR
 subgraph subGraph0["User Layer"]
        U@{ label: "👤 User's Browser" }
  end
 subgraph subGraph1["UI Libraries"]
        T["Tailwind CSS"]
        C["Chart.js"]
  end
 subgraph subGraph2["Frontend Layer (Client-Side)"]
    direction TB
        FE["index.html"]
        PH["Placeholder Data Display"]
        CUI["Chatting UI"]
        subGraph1
  end
 subgraph subGraph3["Web API Server (server.js)"]
        B1["Express.js"]
        B1_Coach["/api/coach<br>(AI Coach & Strategy Briefing)"]
        B1_CRUD["/api/sessions, /api/nutrition<br>(DB Proxy for Data Retrieval)"]
  end
 subgraph subGraph4["LangGraph Engine (node.py, state.py)"]
        AD["AgentDecision Node"]
        TE["ToolExecutor Node"]
        RP["ResultProcessor Node"]
  end
 subgraph subGraph5["LangChain Framework Layer"]
        AE["AgentExecutor<br>(Abstraction Layer)"]
        AE_Features["• Prompt Management<br>• Tool Context Integration<br>• Conversation History<br>• LangChain Rules"]
  end
 subgraph subGraph6["LangGraph Agent Server (graph_builder.py)"]
        B2["FastAPI"]
        B2_Invoke["/invoke<br>(Agent Execution)"]
        subGraph4
        subGraph5
        ST["supabase_tools.py<br>(DB Tool Functions)"]
  end
 subgraph subGraph7["Backend Services Layer"]
    direction TB
        subGraph3
        subGraph6
  end
 subgraph subGraph8["External Services & Data Layer"]
    direction TB
        GPT["🧠 OpenAI GPT Model"]
        DB[("🗃️ Supabase DB")]
  end
    FE --> PH & CUI
    B1 --> B1_Coach & B1_CRUD
    AD --> TE
    TE --> RP & ST
    AE -.-> AE_Features
    B2 --> B2_Invoke
    B2_Invoke --> AD
    RP -- "agent_executor.agent.invoke()" --> AE
    U --> FE
    PH -- Direct Data Retrieval --> B1_CRUD
    B1_CRUD -- Proxy Request --> DB
    CUI -- Natural Language Input --> B2_Invoke
    ST -- Tool Execution<br>(get_workout_history, add_workout_session) --> DB
    B1_Coach -- "SystemPrompt + UserPrompt<br>+ Pre-retrieved Data" --> GPT
    AD -- Decision Making --> GPT
    AE -- Managed LLM Call<br>(with context & history) --> GPT
    U@{ shape: rect}
     U:::layer
     FE:::layer
     PH:::layer
     CUI:::layer
     B1:::layer
     B1_Coach:::service
     B1_CRUD:::service
     AD:::layer
     TE:::layer
     RP:::layer
     AE:::framework
     AE_Features:::framework
     B2:::layer
     B2_Invoke:::service
     ST:::layer
     GPT:::external
     DB:::external
    classDef layer fill:#f2f0ff,stroke:#b695e5,stroke-width:2px
    classDef service fill:#e6f7ff,stroke:#007bff,stroke-width:1px
    classDef external fill:#d4edda,stroke:#155724,stroke-width:1px
    classDef framework fill:#fff9e6,stroke:#ffa500,stroke-width:2px
    classDef dataflow fill:#fff2e6,stroke:#ff8c00,stroke-width:2px
    style T fill:#38bdf8,stroke:#fff,color:#fff
    style C fill:#ff6384,stroke:#fff,color:#fff
```

## ✨ 주요 기능 (Key Features)

-   **운동 및 식단 기록**: 양식을 통한 직접 입력 방식과, 채팅창에 메모를 붙여넣어 AI 에이전트에게 데이터 추가를 요청하는 자연어 기반 입력 방식을 모두 지원합니다.
-   **AI 코칭 및 전략 브리핑**: 저장된 데이터를 기반으로 AI 코치가 개인화된 운동/식단 조언과 분석 리포트를 제공합니다.
-   **자연어 상호작용**: LangGraph 기반 AI 에이전트와 대화(또는 음성)하여 "오늘 운동 뭐했지?"와 같이 자연어로 운동 기록을 조회하거나 추가할 수 있습니다.
-   **성장 시각화**: Chart.js를 활용한 '승리의 연대기' 차트를 통해 운동 볼륨 등의 성장 과정을 시각적으로 추적합니다.
-   **안전한 데이터 관리**: 모든 사용자 데이터는 Supabase 데이터베이스에 안전하게 저장되며, API 키 등 민감 정보는 서버에서 안전하게 관리됩니다.

## 🛠️ 기술 스택 (Tech Stack)

### 프론트엔드
*   **Tailwind CSS**: 반응형 디자인, 다크 모드 등 전체 UI 스타일링을 위한 유틸리티 우선 CSS 프레임워크.
*   **Chart.js**: '승리의 연대기' 기능에서 사용자의 운동 볼륨 변화를 시각화하는 차트 라이브러리.

### 백엔드
1.  **Express.js (Node.js)**
    *   **역할**: 웹 애플리케이션의 메인 API 서버.
    *   **주요 기능**: AI 코치(GPT 호출), Supabase 데이터 프록시.
2.  **FastAPI (Python)**
    *   **역할**: LangGraph 기반 ReAct 에이전트 API 서버.
    *   **주요 기능**: Tool-Calling, 자연어 기반 DB 상호작용.

### 데이터베이스
*   **Supabase**: PostgreSQL 기반의 BaaS(Backend as a Service). 운동 및 식단 데이터 저장소로 사용됩니다.

### AI & 에이전트
*   **GPT (OpenAI)**: AI 코치 기능과 에이전트의 의도 분석 및 Tool-Calling 결정에 사용되는 핵심 LLM.
*   **LangGraph**: ReAct 패턴의 AI 에이전트를 구축하기 위한 프레임워크. `AgentDecision`, `ToolExecutor` 등의 노드를 정의하여 상태 기반의 자율적 에이전트를 구현합니다.
*   **LangChain**: LangGraph의 기반 기술. LLM, Tool, Prompt를 유기적으로 결합하는 데 사용됩니다.

## 🏁 실행 방법 (Quick Start)

### 1. 환경 변수 설정

프로젝트 루트 디렉토리에 `.env` 파일을 생성하고, 아래 내용을 각자의 키 값으로 채워주세요.

```.env
# OpenAI API Key
OPENAI_API_KEY="YOUR_OPENAI_API_KEY"

# Supabase Credentials
SUPABASE_URL="YOUR_SUPABASE_URL"
SUPABASE_ANON_KEY="YOUR_SUPABASE_ANON_KEY"
```

### 2. 백엔드 서버 실행

본 프로젝트는 두 개의 백엔드 서버로 구성되어 있으며, 두 서버를 모두 실행해야 모든 기능이 정상적으로 동작합니다.

#### A. LangGraph 에이전트 서버 (FastAPI)

```bash
# langgraph-agent 디렉토리로 이동
cd langgraph-agent

# (선택) Python 가상 환경 생성 및 활성화
# python3 -m venv venv && source venv/bin/activate

# 종속성 설치
pip install -r requirements.txt

# 서버 실행
uvicorn graph_builder:fastapi_app --reload
```

#### B. 웹 애플리케이션 서버 (Express.js)

```bash
# web 디렉토리로 이동
cd web

# 종속성 설치
npm install

# 서버 실행
node server.js
```

### 3. 프론트엔드 접근

두 서버가 모두 실행된 후, 웹 브라우저를 열어 `http://localhost:3000` 주소로 접속하면 애플리케이션을 사용할 수 있습니다.
