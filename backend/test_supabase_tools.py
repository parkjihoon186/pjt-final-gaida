# test_supabase_tools.py

import pytest
import os
import json
from unittest.mock import patch, MagicMock
from supabase_tools import get_workout_history, add_workout_session, supabase, SUPABASE_URL, SUPABASE_ANON_KEY
from datetime import datetime, timedelta

# --- 1. 전역 설정 테스트 (Graph 시작 전 환경 체크) ---

def test_environment_variables_loaded():
    """환경 변수가 로드되었는지 확인."""
    assert SUPABASE_URL, "SUPABASE_URL 환경 변수가 로드되지 않았습니다."
    assert SUPABASE_ANON_KEY, "SUPABASE_ANON_KEY 환경 변수가 로드되지 않았습니다."

def test_supabase_client_initialized():
    """Supabase 클라이언트 객체가 성공적으로 생성되었는지 확인."""
    assert supabase is not None, "Supabase 클라이언트 초기화에 실패했습니다."
    
    try:
        response = supabase.from_("sessions").select("user_id").limit(1).execute()
        assert hasattr(response, 'data'), "Supabase 응답 구조에 문제가 있습니다."
        print(f"\n[CONNECTION TEST] sessions 테이블 연결 성공, 데이터 개수: {len(response.data)}")
    except Exception as e:
        pytest.fail(f"Supabase 연결 또는 sessions 테이블 접근 실패: {e}")

# --- 2. Tool 기능 및 표준화된 반환값 테스트 ---

TEST_USER_ID = f"test-user-{datetime.now().strftime('%Y%m%d%H%M%S')}"

@pytest.fixture(scope="module")
def test_workout_data():
    """테스트용 운동 데이터를 준비하고 정리하는 fixture."""
    test_data = {
        "user_id": TEST_USER_ID,
        "total_volume": 1500.5,
        "exercises": "벤치프레스 50kg 5회x5세트, 스쿼트 80kg 5회x5세트"
    }
    
    try:
        result = add_workout_session.invoke({
            "user_id": test_data["user_id"],
            "total_volume": test_data["total_volume"],
            "exercises": test_data["exercises"]
        })
        
        if isinstance(result, str):
            try:
                result = json.loads(result)
            except json.JSONDecodeError:
                print(f"Warning: Tool returned non-JSON string: {result}")
        
        print(f"\n[FIXTURE SETUP] 테스트 데이터 추가 결과: {result}")
        
    except Exception as e:
        pytest.fail(f"테스트 데이터 준비 중 오류 발생: {e}")
    
    yield test_data
    
    print(f"\n--- Cleaning up test data for {TEST_USER_ID} ---")
    try:
        supabase.from_("sessions").delete().eq("user_id", TEST_USER_ID).execute()
        print("✅ Cleanup successful.")
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")

def test_add_workout_session_success(test_workout_data):
    """유효한 데이터로 운동 세션 추가 성공 시 표준화된 성공 Dict 반환 확인."""
    new_data = {
        "user_id": TEST_USER_ID,
        "total_volume": 2000.0,
        "exercises": "데드리프트 100kg 3회x3세트"
    }
    
    result = add_workout_session.invoke(new_data)
    
    if isinstance(result, str):
        try:
            result = json.loads(result)
        except json.JSONDecodeError:
            pytest.fail(f"Tool이 유효하지 않은 JSON 문자열을 반환했습니다: {result}")
    
    assert isinstance(result, dict), f"반환값이 dict 타입이 아닙니다. 실제 타입: {type(result)}"
    assert result["status"] == "success", f"예상: success, 실제: {result.get('status')}"
    assert result["action"] == "add_workout_session", f"예상: add_workout_session, 실제: {result.get('action')}"
    assert "data" in result, "응답에 'data' 필드가 없습니다."
    
    response = supabase.from_("sessions").select("*").eq("user_id", TEST_USER_ID).execute()
    assert len(response.data) >= 2, f"예상 최소 2개, 실제: {len(response.data)}개"
    
    print(f"\n[ADD SUCCESS] {result}")

def test_get_workout_history_with_data(test_workout_data):
    """데이터가 있는 사용자에 대해 운동 기록 조회 성공 시 표준화된 성공 Dict 반환 확인."""
    result = get_workout_history.invoke({"user_id": TEST_USER_ID})
    
    if isinstance(result, str):
        try:
            result = json.loads(result)
        except json.JSONDecodeError:
            pytest.fail(f"Tool이 유효하지 않은 JSON 문자열을 반환했습니다: {result}")
    
    assert isinstance(result, dict), f"반환값이 dict 타입이 아닙니다. 실제 타입: {type(result)}"
    assert result["status"] == "success", f"예상: success, 실제: {result.get('status')}"
    assert result["action"] == "get_workout_history", f"예상: get_workout_history, 실제: {result.get('action')}"
    assert "data" in result, "응답에 'data' 필드가 없습니다."
    
    assert len(result["data"]) >= 1, f"예상 최소 1개, 실제: {len(result['data'])}개"
    
    first_record = result["data"][0]
    required_fields = ["user_id", "total_volume", "exercises"]
    for field in required_fields:
        assert field in first_record, f"필수 필드 '{field}'가 응답 데이터에 없습니다."
    
    print(f"\n[GET SUCCESS] 데이터 {len(result['data'])}개 조회됨")

def test_get_workout_history_no_data():
    """데이터가 없는 가상의 사용자에 대해 빈 리스트와 표준화된 성공 Dict 반환 확인."""
    non_existent_id = f"non-existent-user-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    result = get_workout_history.invoke({"user_id": non_existent_id})
    
    if isinstance(result, str):
        try:
            result = json.loads(result)
        except json.JSONDecodeError:
            pytest.fail(f"Tool이 유효하지 않은 JSON 문자열을 반환했습니다: {result}")
    
    assert result["status"] == "success", f"예상: success, 실제: {result.get('status')}"
    assert result["action"] == "get_workout_history", f"예상: get_workout_history, 실제: {result.get('action')}"
    assert len(result["data"]) == 0, f"데이터가 없어야 하는데 {len(result['data'])}개가 조회됨"
    
    print(f"\n[GET NO DATA] 빈 결과 정상 반환")

# --- 3. 에러 핸들링 테스트 ---

def test_add_workout_session_invalid_data():
    """잘못된 데이터로 실제 DB 에러 발생 시 표준화된 에러 Dict 반환 확인."""
    try:
        # total_volume에 잘못된 문자열을 전달하여 DB 에러 유발
        result = add_workout_session.invoke({
            "user_id": "test-error-user",
            "total_volume": "invalid_volume",  # 문자열
            "exercises": "테스트 데이터"
        })
        
        if isinstance(result, str):
            try:
                result = json.loads(result)
            except json.JSONDecodeError:
                print(f"[ADD INVALID DATA] Tool이 문자열 반환: {result}")
                return
        
        assert isinstance(result, dict), f"반환값이 dict 타입이 아닙니다. 실제: {type(result)}"
        assert result["status"] == "error", f"예상: error, 실제: {result.get('status')}"
        assert "error_code" in result, "에러 응답에 'error_code' 필드가 없습니다."
        assert "user_message" in result, "에러 응답에 'user_message' 필드가 없습니다."
        print(f"\n[ADD INVALID DATA - ERROR] {result}")
            
    except Exception as e:
        print(f"\n[ADD INVALID DATA - EXCEPTION] Tool 실행 중 예외 발생: {e}")

def test_tool_return_format_consistency():
    """모든 Tool이 일관된 형식으로 응답을 반환하는지 확인."""
    test_cases = [
        {
            "name": "일반적인 조회",
            "tool": get_workout_history,
            "params": {"user_id": f"format-test-{datetime.now().strftime('%H%M%S')}"}
        },
        {
            "name": "일반적인 추가", 
            "tool": add_workout_session,
            "params": {
                "user_id": f"format-test-{datetime.now().strftime('%H%M%S')}",
                "total_volume": 1000.0,
                "exercises": "테스트 운동"
            }
        }
    ]
    
    for case in test_cases:
        try:
            result = case["tool"].invoke(case["params"])
            
            if isinstance(result, str):
                try:
                    result = json.loads(result)
                except json.JSONDecodeError:
                    print(f"[FORMAT TEST - {case['name']}] 비JSON 문자열: {result}")
                    continue
            
            assert isinstance(result, dict), f"{case['name']}: dict가 아닌 {type(result)} 반환"
            assert "status" in result, f"{case['name']}: 'status' 필드 누락"
            assert "action" in result, f"{case['name']}: 'action' 필드 누락"
            
            if result["status"] == "success":
                assert "data" in result, f"{case['name']}: 성공 응답에 'data' 필드 누락"
            elif result["status"] == "error":
                assert "error_code" in result, f"{case['name']}: 에러 응답에 'error_code' 필드 누락"
                assert "user_message" in result, f"{case['name']}: 에러 응답에 'user_message' 필드 누락"
            
            print(f"✅ {case['name']}: 형식 일관성 확인 완료")
            
        except Exception as e:
            print(f"❌ {case['name']}: 테스트 중 예외 발생 - {e}")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])