<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-card">
        <!-- Logo区域 -->
        <div class="logo-section">
          <el-icon class="logo-icon"><Food /></el-icon>
          <h1 class="logo-text">地域美食</h1>
          <p class="subtitle">发现地道美食，品味文化传承</p>
        </div>
        
        <!-- 登录表单 -->
        <el-form
          ref="loginFormRef"
          :model="loginForm"
          :rules="loginRules"
          class="login-form"
          @submit.prevent="handleLogin"
        >
          <el-form-item prop="username">
            <el-input
              v-model="loginForm.username"
              placeholder="请输入用户名"
              size="large"
              prefix-icon="User"
            />
          </el-form-item>
          
          <el-form-item prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="请输入密码"
              size="large"
              prefix-icon="Lock"
              show-password
              @keyup.enter="handleLogin"
            />
          </el-form-item>
          
          <el-form-item>
            <el-button
              type="primary"
              size="large"
              class="login-button"
              :loading="loading"
              @click="handleLogin"
            >
              登录
            </el-button>
          </el-form-item>
        </el-form>
        
        <!-- 底部链接 -->
        <div class="footer-links">
          <span>还没有账号？</span>
          <el-link type="primary" @click="goToRegister">立即注册</el-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Food } from '@element-plus/icons-vue'
import type { LoginForm } from '@/types'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// 响应式数据
const loading = ref(false)
const loginFormRef = ref<FormInstance>()

const loginForm = reactive<LoginForm>({
  username: '',
  password: ''
})

// 表单验证规则
const loginRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' }
  ]
}

// 处理登录
const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  try {
    await loginFormRef.value.validate()
    
    loading.value = true
    
    // 调用登录接口
    const userData = await userStore.login(loginForm)
    console.log('登录返回的用户数据:', userData)
    console.log('用户状态:', userStore.user)
    console.log('是否管理员:', userStore.isAdmin)
    
    // 根据用户角色决定跳转路径
    // 管理员：始终跳转到管理后台
    // 普通用户：有重定向参数则跳转回原页面，否则跳转到前台首页
    const redirectPath = userStore.getRedirectPath(route.query.redirect as string | undefined)
    
    console.log('准备跳转到:', redirectPath)
    
    // 执行跳转
    await router.push(redirectPath)
    console.log('跳转完成')
    
  } catch (error) {
    console.error('登录失败:', error)
    ElMessage.error('登录失败，请检查用户名和密码')
  } finally {
    loading.value = false
  }
}

// 跳转到注册页
const goToRegister = () => {
  router.push({ 
    name: 'Register',
    query: route.query // 保持重定向参数
  })
}
</script>

<style lang="scss" scoped>
.login-page {
  min-height: 100vh;
  background-image: url('https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=1920&q=80');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  
  // 添加半透明遮罩层，让文字更清晰
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.4);
    z-index: 0;
  }
}

.login-container {
  width: 100%;
  max-width: 400px;
  position: relative;
  z-index: 1;
}

.login-card {
  background: var(--card-bg);
  border-radius: var(--border-radius-large);
  padding: 40px;
  box-shadow: var(--box-shadow-dark);
  text-align: center;
}

.logo-section {
  margin-bottom: 40px;
  
  .logo-icon {
    font-size: 48px;
    color: var(--primary-color);
    margin-bottom: 16px;
  }
  
  .logo-text {
    font-size: 28px;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0 0 8px 0;
  }
  
  .subtitle {
    color: var(--text-secondary);
    font-size: 14px;
    margin: 0;
  }
}

.login-form {
  .el-form-item {
    margin-bottom: 24px;
  }
  
  .login-button {
    width: 100%;
    height: 48px;
    font-size: 16px;
    font-weight: 500;
  }
}

.footer-links {
  margin-top: 24px;
  color: var(--text-secondary);
  font-size: 14px;
  
  .el-link {
    margin-left: 8px;
    font-weight: 500;
  }
}

// 响应式设计
@media (max-width: 480px) {
  .login-page {
    padding: 15px;
  }
  
  .login-card {
    padding: 30px 20px;
  }
  
  .logo-section {
    margin-bottom: 30px;
    
    .logo-icon {
      font-size: 40px;
    }
    
    .logo-text {
      font-size: 24px;
    }
  }
}
</style>