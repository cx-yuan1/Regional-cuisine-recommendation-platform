<template>
  <div class="admin-layout">
    <!-- 侧边栏 -->
    <div class="admin-sidebar" :class="{ 'is-collapse': isCollapse }">
      <div class="sidebar-header">
        <div class="logo">
          <el-icon class="logo-icon"><Shop /></el-icon>
          <span v-show="!isCollapse" class="logo-text">美食管理</span>
        </div>
      </div>
      
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        :unique-opened="true"
        router
        class="sidebar-menu"
      >
        <!-- 管理员端菜单 -->
        <template v-if="userStore.isAdmin">
          <el-menu-item index="/admin/dashboard">
            <el-icon><DataAnalysis /></el-icon>
            <template #title>数据统计</template>
          </el-menu-item>
          <el-menu-item index="/admin/users">
            <el-icon><User /></el-icon>
            <template #title>用户管理</template>
          </el-menu-item>
          <el-menu-item index="/admin/foods">
            <el-icon><Food /></el-icon>
            <template #title>美食管理</template>
          </el-menu-item>
          <el-menu-item index="/admin/categories">
            <el-icon><Grid /></el-icon>
            <template #title>分类管理</template>
          </el-menu-item>
          <el-menu-item index="/admin/comments">
            <el-icon><ChatDotRound /></el-icon>
            <template #title>评论管理</template>
          </el-menu-item>
          <el-menu-item index="/admin/merchants">
            <el-icon><Shop /></el-icon>
            <template #title>商家管理</template>
          </el-menu-item>
          <el-menu-item index="/admin/banners">
            <el-icon><Picture /></el-icon>
            <template #title>轮播图管理</template>
          </el-menu-item>
          <el-menu-item index="/admin/announcements">
            <el-icon><Bell /></el-icon>
            <template #title>公告管理</template>
          </el-menu-item>
        </template>
      </el-menu>
    </div>

    <!-- 主内容区 -->
    <div class="admin-main" :class="{ 'is-collapse': isCollapse }">
      <!-- 顶部导航栏 -->
      <div class="admin-header">
        <div class="header-left">
          <el-button 
            type="text" 
            @click="toggleSidebar"
            class="collapse-btn"
          >
            <el-icon><Expand v-if="isCollapse" /><Fold v-else /></el-icon>
          </el-button>
          
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/admin/dashboard' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="breadcrumbTitle">{{ breadcrumbTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <div class="user-info">
              <el-avatar 
                :size="32" 
                :src="getUserAvatar(userStore.user?.avatar)"
                @error="() => true"
              >
                <el-icon><User /></el-icon>
              </el-avatar>
              <span class="username">{{ userStore.user?.username }}</span>
              <el-icon><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人设置</el-dropdown-item>
                <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>

      <!-- 页面内容 -->
      <div class="admin-content">
        <router-view />
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Shop,
  DataAnalysis,
  User,
  Food,
  Grid,
  ChatDotRound,
  Picture,
  Bell,
  Expand,
  Fold,
  ArrowDown
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// 响应式数据
const isCollapse = ref(false)

// 计算属性
const activeMenu = computed(() => route.path)

const breadcrumbTitle = computed(() => {
  const routeMap: Record<string, string> = {
    '/admin/dashboard': '',
    '/admin/users': '用户管理',
    '/admin/foods': '美食管理',
    '/admin/categories': '分类管理',
    '/admin/comments': '评论管理',
    '/admin/merchants': '商家管理',
    '/admin/banners': '轮播图管理',
    '/admin/announcements': '公告管理',
    '/admin/profile': '个人设置'
  }
  return routeMap[route.path] || ''
})

// 切换侧边栏
const toggleSidebar = () => {
  isCollapse.value = !isCollapse.value
}

// 获取用户头像（无头像时返回空，el-avatar 会显示默认图标）
const getUserAvatar = (avatarPath?: string) => {
  if (!avatarPath) return ''
  if (avatarPath.startsWith('http')) return avatarPath
  // 相对路径由 Vite 代理转发到后端
  return avatarPath.startsWith('/') ? avatarPath : `/${avatarPath}`
}

// 处理下拉菜单命令
const handleCommand = async (command: string) => {
  switch (command) {
    case 'profile':
      // 跳转到个人设置页面
      router.push('/admin/profile')
      break
    case 'logout':
      // 退出登录
      try {
        await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        await userStore.logout()
        router.push('/login')
      } catch (error) {
        // 用户取消操作
      }
      break
  }
}

// 页面初始化
onMounted(() => {
  // 检查管理员或商家权限
  if (!userStore.isAdmin && !userStore.isMerchant) {
    ElMessage.error('无权访问管理后台')
    router.push('/')
  }
})
</script>

<style scoped lang="scss">
.admin-layout {
  display: flex;
  height: 100vh;
  background: #f0f2f5;
}

.admin-sidebar {
  width: 220px;
  background: linear-gradient(180deg, #f0f4f8 0%, #f8f9fa 100%);
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
  transition: width 0.3s ease;
  overflow: hidden;
  
  &.is-collapse {
    width: 64px;
  }
}

.sidebar-header {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid #e4e7ed;
  padding: 0 16px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #409eff;
  font-weight: 600;
}

.logo-icon {
  font-size: 24px;
}

.logo-text {
  font-size: 18px;
  white-space: nowrap;
}

.sidebar-menu {
  border: none;
  background: transparent;
  
  :deep(.el-menu-item) {
    margin: 4px 8px;
    border-radius: 8px;
    color: #606266;
    
    &:hover {
      background: rgba(64, 158, 255, 0.1);
      color: #409eff;
    }
    
    &.is-active {
      background: #409eff;
      color: white;
      
      &::before {
        display: none;
      }
    }
  }
}

.admin-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-left: 0;
  transition: margin-left 0.3s ease;
}

.admin-header {
  height: 60px;
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.collapse-btn {
  font-size: 18px;
  color: #606266;
  
  &:hover {
    color: #409eff;
  }
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 8px;
  transition: background-color 0.3s ease;
  
  &:hover {
    background: #f5f7fa;
  }
}

.username {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
}

.admin-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  background: #f0f2f5;
}

@media (max-width: 768px) {
  .admin-sidebar {
    position: fixed;
    left: 0;
    top: 0;
    z-index: 1000;
    height: 100vh;
    
    &.is-collapse {
      left: -220px;
    }
  }
  
  .admin-main {
    margin-left: 0;
  }
  
  .admin-header {
    padding: 0 16px;
  }
  
  .admin-content {
    padding: 16px;
  }
}
</style>