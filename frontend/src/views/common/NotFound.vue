<template>
  <div class="not-found">
    <div class="not-found-content">
      <div class="error-code">404</div>
      <h1>页面不存在</h1>
      <p>抱歉，您访问的页面不存在或已被删除</p>
      <div class="actions">
        <el-button type="primary" @click="goHome">返回首页</el-button>
        <el-button @click="goBack">返回上页</el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const goHome = () => {
  router.push('/')
}

const goBack = () => {
  router.go(-1)
}
</script>

<style lang="scss" scoped>
.not-found {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-color);
}

.not-found-content {
  text-align: center;
  padding: 40px;
}

.error-code {
  font-size: 120px;
  font-weight: bold;
  color: var(--primary-color);
  line-height: 1;
  margin-bottom: 20px;
}

h1 {
  font-size: 32px;
  color: var(--text-primary);
  margin-bottom: 16px;
}

p {
  font-size: 16px;
  color: var(--text-secondary);
  margin-bottom: 40px;
}

.actions {
  .el-button + .el-button {
    margin-left: 16px;
  }
}

@media (max-width: 768px) {
  .error-code {
    font-size: 80px;
  }
  
  h1 {
    font-size: 24px;
  }
  
  .actions {
    .el-button {
      display: block;
      width: 100%;
      margin: 0 0 12px 0;
    }
  }
}
</style>