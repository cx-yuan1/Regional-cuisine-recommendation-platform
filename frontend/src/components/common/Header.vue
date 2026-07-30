<template>
  <header class="header">
    <div class="header-container">
      <!-- Logo -->
      <div class="logo" @click="goHome">
        <el-icon class="logo-icon"><Food /></el-icon>
        <span class="logo-text">地域美食</span>
      </div>
      
      <!-- 导航菜单 -->
      <nav class="nav-menu">
        <el-menu 
          mode="horizontal" 
          :default-active="activeMenu"
          class="nav-menu-list"
          @select="handleMenuSelect"
        >
          <el-menu-item index="/">首页</el-menu-item>
          <el-menu-item index="/foods">美食</el-menu-item>
          <el-menu-item index="/recommend">美食推荐</el-menu-item>
          <el-menu-item index="/announcements">公告</el-menu-item>
        </el-menu>
      </nav>
      
      <!-- 搜索框 -->
      <div class="search-box">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索美食..."
          class="search-input"
          @keyup.enter="handleSearch"
        >
          <template #append>
            <el-button @click="handleSearch">
              <el-icon><Search /></el-icon>
            </el-button>
          </template>
        </el-input>
      </div>
      
      <!-- 用户操作区 -->
      <div class="user-actions">
        <template v-if="userStore.isLoggedIn">
          <!-- 已登录 -->
          <el-dropdown @command="handleUserCommand">
            <div class="user-info">
              <el-avatar 
                :src="userStore.user?.avatar" 
                :size="32"
                class="user-avatar"
              >
                <el-icon><User /></el-icon>
              </el-avatar>
              <span class="username">{{ userStore.user?.username }}</span>
              <el-icon class="dropdown-icon"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                <el-dropdown-item command="favorites">我的收藏</el-dropdown-item>
                <el-dropdown-item 
                  v-if="userStore.isAdmin" 
                  command="admin"
                  divided
                >
                  管理后台
                </el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
        <template v-else>
          <!-- 未登录 -->
          <div class="auth-buttons">
            <el-button @click="goLogin">登录</el-button>
            <el-button type="primary" @click="goRegister">注册</el-button>
          </div>
        </template>
      </div>
      
      <!-- 移动端菜单按钮 -->
      <div class="mobile-menu-btn" @click="showMobileMenu = true">
        <el-icon><Menu /></el-icon>
      </div>
    </div>
    
    <!-- 移动端抽屉菜单 -->
    <el-drawer
      v-model="showMobileMenu"
      title="菜单"
      direction="rtl"
      size="280px"
    >
      <div class="mobile-menu">
        <el-menu 
          :default-active="activeMenu"
          @select="handleMobileMenuSelect"
        >
          <el-menu-item index="/">
            <el-icon><HomeFilled /></el-icon>
            <span>首页</span>
          </el-menu-item>
          <el-menu-item index="/foods">
            <el-icon><Food /></el-icon>
            <span>美食</span>
          </el-menu-item>
          <el-menu-item index="/recommend">
            <el-icon><Star /></el-icon>
            <span>美食推荐</span>
          </el-menu-item>
          <el-menu-item index="/announcements">
            <el-icon><Bell /></el-icon>
            <span>公告</span>
          </el-menu-item>
        </el-menu>
        
        <div class="mobile-user-section">
          <template v-if="userStore.isLoggedIn">
            <div class="mobile-user-info">
              <el-avatar :src="userStore.user?.avatar" :size="40">
                <el-icon><User /></el-icon>
              </el-avatar>
              <span class="mobile-username">{{ userStore.user?.username }}</span>
            </div>
            <el-button @click="goProfile" class="mobile-menu-btn">个人中心</el-button>
            <el-button @click="goFavorites" class="mobile-menu-btn">我的收藏</el-button>
            <el-button 
              v-if="userStore.isAdmin" 
              @click="goAdmin" 
              class="mobile-menu-btn"
            >
              管理后台
            </el-button>
            <el-button @click="handleLogout" type="danger" class="mobile-menu-btn">
              退出登录
            </el-button>
          </template>
          <template v-else>
            <el-button @click="goLogin" class="mobile-menu-btn">登录</el-button>
            <el-button @click="goRegister" type="primary" class="mobile-menu-btn">
              注册
            </el-button>
          </template>
        </div>
      </div>
    </el-drawer>
  </header>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessageBox } from 'element-plus'
import { 
  Food, 
  Search, 
  User, 
  ArrowDown, 
  Menu, 
  HomeFilled, 
  Bell,
  Star
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// 响应式数据
const searchKeyword = ref('')
const showMobileMenu = ref(false)

// 计算属性
const activeMenu = computed(() => route.path)

// 方法
const goHome = () => {
  router.push('/')
}

const goLogin = () => {
  router.push('/login')
}

const goRegister = () => {
  router.push('/register')
}

const goProfile = () => {
  router.push('/profile')
  showMobileMenu.value = false
}

const goFavorites = () => {
  router.push('/favorites')
  showMobileMenu.value = false
}

const goAdmin = () => {
  router.push('/admin')
  showMobileMenu.value = false
}

const handleSearch = () => {
  if (searchKeyword.value.trim()) {
    router.push({
      name: 'FoodList',
      query: { keyword: searchKeyword.value.trim() }
    })
  }
}

const handleMenuSelect = (index: string) => {
  router.push(index)
}

const handleMobileMenuSelect = (index: string) => {
  router.push(index)
  showMobileMenu.value = false
}

const handleUserCommand = (command: string) => {
  switch (command) {
    case 'profile':
      goProfile()
      break
    case 'favorites':
      goFavorites()
      break
    case 'admin':
      goAdmin()
      break
    case 'logout':
      handleLogout()
      break
  }
}

const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await userStore.logout()
    router.push('/login')
    showMobileMenu.value = false
  } catch (error) {
    // 用户取消或其他错误
  }
}
</script>

<style lang="scss" scoped>
.header {
  background: var(--card-bg);
  border-bottom: 1px solid var(--border-color-lighter);
  box-shadow: var(--box-shadow-base);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.header-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  display: flex;
  align-items: center;
  cursor: pointer;
  color: var(--primary-color);
  font-weight: 600;
  font-size: 18px;
  
  .logo-icon {
    font-size: 24px;
    margin-right: 8px;
  }
}

.nav-menu {
  flex: 1;
  margin: 0 40px;
  
  .nav-menu-list {
    border: none;
    background: transparent;
  }
}

.search-box {
  width: 300px;
  margin-right: 20px;
  
  .search-input {
    :deep(.el-input-group__append) {
      padding: 0 15px;
    }
  }
}

.user-actions {
  .user-info {
    display: flex;
    align-items: center;
    cursor: pointer;
    padding: 8px 12px;
    border-radius: var(--border-radius-base);
    transition: background-color 0.3s;
    
    &:hover {
      background: var(--bg-color);
    }
    
    .user-avatar {
      margin-right: 8px;
    }
    
    .username {
      margin-right: 4px;
      font-size: 14px;
    }
    
    .dropdown-icon {
      font-size: 12px;
      color: var(--text-secondary);
    }
  }
  
  .auth-buttons {
    .el-button + .el-button {
      margin-left: 12px;
    }
  }
}

.mobile-menu-btn {
  display: none;
  font-size: 20px;
  cursor: pointer;
  padding: 8px;
}

.mobile-menu {
  .mobile-user-section {
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px solid var(--border-color-lighter);
    
    .mobile-user-info {
      display: flex;
      align-items: center;
      margin-bottom: 20px;
      
      .mobile-username {
        margin-left: 12px;
        font-weight: 500;
      }
    }
    
    .mobile-menu-btn {
      width: 100%;
      margin-bottom: 12px;
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .nav-menu {
    display: none;
  }
  
  .search-box {
    display: none;
  }
  
  .user-actions {
    display: none;
  }
  
  .mobile-menu-btn {
    display: block;
  }
}

@media (max-width: 480px) {
  .header-container {
    padding: 0 15px;
  }
  
  .logo {
    font-size: 16px;
    
    .logo-icon {
      font-size: 20px;
    }
  }
}
</style>