import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { supabase } from '@/lib/supabase'
import type { Word, WordInsert, WordUpdate } from '@/types/database'
import { useAuthStore } from './auth'

export const useVocabularyStore = defineStore('vocabulary', () => {
  const words = ref<Word[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const authStore = useAuthStore()

  const totalWords = computed(() => words.value.length)
  const recentWords = computed(() => 
    words.value
      .filter(word => {
        const createdAt = new Date(word.created_at)
        const threeDaysAgo = new Date()
        threeDaysAgo.setDate(threeDaysAgo.getDate() - 3)
        return createdAt >= threeDaysAgo
      })
      .length
  )

  const difficultWords = computed(() => 
    words.value.filter(word => word.difficulty_level >= 3)
  )

  // 載入所有單字
  const loadWords = async () => {
    if (!authStore.user) return

    loading.value = true
    error.value = null

    try {
      const { data, error: supabaseError } = await supabase
        .from('words')
        .select('*')
        .eq('user_id', authStore.user.id)
        .order('created_at', { ascending: false })

      if (supabaseError) throw supabaseError
      words.value = data || []
    } catch (err) {
      error.value = err instanceof Error ? err.message : '載入單字失敗'
      console.error('Load words error:', err)
    } finally {
      loading.value = false
    }
  }

  // 新增單字
  const addWord = async (wordData: Omit<WordInsert, 'user_id'>) => {
    if (!authStore.user) throw new Error('未登入')

    const { data, error: supabaseError } = await supabase
      .from('words')
      .insert({
        ...wordData,
        user_id: authStore.user.id
      })
      .select()
      .single()

    if (supabaseError) throw supabaseError
    
    words.value.unshift(data)
    return data
  }

  // 批次新增單字
  const addWords = async (wordsData: Omit<WordInsert, 'user_id'>[]) => {
    if (!authStore.user) throw new Error('未登入')

    const insertData = wordsData.map(word => ({
      ...word,
      user_id: authStore.user!.id
    }))

    const { data, error: supabaseError } = await supabase
      .from('words')
      .insert(insertData)
      .select()

    if (supabaseError) throw supabaseError
    
    words.value.unshift(...(data || []))
    return data
  }

  // 更新單字
  const updateWord = async (id: string, updates: WordUpdate) => {
    const { data, error: supabaseError } = await supabase
      .from('words')
      .update({
        ...updates,
        updated_at: new Date().toISOString()
      })
      .eq('id', id)
      .select()
      .single()

    if (supabaseError) throw supabaseError

    const index = words.value.findIndex(word => word.id === id)
    if (index !== -1) {
      words.value[index] = data
    }
    
    return data
  }

  // 刪除單字
  const deleteWord = async (id: string) => {
    const { error: supabaseError } = await supabase
      .from('words')
      .delete()
      .eq('id', id)

    if (supabaseError) throw supabaseError

    words.value = words.value.filter(word => word.id !== id)
  }

  // 搜尋單字
  const searchWords = async (query: string) => {
    if (!authStore.user) return []

    const { data, error: supabaseError } = await supabase
      .from('words')
      .select('*')
      .eq('user_id', authStore.user.id)
      .or(`word.ilike.%${query}%,chinese_meaning.ilike.%${query}%,english_meaning.ilike.%${query}%`)
      .order('created_at', { ascending: false })

    if (supabaseError) throw supabaseError
    return data || []
  }

  // 檢查單字是否存在
  const wordExists = async (word: string) => {
    if (!authStore.user) return false

    const { data, error: supabaseError } = await supabase
      .from('words')
      .select('id')
      .eq('user_id', authStore.user.id)
      .ilike('word', word)
      .limit(1)

    if (supabaseError) throw supabaseError
    return (data?.length || 0) > 0
  }

  // 獲取隨機單字用於複習
  const getRandomWords = async (limit: number = 20) => {
    if (!authStore.user) return []

    const { data, error: supabaseError } = await supabase
      .rpc('get_random_words', {
        user_id_param: authStore.user.id,
        limit_param: limit
      })

    if (supabaseError) {
      // 如果 RPC 函數不存在，使用備用方法
      console.warn('RPC function not found, using fallback method')
      const allWords = words.value.length > 0 ? words.value : await loadWords().then(() => words.value)
      const shuffled = [...allWords].sort(() => Math.random() - 0.5)
      return shuffled.slice(0, limit)
    }

    return data || []
  }

  // 更新單字難度
  const updateWordDifficulty = async (id: string, difficulty: number) => {
    return updateWord(id, { 
      difficulty_level: difficulty,
      review_count: words.value.find(w => w.id === id)?.review_count || 0 + 1,
      last_reviewed: new Date().toISOString()
    })
  }

  // 清空所有資料 (用於登出)
  const clearData = () => {
    words.value = []
    error.value = null
  }

  return {
    words,
    loading,
    error,
    totalWords,
    recentWords,
    difficultWords,
    loadWords,
    addWord,
    addWords,
    updateWord,
    deleteWord,
    searchWords,
    wordExists,
    getRandomWords,
    updateWordDifficulty,
    clearData
  }
})