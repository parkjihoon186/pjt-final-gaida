# 사전 검증 결과
```
### 현 이중 백엔드 구조
- **장점**: 웹 서비스와 AI 에이전트의 역할이 명확히 분리됨.
- **단점**: 두 개의 서버를 관리해야 하므로 복잡성이 높고, 배포 및 유지보수 오버헤드가 발생함.

### 단일 FastAPI 백엔드 전환 시 기대효과
- **단순성**: 하나의 프레임워크와 언어로 전체 백엔드를 관리하여 구조가 간결해짐.
- **효율성**: API 개발, DB 연동, AI 로직 처리가 한 곳에서 이루어져 개발 효율이 증대됨.
- **유지보수 용이성**: 배포, 모니터링, 로깅 대상이 하나로 통합되어 관리가 용이해짐.


단순 Pass-through 구조: Express 서버는 클라이언트의 요청을 받아 Supabase로 전달하는 단순 프록시(Pass-through) 역할만 수행합니다. 중간에서 데이터를 가공하거나 복잡한 비즈니스 로직을 처리하지 않습니다.

인증 로직 부재: 서버 자체에 별도의 세션 관리나 JWT 토큰 검증과 같은 인증/권한 부여 로직이 없습니다.

사용자 식별 방식: 사용자는 클라이언트에서 보낸 x-user-id HTTP 헤더를 통해 식별됩니다. Express 서버는 이 ID를 그대로 Supabase 쿼리의 where 조건(eq('user_id', userId))에 사용합니다.

보안 의존성: 데이터 접근 제어는 전적으로 Supabase의 RLS(Row Level Security) 정책에 의존하고 있습니다. server.js는 SUPABASE_ANON_KEY (익명 키)를 사용하므로, Supabase에 "사용자는 자신의 user_id와 일치하는 데이터만 읽고 쓸 수 있다"는 RLS 규칙이 설정되어 있을 것으로 예상됩니다.
```

# 아키텍처 업데이트 계획: 단일 FastAPI 백엔드로 전환

## 1. 목표

현재의 이중 백엔드(Express.js + FastAPI) 구조를 단일 FastAPI 백엔드 아키텍처로 통합하여 프로젝트 구조를 단순화하고 개발 및 유지보수 효율성을 높인다.

## 2. 수정 작업 계획 (Task List)

> Express.js (`web/server.js`)의 모든 기능을 FastAPI (`langgraph-agent/`)로 이전하는 것을 목표로 한다.

### 2.1. [Phase 1] Express 기능 FastAPI로 이전


지금 단계에서는 **Task에 추가하는 것이 안전하고 권장**돼요. 이유는 단순히 무시하면 개발 환경에서 문제가 바로 드러날 수 있기 때문입니다. 각 항목을 Task에 넣으면 나중에 테스트 단계에서 발생할 수 있는 혼란을 미리 방지할 수 있어요.

### 제안된 Task 반영 예시

**[Phase 1] Express 기능 FastAPI로 이전** 하위에 추가:

- [x] **CORS 설정**
  * `fastapi.middleware.cors.CORSMiddleware`를 사용하여 프론트엔드 주소(`http://localhost:3000`)에서의 요청 허용
- [x] **환경 변수 로딩**
  * `python-dotenv` 설치 및 `load_dotenv()` 호출로 `.env` 파일 로드
- [x] **x-user-id 헤더 처리**
  * `from fastapi import Header` 사용하여 라우트에서 커스텀 헤더 읽기 구현
- [x] **DB 프록시 API 엔드포인트 이전**
    - [x] `langgraph-agent/api_router.py`에 `/api/sessions` (GET, POST) 라우터 추가
    - [x] `langgraph-agent/api_router.py`에 `/api/nutrition` (GET, POST) 라우터 추가
    - [x] `x-user-id` 헤더를 읽어 Supabase 쿼리에 사용하는 로직 구현 및 검증

- [x] **AI 코치 API 엔드포인트 이전 (OpenAI 기반)**
    - [x] `langgraph-agent/api_router.py`에 `/api/coach` 라우터 추가
    - [x] 프론트엔드에서 받은 프롬프트를 사용하여 LangChain으로 OpenAI LLM을 호출하는 로직 구현

- [x] **정적 파일 서빙 기능 추가**
    - [x] `fastapi.staticfiles.StaticFiles`를 사용하여 `web` 디렉토리를 서빙하도록 설정
    - [x] `/` 경로 요청 시 `web/index.html`을 반환하는 라우트 추가

### 2.2. [Phase 2] 프론트엔드 연결 및 통합 테스트

- [x] **프론트엔드 API 요청 주소 변경**
    - [x] `web/index.html`의 모든 `fetch` 요청 URL을 FastAPI 서버 주소(예: `/api/...`)로 수정
    - [x] 기존 LangGraph 에이전트 호출(`/invoke`) 주소도 상대 경로로 변경

- [x] **통합 테스트**
    - [x] FastAPI 서버만 실행한 상태에서 프론트엔드 접속 (`http://localhost:8000`)
    - [x] 데이터 조회, 기록, AI 코치, AI 에이전트 채팅 등 모든 기능이 정상 동작하는지 검증

### 2.3. [Phase 3] 프로젝트 구조 정리 및 문서화

- [ ] **프로젝트 구조 재구성** (진행 중)
    - [x] `langgraph-agent` 디렉토리 이름을 `backend`로 변경
    - [x] `web` 디렉토리 이름을 `frontend`로 변경하고 `backend` 디렉토리 하위로 이동
    - [ ] `tablecreate.sql` 등 공용 파일을 `backend/database` 등으로 이동

- [ ] **불필요한 파일 및 종속성 제거**
    - [ ] `frontend/server.js`, `frontend/package.json` 등 Node.js 관련 파일 모두 삭제
    - [ ] `.env` 파일에서 불필요한 변수 정리

- [ ] **문서 업데이트**
    - [ ] `README.md`의 아키텍처 다이어그램을 단일 FastAPI 서버 구조로 수정
    - [ ] `README.md`의 `Quick Start` 가이드를 단일 FastAPI 서버 실행 방법으로 수정
