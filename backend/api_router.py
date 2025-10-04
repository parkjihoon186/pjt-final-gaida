# api_router.py

import os
from fastapi import APIRouter, Header, HTTPException, Body, Response
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# supabase_tools에서 실제 DB 작업을 수행하는 함수들을 가져옵니다.
from supabase_tools import supabase

# Pydantic 모델 정의 (server.js의 body 파싱 로직 참고)
class SessionData(BaseModel):
    total_volume: float
    exercises: Dict[str, Any] | List[Any] # JSON 객체/배열을 직접 받도록 수정

class NutritionData(BaseModel):
    # meal_date는 DB에 없으므로 제거. created_at이 자동으로 생성됨.
    carbs: float
    protein: float
    fat: float
    extra_nutrients: Dict[str, Any] = {} # bcaa, creatine 등 추가 필드를 받기 위함

# AI Coach API 요청을 위한 Pydantic 모델
class CoachRequest(BaseModel):
    system_prompt: str
    user_prompt: str


# API 라우터 생성
router = APIRouter(
    prefix="/api",
    tags=["db_proxy"],
)

# --- /api/sessions 엔드포인트 ---

@router.get("/sessions", response_model=List[Dict[str, Any]])
async def get_sessions(x_user_id: Optional[str] = Header(None)):
    """사용자의 모든 운동 세션 기록을 조회합니다."""
    if not x_user_id:
        raise HTTPException(status_code=400, detail="x-user-id header is required")
    
    try:
        response = supabase.from_("sessions").select("*").eq("user_id", x_user_id).order("created_at", desc=True).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")

@router.post("/sessions")
async def post_session(data: SessionData, x_user_id: Optional[str] = Header(None)):
    """새로운 운동 세션을 기록합니다."""
    if not x_user_id:
        raise HTTPException(status_code=400, detail="x-user-id header is required")

    try:
        insert_data = {
            "user_id": x_user_id,
            "total_volume": data.total_volume,
            "etc": data.exercises # DB 컬럼명 'etc'와 일치하도록 수정
        }
        response = supabase.from_("sessions").insert(insert_data).execute()
        return Response(status_code=201) # 201 Created
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database insert failed: {str(e)}")


# --- /api/nutrition 엔드포인트 ---

@router.get("/nutrition", response_model=List[Dict[str, Any]])
async def get_nutrition(x_user_id: Optional[str] = Header(None)):
    """사용자의 모든 영양 기록을 조회합니다."""
    if not x_user_id:
        raise HTTPException(status_code=400, detail="x-user-id header is required")
    
    try:
        response = supabase.from_("nutrition").select("*").eq("user_id", x_user_id).order("created_at", desc=True).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")

@router.post("/nutrition")
async def post_nutrition(data: NutritionData, x_user_id: Optional[str] = Header(None)):
    """새로운 영양 정보를 기록합니다."""
    if not x_user_id:
        raise HTTPException(status_code=400, detail="x-user-id header is required")

    try:
        insert_data = {
            "user_id": x_user_id,
            "carbs": data.carbs,
            "protein": data.protein,
            "fat": data.fat,
            **data.extra_nutrients # 추가 영양소들을 insert_data에 병합
        }
        response = supabase.from_("nutrition").insert(insert_data).execute()
        return Response(status_code=201) # 201 Created
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database insert failed: {str(e)}")


# --- /api/coach 엔드포인트 (AI 코치 - OpenAI 사용) ---

@router.post("/coach", response_model=Dict[str, str])
async def get_coaching_advice(request: CoachRequest):
    """
    프론트엔드로부터 받은 시스템 프롬프트와 사용자 프롬프트를 사용하여
    OpenAI LLM을 호출하고, 생성된 조언을 반환합니다.
    """
    try:
        # LLM 초기화 (gpt-4o-mini는 비용 효율적이고 빠릅니다)
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

        # 프롬프트 템플릿 설정
        prompt = ChatPromptTemplate.from_messages([
            ("system", request.system_prompt),
            ("user", "{input}")
        ])

        # 출력 파서 설정
        output_parser = StrOutputParser()

        # 체인 구성 및 실행
        chain = prompt | llm | output_parser
        advice = await chain.ainvoke({"input": request.user_prompt})

        return {"advice": advice}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Coach API 요청 실패: {str(e)}")