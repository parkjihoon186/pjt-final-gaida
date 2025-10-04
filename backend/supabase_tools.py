# supabase_tools.py (최종 수정안)

import os
from dotenv import load_dotenv
from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions
from langchain_core.tools import tool
from typing import Dict, Any, Union

# ----------------------------------------------------
# 1. Supabase 클라이언트 연결 안정화 및 환경 변수 체크
# ----------------------------------------------------

load_dotenv(override=True) 

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    raise ValueError(
        "Supabase 환경 변수(SUPABASE_URL, SUPABASE_ANON_KEY)가 .env 파일에 설정되지 않았습니다."
    )

# Supabase 클라이언트 전역 변수 초기화
try:
    # ClientOptions는 필수는 아니지만 안정성을 높일 수 있습니다.
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY, options=ClientOptions(postgrest_client_timeout=10))
except Exception as e:
    # 초기화 오류는 치명적이므로 ConnectionError 발생
    raise ConnectionError(f"Supabase 클라이언트 초기화 중 치명적인 오류 발생: {e}")

# ----------------------------------------------------
# 2. 도구 정의 (실제 스키마: id, user_id, created_at, total_volume, exercises)
# ----------------------------------------------------

@tool
def get_workout_history(user_id: str) -> Union[Dict[str, Any], str]:
    """
    특정 사용자의 운동 기록을 가져옵니다. 
    반환값은 항상 구조화된 JSON/Dict 형태를 따릅니다.
    """
    try:
        # 'sessions' 테이블에서 user_id에 해당하는 데이터를 조회
        response = (
            supabase.from_("sessions")
            .select("*") # total_volume, exercises 포함
            .eq("user_id", user_id)
            .order("created_at", desc=True) # created_at을 기준으로 정렬
            .execute()
        )
        
        # 성공 시 표준화된 Dict 반환
        return {
            "status": "success",
            "action": "get_workout_history",
            "user_id": user_id,
            "data": response.data
        }
    
    except Exception as e:
        # 에러 메시지 포맷 수정 (type(e).__name__은 올바른 사용법입니다. 이전 오류는 캐시 때문일 가능성이 높음)
        return {
            "status": "error",
            "action": "get_workout_history",
            "error_code": "DB_QUERY_FAILURE",
            "message": f"운동 기록 조회 실패: {type(e).__name__} - {str(e)}",
            "user_message": "현재 사용자님의 운동 기록을 조회하는 데 문제가 발생했습니다. 잠시 후 다시 시도해 주세요."
        }

@tool
def add_workout_session(user_id: str, total_volume: float, exercises: str) -> Union[Dict[str, Any], str]:
    """
    새로운 운동 세션을 데이터베이스에 추가합니다. (스키마에 맞춰 컬럼 수정)
    
    Args:
        user_id (str): 사용자 ID.
        total_volume (float): 운동의 총 볼륨 (kg).
        exercises (str): 수행한 운동 목록 및 상세 내용 (JSON 문자열 형태 권장).
    """
    data_to_insert = {
        "user_id": user_id,
        "total_volume": total_volume,
        "exercises": exercises
        # 'date' 대신 'created_at'이 자동 생성되므로 수동 삽입에서 제외
    }
    
    try:
        # 'sessions' 테이블에 데이터 삽입
        response = (
            supabase.from_("sessions")
            .insert(data_to_insert)
            .execute()
        )
        
        # 성공 시 표준화된 Dict 반환
        return {
            "status": "success",
            "action": "add_workout_session",
            "user_id": user_id,
            "data": response.data
        }
        
    except Exception as e:
        # 에러 메시지 포맷 수정
        return {
            "status": "error",
            "action": "add_workout_session",
            "error_code": "DB_INSERT_FAILURE",
            # e는 예외 객체이므로 type(e).__name__은 정상 작동해야 합니다.
            "message": f"운동 세션 추가 실패: {type(e).__name__} - {str(e)}",
            "user_message": "죄송합니다. 새로운 운동 기록을 저장하지 못했습니다. 입력값을 확인해 주세요."
        }