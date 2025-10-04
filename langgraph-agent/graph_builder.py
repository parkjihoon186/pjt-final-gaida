# graph_builder.py

import os
from dotenv import load_dotenv
import sys
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from typing import Literal
from IPython.display import Image, display # Jupyter/Colab 환경을 위해 유지
from state import State # State 정의 임포트
from node import (
    agent_decision, 
    tool_executor, 
    result_processor, 
    error_handler, 
    route_decision, 
    TOOLS, 
    agent_executor # AgentExecutor 초기화로 인해 임포트 필요
) 

# FastAPI 및 관련 라이브러리 임포트
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from api_router import router as db_proxy_router # 새로 만든 라우터 임포트

# .env 파일에서 환경 변수 로드
load_dotenv()


# ----------------------------------------------------
# 1. Graph 정의 및 구축
# ----------------------------------------------------

def build_agent_graph():
    """LangGraph StateGraph를 구축하고 컴파일합니다."""
    
    # StateGraph 인스턴스 생성
    workflow = StateGraph(State)
    
    # 1. 노드 추가
    workflow.add_node("AgentDecision", agent_decision)
    workflow.add_node("ToolExecutor", tool_executor)
    workflow.add_node("ResultProcessor", result_processor)
    workflow.add_node("ErrorHandler", error_handler)
    
    # 2. 진입점 설정
    workflow.set_entry_point("AgentDecision")
    
    # 3. 엣지(Edge) 정의 (라우팅)
    
    # AgentDecision -> 동적 라우팅
    workflow.add_conditional_edges(
        "AgentDecision",
        route_decision,
        {
            "ToolExecutor": "ToolExecutor",       # 도구 호출 시
            "ResultProcessor": "ResultProcessor", # 최종 답변 시 (비관련 질문)
            "ErrorHandler": "ErrorHandler"        # 결정 오류 시
        }
    )
    
    # ToolExecutor -> ResultProcessor 또는 ErrorHandler (결과 처리는 ResultProcessor)
    # ToolExecutor에서 에러가 반환될 경우 route_decision을 통해 ErrorHandler로 자동 분기됩니다.
    workflow.add_edge("ToolExecutor", "ResultProcessor") 
    
    # 4. 종료점 설정
    workflow.add_edge("ResultProcessor", END)
    workflow.add_edge("ErrorHandler", END)
    
    # 5. 컴파일
    app = workflow.compile()
    
    return app

# ----------------------------------------------------
# 2. Graph 시각화 및 진단 (요청 사항)
# ----------------------------------------------------

# Graph 구축
app = build_agent_graph()

def visualize_graph(app, filename="langgraph_flow.png"):
    """
    LangGraph를 시각화하고 PNG 파일로 저장하며, 실패 시 진단 메시지를 출력합니다.
    """
    print("\n" + "="*50)
    print("      LangGraph Architecture Visualization")
    print("="*50)

    # 1. Mermaid 텍스트 다이어그램 출력 (항상 성공)
    mermaid_text = app.get_graph().draw_mermaid()
    print("\n--- Mermaid Text Diagram (Raw Flow) ---")
    print(mermaid_text)
    
    # 2. PNG/이미지 생성 시도 및 진단
    try:
        # PNG 생성을 시도 (pygraphviz 또는 pydot 필요)
        app.get_graph().draw_mermaid_png(output_file_path=filename)
        print(f"\n✅ Graph 다이어그램이 '{filename}' 파일로 저장되었습니다.")
        
        # Jupyter/Colab 환경일 경우 이미지를 바로 출력
        if 'ipykernel' in sys.modules:
            print("✅ Jupyter 환경에서 이미지를 출력합니다.")
            display(Image(filename=filename))
        
    except Exception as e:
        # PNG 생성 실패 시 진단 메시지 출력
        print(f"\n⚠️ PNG/이미지 생성 실패: {type(e).__name__}")
        print("--- 진단 정보 ---")
        print("PNG 파일 생성을 위해서는 'pygraphviz' 또는 'pydot' 라이브러리가 필요합니다.")
        print("설치 방법:")
        print("  1. 'pip install pygraphviz' 또는 'pip install pydot'")
        print("  2. 'graphviz' 시스템 패키지가 설치되어 있어야 합니다 (macOS: 'brew install graphviz').")
        print(f"상세 에러: {e}")
        
    print("="*50 + "\n")


# ----------------------------------------------------
# 3. FastAPI 애플리케이션 정의
# ----------------------------------------------------

# LangGraph 앱을 전역적으로 한 번만 초기화하여 성능을 최적화합니다.
langgraph_app = build_agent_graph()

# Pydantic 모델로 요청 바디를 정의
class AgentRequest(BaseModel):
    """
    API 요청에 사용될 데이터 모델.
    """
    question: str

# FastAPI 앱 인스턴스 생성. 이 변수가 웹 서버의 진입점이 됩니다.
fastapi_app = FastAPI(title="VS-ME Unified Backend API")

# CORS 미들웨어 추가
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 프론트엔드 주소
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메소드 허용
    allow_headers=["*"],  # 모든 HTTP 헤더 허용
)

# LangGraph 에이전트 라우터 생성
agent_router = APIRouter()

# DB 프록시 라우터 추가
fastapi_app.include_router(db_proxy_router)

# LangGraph 에이전트 API 엔드포인트
@fastapi_app.post("/invoke")
async def invoke_agent_api(request: AgentRequest):
    """
    HTTP 요청을 받아 LangGraph 에이전트를 실행합니다.
    """
    # LangGraph의 입력 형식에 맞게 데이터를 준비합니다.
    input_data = {
        "question": request.question,
        "messages": [HumanMessage(content=request.question)],
        "loop_counter": 0,
        "tool_outputs": [],
        "intermediate_steps": []
    }
    
    # LangGraph 앱을 동기적으로 호출합니다.
    result = langgraph_app.invoke(input_data)
    
    # 최종 메시지만 추출하여 반환
    final_message_content = result.get("messages", [AIMessage(content="결과 없음.")])[-1].content
    
    return {"result": final_message_content}

# 루트 경로(/) 요청 시 index.html 반환
@fastapi_app.get("/")
async def read_index():
    # web 디렉토리의 index.html을 반환합니다.
    return FileResponse('../web/index.html')

# 정적 파일 서빙 (CSS, JS, 이미지 등)
# ../web 경로를 / 경로에 마운트합니다.
fastapi_app.mount("/", StaticFiles(directory="../web"), name="static")

# 에이전트 라우터를 메인 앱에 포함 (prefix를 사용할 경우)
# fastapi_app.include_router(agent_router, prefix="/agent")


# ----------------------------------------------------
# 4. Local Test (기존 코드 유지)
# ----------------------------------------------------


if __name__ == "__main__":
    # 이 블록은 스크립트를 직접 실행했을 때만 동작하며, 웹 서버와는 별개입니다.
    # 기존의 로컬 테스트 및 시각화 로직을 그대로 유지합니다.
    
    # Graph 시각화 및 구조 점검
    visualize_graph(langgraph_app)
    
    # 구조 확인 후, 최소 기능 통합 테스트 실행 (선택 사항)
    print("\n--- 최소 기능 Graph 실행 (테스트 입력) ---")
    try:
        test_question = f"내 운동 기록을 조회해 줘. 사용자 ID는 '7356cf0e-19c2-4aef-982b-2607fdc00752'야"
        input_data = {
            "question": test_question,
            "messages": [HumanMessage(content=test_question)],
            "loop_counter": 0,
            "tool_outputs": [],
            "intermediate_steps": []
        }
        
        # 실제 데이터베이스 연결 및 LLM 호출이 발생합니다.
        result = langgraph_app.invoke(input_data)
        
        print("\n--- Graph 실행 결과 (최종 State) ---")
        # 최종 메시지만 깔끔하게 출력
        final_message_content = result.get("messages", [AIMessage(content="결과 없음.")])[-1].content
        print(f"Answer: {final_message_content}")
        print(f"Active Node: {result.get('active_node')}")
        
    except Exception as e:
        print(f"\n❌ Graph 실행 중 오류 발생 (DB/LLM 연결 문제일 수 있음): {type(e).__name__} - {str(e)}")