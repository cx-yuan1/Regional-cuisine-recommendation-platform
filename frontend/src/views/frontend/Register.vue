<template>
  <div class="register-page">
    <div class="register-container">
      <div class="register-card">
        <!-- Logo区域 -->
        <div class="logo-section">
          <el-icon class="logo-icon"><Food /></el-icon>
          <h1 class="logo-text">地域美食</h1>
          <p class="subtitle">加入我们，开启美食探索之旅</p>
        </div>
        
        <!-- 注册类型（标语下方、表单上方，居中） -->
        <div class="register-type-wrap">
          <el-radio-group v-model="registerForm.register_type" size="large" class="register-type-group">
            <el-radio-button value="user">普通用户</el-radio-button>
            <el-radio-button value="merchant">商家</el-radio-button>
          </el-radio-group>
        </div>
        
        <!-- 注册表单 -->
        <el-form
          ref="registerFormRef"
          :model="registerForm"
          :rules="registerRules"
          class="register-form"
          @submit.prevent="handleRegister"
        >
          <el-form-item prop="username">
            <el-input
              v-model="registerForm.username"
              placeholder="请输入用户名"
              size="large"
              prefix-icon="User"
            />
          </el-form-item>
          
          <el-form-item prop="email">
            <el-input
              v-model="registerForm.email"
              placeholder="请输入邮箱"
              size="large"
              prefix-icon="Message"
            />
          </el-form-item>
          
          <el-form-item prop="password">
            <el-input
              v-model="registerForm.password"
              type="password"
              placeholder="请输入密码"
              size="large"
              prefix-icon="Lock"
              show-password
            />
          </el-form-item>
          
          <el-form-item prop="confirmPassword">
            <el-input
              v-model="registerForm.confirmPassword"
              type="password"
              placeholder="请确认密码"
              size="large"
              prefix-icon="Lock"
              show-password
              @keyup.enter="handleRegister"
            />
          </el-form-item>
          
          <el-form-item>
            <el-button
              type="primary"
              size="large"
              class="register-button"
              :loading="loading"
              @click="handleRegister"
            >
              注册
            </el-button>
          </el-form-item>
        </el-form>
        
        <!-- 底部链接 -->
        <div class="footer-links">
          <span>已有账号？</span>
          <el-link type="primary" @click="goToLogin">立即登录</el-link>
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
import type { RegisterForm } from '@/types'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// 响应式数据
const loading = ref(false)
const registerFormRef = ref<FormInstance>()

const registerForm = reactive<RegisterForm & { confirmPassword: string }>({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  register_type: 'user'
})

// 自定义验证规则
const validateConfirmPassword = (rule: any, value: string, callback: any) => {
  if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

// 表单验证规则
const registerRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_\u4e00-\u9fa5]+$/, message: '用户名只能包含字母、数字、下划线和中文', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ],
}

// 处理注册
const handleRegister = async () => {
  if (!registerFormRef.value) return
  
  try {
    await registerFormRef.value.validate()
    
    loading.value = true
    
    // 提取注册数据（排除确认密码字段）
    const { confirmPassword, ...registerData } = registerForm
    await userStore.register(registerData)
    
    // 注册成功后跳转登录页
    const msg = registerForm.register_type === 'merchant'
      ? '注册成功，请登录后进入商家中心提交入驻申请'
      : '注册成功，请登录'
    ElMessage.success(msg)
    router.push({ name: 'Login' })
  } catch (error) {
    console.error('注册失败:', error)
  } finally {
    loading.value = false
  }
}

// 跳转到登录页
const goToLogin = () => {
  router.push({ 
    name: 'Login',
    query: route.query // 保持重定向参数
  })
}
</script>

<style lang="scss" scoped>
.register-page {
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

.register-container {
  width: 100%;
  max-width: 440px;
  position: relative;
  z-index: 1;
}

.register-card {
  background: var(--card-bg);
  border-radius: var(--border-radius-large);
  padding: 40px;
  box-shadow: var(--box-shadow-dark);
  text-align: center;
}

.register-type-wrap {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 24px;
} 

.register-type-group {
  width: fit-content;
  display: inline-flex;
}

.register-type-group :deep(.el-radio-button) {
  flex: 1;
  min-width: 100px;
}

.logo-section {
  margin-bottom: 24px;
  
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

.register-form {
  .el-form-item {
    margin-bottom: 24px;
  }
  
  .register-button {
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
  .register-page {
    padding: 15px;
  }
  
  .register-card {
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