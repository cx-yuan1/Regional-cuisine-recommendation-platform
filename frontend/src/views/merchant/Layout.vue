<template>
  <div class="merchant-layout">
    <div class="merchant-sidebar" :class="{ 'is-collapse': isCollapse }">
      <div class="sidebar-header">
        <div class="logo">
          <el-icon class="logo-icon"><Shop /></el-icon>
          <span v-show="!isCollapse" class="logo-text">商家中心</span>
        </div>
      </div>
      
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        router
        class="sidebar-menu"
      >
        <el-menu-item index="/merchant/apply">
          <el-icon><DocumentAdd /></el-icon>
          <template #title>入驻申请</template>
        </el-menu-item>
        <template v-if="userStore.isMerchantApproved">
          <el-menu-item index="/merchant/dashboard">
            <el-icon><DataAnalysis /></el-icon>
            <template #title>商家首页</template>
          </el-menu-item>
          <el-menu-item index="/merchant/store">
            <el-icon><Shop /></el-icon>
            <template #title>店铺信息</template>
          </el-menu-item>
          <el-menu-item index="/merchant/foods">
            <el-icon><Food /></el-icon>
            <template #title>美食管理</template>
          </el-menu-item>
          <el-menu-item index="/merchant/comments">
            <el-icon><ChatDotRound /></el-icon>
            <template #title>评价回复</template>
          </el-menu-item>
        </template>
      </el-menu>
    </div>

    <div class="merchant-main" :class="{ 'is-collapse': isCollapse }">
      <div class="merchant-header">
        <div class="header-left">
          <el-button type="text" @click="toggleSidebar" class="collapse-btn">
            <el-icon><Expand v-if="isCollapse" /><Fold v-else /></el-icon>
          </el-button>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: userStore.isMerchantApproved ? '/merchant/dashboard' : '/merchant/apply' }">商家中心</el-breadcrumb-item>
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
      <div class="merchant-content">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessageBox } from 'element-plus'
import { Shop, DataAnalysis, Food, ChatDotRound, DocumentAdd, Expand, Fold, ArrowDown, User } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const isCollapse = ref(false)
const activeMenu = computed(() => route.path)

const breadcrumbTitle = computed(() => {
  const map: Record<string, string> = {
    '/merchant/apply': '入驻申请',
    '/merchant/dashboard': '',
    '/merchant/store': '店铺信息',
    '/merchant/foods': '美食管理',
    '/merchant/comments': '评价回复',
    '/merchant/profile': '个人设置'
  }
  return map[route.path] || ''
})

const toggleSidebar = () => { isCollapse.value = !isCollapse.value }

const getUserAvatar = (avatarPath?: string) => {
  if (!avatarPath) return ''
  if (avatarPath.startsWith('http')) return avatarPath
  return avatarPath.startsWith('/') ? avatarPath : `/${avatarPath}`
}

const handleCommand = async (command: string) => {
  if (command === 'profile') {
    router.push('/merchant/profile')
    return
  }
  if (command === 'logout') {
    try {
      await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
      await userStore.logout()
      router.push('/login')
    } catch {
      // 用户取消
    }
  }
}

onMounted(async () => {
  await userStore.getUserInfo()
})
</script>

<style scoped lang="scss">
.merchant-layout {
  display: flex;
  height: 100vh;
  background: #f0f2f5;
}
.merchant-sidebar {
  width: 220px;
  background: linear-gradient(180deg, #e8f4ea 0%, #f8faf8 100%);
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.08);
  transition: width 0.3s;
  &.is-collapse { width: 64px; }
}
.sidebar-header {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid #e4e7ed;
}
.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #67c23a;
  font-weight: 600;
}
.logo-icon { font-size: 24px; }
.logo-text { font-size: 18px; white-space: nowrap; }
.sidebar-menu {
  border: none;
  background: transparent;
  :deep(.el-menu-item) {
    margin: 4px 8px;
    border-radius: 8px;
    &:hover { background: rgba(103, 194, 58, 0.1); color: #67c23a; }
    &.is-active { background: #67c23a; color: white; }
  }
}
.merchant-main {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.merchant-header {
  height: 60px;
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
}
.header-left { display: flex; align-items: center; gap: 16px; }
.collapse-btn { font-size: 18px; color: #606266; }
.header-right { display: flex; align-items: center; }
.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 8px;
  transition: background-color 0.3s ease;
  &:hover { background: #f5f7fa; }
}
.username {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
}
.merchant-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  background: #f0f2f5;
}
</style>
