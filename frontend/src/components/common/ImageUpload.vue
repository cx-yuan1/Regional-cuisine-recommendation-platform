<template>
  <div class="image-upload">
    <el-upload
      :action="uploadUrl"
      name="file"
      :data="{ type: uploadType }"
      :show-file-list="false"
      :before-upload="beforeUpload"
      :on-success="handleSuccess"
      :on-error="handleError"
      :disabled="disabled"
      accept="image/*"
    >
      <div class="upload-trigger">
        <div v-if="imageUrl" class="image-preview">
          <img :src="imageUrl" alt="预览图片" />
          <div class="image-overlay">
            <el-icon class="preview-icon" @click.stop="handlePreview">
              <ZoomIn />
            </el-icon>
            <el-icon class="delete-icon" @click.stop="handleRemove">
              <Delete />
            </el-icon>
          </div>
        </div>
        <div v-else class="upload-placeholder">
          <el-icon class="upload-icon"><Plus /></el-icon>
          <div class="upload-text">{{ placeholder }}</div>
        </div>
      </div>
    </el-upload>
    
    <!-- 图片预览对话框 -->
    <el-dialog
      v-model="previewVisible"
      title="图片预览"
      width="800px"
      append-to-body
    >
      <img :src="imageUrl" alt="预览" style="width: 100%;" />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, ZoomIn, Delete } from '@element-plus/icons-vue'
import type { UploadProps } from 'element-plus'

interface Props {
  modelValue?: string
  uploadType?: string
  placeholder?: string
  disabled?: boolean
  maxSize?: number // MB
}

interface Emits {
  (e: 'update:modelValue', value: string): void
}

const props = withDefaults(defineProps<Props>(), {
  uploadType: 'food',
  placeholder: '点击上传图片',
  disabled: false,
  maxSize: 2
})

const emit = defineEmits<Emits>()

// 响应式数据
const imageUrl = ref(props.modelValue || '')
const previewVisible = ref(false)

// 上传地址（相对路径，Vite 会代理到后端）
const uploadUrl = computed(() => '/api/upload/image')

// 注意：不要设置 Content-Type，浏览器会自动添加 multipart/form-data 及 boundary

// 上传前验证
const beforeUpload: UploadProps['beforeUpload'] = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLtMaxSize = file.size / 1024 / 1024 < props.maxSize

  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (!isLtMaxSize) {
    ElMessage.error(`图片大小不能超过 ${props.maxSize}MB!`)
    return false
  }
  return true
}

// 上传成功
const handleSuccess = (response: any) => {
  if (response.code === 200) {
    const fullUrl = getFullImageUrl(response.data.path)
    imageUrl.value = fullUrl
    emit('update:modelValue', response.data.path)
    ElMessage.success('上传成功')
  } else {
    ElMessage.error(response.message || '上传失败')
  }
}

// 上传失败
const handleError = () => {
  ElMessage.error('上传失败，请重试')
}

// 预览图片
const handlePreview = () => {
  previewVisible.value = true
}

// 删除图片
const handleRemove = () => {
  imageUrl.value = ''
  emit('update:modelValue', '')
  ElMessage.success('已删除')
}

// 获取完整图片URL
const getFullImageUrl = (path: string) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'}${path}`
}

// 监听外部值变化
watch(() => props.modelValue, (newValue) => {
  if (newValue) {
    imageUrl.value = getFullImageUrl(newValue)
  } else {
    imageUrl.value = ''
  }
})
</script>

<style lang="scss" scoped>
.image-upload {
  display: inline-block;
}

.upload-trigger {
  width: 148px;
  height: 148px;
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.3s;
  
  &:hover {
    border-color: #a8d8ea;
  }
}

.image-preview {
  width: 100%;
  height: 100%;
  position: relative;
  
  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  
  .image-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 20px;
    opacity: 0;
    transition: opacity 0.3s;
    
    .el-icon {
      font-size: 20px;
      color: white;
      cursor: pointer;
      transition: transform 0.3s;
      
      &:hover {
        transform: scale(1.2);
      }
    }
  }
  
  &:hover .image-overlay {
    opacity: 1;
  }
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  
  .upload-icon {
    font-size: 28px;
    color: #8c939d;
    margin-bottom: 8px;
  }
  
  .upload-text {
    font-size: 12px;
    color: #8c939d;
  }
}

:deep(.el-upload) {
  width: 100%;
  height: 100%;
}
</style>
