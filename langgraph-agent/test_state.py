# 'test_state.py'
# 1. 올바른 TypedDict 사용법: 일반 dict로 생성 후 타입 힌트 적용

from state import State, AgentDecisionModel
import json
test_state: State = {
    "question": "Test serialization",
    "dataset": None,
    "code": "",
    "code_lang": "python",
    "result": "",
    "answer": "",
    "execution_context": None,
    "messages": [],
    "intermediate_steps": [],
    "active_node": "DecisionNode",
    "loop_counter": 0,
    "decision": AgentDecisionModel(
        action_type="tool_call", 
        tool_calls=[{"name": "test_tool", "args": {"user_id": "123"}}]
    ).model_dump(),
    "tool_outputs": [],
    "error_info": None,
    "subgraph_output": None
}

# 2. JSON 직렬화 테스트
try:
    json_output = json.dumps(test_state, indent=2)
    print("✅ State 객체 JSON 직렬화 성공")
    print(f"직렬화된 데이터 샘플:\n{json_output[:200]}...")
except TypeError as e:
    print(f"❌ JSON 직렬화 실패: {e}")

# 3. 추가 검증: 필수 필드 누락 검사
required_fields = ["question", "messages", "intermediate_steps"]
missing_fields = [field for field in required_fields if field not in test_state]
if missing_fields:
    print(f"⚠️ 필수 필드 누락: {missing_fields}")
else:
    print("✅ 필수 필드 모두 존재")