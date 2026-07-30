import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  // 全局加载状态
  const loading = ref(false)
  
  // 侧边栏折叠状态（管理后台用）
  const sidebarCollapsed = ref(false)
  
  // 设备类型
  const isMobile = ref(false)
  
  // 主题模式
  const isDark = ref(false)

  // 设置加载状态
  const setLoading = (status: boolean) => {
    loading.value = status
  }

  // 切换侧边栏
  const toggleSidebar = () => {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  // 设置设备类型
  const setDevice = (mobile: boolean) => {
    isMobile.value = mobile
  }

  // 切换主题
  const toggleTheme = () => {
    isDark.value = !isDark.value
    // 这里可以添加主题切换逻辑
    document.documentElement.classList.toggle('dark', isDark.value)
  }

  // 初始化应用设置
  const initApp = () => {
    // 检测设备类型
    const checkDevice = () => {
      setDevice(window.innerWidth < 768)
    }
    
    checkDevice()
    window.addEventListener('resize', checkDevice)
    
    // 从本地存储恢复主题设置
    const savedTheme = localStorage.getItem('theme')
    if (savedTheme === 'dark') {
      isDark.value = true
      document.documentElement.classList.add('dark')
    }
  }

  return {
    // 状态
    loading: readonly(loading),
    sidebarCollapsed: readonly(sidebarCollapsed),
    isMobile: readonly(isMobile),
    isDark: readonly(isDark),
    
    // 方法
    setLoading,
    toggleSidebar,
    setDevice,
    toggleTheme,
    initApp
  }
})