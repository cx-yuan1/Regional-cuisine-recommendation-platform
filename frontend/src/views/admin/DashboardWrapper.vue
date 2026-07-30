<template>
  <AdminDashboard v-if="userStore.isAdmin" />
  <MerchantDashboard v-else-if="userStore.isMerchant" />
  <div v-else class="no-access">
    <el-result icon="warning" title="无权访问" sub-title="请使用管理员或商家账号登录" />
  </div>
</template>

<script setup lang="ts">
import { useUserStore } from '@/stores/user'
import AdminDashboard from './Dashboard.vue'
import MerchantDashboard from '@/views/merchant/MerchantDashboard.vue'

const userStore = useUserStore()
</script>

<style scoped>
.no-access {
  padding: 40px;
}
</style>
