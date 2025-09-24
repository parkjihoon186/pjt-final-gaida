
systemprompt
- 문제정의를 task 중심으로 재정의하고 문제 해결은 다각도로 창의적으로 접근해봐야 한다.
- 최소화된 기능 단위 최소한의 task 단위로 구현하고 확장 하는 식으로 한 단계씩 넘어가라


## starting_point
### 주소

(.venv) jaehyuntak@Jaehyunui-MacBookAir langgraph-agent % tree
.
├── langgraph.ipynb
├── llm-systemprompt.md
├── node.py
└── requirements.txt

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

## Task_Plan

langgraph-agent에서 tool-calling하는 Re Act 구조의 agent 파이썬 코드 작성해줘 

예상 작업 순서는 다음과 같아
- ipynb 파일 생성, 파이썬 인터프리터 설정 등 기본 설정
- langgraph 및 모듈 설정
- tool-calling 테스트 할 때  모듈화하면서 py파일로 옮기기 
- tool-calling은 처음에 supabase 연결
- 이후에 직접 만든 tool 기능과 sql,  coding 기능 추가
- supabase와 연동되는 운동, 식단 관련 state설정
- 아래 문서와 연동
"""
This JavaScript code structures a web application for tracking strength training and nutritional data, using a Node.js server to handle API requests and a front-end built with HTML, CSS (Tailwind), and JavaScript. The architecture follows a **Client-Server model**, where the client-side (index.html, JavaScript) interacts with the server-side (`server.js`) to manage data and utilize external services.

The structure can be broken down into the following key components:

### 1. **Client-Side (index.html & Script)**

This is the user interface and logic that runs in the browser. It's built with standard web technologies and external libraries for enhanced functionality.

* **HTML:** The `index.html` file defines the entire user interface. It's structured with a clean, responsive layout using **Tailwind CSS**, a utility-first framework [1]. It includes various sections for user input, data logs, and data visualization.
* **CSS:** The `<style>` block contains custom CSS, defining the application's dark theme, font styles (using Google Fonts), and animations (e.g., the `pulse` for loading and `sparkle` for achievements).
* **JavaScript:** The `<script type="module">` block at the end of `index.html` contains the core client-side logic.
    * **UI Management:** It manages interactions with the DOM (Document Object Model), handling form submissions, button clicks, and dynamic content updates.
    * **API Calls:** It makes `fetch` requests to the Node.js server's API endpoints (`/api/sessions`, `/api/nutrition`, `/api/gemini`) to perform CRUD (Create, Read, Update, Delete) operations on data and to get AI analysis. This follows a **single-page application (SPA)** pattern, where the page content is updated dynamically without full page reloads.
    * **Local Storage:** It uses `localStorage` to persist non-sensitive user profile data and a unique `userId` across sessions, providing a simple form of personalization without requiring a formal login system.
    * **Data Visualization:** It uses the **Chart.js** library to dynamically create and update a progress chart, which is a common practice for data-driven front-end applications [2].

---

### 2. **Server-Side (`server.js`)**

This is a backend server built with **Node.js** and the **Express.js** framework [3]. It acts as an intermediary between the client and external services.

* **Express Server:** It sets up an HTTP server and defines various routes (`/`, `/api/sessions`, `/api/nutrition`, `/api/gemini`) to handle incoming requests from the client.
* **API Gateway/Proxy:** The server functions as a **proxy**, protecting sensitive information and managing requests to third-party services.
    * **Supabase Proxy:** It handles all interactions with the **Supabase** backend-as-a-service. By proxying these requests, it hides the `SUPABASE_ANON_KEY` from the client and allows for server-side validation and data manipulation. The use of Supabase for database operations (e.g., `supabase.from('sessions').insert(...)`) is an example of a **BaaS (Backend as a Service)** architecture [4].
    * **Gemini API Proxy:** The `/api/gemini` endpoint is crucial. It securely handles the `GEMINI_API_KEY` on the server and forwards the client's request to the Google Gemini API. This prevents the API key from being exposed in the client-side code, which is a critical security practice [5].

---

### 3. **Data & External Services**

The application relies on several external components to function.

* **Supabase:** A backend platform providing a PostgreSQL database, authentication, and API services. It's used here for data storage, including user sessions and nutrition information.
* **Google Gemini API:** A generative AI service used for analyzing training and nutrition data and providing personalized feedback. The server communicates with this API.
* **Environment Variables (`.env`):** The application uses a `.env` file to store sensitive keys (`SUPABASE_URL`, `SUPABASE_ANON_KEY`, `GEMINI_API_KEY`). This practice, part of the **Twelve-Factor App methodology**, ensures that sensitive configurations are not hardcoded into the source code and can be managed separately in different environments [6].

### **Architecture Diagram**



### **Representative Documents & Citations**

1.  **Tailwind CSS:** **"Tailwind CSS: A Utility-First CSS Framework."** This framework's documentation outlines its core philosophy of using pre-defined utility classes directly in HTML to build UIs, a key part of this application's front-end styling.
2.  **Chart.js:** **"Chart.js Documentation."** The official documentation for this open-source JavaScript library is the go-to resource for understanding how to render charts on the front-end based on data fetched from an API.
3.  **Express.js:** **"Express.js Guide."** This document explains how to set up a Node.js server, define API routes (`app.get`, `app.post`), and use middleware (`app.use(express.json())`), all of which are fundamental to the `server.js` file.
4.  **Supabase:** **"Supabase: The Open Source Firebase Alternative."** This platform's documentation details its aBaaS (Auth as a Service, Backend as a Service) features and how to use the Supabase JavaScript client library (`@supabase/supabase-js`) to interact with the database.
5.  **OWASP Top 10:** **"A05:2021-Security Misconfiguration."** The use of a server-side proxy to handle the Gemini API key, rather than exposing it on the client, is a direct application of this security principle to prevent sensitive data leakage.
6.  **The Twelve-Factor App:** **"III. Config."** This section of the influential manifesto for building software-as-a-service emphasizes the importance of storing configuration data, such as API keys, in environment variables. This is reflected in the use of the `dotenv` library in `server.js`.
"""

genemi-system-prompt-policy
- 최소화된 기능 단위 최소한의 task로 구현하고 확장 하는 식으로 한 단계씩 넘어갈꺼야
- ### process-task-list.mdc
---
description: 
globs: 
alwaysApply: false
---
# Task List Management

Guidelines for managing task lists in markdown files to track progress on completing a PRD

## Task Implementation
- **One sub-task at a time:** Do **NOT** start the next sub‑task until you ask the user for permission and they say “yes” or "y"
- **Completion protocol:**  
  1. When you finish a **sub‑task**, immediately mark it as completed by changing `[ ]` to `[x]`.  
  2. If **all** subtasks underneath a parent task are now `[x]`, also mark the **parent task** as completed.  
- Stop after each sub‑task and wait for the user’s go‑ahead.

## Task List Maintenance

1. **Update the task list as you work:**
   - Mark tasks and subtasks as completed (`[x]`) per the protocol above.
   - Add new tasks as they emerge.

2. **Maintain the “Relevant Files” section:**
   - List every file created or modified.
   - Give each file a one‑line description of its purpose.

## AI Instructions

When working with task lists, the AI must:

1. Regularly update the task list file after finishing any significant work.
2. Follow the completion protocol:
   - Mark each finished **sub‑task** `[x]`.
   - Mark the **parent task** `[x]` once **all** its subtasks are `[x]`.
3. Add newly discovered tasks.
4. Keep “Relevant Files” accurate and up to date.
5. Before starting work, check which sub‑task is next.
6. After implementing a sub‑task, update the file and then pause for user approval.

---
