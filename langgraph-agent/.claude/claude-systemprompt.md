
systemprompt
- 최소화된 기능 단위 최소한의 task 단위로 구현하고 확장 하는 식으로 한 단계씩 넘어가라
   - 진행 상황을 체크 박스로 표시하고 완료된 것은 체크하면서 관리하라
- IF 3회 이상 문제 해결에 실패하면
   - 문제정의를 task 중심으로 재정의하라
   - 명시되지 않은 조건이 무엇인지 사용자 질의 및 추론해야 한다.
   - IF 3회 이상 같은 해결 방법에 실패하면
      - 해결 방법은 기존 해결 사례를 바탕으로 새로운 해결 방법을 추론해라
         - 기존 사례를 분석하기 위하여 핵심 키워드를 추론하라
      - 해결 방법은 창의적으로 접근해봐야 한다.
         - 이상적인 조건이 무엇인지 사용자 질의 및 추론해야 한다.
         - 이상적인 조건에 도달하기 위해서 현재 조건에서 조작가능한 변수(하이퍼 파라미터)가 무엇인지 추론해야 한다.


## starting_point
### 주소

(venv) jaehyuntak@Jaehyunui-MacBookAir langgraph-agent % tree
.
├── __pycache__
│   ├── state.cpython-313.pyc
│   └── supabase_tools.cpython-313.pyc
├── langgraph.ipynb
├── llm-systemprompt.md #
├── node.py
├── requirements.txt
├── state.py
├── supabase_tools.py
└── test_langgraph.py

### .env
#### 위치 
- '/Users/jaehyuntak/Desktop/project_at25-09-15/pjt-final-gaida/.env'
#### 내부 key 정보
- SUPABASE_URL
- SUPABASE_ANON_KEY
- GEMINI_API_KEY
- OPENAI_API_KEY

### vscode-settings
#### 위치
- 'pjt-final-gaida/langgraph-agent/.vscode/settings.json'
