# VS-ME

## 🚀 프로젝트 소개

VS-ME는 정체기를 극복하고 자신의 수행능력을 키워가고 싶은 개인을 위한 플랫폼입니다.
운동·식단뿐만 아니라 수면, 영양제 등 사용자가 원하는 데이터를 자유롭게 기록할 수 있으며, AI는 이를 바탕으로 신뢰성 있는 성장 피드백을 제공합니다.


### 핵심 가치
**데이터 기록 유연성**
* **운동, 식단뿐만 아니라 개인이 원하는 모든 항목(예: 수면, 영양제, 컨디션)을 jsonb 형식으로 저장 가능**
* **개인화된 데이터 스키마를 강제하지 않고, 사용자가 원하는 만큼 확장 가능**
- AI 기반 분석 보고서와 실시간 조언**
* **LLangGraph 기반 에이전트가 자연어 요청(NLQ)을 이해하고 적절한 Tool을 호출**
* **LGPT 모델이 단순 요약이 아니라, 개인의 누적 데이터를 바탕으로 신뢰성 높은 전략적 피드백 제공**
**단기적 /장기적 성장 별도 분석 전략**
* **LChart.js 기반의 운동별 분석 시각화와 리포트를 통해 단기적인 성과와 장기적인 성장을 동시에 관리**

### ✨ 핵심 기능
**AI 코치 기능 (실시간)**
* **LangGraph 기반으로 DB에서 필요한 데이터만 가져와 응답**
* **운동/식단/수면/영양제 등 유연한 데이터 입력 지원**
* **L자연어 기반 개인 맞춤 조언 제공**   
**AI 분석 기능 (비실시간)**
* **LLM이 사용자의 모든 데이터를 직접 분석**
* **개인화 보고서 생성 및 성장 전략 제안**
* **데이터 시각화**
* **운동별 “승리의 연대기” 차트를 통해 수행능력 변화 추세**
* **최대 수행능력 달성 유무 시각화**

### 📊 우리의 Positioning

- 우리 서비스의 포지션은 **“즉각성보다 타당성, 기록 편의성보다 콘텐츠 다양성”**입니다.

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


- 즉, GPT는 빠르고 즉각적인 응답에 강점이 있는 반면,
- 우리 서비스는 충분한 데이터를 모으고 분석하여 개인의 성장에 타당한 인사이트를 제공하는 데 집중합니다.

### ⚠️ UX 관점
- 우리 서비스의 UI는 직관적이거나 단순하지 않습니다.
- 그러나 이는 단순 기록 도구가 아니라, 성장 지향적 분석 플랫폼이라는 포지션을 강화합니다.

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

### data-flow

```mermaid

graph LR
    subgraph "Input Data Types"
        NLQ["Natural Language Query<br/>question: str"]
        DIR["Direct Data Request<br/>user_id: text"]
    end
    
    subgraph "Frontend Data Layer"
        REQ_Direct["Direct Request<br/>{ user_id: text }"]
        REQ_Agent["Agent Request<br/>{ question: str, user_id: text }"]
    end
    
    subgraph "Backend Data Processing"
        subgraph "Web API Flow"
            WEB["Web API Processing<br/>SystemPrompt + UserPrompt + DB_Data"]
        end
        
        subgraph "LangGraph State Flow"
            STATE["State (TypedDict)<br/>• question: str<br/>• decision: AgentDecisionModel<br/>• tool_outputs: List[ToolMessage]<br/>• answer: str"]
            
            DECISION["AgentDecisionModel<br/>• action_type: Literal<br/>• tool_calls: List[dict]<br/>• final_answer: str"]
            
            TOOLS["Tool Parameters<br/>• user_id: text<br/>• date_filter?: str"]
        end
    end
    
    subgraph "Database Schema"
        SESSIONS["sessions<br/>• id: bigint<br/>• user_id: text<br/>• total_volume: numeric<br/>• exercises: jsonb"]
        
        NUTRITION["nutrition<br/>• id: bigint<br/>• user_id: text<br/>• carbs: numeric<br/>• protein: numeric<br/>• fat: numeric"]
    end
    
    subgraph "AI Processing"
        GPT["GPT Model<br/>Input: structured prompts<br/>Output: text responses"]
    end
    
    %% Styling
    classDef input fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef frontend fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef backend fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef database fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef ai fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    
    %% Data Flow Connections
    
    %% Direct Flow
    DIR --> REQ_Direct
    REQ_Direct --> WEB
    WEB --> SESSIONS
    WEB --> NUTRITION
    WEB --> GPT
    
    %% Agent Flow
    NLQ --> REQ_Agent
    REQ_Agent --> STATE
    STATE --> DECISION
    DECISION --> TOOLS
    TOOLS --> SESSIONS
    TOOLS --> NUTRITION
    SESSIONS --> STATE
    NUTRITION --> STATE
    STATE --> GPT
    
    %% Apply Classes
    class NLQ,DIR input
    class REQ_Direct,REQ_Agent frontend
    class WEB,STATE,DECISION,TOOLS backend
    class SESSIONS,NUTRITION database
    class GPT ai

```

## 🛠️ 기술 스택 (Tech Stack)

### 프론트엔드

* **Tailwind CSS**: 전체 UI 스타일링을 위한 유틸리티 우선 CSS 프레임워크. 반응형 디자인과 일관된 레이아웃 제공.
* **Chart.js**: 사용자의 기록 데이터를 기반으로 그래프 및 차트 시각화.

### 백엔드

1. **Express.js (Node.js)**
   * **역할**: 웹 애플리케이션의 메인 API 서버.
   * **주요 기능**: AI 코치 기능(GPT 호출), 데이터 요청 처리 및 Supabase 프록시.
2. **FastAPI (Python)**
   * **역할**: LangGraph 기반 ReAct 에이전트 API 서버.
   * **주요 기능**: 자연어 질의 처리, Tool-Calling, 데이터베이스 상호작용.

### 데이터베이스
* **Supabase (PostgreSQL 기반)**: 사용자 운동/식단/기타 데이터 저장 및 관리. 백엔드 및 AI 에이전트에서 모두 접근 가능.

### AI & 에이전트
* **GPT (OpenAI)**: AI 코치 및 LangGraph 에이전트의 분석/피드백 생성.
* **LangGraph**: ReAct 패턴 기반의 상태 기반 자율 에이전트 구축. `AgentDecision`, `ToolExecutor` 노드를 활용.
* **LangChain**: LLM, Tool, Prompt 결합을 통한 LangGraph 에이전트 실행 기반 제공.

좋아요. 말씀하신 내용 반영해서 **Supabase DB 세팅 포함**, 순서 재정리된 **Quick Start** 전체를 Markdown 형식으로 작성했습니다.

---

## 🏁 Quick Start


### 1. 환경 변수 설정

프로젝트 루트 디렉토리에 `.env` 파일을 생성하고, 아래 내용을 각자의 키 값으로 채워주세요.

```env
# OpenAI API Key
OPENAI_API_KEY="YOUR_OPENAI_API_KEY"

# Supabase Credentials
SUPABASE_URL="YOUR_SUPABASE_URL"
SUPABASE_ANON_KEY="YOUR_SUPABASE_ANON_KEY"
```

---

### 2. Supabase DB 세팅

1. Supabase 프로젝트를 생성합니다.
2. `.env` 파일에 Supabase URL과 Anon Key를 설정합니다 (아래 참조).
3. `tablecreate.sql` 파일에 있는 쿼리를 Supabase SQL Editor 또는 CLI를 통해 실행하여 데이터베이스 스키마를 생성합니다.

```bash
# supabase CLI 예시
supabase db connect
psql "postgresql://<user>:<password>@<host>:<port>/<database>" -f tablecreate.sql
```

> **참고**: `tablecreate.sql`에는 운동, 식단, 세션 등 프로젝트에서 필요한 모든 테이블과 초기 구조가 정의되어 있습니다.

---

### 3. 백엔드 서버 실행

본 프로젝트는 **두 개의 백엔드 서버**로 구성되어 있으며, 두 서버를 모두 실행해야 모든 기능이 정상적으로 동작합니다.

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

---

### 4. 프론트엔드 접근

두 서버가 모두 실행된 후, 웹 브라우저를 열어 아래 주소로 접속하면 애플리케이션을 사용할 수 있습니다.

```
http://localhost:3000
```


### Directory structure
```
web
.
├── index.html
├── node_modules
├── package-lock.json
├── package.json
├── server.js
└── tablecreate.sql

langgraph-agent
.
├── graph_builder.py
├── langgraph.ipynb
├── langgraph.json
├── langgraph.log
├── llm-systemprompt.md
├── node.py
├── requirements.txt
├── state.py
├── supabase_tools.py
├── test_decision_to_tool_flow.py
├── test_node.py
├── test_state.py
└── test_supabase_tools.py
```