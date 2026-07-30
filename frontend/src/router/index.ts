import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: () => import('@/views/frontend/Home.vue'),
      meta: { title: '首页', requiresAuth: true }
    },
    {
      path: '/foods',
      name: 'FoodList',
      component: () => import('@/views/frontend/FoodList.vue'),
      meta: { title: '美食列表', requiresAuth: true }
    },
    {
      path: '/foods/:id',
      name: 'FoodDetail',
      component: () => import('@/views/frontend/FoodDetail.vue'),
      meta: { title: '美食详情', requiresAuth: true }
    },
    {
      path: '/recommend',
      name: 'FoodRecommend',
      component: () => import('@/views/frontend/FoodRecommend.vue'),
      meta: { title: '美食推荐', requiresAuth: true }
    },
    {
      path: '/category/:id',
      name: 'CategoryFoods',
      component: () => import('@/views/frontend/CategoryFoods.vue'),
      meta: { title: '分类美食', requiresAuth: true }
    },
    {
      path: '/announcements',
      name: 'AnnouncementList',
      component: () => import('@/views/frontend/AnnouncementList.vue'),
      meta: { title: '公告列表', requiresAuth: true }
    },
    {
      path: '/announcements/:id',
      name: 'AnnouncementDetail',
      component: () => import('@/views/frontend/AnnouncementDetail.vue'),
      meta: { title: '公告详情', requiresAuth: true }
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/frontend/Login.vue'),
      meta: { title: '登录', hideForAuth: true }
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('@/views/frontend/Register.vue'),
      meta: { title: '注册', hideForAuth: true }
    },
    {
      path: '/profile',
      name: 'Profile',
      component: () => import('@/views/frontend/Profile.vue'),
      meta: { title: '个人中心', requiresAuth: true }
    },
    {
      path: '/favorites',
      name: 'Favorites',
      component: () => import('@/views/frontend/Favorites.vue'),
      meta: { title: '我的收藏', requiresAuth: true }
    },
    // 商家端路由（入驻申请 /merchant/apply，审核通过后使用 /merchant/*）
    {
      path: '/merchant',
      component: () => import('@/views/merchant/Layout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          redirect: '/merchant/apply'
        },
        {
          path: 'apply',
          name: 'MerchantApply',
          component: () => import('@/views/merchant/MerchantApply.vue'),
          meta: { title: '商家入驻', requiresAuth: true }
        },
        {
          path: 'dashboard',
          name: 'MerchantDashboard',
          component: () => import('@/views/merchant/MerchantDashboard.vue'),
          meta: { title: '商家首页', requiresAuth: true, requiresMerchant: true }
        },
        {
          path: 'store',
          name: 'MerchantStore',
          component: () => import('@/views/merchant/MerchantStore.vue'),
          meta: { title: '店铺信息', requiresAuth: true, requiresMerchant: true }
        },
        {
          path: 'foods',
          name: 'MerchantFoods',
          component: () => import('@/views/merchant/MerchantFoods.vue'),
          meta: { title: '美食管理', requiresAuth: true, requiresMerchant: true }
        },
        {
          path: 'comments',
          name: 'MerchantComments',
          component: () => import('@/views/merchant/MerchantComments.vue'),
          meta: { title: '评价回复', requiresAuth: true, requiresMerchant: true }
        },
        {
          path: 'profile',
          name: 'MerchantProfile',
          component: () => import('@/views/merchant/MerchantProfile.vue'),
          meta: { title: '个人设置', requiresAuth: true }
        }
      ]
    },
    // 管理后台路由（仅管理员）
    {
      path: '/admin',
      component: () => import('@/views/admin/Layout.vue'),
      meta: { requiresAuth: true, requiresAdmin: true },
      children: [
        {
          path: '',
          redirect: '/admin/dashboard'
        },
        {
          path: 'dashboard',
          name: 'AdminDashboard',
          component: () => import('@/views/admin/Dashboard.vue'),
          meta: { title: '仪表盘', requiresAuth: true, requiresAdmin: true }
        },
        {
          path: 'users',
          name: 'UserManage',
          component: () => import('@/views/admin/UserManage.vue'),
          meta: { title: '用户管理', requiresAuth: true, requiresAdmin: true }
        },
        {
          path: 'foods',
          name: 'FoodManage',
          component: () => import('@/views/admin/FoodManage.vue'),
          meta: { title: '美食管理', requiresAuth: true, requiresAdmin: true }
        },
        {
          path: 'categories',
          name: 'CategoryManage',
          component: () => import('@/views/admin/CategoryManage.vue'),
          meta: { title: '分类管理', requiresAuth: true, requiresAdmin: true }
        },
        {
          path: 'comments',
          name: 'CommentManage',
          component: () => import('@/views/admin/CommentManage.vue'),
          meta: { title: '评论管理', requiresAuth: true, requiresAdmin: true }
        },
        {
          path: 'merchants',
          name: 'MerchantManage',
          component: () => import('@/views/admin/MerchantManage.vue'),
          meta: { title: '商家管理', requiresAuth: true, requiresAdmin: true }
        },
        {
          path: 'banners',
          name: 'BannerManage',
          component: () => import('@/views/admin/BannerManage.vue'),
          meta: { title: '轮播图管理', requiresAuth: true, requiresAdmin: true }
        },
        {
          path: 'announcements',
          name: 'AnnouncementManage',
          component: () => import('@/views/admin/AnnouncementManage.vue'),
          meta: { title: '公告管理', requiresAuth: true, requiresAdmin: true }
        },
        {
          path: 'statistics',
          name: 'Statistics',
          component: () => import('@/views/admin/Statistics.vue'),
          meta: { title: '数据统计', requiresAuth: true, requiresAdmin: true }
        },
        {
          path: 'profile',
          name: 'AdminProfile',
          component: () => import('@/views/admin/AdminProfile.vue'),
          meta: { title: '个人设置', requiresAuth: true, requiresAdmin: true }
        }
      ]
    },
    {
      path: '/test',
      name: 'Test',
      component: () => import('@/views/common/Test.vue'),
      meta: { title: '功能测试', requiresAuth: true }
    },
    // 404页面
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      component: () => import('@/views/common/NotFound.vue'),
      meta: { title: '页面不存在', requiresAuth: true }
    }
  ]
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()
  
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - 地域美食推荐平台`
  }
  
  // 检查是否需要登录
  if (to.meta.requiresAuth) {
    // 若 store 中无用户信息，先尝试从后端恢复（处理刷新页面等场景）
    if (!userStore.isLoggedIn) {
      try {
        await userStore.getUserInfo()
      } catch {
        // 恢复失败，说明未登录
      }
    }
    
    if (!userStore.isLoggedIn) {
      ElMessage.warning('请先登录')
      next({ name: 'Login', query: { redirect: to.fullPath } })
      return
    }
  }
  
  // 商家访问 /admin 时重定向到商家中心
  if (to.path.startsWith('/admin') && userStore.isMerchant) {
    next({ path: userStore.isMerchantApproved ? '/merchant/dashboard' : '/merchant/apply' })
    return
  }
  
  // 检查是否需要管理员权限（管理后台仅管理员）
  if (to.meta.requiresAdmin && !userStore.isAdmin) {
    ElMessage.error('无权访问管理后台')
    next({ name: 'Home' })
    return
  }
  
  // 检查是否需要商家入驻已通过（商家首页、店铺信息等）
  if (to.meta.requiresMerchant && !userStore.isMerchantApproved) {
    ElMessage.error('请先完成商家入驻申请并通过审核')
    next({ path: '/merchant/apply' })
    return
  }
  
  // 已登录用户访问登录/注册页面，根据角色重定向
  if (to.meta.hideForAuth && userStore.isLoggedIn) {
    next({ path: userStore.getRedirectPath() })
    return
  }
  
  next()
})

export default router