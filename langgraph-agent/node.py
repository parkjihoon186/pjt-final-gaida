# node.py

import json
from typing import Dict, Any, List, Literal, Union
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, BaseMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain import hub
from langchain.agents import create_tool_calling_agent, AgentExecutor
from state import State, AgentDecisionModel, ErrorInfo # state.py에서 정의된 클래스 임포트
from supabase_tools import get_workout_history, add_workout_session # 실제 도구 임포트

# ----------------------------------------------------
# 0. 초기 설정 및 도구 바인딩
# ----------------------------------------------------

# AgentExecutor에서 사용할 전체 도구 목록
TOOLS = [get_workout_history, add_workout_session]

# LLM 초기화 (gpt-4가 추론 및 Tool Calling 성능이 더 좋으므로, 필요시 gpt-4o-mini로 변경 가능)
llm = ChatOpenAI(model="gpt-4", temperature=0)

# Decision 노드에서 사용할 LLM (gpt-4로 )
llm_decision = ChatOpenAI(model="gpt-4", temperature=0)

# Agent Executor 설정 (Tool 호출 로직 처리를 위해 필요)
agent = create_tool_calling_agent(llm, TOOLS, hub.pull("hwchase17/openai-tools-agent"))
agent_executor = AgentExecutor(agent=agent, tools=TOOLS, verbose=True)

# ----------------------------------------------------
# A-2: AgentDecision 노드 구현 (Graph의 라우터 역할)
# ----------------------------------------------------

def extract_message_content(message):
    """메시지에서 content를 안전하게 추출하는 헬퍼 함수"""
    if hasattr(message, 'content'):
        return message.content
    elif isinstance(message, dict) and 'content' in message:
        return message['content']
    else:
        return str(message)

def agent_decision(state: State) -> Dict[str, Union[AgentDecisionModel, str, int]]:
    """
    사용자 질의를 분석하여 다음 행동(응답, 도구 호출, 최종 답변, 에러)을 결정합니다.
    """
    print(f"--- Node: AgentDecision (Loop: {state.get('loop_counter', 0)}) ---")
    
    # 상태 업데이트: 현재 실행 노드와 루프 카운터 기록
    current_loop = state.get('loop_counter', 0)
    
    # LLM이 도구 호출 또는 최종 답변을 결정하도록 유도하는 프롬프트
    
    # AgentExecutor를 사용하여 결정 로직을 간결하게 구현합니다.
    # 메시지에서 content 추출 (dict 또는 Message 객체 모두 처리)
    if state["messages"]:
        last_message = state["messages"][-1]
        if hasattr(last_message, 'content'):
            input_text = last_message.content
        elif isinstance(last_message, dict) and 'content' in last_message:
            input_text = last_message['content']
        else:
            input_text = str(last_message)
    else:
        input_text = "안녕하세요"
    
    agent_input = {
        "input": input_text,
        "chat_history": state["messages"][:-1],
        # "intermediate_steps": state.get("intermediate_steps", [])
    }
    
    # (Simplified approach for A-2): AgentExecutor를 활용하여 Tool 호출 여부 결정
    try:
        # **[!!! 핵심 수정 !!!] agent_executor.agent.invoke 대신, AgentExecutor 전체를 호출합니다.**
        # AgentExecutor의 invoke는 AgentAction (Tool Call) 또는 AgentFinish (Final Answer)를 반환합니다.
        # tools=[...]와 verbose=True 등의 설정은 이미 agent_executor 인스턴스에 포함되어 있습니다.
        agent_outcome = agent_executor.invoke(agent_input) # <-- 이 부분을 수정했습니다!
        
        # AgentExecutor의 실행 결과를 분석 (Tool Calling Agent 기준)
        if agent_outcome.get("tool_calls"):
            # Tool 호출을 결정한 경우 (AgentAction)
            tool_calls = agent_outcome["tool_calls"]
            decision_model = AgentDecisionModel(
                action_type="tool_call",
                tool_calls=tool_calls,
                subgraph_id=None
            )
            # LangGraph에서는 AgentExecutor가 전체 실행을 책임지므로,
            # LangGraph의 AgentDecision에서는 Tool Call만 감지하고 ToolExecutor로 라우팅합니다.
            
        elif agent_outcome.get("output"):
            # 최종 답변을 결정한 경우 (AgentFinish)
            final_answer = agent_outcome["output"]
            decision_model = AgentDecisionModel(
                action_type="final_answer",
                final_answer=final_answer
            )
        else:
            # 예상치 못한 결과
            raise ValueError("AgentExecutor가 Tool Call 또는 Final Answer를 반환하지 않았습니다.")


        # 상태 업데이트
        return {
            "active_node": "AgentDecision",
            "loop_counter": current_loop + 1,
            "decision": decision_model,
            "intermediate_steps": agent_outcome.get("intermediate_steps", []) # LangChain의 Intermediate Steps 반영
        }

    except Exception as e:
        # LLM 호출 실패 등 예외 발생 시 ErrorHandler로 전달 준비
        error_info = ErrorInfo(
            error_code="DECISION_LLM_FAILURE",
            # 상세 에러 메시지를 포함하여 디버깅 용이성 확보
            message=f"AgentDecision LLM 호출 실패: {type(e).__name__} - {str(e)}", 
            user_message="죄송합니다. 현재 질문을 이해하는 데 문제가 발생했습니다.",
            node="AgentDecision"
        )
        # ErrorHandler 노드로 라우팅하기 위해 error_info와 action_type을 설정
        return {
            "active_node": "AgentDecision",
            "error_info": error_info,
            "decision": AgentDecisionModel(action_type="error", tool_calls=None, final_answer=None), # action_type="error" 명시
            "loop_counter": current_loop + 1
        }
        
# ----------------------------------------------------
# A-3: ToolExecutor 노드 구현 (실제 도구 실행)
# ----------------------------------------------------

def tool_executor(state: State) -> Dict[str, Any]:
    """
    AgentDecision에서 결정된 도구 호출을 실행하고 그 결과를 상태에 저장합니다.
    """
    print("--- Node: ToolExecutor ---")
    
    # A-2에서 결정된 Tool 호출 목록 가져오기
    tool_calls = state["decision"].tool_calls
    if not tool_calls:
        # 예외 상황: decision이 tool_call인데 tool_calls가 없는 경우 (ErrorHandler로)
        error_info = ErrorInfo(
            error_code="TOOL_CALL_MISSING",
            message="AgentDecision에서 tool_call이 결정되었으나 호출 목록이 비어있음.",
            user_message="내부 시스템 오류로 도구 실행을 준비할 수 없습니다.",
            node="ToolExecutor"
        )
        return {"active_node": "ToolExecutor", "error_info": error_info}
        
    tool_outputs: List[ToolMessage] = []
    
    # 툴 호출 및 결과 수집
    for call in tool_calls:
        tool_name = call['function']['name']
        tool_args = json.loads(call['function']['arguments']) # JSON 문자열을 Dict로 변환
        tool_id = call['id']
        
        # TOOLS 목록에서 이름으로 해당 함수 찾기
        selected_tool = next(
            (t for t in TOOLS if t.name == tool_name),
            None
        )

        if not selected_tool:
            # 등록되지 않은 도구 호출 시 (ErrorHandler로)
            error_info = ErrorInfo(
                error_code="TOOL_NOT_FOUND",
                message=f"요청된 도구 '{tool_name}'을 찾을 수 없습니다.",
                user_message="요청하신 기능을 처리할 수 있는 도구가 없습니다.",
                node="ToolExecutor"
            )
            return {"active_node": "ToolExecutor", "error_info": error_info}

        # 실제 도구 실행 (supabase_tools.py의 함수 호출)
        try:
            # **S-2/S-3 표준화된 반환값**을 받습니다.
            tool_output_data = selected_tool.func(**tool_args)
            
            # ToolMessage 형태로 결과 저장 (LLM이 해석할 수 있는 형식)
            tool_outputs.append(
                ToolMessage(
                    content=json.dumps(tool_output_data), # 표준화된 Dict를 JSON 문자열로 변환
                    tool_call_id=tool_id,
                )
            )

        except Exception as e:
            # 도구 실행 중 예상치 못한 시스템 에러 발생 시 (ErrorHandler로)
            error_info = ErrorInfo(
                error_code="TOOL_EXECUTION_FAILURE",
                message=f"도구 '{tool_name}' 실행 중 시스템 오류 발생: {type(e).__name__} - {str(e)}",
                user_message="도구 실행 과정에서 예상치 못한 오류가 발생했습니다. 개발팀에 문의해 주세요.",
                node="ToolExecutor"
            )
            return {"active_node": "ToolExecutor", "error_info": error_info}
        
    # 성공적으로 실행된 경우 결과 반환
    return {
        "active_node": "ToolExecutor",
        "tool_outputs": tool_outputs, # ToolMessage 리스트
        "messages": tool_outputs # messages에도 추가하여 다음 LLM 추론에 사용
    }

# ----------------------------------------------------
# B-2: ResultProcessor 노드 구현 (결과 가공)
# ----------------------------------------------------

def result_processor(state: State) -> Dict[str, Any]:
    """
    ToolExecutor의 결과 또는 AgentDecision의 최종 답변을 받아 사용자에게 친화적인
    최종 메시지로 가공하고 Graph를 종료합니다.
    """
    print("--- Node: ResultProcessor ---")
    
    decision_type = state["decision"].action_type

    if decision_type == "final_answer":
        # A-2에서 LLM이 최종 답변을 바로 준 경우
        final_answer = state["decision"].final_answer
        
    elif decision_type == "tool_call" and state.get("tool_outputs"):
        # A-3에서 Tool이 실행된 결과를 기반으로 답변을 생성해야 하는 경우
        
        # AgentExecutor의 실행을 사용하여 Tool 결과를 기반으로 최종 답변 생성
        tool_output_messages = state["tool_outputs"] 
        
        # Tool 결과를 포함하여 AgentExecutor를 다시 실행
        agent_input = {
            "input": state["messages"][-2].content if len(state["messages"]) >= 2 else "", # 원본 HumanMessage
            "chat_history": state["messages"][:-2] + [state["messages"][-1]] if len(state["messages"]) >= 2 else [],
            "intermediate_steps": state.get("intermediate_steps", [])
        }
        
        # Tool 호출 이후의 메시지 (ToolMessage)는 intermediate_steps에 포함되지 않고 messages에 추가되어야 합니다.
        
        # AgentExecutor에 Tool 호출 결과(ToolMessage)를 포함하여 최종 답변 유도
        final_outcome = agent_executor.agent.invoke(agent_input)
        
        final_answer = final_outcome.content
        
    else:
        # tool_call이었으나 tool_outputs이 없는 경우 (ErrorHandler로 가는 것이 맞으나, 여기서는 안전 종료)
        final_answer = "죄송합니다. 요청하신 정보 처리에 실패했지만, 에러 핸들러로 라우팅되지 않았습니다. (내부 로직 오류)"

    # 최종 결과 반환 (Graph 종료 준비)
    final_message = AIMessage(content=final_answer)

    # Graph 종료 시 answer와 messages를 반환
    return {
        "active_node": "ResultProcessor",
        "answer": final_answer,
        "messages": [final_message]
    }


# ----------------------------------------------------
# C-1: ErrorHandler 노드 구현 (에러 처리)
# ----------------------------------------------------

def error_handler(state: State) -> Dict[str, Any]:
    """
    에러 정보를 받아 사용자 친화적인 메시지를 생성하고 Graph를 안전하게 종료합니다.
    """
    print("--- Node: ErrorHandler ---")
    
    # **수정: state["error_info"]가 딕셔너리일 경우 Pydantic 객체로 변환**
    error_info_raw = state.get("error_info")
    if isinstance(error_info_raw, dict):
        # 딕셔너리를 ErrorInfo Pydantic 모델로 변환
        error_info = ErrorInfo(**error_info_raw)
    elif isinstance(error_info_raw, ErrorInfo):
        # 이미 Pydantic 객체인 경우 그대로 사용
        error_info = error_info_raw
    else:
        # 예상치 못한 에러 정보 형식 (비상 종료)
        error_info = ErrorInfo(
            error_code="INTERNAL_ERROR",
            message=f"ErrorHandler called with invalid error_info type: {type(error_info_raw)}",
            user_message="내부 시스템 오류가 발생했습니다. 개발자에게 문의해 주세요.",
            node="ErrorHandler"
        )
    
    # 1. 개발자용 로그 기록 
    print(f"\n[SYSTEM ERROR LOG] Node: {error_info.node} | Code: {error_info.error_code}")
    print(f"[SYSTEM ERROR LOG] Detail: {error_info.message}\n")
    
    # 2. 사용자에게 보여줄 최종 메시지 생성
    user_friendly_message = error_info.user_message

    final_message = AIMessage(
        content=f"🚨 오류 발생: {user_friendly_message}\n\n(오류 코드: {error_info.error_code})",
    )

    # Graph 종료 시 answer와 messages를 반환
    return {
        "active_node": "ErrorHandler",
        "answer": final_message.content, # 최종 메시지 전체를 answer에 저장
        "messages": state["messages"] + [final_message]
    }

# ----------------------------------------------------
# Graph 라우팅 결정 함수 (Edge 결정에 사용)
# ----------------------------------------------------

def route_decision(state: State) -> Literal["ToolExecutor", "ResultProcessor", "ErrorHandler"]:
    """
    AgentDecision 노드가 반환한 decision 모델을 기반으로 다음 노드를 결정합니다.
    """
    # 에러 정보가 State에 있다면 즉시 ErrorHandler로 라우팅
    if state.get("error_info"):
        return "ErrorHandler"
    
    # decision이 없는 경우 (예외 상황)
    if not state.get("decision"):
        return "ErrorHandler" 

    decision_type = state["decision"].action_type

    if decision_type == "tool_call":
        return "ToolExecutor"
    elif decision_type == "final_answer":
        return "ResultProcessor"
    elif decision_type == "error":
        # AgentDecision 자체에서 결정 오류를 인지한 경우
        return "ErrorHandler"
    else:
        # 예상치 못한 decision_type
        return "ErrorHandler"