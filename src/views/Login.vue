<template>
  <div class="row justify-content-center">
    <div class="col-md-6 col-lg-4">
      <div class="card">
        <div class="card-body p-4">
          <div class="text-center mb-4">
            <i class="bi bi-book text-primary" style="font-size: 3rem;"></i>
            <h2 class="mt-3">歡迎回來</h2>
            <p class="text-muted">登入您的單字筆記本</p>
          </div>

          <!-- 登入表單 -->
          <form @submit.prevent="handleSubmit" v-if="!showSignUp">
            <div class="mb-3">
              <label for="email" class="form-label">電子郵件</label>
              <input
                type="email"
                class="form-control"
                id="email"
                v-model="email"
                required
                :disabled="loading"
              >
            </div>
            
            <div class="mb-3">
              <label for="password" class="form-label">密碼</label>
              <input
                type="password"
                class="form-control"
                id="password"
                v-model="password"
                required
                :disabled="loading"
              >
            </div>

            <div class="d-grid gap-2 mb-3">
              <button type="submit" class="btn btn-primary" :disabled="loading">
                <span v-if="loading" class="loading-spinner me-2"></span>
                登入
              </button>
            </div>
          </form>

          <!-- 註冊表單 -->
          <form @submit.prevent="handleSubmit" v-else>
            <div class="mb-3">
              <label for="signupEmail" class="form-label">電子郵件</label>
              <input
                type="email"
                class="form-control"
                id="signupEmail"
                v-model="email"
                required
                :disabled="loading"
              >
            </div>
            
            <div class="mb-3">
              <label for="signupPassword" class="form-label">密碼</label>
              <input
                type="password"
                class="form-control"
                id="signupPassword"
                v-model="password"
                required
                minlength="6"
                :disabled="loading"
              >
              <div class="form-text">密碼至少需要 6 個字元</div>
            </div>

            <div class="d-grid gap-2 mb-3">
              <button type="submit" class="btn btn-primary" :disabled="loading">
                <span v-if="loading" class="loading-spinner me-2"></span>
                註冊
              </button>
            </div>
          </form>

          <!-- Google 登入 -->
          <div class="d-grid gap-2 mb-3">
            <button 
              class="btn btn-outline-secondary" 
              @click="handleGoogleSignIn"
              :disabled="loading"
            >
              <i class="bi bi-google me-2"></i>
              使用 Google 登入
            </button>
          </div>

          <!-- 切換登入/註冊 -->
          <div class="text-center">
            <button 
              class="btn btn-link text-decoration-none" 
              @click="showSignUp = !showSignUp"
              :disabled="loading"
            >
              {{ showSignUp ? '已有帳號？點此登入' : '沒有帳號？點此註冊' }}
            </button>
          </div>

          <!-- 錯誤訊息 -->
          <div v-if="error" class="alert alert-danger mt-3">
            <i class="bi bi-exclamation-triangle me-2"></i>
            {{ error }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const showSignUp = ref(false)
const loading = ref(false)
const error = ref('')

const handleSubmit = async () => {
  if (!email.value || !password.value) return

  loading.value = true
  error.value = ''

  try {
    if (showSignUp.value) {
      await authStore.signUp(email.value, password.value)
      // 註冊成功後顯示訊息
      alert('註冊成功！請檢查您的電子郵件以驗證帳號。')
    } else {
      await authStore.signIn(email.value, password.value)
      router.push('/')
    }
  } catch (err: any) {
    error.value = err.message || '操作失敗，請稍後再試'
  } finally {
    loading.value = false
  }
}

const handleGoogleSignIn = async () => {
  loading.value = true
  error.value = ''

  try {
    await authStore.signInWithGoogle()
    // Google 登入會重新導向，不需要手動跳轉
  } catch (err: any) {
    error.value = err.message || 'Google 登入失敗'
    loading.value = false
  }
}
</script>

<style scoped>
.card {
  border: none;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

.btn-link {
  font-size: 0.9rem;
}
</style>