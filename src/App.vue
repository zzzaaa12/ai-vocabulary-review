<template>
  <div id="app">
    <!-- 導航欄 -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary sticky-top">
      <div class="container-fluid">
        <router-link class="navbar-brand" to="/">
          <i class="bi bi-book"></i>
          英文單字筆記本
        </router-link>

        <button 
          class="navbar-toggler" 
          type="button" 
          data-bs-toggle="collapse" 
          data-bs-target="#navbarNav"
        >
          <span class="navbar-toggler-icon"></span>
        </button>

        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav me-auto" v-if="authStore.isAuthenticated">
            <li class="nav-item">
              <router-link class="nav-link" to="/">
                <i class="bi bi-house"></i> 首頁
              </router-link>
            </li>
            <li class="nav-item dropdown">
              <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
                <i class="bi bi-plus-circle"></i> 新增單字
              </a>
              <ul class="dropdown-menu">
                <li>
                  <router-link class="dropdown-item" to="/add">
                    <i class="bi bi-plus-circle"></i> 單個新增
                  </router-link>
                </li>
                <li>
                  <router-link class="dropdown-item" to="/batch-add">
                    <i class="bi bi-plus-square"></i> 批次新增
                  </router-link>
                </li>
              </ul>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/review">
                <i class="bi bi-shuffle"></i> 隨機複習
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/search">
                <i class="bi bi-search"></i> 搜尋
              </router-link>
            </li>
          </ul>

          <ul class="navbar-nav">
            <li class="nav-item" v-if="!authStore.isAuthenticated">
              <router-link class="nav-link" to="/login">
                <i class="bi bi-box-arrow-in-right"></i> 登入
              </router-link>
            </li>
            <li class="nav-item dropdown" v-else>
              <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
                <i class="bi bi-person-circle"></i>
                {{ authStore.user?.email }}
              </a>
              <ul class="dropdown-menu dropdown-menu-end">
                <li>
                  <button class="dropdown-item" @click="handleSignOut">
                    <i class="bi bi-box-arrow-right"></i> 登出
                  </button>
                </li>
              </ul>
            </li>
          </ul>
        </div>
      </div>
    </nav>

    <!-- 主要內容 -->
    <main class="container-fluid py-4">
      <router-view v-if="!authStore.loading" />
      
      <!-- 載入中畫面 -->
      <div v-else class="d-flex justify-content-center align-items-center" style="height: 50vh;">
        <div class="text-center">
          <div class="loading-spinner mb-3"></div>
          <p class="text-muted">載入中...</p>
        </div>
      </div>
    </main>

    <!-- Toast 通知容器 -->
    <div class="toast-container position-fixed top-0 end-0 p-3" style="z-index: 1050;">
      <!-- Toast 通知會動態插入這裡 -->
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useVocabularyStore } from '@/stores/vocabulary'

const router = useRouter()
const authStore = useAuthStore()
const vocabularyStore = useVocabularyStore()

onMounted(async () => {
  await authStore.initialize()
  
  // 如果已登入，載入單字資料
  if (authStore.isAuthenticated) {
    await vocabularyStore.loadWords()
  }
})

const handleSignOut = async () => {
  try {
    await authStore.signOut()
    vocabularyStore.clearData()
    router.push('/login')
  } catch (error) {
    console.error('Sign out error:', error)
  }
}
</script>

<style scoped>
.navbar-brand {
  font-weight: 600;
  font-size: 1.25rem;
}

.nav-link {
  font-weight: 500;
}

.dropdown-item {
  font-weight: 500;
}
</style>