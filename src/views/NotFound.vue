<template>
  <div class="container text-center py-5">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <i class="bi bi-exclamation-triangle text-warning" style="font-size: 5rem;"></i>
        <h1 class="mt-4 mb-3">404 - 頁面不存在</h1>
        <p class="text-muted mb-4">抱歉，您要找的頁面不存在或已被移除。</p>
        <div class="btn-group">
          <router-link to="/" class="btn btn-primary">
            <i class="bi bi-house"></i> 返回首頁
          </router-link>
          <button class="btn btn-outline-secondary" @click="$router.go(-1)">
            <i class="bi bi-arrow-left"></i> 返回上頁
          </button>
        </div>
      </div>
    </div>
  </div>
</template>