<template>
  <div class="profile-page">
    <Header />
    
    <div class="page-container">
      <div class="profile-content">
        <!-- 用户信息卡片 -->
        <div class="user-card">
          <div class="avatar-section">
            <el-avatar :src="userStore.user?.avatar" :size="80">
              <el-icon><User /></el-icon>
            </el-avatar>
            <el-button size="small" @click="showAvatarDialog = true">
              更换头像
            </el-button>
          </div>
          
          <div class="user-info">
            <h2>{{ userStore.user?.username }}</h2>
            <p class="email">{{ userStore.user?.email }}</p>
            <p class="join-date">
              加入时间：{{ formatDate(userStore.user?.created_at) }}
            </p>
          </div>
        </div>
        
        <!-- 编辑表单 -->
        <div class="edit-form">
          <h3>编辑资料</h3>
          <el-form :model="editForm" label-width="100px">
            <el-form-item label="用户名">
              <el-input v-model="editForm.username" disabled />
            </el-form-item>
            <el-form-item label="邮箱">
              <el-input v-model="editForm.email" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="updateProfile">
                保存修改
              </el-button>
            </el-form-item>
          </el-form>
        </div>
      </div>
    </div>
    
    <!-- 头像上传对话框 -->
    <el-dialog v-model="showAvatarDialog" title="更换头像" width="400px">
      <el-upload
        class="avatar-uploader"
        :show-file-list="false"
        :before-upload="beforeAvatarUpload"
        :http-request="uploadAvatar"
      >
        <img v-if="previewUrl" :src="previewUrl" class="avatar-preview" />
        <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
      </el-upload>
    </el-dialog>
    
    <Footer />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { User, Plus } from '@element-plus/icons-vue'
import type { UploadRequestOptions } from 'element-plus'
import { uploadApi } from '@/api/upload'
import { userApi } from '@/api/user'

// 组件导入
import Header from '@/components/common/Header.vue'
import Footer from '@/components/common/Footer.vue'

const userStore = useUserStore()

// 响应式数据
const showAvatarDialog = ref(false)
const previewUrl = ref('')

const editForm = reactive({
  username: '',
  email: ''
})

// 初始化表单数据
const initForm = () => {
  if (userStore.user) {
    editForm.username = userStore.user.username
    editForm.email = userStore.user.email
  }
}
// 更新用户资料
const updateProfile = async () => {
  try {
    await userApi.updateProfile({ email: editForm.email })
    await userStore.fetchUserInfo()
    ElMessage.success('资料更新成功')
  } catch (error) {
    console.error('更新资料失败:', error)
    ElMessage.error('更新资料失败')
  }
}

// 头像上传前验证
const beforeAvatarUpload = (file: File) => {
  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB!')
    return false
  }
  
  // 预览图片
  const reader = new FileReader()
  reader.onload = (e) => {
    previewUrl.value = e.target?.result as string
  }
  reader.readAsDataURL(file)
  
  return true
}

// 上传头像
const uploadAvatar = async (options: UploadRequestOptions) => {
  try {
    const response = await uploadApi.uploadImage(options.file as File, 'avatar')
    
    // 更新用户头像
    await userApi.updateProfile({ avatar: response.data.path })
    
    // 更新store中的用户信息
    await userStore.fetchUserInfo()
    
    ElMessage.success('头像更新成功')
    showAvatarDialog.value = false
    previewUrl.value = ''
  } catch (error) {
    console.error('上传头像失败:', error)
    ElMessage.error('上传头像失败')
  }
}

// 格式化日期
const formatDate = (dateString?: string) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString()
}

onMounted(() => {
  initForm()
})
</script>

<style lang="scss" scoped>
.profile-page {
  min-height: 100vh;
  background: var(--bg-color);
}

.page-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.profile-content {
  display: grid;
  gap: 30px;
}

.user-card {
  background: var(--card-bg);
  padding: 30px;
  border-radius: var(--border-radius-base);
  box-shadow: var(--box-shadow-base);
  display: flex;
  gap: 30px;
  align-items: center;
}

.avatar-section {
  text-align: center;
  
  .el-button {
    margin-top: 10px;
  }
}

.user-info {
  flex: 1;
  
  h2 {
    margin: 0 0 10px 0;
    color: var(--text-primary);
  }
  
  .email {
    color: var(--text-secondary);
    margin: 5px 0;
  }
  
  .join-date {
    color: var(--text-secondary);
    font-size: 14px;
    margin: 5px 0;
  }
}

.edit-form {
  background: var(--card-bg);
  padding: 30px;
  border-radius: var(--border-radius-base);
  box-shadow: var(--box-shadow-base);
  
  h3 {
    margin-bottom: 20px;
    color: var(--text-primary);
  }
}

.avatar-uploader {
  :deep(.el-upload) {
    border: 1px dashed var(--border-color);
    border-radius: 6px;
    cursor: pointer;
    position: relative;
    overflow: hidden;
    transition: var(--transition-base);
    
    &:hover {
      border-color: var(--primary-color);
    }
  }
}

.avatar-preview {
  width: 178px;
  height: 178px;
  display: block;
  object-fit: cover;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 178px;
  height: 178px;
  text-align: center;
  line-height: 178px;
}

@media (max-width: 768px) {
  .user-card {
    flex-direction: column;
    text-align: center;
  }
}
</style>