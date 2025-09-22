const express = require('express');
const path = require('path');
require('dotenv').config(); // .env 파일에서 환경 변수를 로드합니다.

const app = express();
const port = process.env.PORT || 3000;

// 요청의 본문을 JSON으로 파싱하기 위한 미들웨어입니다.
app.use(express.json());

// 현재 디렉토리의 정적 파일(HTML, CSS, 클라이언트 JS)을 제공합니다.
app.use(express.static(__dirname));

// Gemini API 요청을 대신 처리해 줄 API 엔드포인트입니다.
app.post('/api/gemini', async (req, res) => {
    const { payload } = req.body;
    const apiKey = process.env.GEMINI_API_KEY;

    if (!apiKey) {
        return res.status(500).json({ error: '서버에 GEMINI_API_KEY가 설정되지 않았습니다.' });
    }
    if (!payload) {
        return res.status(400).json({ error: '요청 본문에 payload가 없습니다.' });
    }

    const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key=${apiKey}`;

    try {
        const geminiResponse = await fetch(apiUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!geminiResponse.ok) {
            const errorBody = await geminiResponse.text();
            console.error("Gemini API 오류:", errorBody);
            throw new Error(`Gemini API 요청 실패: ${geminiResponse.status}`);
        }

        const data = await geminiResponse.json();
        res.json(data);
    } catch (error) {
        console.error('Gemini API 프록시 오류:', error);
        res.status(500).json({ error: 'Gemini API로부터 응답을 받는데 실패했습니다.' });
    }
});

app.listen(port, () => {
    console.log(`서버가 http://localhost:${port} 에서 실행 중입니다.`);
    console.log(`앱에 접속하려면 브라우저에서 http://localhost:${port}/test_pjhat25-09-18.html 를 여세요.`);
});
