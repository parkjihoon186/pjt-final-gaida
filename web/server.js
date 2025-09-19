const express = require('express');
const path = require('path');
require('dotenv').config(); // .env 파일에서 환경 변수를 로드합니다.
const { createClient } = require('@supabase/supabase-js');

const app = express();
const port = process.env.PORT || 3000;

// 요청의 본문을 JSON으로 파싱하기 위한 미들웨어입니다.
app.use(express.json());

// Supabase 클라이언트 초기화
const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_ANON_KEY;
if (!supabaseUrl || !supabaseKey) {
    console.error("치명적 오류: Supabase URL 또는 Key가 .env 파일에 설정되지 않았습니다.");
    process.exit(1); // 키가 없으면 서버 실행 중단
}
const supabase = createClient(supabaseUrl, supabaseKey);

const getUserId = (req) => req.headers['x-user-id'];

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

// --- Supabase 데이터 프록시 엔드포인트 ---

// 세션 데이터 가져오기
app.get('/api/sessions', async (req, res) => {
    const userId = getUserId(req);
    if (!userId) return res.status(400).json({ error: 'User ID가 필요합니다.' });

    try {
        const { data, error } = await supabase.from('sessions').select('*').eq('user_id', userId).order('created_at', { ascending: false });
        if (error) throw error;
        res.json(data);
    } catch (error) {
        console.error('세션 데이터 로드 오류:', error);
        res.status(500).json({ error: '세션 데이터를 가져오는 데 실패했습니다.' });
    }
});

// 세션 데이터 기록하기
app.post('/api/sessions', async (req, res) => {
    const userId = getUserId(req);
    if (!userId) return res.status(400).json({ error: 'User ID가 필요합니다.' });

    const { total_volume, exercises } = req.body;
    try {
        const { data, error } = await supabase.from('sessions').insert({ user_id: userId, total_volume, exercises }).select();
        if (error) throw error;
        res.status(201).json(data);
    } catch (error) {
        console.error('세션 기록 오류:', error);
        res.status(500).json({ error: '세션 기록에 실패했습니다.' });
    }
});

// 영양 데이터 가져오기
app.get('/api/nutrition', async (req, res) => {
    const userId = getUserId(req);
    if (!userId) return res.status(400).json({ error: 'User ID가 필요합니다.' });

    try {
        const { data, error } = await supabase.from('nutrition').select('*').eq('user_id', userId).order('created_at', { ascending: false });
        if (error) throw error;
        res.json(data);
    } catch (error) {
        console.error('영양 데이터 로드 오류:', error);
        res.status(500).json({ error: '영양 데이터를 가져오는 데 실패했습니다.' });
    }
});

// 영양 데이터 기록하기
app.post('/api/nutrition', async (req, res) => {
    const userId = getUserId(req);
    if (!userId) return res.status(400).json({ error: 'User ID가 필요합니다.' });

    try {
        const { data, error } = await supabase.from('nutrition').insert({ ...req.body, user_id: userId }).select();
        if (error) throw error;
        res.status(201).json(data);
    } catch (error) {
        res.status(500).json({ error: '영양 기록에 실패했습니다.' });
    }
});

app.listen(port, () => {
    console.log(`서버가 http://localhost:${port} 에서 실행 중입니다.`);
    console.log(`앱에 접속하려면 브라우저에서 http://localhost:${port} 를 여세요.`);
});
