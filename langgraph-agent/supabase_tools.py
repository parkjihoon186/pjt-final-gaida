import os
from dotenv import load_dotenv
from supabase import create_client, Client
from langchain_core.tools import tool
from typing import Optional

load_dotenv()

# Supabase 클라이언트 초기화
url: Optional[str] = os.environ.get("SUPABASE_URL")
key: Optional[str] = os.environ.get("SUPABASE_ANON_KEY")

# 기존 코드의 문제점:
# 이전에 오류가 발생했을 때 supabase 객체가 None이 될 수 있습니다.
# try-except 블록 밖에서 supabase 객체를 다시 생성해야 합니다.

# 수정된 코드:
# try-except 블록을 재시작하는 함수를 만듭니다.
def initialize_supabase_client():
    url: Optional[str] = os.environ.get("SUPABASE_URL")
    key: Optional[str] = os.environ.get("SUPABASE_ANON_KEY")
    
    try:
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in the .env file")
        return create_client(url, key)
    except Exception as e:
        print(f"Error initializing Supabase client: {e}")
        return None

# 전역 변수 초기화
supabase = initialize_supabase_client()

@tool
def get_workout_history(user_id: str) -> str:
    """Gets the workout history for a specific user.
    This tool connects to the 'sessions' table in Supabase.
    """
    if not supabase:
        return "Supabase connection is not available."

    try:
        # 수정된 부분: .from_() 메서드 사용
        response = supabase.table('sessions').select('*').eq('user_id', user_id).execute()
        
        if response.data:
            return f"Found workout history for user {user_id}: {response.data}"
        else:
            return f"No workout history found for user {user_id}."

    except Exception as e:
        return f"An error occurred while fetching workout history: {e}"

@tool
def add_workout_session(user_id: str, date: str, session_details: str) -> str:
    """Adds a new workout session for a user.
    This tool connects to the 'sessions' table in Supabase.
    """
    if not supabase:
        return "Supabase connection is not available."
    
    try:
        data = {
            'user_id': user_id,
            'date': date,
            'session_details': session_details
        }
        # 수정된 부분: .from_() 메서드 사용
        response = supabase.table('sessions').insert(data).execute()
        
        if response.data:
            return f"Successfully added workout session for user {user_id} on {date}."
        else:
            return "Failed to add workout session."

    except Exception as e:
        return f"An error occurred while adding workout session: {str(e)}"