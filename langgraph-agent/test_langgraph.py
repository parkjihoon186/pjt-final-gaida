import os
from dotenv import load_dotenv
from supabase import create_client

# .env 파일 경로 설정
# 현재 프로젝트 디렉토리(/langgraph-agent)의 상위 폴더인 'pjt-final-gaida'에 .env 파일이 있습니다.
dotenv_path = '/Users/jaehyuntak/Desktop/project_at25-09-15/pjt-final-gaida/.env'

# .env 파일 로드
load_dotenv(dotenv_path)

# 환경 변수에서 Supabase URL과 Anon Key 불러오기
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

# 환경 변수가 제대로 로드되었는지 확인하고, 없을 경우 오류 메시지 출력
if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    raise ValueError("환경 변수 SUPABASE_URL 또는 SUPABASE_ANON_KEY가 설정되지 않았습니다.")

# Supabase 클라이언트 초기화
supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# 클라이언트가 성공적으로 초기화되었는지 확인
print("Supabase 클라이언트 초기화 완료")
print(f"Supabase URL: {SUPABASE_URL}")