from typing import TypedDict, Optional, Any, List
from langchain_core.messages import BaseMessage
from typing_extensions import Annotated
import operator
from langgraph.graph import StateGraph


class State(TypedDict):
    """
    State는 LangGraph의 상태를 나타냅니다.
    LangGraph의 노드를 통과할 때마다 이 상태가 업데이트됩니다.
    """
    question: str  # 사용자의 질문
    dataset: Any  # 임의의 데이터셋 Any : 모든 데이터 타입 허용
    code: str  # 코드 블럭
    code_lang: str  # 프로그래밍 언어, Default: python
    result: str  # 'code'의 실행결과(터미널)
    answer: str  # 최종 답변
    execution_context: Optional[dict]  # 사용자 실행에 대한 컨텍스트
    messages: Annotated[List[BaseMessage], operator.add] # 핵심: 모든 대화 기록을 'messages'로 통합하여 관리
    intermediate_steps: Annotated[List[Any], operator.add]
    # messages: Annotated[List[BaseMessage], operator.add] # 대화 기록을 직접 정의합니다.
    # input: str # LangChain 에이전트 호환성을 위한 키 추가
    # chat_history: List[BaseMessage] # LangChain 에이전트 호환성을 위한 키 추가
