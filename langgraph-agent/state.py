# state.py (개선)
import operator
from typing import TypedDict, List, Any, Optional, Union, Literal
from langchain_core.messages import BaseMessage, ToolMessage
from typing_extensions import Annotated
from pydantic import BaseModel, Field

# ----------------------------------------------------
# B-1 메시지 포맷 표준화: 노드 간 전달 정보를 구조화
# ----------------------------------------------------

class ErrorInfo(BaseModel):
    """오류 처리 노드(ErrorHandler)로 전달되는 구조화된 에러 정보."""
    error_code: str = Field(..., description="내부 정의된 에러 코드 (e.g., TOOL_TIMEOUT, LLM_RATE_LIMIT)")
    message: str = Field(..., description="개발자용 상세 에러 메시지")
    user_message: str = Field(..., description="사용자에게 친화적으로 표시할 메시지")
    node: str = Field(..., description="에러가 발생한 노드 이름")
    trace_id: Optional[str] = None

class AgentDecisionModel(BaseModel):
    """AgentDecision 노드의 출력 표준화 모델."""
    action_type: Literal["tool_call", "final_answer", "subgraph_call", "error"] = Field(..., description="결정된 다음 행동 타입")
    tool_calls: Optional[List[dict]] = Field(None, description="tool_call 액션일 경우 호출할 도구 목록 (LangChain 형식)")
    final_answer: Optional[str] = Field(None, description="final_answer 액션일 경우 최종 답변")
    subgraph_id: Optional[str] = Field(None, description="subgraph_call 액션일 경우 호출할 서브그래프 ID")
    
# ----------------------------------------------------
# LangGraph State 정의
# ----------------------------------------------------

class State(TypedDict):
    """
    LangGraph의 상태를 정의하는 TypedDict. 
    Annotated[..., operator.add]를 사용하여 필드에 값을 누적합니다.
    """
    
    # 1. 기존 LangChain/LangGraph 기본 필드
    question: str # 초기 사용자 질문
    dataset: Any # (기존) 데이터 분석용
    code: str # (기존) 코드 실행용
    code_lang: str
    result: str # (기존) 코드 실행 결과
    answer: str # 최종 사용자에게 보여줄 답변
    execution_context: Optional[dict]
    
    # 누적되는 필드
    messages: Annotated[List[BaseMessage], operator.add]
    intermediate_steps: Annotated[List[Any], operator.add]
    
    # 2. 멀티노드 및 안정성 확보를 위한 추가 필드 (설계서 반영)
    active_node: Optional[str] # 현재 실행 중인 노드의 이름 (디버깅용)
    loop_counter: int # 루프 안전장치 카운터
    
    # 3. 노드 간 데이터 전달 및 표준화 필드 (B-1 반영)
    # AgentDecision의 결과를 구조화하여 저장
    decision: Optional[AgentDecisionModel] 
    
    # ToolExecutor/JoinNode의 출력을 임시 저장
    tool_outputs: Annotated[List[ToolMessage], operator.add] 
    
    # ErrorHandler 노드의 입력을 구조화하여 저장
    error_info: Optional[ErrorInfo]
    
    # 4. 서브그래프 호출 결과 (향후 D-1 확장 시 사용)
    subgraph_output: Optional[Any]
