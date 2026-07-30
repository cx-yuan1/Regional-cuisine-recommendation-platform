<template>
  <div class="admin-profile">
    <div class="profile-card">
      <h3 class="card-title">个人信息</h3>
      
      <div class="profile-header">
        <div class="avatar-section">
          <ImageUpload
            v-model="avatarPath"
            upload-type="avatar"
            placeholder="更换头像"
            @update:modelValue="onAvatarUploaded"
          />
        </div>
        <div class="user-basic-info">
          <h2>{{ userStore.user?.username }}</h2>
          <el-tag type="danger" size="small">管理员</el-tag>
          <p class="join-date">加入时间：{{ formatDate(userStore.user?.created_at) }}</p>
        </div>
      </div>
      
      <el-divider />
      
      <el-form
        ref="formRef"
        :model="editForm"
        :rules="formRules"
        label-width="100px"
        class="profile-form"
      >
        <el-form-item label="用户名">
          <el-input v-model="editForm.username" disabled />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="editForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="saveLoading" @click="handleSave">
            保存修改
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { userApi } from '@/api/user'
import ImageUpload from '@/components/common/ImageUpload.vue'

const userStore = useUserStore()

// 响应式数据
const formRef = ref<FormInstance>()
const saveLoading = ref(false)
const avatarPath = ref('')

const editForm = reactive({
  username: '',
  email: ''
})

// 表单验证规则
const formRules: FormRules = {
  email: [
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ]
}

// 头像上传成功后更新后端
const onAvatarUploaded = async (path: string) => {
  if (!path) return
  try {
    await userApi.updateProfile({ avatar: path })
    await userStore.fetchUserInfo()
  } catch (error) {
    console.error('更新头像失败:', error)
    ElMessage.error('头像更新失败')
  }
}

// 初始化表单
const initForm = () => {
  if (userStore.user) {
    editForm.username = userStore.user.username
    editForm.email = userStore.user.email || ''
    avatarPath.value = userStore.user.avatar || ''
  }
}

// 保存修改
const handleSave = async () => {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
    saveLoading.value = true
    await userApi.updateProfile({ email: editForm.email })
    await userStore.fetchUserInfo()
    ElMessage.success('资料更新成功')
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('更新资料失败:', error)
      ElMessage.error('更新资料失败')
    }
  } finally {
    saveLoading.value = false
  }
}

// 格式化日期
const formatDate = (dateString?: string) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('zh-CN')
}

onMounted(() => {
  initForm()
})
</script>

<style scoped lang="scss">
.admin-profile {
  width: 100%;
  min-height: 100%;
}

.profile-card {
  width: 100%;
  min-height: 100%;
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  box-sizing: border-box;
}

.card-title {
  margin: 0 0 24px 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 24px;
}

.avatar-section {
  flex-shrink: 0;
}

.user-basic-info {
  flex: 1;
  
  h2 {
    margin: 0 0 8px 0;
    font-size: 20px;
    font-weight: 600;
    color: #303133;
  }
  
  .el-tag {
    margin-bottom: 8px;
  }
  
  .join-date {
    margin: 0;
    font-size: 14px;
    color: #909399;
  }
}

.profile-form {
  margin-top: 8px;
}

@media (max-width: 768px) {
  .profile-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
