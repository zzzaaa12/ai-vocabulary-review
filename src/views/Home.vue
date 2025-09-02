<template>
  <div>
    <!-- 歡迎區域 -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="card bg-primary text-white">
          <div class="card-body">
            <div class="row align-items-center">
              <div class="col-md-8">
                <h1 class="card-title mb-2">
                  <i class="bi bi-book me-2"></i>
                  歡迎回來！
                </h1>
                <p class="card-text mb-0">
                  繼續您的英文學習之旅，目前已收錄 {{ vocabularyStore.totalWords }} 個單字
                </p>
              </div>
              <div class="col-md-4 text-md-end">
                <div class="btn-group">
                  <router-link to="/add" class="btn btn-light">
                    <i class="bi bi-plus-circle"></i> 新增單字
                  </router-link>
                  <router-link to="/batch-add" class="btn btn-outline-light">
                    <i class="bi bi-plus-square"></i> 批次新增
                  </router-link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 統計卡片 -->
    <div class="row mb-4">
      <div class="col-md-3 col-sm-6 mb-3">
        <div class="card text-center">
          <div class="card-body">
            <i class="bi bi-collection text-primary" style="font-size: 2rem;"></i>
            <h3 class="mt-2 mb-1">{{ vocabularyStore.totalWords }}</h3>
            <p class="text-muted mb-0">總單字數</p>
          </div>
        </div>
      </div>
      
      <div class="col-md-3 col-sm-6 mb-3">
        <div class="card text-center">
          <div class="card-body">
            <i class="bi bi-calendar-plus text-success" style="font-size: 2rem;"></i>
            <h3 class="mt-2 mb-1">{{ vocabularyStore.recentWords }}</h3>
            <p class="text-muted mb-0">近三天新增</p>
          </div>
        </div>
      </div>
      
      <div class="col-md-3 col-sm-6 mb-3">
        <div class="card text-center">
          <div class="card-body">
            <i class="bi bi-star text-warning" style="font-size: 2rem;"></i>
            <h3 class="mt-2 mb-1">{{ vocabularyStore.difficultWords.length }}</h3>
            <p class="text-muted mb-0">困難單字</p>
          </div>
        </div>
      </div>
      
      <div class="col-md-3 col-sm-6 mb-3">
        <div class="card text-center">
          <div class="card-body">
            <i class="bi bi-shuffle text-info" style="font-size: 2rem;"></i>
            <h3 class="mt-2 mb-1">{{ reviewSessions }}</h3>
            <p class="text-muted mb-0">複習次數</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 快速操作 -->
    <div class="row mb-4">
      <div class="col-md-8">
        <div class="card">
          <div class="card-header">
            <h5 class="card-title mb-0">
              <i class="bi bi-lightning"></i> 快速操作
            </h5>
          </div>
          <div class="card-body">
            <div class="row">
              <div class="col-md-6 mb-3">
                <router-link to="/review" class="btn btn-outline-primary w-100 h-100 d-flex align-items-center justify-content-center">
                  <div class="text-center">
                    <i class="bi bi-shuffle d-block mb-2" style="font-size: 2rem;"></i>
                    <strong>開始複習</strong>
                    <div class="small text-muted">隨機複習單字</div>
                  </div>
                </router-link>
              </div>
              
              <div class="col-md-6 mb-3">
                <router-link to="/search" class="btn btn-outline-success w-100 h-100 d-flex align-items-center justify-content-center">
                  <div class="text-center">
                    <i class="bi bi-search d-block mb-2" style="font-size: 2rem;"></i>
                    <strong>搜尋單字</strong>
                    <div class="small text-muted">查找已學單字</div>
                  </div>
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="col-md-4">
        <div class="card">
          <div class="card-header">
            <h5 class="card-title mb-0">
              <i class="bi bi-lightbulb"></i> 學習建議
            </h5>
          </div>
          <div class="card-body">
            <div class="alert alert-info mb-3">
              <i class="bi bi-info-circle me-2"></i>
              <span v-if="vocabularyStore.recentWords === 0">
                今天還沒有新增單字，開始學習吧！
              </span>
              <span v-else-if="vocabularyStore.recentWords < 3">
                保持學習節奏，每天學習效果更好！
              </span>
              <span v-else>
                很棒的學習進度，繼續保持！
              </span>
            </div>
            
            <div class="d-grid gap-2">
              <router-link to="/add" class="btn btn-primary">
                <i class="bi bi-plus-circle"></i> 新增單字
              </router-link>
              
              <button 
                class="btn btn-outline-warning"
                @click="reviewDifficultWords"
                :disabled="vocabularyStore.difficultWords.length === 0"
              >
                <i class="bi bi-star"></i> 複習困難單字
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 最近新增的單字 -->
    <div class="row" v-if="recentWordsList.length > 0">
      <div class="col-12">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="card-title mb-0">
              <i class="bi bi-clock-history"></i> 最近新增
            </h5>
            <router-link to="/search" class="btn btn-sm btn-outline-primary">
              查看全部
            </router-link>
          </div>
          <div class="card-body">
            <div class="row">
              <div 
                v-for="word in recentWordsList.slice(0, 6)" 
                :key="word.id"
                class="col-md-4 col-sm-6 mb-3"
              >
                <div class="card h-100">
                  <div class="card-body">
                    <h6 class="card-title text-primary">{{ word.word }}</h6>
                    <p class="card-text small text-muted">{{ word.phonetic }}</p>
                    <p class="card-text">{{ word.chinese_meaning }}</p>
                    <div class="d-flex justify-content-between align-items-center">
                      <small class="text-muted">
                        {{ formatDate(word.created_at) }}
                      </small>
                      <router-link 
                        :to="`/edit/${word.id}`" 
                        class="btn btn-sm btn-outline-primary"
                      >
                        編輯
                      </router-link>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 空狀態 -->
    <div v-else-if="!vocabularyStore.loading && vocabularyStore.totalWords === 0" class="row">
      <div class="col-12">
        <div class="card text-center">
          <div class="card-body py-5">
            <i class="bi bi-book text-muted" style="font-size: 4rem;"></i>
            <h3 class="mt-3 mb-3">還沒有任何單字</h3>
            <p class="text-muted mb-4">開始新增你的第一個單字吧！</p>
            <div class="btn-group">
              <router-link to="/add" class="btn btn-primary">
                <i class="bi bi-plus-circle"></i> 新增單字
              </router-link>
              <router-link to="/batch-add" class="btn btn-outline-primary">
                <i class="bi bi-plus-square"></i> 批次新增
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useVocabularyStore } from '@/stores/vocabulary'

const router = useRouter()
const vocabularyStore = useVocabularyStore()

const reviewSessions = ref(0)

const recentWordsList = computed(() => {
  const threeDaysAgo = new Date()
  threeDaysAgo.setDate(threeDaysAgo.getDate() - 7) // 顯示一週內的
  
  return vocabularyStore.words.filter(word => {
    const createdAt = new Date(word.created_at)
    return createdAt >= threeDaysAgo
  }).slice(0, 6)
})

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffTime = Math.abs(now.getTime() - date.getTime())
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays === 1) return '今天'
  if (diffDays === 2) return '昨天'
  if (diffDays <= 7) return `${diffDays} 天前`
  
  return date.toLocaleDateString('zh-TW')
}

const reviewDifficultWords = () => {
  router.push('/review?difficulty=true')
}

onMounted(() => {
  // 載入複習統計等額外資料
  // 這裡可以添加載入複習次數的邏輯
})
</script>

<style scoped>
.card {
  transition: transform 0.2s ease;
}

.card:hover {
  transform: translateY(-2px);
}

.btn-group .btn {
  border-radius: 0.375rem;
}

.btn-group .btn:not(:last-child) {
  margin-right: 0.5rem;
}
</style>