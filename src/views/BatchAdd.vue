<template>
  <div>
    <!-- 頁面標題 -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center">
          <h1>
            <i class="bi bi-plus-square"></i> 批次新增單字
          </h1>
          <div class="btn-group">
            <router-link to="/add" class="btn btn-outline-secondary">
              <i class="bi bi-plus-circle"></i> 單個新增
            </router-link>
            <router-link to="/" class="btn btn-outline-secondary">
              <i class="bi bi-arrow-left"></i> 返回首頁
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- 設定面板 -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="card bg-light">
          <div class="card-body">
            <div class="row align-items-center">
              <div class="col-md-6">
                <div class="d-flex align-items-center gap-3">
                  <label for="maxWords" class="form-label mb-0">單次限制：</label>
                  <input 
                    type="number" 
                    class="form-control" 
                    id="maxWords" 
                    v-model="maxWordsLimit"
                    min="1" 
                    max="50" 
                    style="width: 80px;"
                  >
                  <span class="text-muted">個單字</span>
                </div>
              </div>
              <div class="col-md-6 text-md-end">
                <span 
                  class="fw-bold"
                  :class="{
                    'text-primary': currentWords.length <= maxWordsLimit,
                    'text-warning': currentWords.length > maxWordsLimit * 0.8 && currentWords.length <= maxWordsLimit,
                    'text-danger': currentWords.length > maxWordsLimit
                  }"
                >
                  {{ currentWords.length }} / {{ maxWordsLimit }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 輸入區域 -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="card">
          <div class="card-header">
            <h5 class="card-title mb-0">
              <i class="bi bi-keyboard"></i> 輸入單字
            </h5>
          </div>
          <div class="card-body">
            <div class="mb-3">
              <label for="wordsInput" class="form-label">
                <i class="bi bi-type"></i> 英文單字（用空格分隔）
              </label>
              <textarea
                class="form-control"
                id="wordsInput"
                rows="6"
                v-model="wordsInput"
                placeholder="請輸入英文單字，用空格分隔，例如：apple banana orange cat dog"
                :disabled="loading"
                style="font-family: 'Courier New', monospace; font-size: 1rem;"
              ></textarea>
            </div>
            
            <div class="d-flex justify-content-between align-items-center">
              <div class="text-muted">
                <i class="bi bi-info-circle"></i> 
                輸入單字後點擊「AI 查詢」，系統會自動獲取音標、中文翻譯等資訊
              </div>
              <div class="btn-group">
                <button 
                  type="button" 
                  class="btn btn-outline-secondary" 
                  @click="clearInput"
                  :disabled="loading"
                >
                  <i class="bi bi-trash"></i> 清空
                </button>
                <button 
                  type="button" 
                  class="btn btn-primary" 
                  @click="startAIQuery"
                  :disabled="!canQuery || loading"
                >
                  <span v-if="loading" class="loading-spinner me-2"></span>
                  <i v-else class="bi bi-magic"></i> AI 查詢
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 預覽區域 -->
    <div class="row" v-if="showPreview">
      <div class="col-12">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="card-title mb-0">
              <i class="bi bi-eye"></i> 單字預覽
            </h5>
            <div class="btn-group">
              <button 
                type="button" 
                class="btn btn-outline-warning" 
                @click="retryErrors"
                v-if="errorWords.length > 0"
                :disabled="loading"
              >
                <i class="bi bi-arrow-repeat"></i> 重試錯誤 ({{ errorWords.length }})
              </button>
              <button 
                type="button" 
                class="btn btn-success" 
                @click="saveAllWords"
                :disabled="successWords.length === 0 || loading"
              >
                <span v-if="loading" class="loading-spinner me-2"></span>
                <i v-else class="bi bi-check-lg"></i> 儲存全部 ({{ successWords.length }})
              </button>
            </div>
          </div>
          <div class="card-body">
            <div class="row">
              <div 
                v-for="(result, word) in wordResults" 
                :key="word"
                class="col-md-6 col-lg-4 mb-3"
              >
                <div 
                  class="card h-100"
                  :class="{
                    'border-success': result.status === 'success',
                    'border-danger': result.status === 'error'
                  }"
                >
                  <div class="card-body">
                    <div v-if="result.status === 'success'">
                      <h6 class="card-title text-primary">{{ result.word }}</h6>
                      <p class="card-text small text-muted">{{ result.phonetic }}</p>
                      <p class="card-text">{{ result.chinese_meaning }}</p>
                      <p class="card-text small">{{ result.english_meaning }}</p>
                      <div v-if="result.example_sentence" class="small text-muted">
                        <strong>例句：</strong>{{ result.example_sentence }}
                      </div>
                    </div>
                    <div v-else>
                      <div class="d-flex justify-content-between align-items-start">
                        <div>
                          <h6 class="card-title text-danger">{{ word }}</h6>
                          <p class="card-text small text-muted">錯誤: {{ result.error }}</p>
                        </div>
                        <button 
                          class="btn btn-sm btn-outline-primary" 
                          @click="retryWord(word)"
                          :disabled="loading"
                        >
                          <i class="bi bi-arrow-repeat"></i>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 處理中覆蓋層 -->
    <div 
      v-if="loading && showProcessing" 
      class="position-fixed top-0 start-0 w-100 h-100 d-flex justify-content-center align-items-center"
      style="background: rgba(0,0,0,0.7); z-index: 9999;"
    >
      <div class="bg-white p-4 rounded text-center" style="min-width: 300px;">
        <div class="loading-spinner mb-3" style="width: 3rem; height: 3rem;"></div>
        <h5>{{ processingTitle }}</h5>
        <p class="text-muted mb-3">{{ processingMessage }}</p>
        <div class="progress mb-3">
          <div 
            class="progress-bar" 
            :style="{ width: processingProgress + '%' }"
          ></div>
        </div>
        <div v-if="processingDetails">
          <small class="text-muted">{{ processingDetails }}</small>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useVocabularyStore } from '@/stores/vocabulary'
import { supabase } from '@/lib/supabase'

const router = useRouter()
const vocabularyStore = useVocabularyStore()

// 響應式資料
const wordsInput = ref('')
const maxWordsLimit = ref(20)
const loading = ref(false)
const showPreview = ref(false)
const showProcessing = ref(false)
const wordResults = ref<Record<string, any>>({})

// 處理進度相關
const processingTitle = ref('AI 查詢中...')
const processingMessage = ref('正在獲取單字資訊，請稍候')
const processingProgress = ref(0)
const processingDetails = ref('')

// 計算屬性
const currentWords = computed(() => {
  const input = wordsInput.value.trim()
  if (!input) return []
  
  const words = input.split(/\s+/).filter(word => word.length > 0)
  return [...new Set(words.map(word => word.toLowerCase()))]
})

const canQuery = computed(() => {
  return currentWords.value.length > 0 && currentWords.value.length <= maxWordsLimit.value
})

const successWords = computed(() => {
  return Object.entries(wordResults.value)
    .filter(([_, result]) => result.status === 'success')
    .map(([word, _]) => word)
})

const errorWords = computed(() => {
  return Object.entries(wordResults.value)
    .filter(([_, result]) => result.status === 'error')
    .map(([word, _]) => word)
})

// 監聽單字數量變化
watch(currentWords, (newWords) => {
  if (newWords.length > maxWordsLimit.value) {
    // 可以在這裡顯示警告
  }
})

// 方法
const clearInput = () => {
  wordsInput.value = ''
  wordResults.value = {}
  showPreview.value = false
}

const startAIQuery = async () => {
  if (!canQuery.value) return

  loading.value = true
  showProcessing.value = true
  wordResults.value = {}
  processingProgress.value = 0

  try {
    const words = currentWords.value
    const total = words.length

    for (let i = 0; i < words.length; i++) {
      const word = words[i]
      const progress = ((i + 1) / total) * 100

      processingProgress.value = progress
      processingMessage.value = `處理中: ${word}`
      processingDetails.value = `${i + 1} / ${total}`

      try {
        const result = await queryWordInfo(word)
        wordResults.value[word] = { ...result, status: 'success' }
      } catch (error: any) {
        wordResults.value[word] = {
          word: word,
          status: 'error',
          error: error.message || '查詢失敗'
        }
      }

      // 避免請求過於頻繁
      if (i < words.length - 1) {
        await new Promise(resolve => setTimeout(resolve, 500))
      }
    }

    showPreview.value = true
  } catch (error) {
    console.error('AI 查詢失敗:', error)
  } finally {
    loading.value = false
    showProcessing.value = false
  }
}

const queryWordInfo = async (word: string) => {
  const { data, error } = await supabase.functions.invoke('ai-generate-word', {
    body: { word }
  })

  if (error) throw error
  return data
}

const retryWord = async (word: string) => {
  loading.value = true
  
  try {
    const result = await queryWordInfo(word)
    wordResults.value[word] = { ...result, status: 'success' }
  } catch (error: any) {
    wordResults.value[word] = {
      word: word,
      status: 'error',
      error: error.message || '查詢失敗'
    }
  } finally {
    loading.value = false
  }
}

const retryErrors = async () => {
  const errors = errorWords.value
  if (errors.length === 0) return

  loading.value = true
  showProcessing.value = true
  processingTitle.value = '重試錯誤單字...'
  processingMessage.value = '正在重新查詢失敗的單字'

  try {
    const total = errors.length

    for (let i = 0; i < errors.length; i++) {
      const word = errors[i]
      const progress = ((i + 1) / total) * 100

      processingProgress.value = progress
      processingMessage.value = `重試中: ${word}`
      processingDetails.value = `${i + 1} / ${total}`

      try {
        const result = await queryWordInfo(word)
        wordResults.value[word] = { ...result, status: 'success' }
      } catch (error: any) {
        wordResults.value[word] = {
          word: word,
          status: 'error',
          error: error.message || '查詢失敗'
        }
      }

      if (i < errors.length - 1) {
        await new Promise(resolve => setTimeout(resolve, 500))
      }
    }
  } finally {
    loading.value = false
    showProcessing.value = false
    processingTitle.value = 'AI 查詢中...'
  }
}

const saveAllWords = async () => {
  const wordsToSave = successWords.value.map(word => {
    const result = wordResults.value[word]
    return {
      word: result.word,
      chinese_meaning: result.chinese_meaning,
      english_meaning: result.english_meaning || '',
      phonetic: result.phonetic || '',
      example_sentence: result.example_sentence || '',
      synonyms: result.synonyms || [],
      antonyms: result.antonyms || []
    }
  })

  if (wordsToSave.length === 0) return

  loading.value = true
  showProcessing.value = true
  processingTitle.value = '儲存中...'
  processingMessage.value = '正在儲存單字到資料庫'

  try {
    await vocabularyStore.addWords(wordsToSave)
    
    // 顯示成功訊息
    alert(`成功新增 ${wordsToSave.length} 個單字！`)
    
    // 清空並返回首頁
    clearInput()
    router.push('/')
  } catch (error: any) {
    console.error('儲存失敗:', error)
    alert(`儲存失敗: ${error.message}`)
  } finally {
    loading.value = false
    showProcessing.value = false
  }
}
</script>

<style scoped>
.card {
  transition: transform 0.2s ease;
}

.card:hover {
  transform: translateY(-2px);
}

.border-success {
  border-color: #198754 !important;
  border-width: 2px !important;
}

.border-danger {
  border-color: #dc3545 !important;
  border-width: 2px !important;
}

.loading-spinner {
  width: 1rem;
  height: 1rem;
  border: 2px solid #f3f3f3;
  border-top: 2px solid #0d6efd;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>