import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

interface WordRequest {
  word: string
}

interface WordResponse {
  word: string
  chinese_meaning: string
  english_meaning: string
  phonetic: string
  example_sentence: string
  synonyms: string[]
  antonyms: string[]
}

serve(async (req) => {
  // Handle CORS preflight requests
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    // Verify authentication
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_ANON_KEY') ?? '',
      {
        global: {
          headers: { Authorization: req.headers.get('Authorization')! },
        },
      }
    )

    const {
      data: { user },
    } = await supabaseClient.auth.getUser()

    if (!user) {
      return new Response(
        JSON.stringify({ error: 'Unauthorized' }),
        {
          status: 401,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        }
      )
    }

    const { word }: WordRequest = await req.json()

    if (!word) {
      return new Response(
        JSON.stringify({ error: 'Word is required' }),
        {
          status: 400,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        }
      )
    }

    // Call OpenAI API
    const openaiApiKey = Deno.env.get('OPENAI_API_KEY')
    if (!openaiApiKey) {
      throw new Error('OpenAI API key not configured')
    }

    const prompt = `請為英文單字 "${word}" 提供以下資訊，以 JSON 格式回應：
{
  "word": "${word}",
  "chinese_meaning": "中文翻譯",
  "english_meaning": "英文定義",
  "phonetic": "音標 (IPA格式)",
  "example_sentence": "英文例句",
  "synonyms": ["同義詞1", "同義詞2"],
  "antonyms": ["反義詞1", "反義詞2"]
}

請確保：
1. 中文翻譯準確且常用
2. 英文定義簡潔明瞭
3. 音標使用標準 IPA 格式
4. 例句實用且不超過20個單字
5. 同義詞和反義詞各提供2-3個，如果沒有可以提供空陣列
6. 只回應 JSON，不要其他文字`

    const openaiResponse = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${openaiApiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'gpt-3.5-turbo',
        messages: [
          {
            role: 'user',
            content: prompt
          }
        ],
        temperature: 0.3,
        max_tokens: 500
      })
    })

    if (!openaiResponse.ok) {
      throw new Error(`OpenAI API error: ${openaiResponse.status}`)
    }

    const openaiData = await openaiResponse.json()
    const content = openaiData.choices[0]?.message?.content

    if (!content) {
      throw new Error('No response from OpenAI')
    }

    // Parse JSON response
    let wordData: WordResponse
    try {
      wordData = JSON.parse(content)
    } catch (parseError) {
      console.error('Failed to parse OpenAI response:', content)
      throw new Error('Invalid response format from AI')
    }

    // Validate response structure
    if (!wordData.word || !wordData.chinese_meaning) {
      throw new Error('Incomplete word data from AI')
    }

    return new Response(
      JSON.stringify(wordData),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      }
    )

  } catch (error) {
    console.error('Error in ai-generate-word function:', error)
    
    return new Response(
      JSON.stringify({ 
        error: error.message || 'Internal server error',
        word: req.url.includes('word=') ? new URL(req.url).searchParams.get('word') : undefined
      }),
      {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      }
    )
  }
})