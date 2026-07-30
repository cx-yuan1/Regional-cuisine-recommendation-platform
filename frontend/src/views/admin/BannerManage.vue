<template>
  <div class="banner-manage">
    <!-- 操作栏 -->
    <div class="action-bar">
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>
        添加轮播图
      </el-button>
    </div>

    <!-- 轮播图表格 -->
    <div class="table-container">
      <el-table
        v-loading="loading"
        :data="bannerList"
        style="width: 100%"
      >
        <el-table-column label="序号" width="80" align="center">
          <template #default="{ $index }">
            {{ $index + 1 }}
          </template>
        </el-table-column>
        
        <el-table-column prop="image" label="图片" width="150" align="center">
          <template #default="{ row }">
            <el-image
              v-if="row.image"
              :src="getImageUrl(row.image)"
              :preview-src-list="[getImageUrl(row.image)]"
              style="width: 120px; height: 60px; border-radius: 4px"
              fit="cover"
            />
            <span v-else class="no-image">无图片</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="title" label="标题" align="center" />
        
        <el-table-column prop="link_url" label="链接地址" align="center">
          <template #default="{ row }">
            <span>{{ row.link_url || '-' }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="sort_order" label="排序" width="100" align="center" />
        
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'">
              {{ row.status === 1 ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="创建时间" width="180" align="center">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="200" align="center">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              @click="handleEdit(row)"
            >
              编辑
            </el-button>
            
            <el-button
              type="danger"
              size="small"
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 编辑轮播图对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      :title="editForm.id ? '编辑轮播图' : '添加轮播图'"
      width="600px"
    >
      <el-form
        ref="editFormRef"
        :model="editForm"
        :rules="editRules"
        label-width="80px"
      >
        <el-form-item label="标题" prop="title">
          <el-input v-model="editForm.title" placeholder="请输入轮播图标题" />
        </el-form-item>
        
        <el-form-item label="链接地址" prop="link_url">
          <el-input v-model="editForm.link_url" placeholder="请输入链接地址（可选）" />
        </el-form-item>
        
        <el-form-item label="排序" prop="sort_order">
          <el-input-number
            v-model="editForm.sort_order"
            :min="0"
            :max="999"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="editForm.status">
            <el-radio :label="1">启用</el-radio>
            <el-radio :label="0">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="图片" prop="image">
          <ImageUpload
            v-model="editForm.image"
            upload-type="banner"
            placeholder="点击上传轮播图"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saveLoading">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>
<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getAdminBanners, createBanner, updateBanner, deleteBanner } from '@/api/admin'
import ImageUpload from '@/components/common/ImageUpload.vue'
import type { Banner } from '@/types'

// 响应式数据
const loading = ref(false)
const saveLoading = ref(false)
const bannerList = ref<Banner[]>([])

// 编辑表单
const editDialogVisible = ref(false)
const editFormRef = ref<FormInstance>()
const editForm = reactive({
  id: 0,
  title: '',
  image: '',
  link_url: '',
  sort_order: 0,
  status: 1
})

// 表单验证规则
const editRules: FormRules = {
  title: [
    { required: true, message: '请输入轮播图标题', trigger: 'blur' },
    { min: 2, max: 50, message: '标题长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  sort_order: [
    { required: true, message: '请输入排序值', trigger: 'blur' }
  ],
  status: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ]
}

// 获取轮播图列表
const getBannerList = async () => {
  try {
    loading.value = true
    const response = await getAdminBanners()
    if (response.code === 200) {
      bannerList.value = response.data || []
    }
  } catch (error) {
    console.error('获取轮播图列表失败:', error)
    ElMessage.error('获取轮播图列表失败')
  } finally {
    loading.value = false
  }
}

// 添加轮播图
const handleAdd = () => {
  editForm.id = 0
  editForm.title = ''
  editForm.image = ''
  editForm.link_url = ''
  editForm.sort_order = 0
  editForm.status = 1
  editDialogVisible.value = true
}

// 编辑轮播图
const handleEdit = (row: Banner) => {
  editForm.id = row.id
  editForm.title = row.title
  editForm.image = row.image || ''
  editForm.link_url = row.link_url || ''
  editForm.sort_order = row.sort_order
  editForm.status = row.status
  editDialogVisible.value = true
}

// 保存轮播图
const handleSave = async () => {
  if (!editFormRef.value) return
  
  try {
    await editFormRef.value.validate()
    
    // 新增时必须选择图片
    if (!editForm.id && !editForm.image) {
      ElMessage.error('请上传轮播图图片')
      return
    }
    
    saveLoading.value = true
    
    const submitData = {
      title: editForm.title,
      image: editForm.image,
      link_url: editForm.link_url,
      sort_order: editForm.sort_order,
      status: editForm.status
    }
    
    if (editForm.id) {
      await updateBanner(editForm.id, submitData)
      ElMessage.success('更新成功')
    } else {
      await createBanner(submitData)
      ElMessage.success('添加成功')
    }
    
    editDialogVisible.value = false
    getBannerList()
  } catch (error: any) {
    console.error('保存失败:', error)
    ElMessage.error(error.message || '操作失败')
  } finally {
    saveLoading.value = false
  }
}

// 删除轮播图
const handleDelete = async (row: Banner) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除轮播图 "${row.title}" 吗？\n\n删除后用户将无法在首页看到此轮播图，此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        dangerouslyUseHTMLString: false
      }
    )
    
    await deleteBanner(row.id)
    ElMessage.success('删除成功')
    getBannerList()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error(error.message || '删除失败，请稍后重试')
    }
  }
}

// 获取图片URL
const getImageUrl = (imagePath: string) => {
  if (!imagePath) return ''
  if (imagePath.startsWith('http')) return imagePath
  return `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'}${imagePath}`
}

// 格式化时间
const formatTime = (timeStr: string) => {
  return new Date(timeStr).toLocaleString('zh-CN')
}

// 页面初始化
onMounted(() => {
  getBannerList()
})
</script>
<style scoped lang="scss">
.banner-manage {
  padding: 0;
}

.action-bar {
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.table-container {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.no-image {
  color: #c0c4cc;
  font-size: 12px;
}

// Element Plus 组件样式覆盖
:deep(.el-table) {
  .el-table__header {
    th {
      background: #f8f9fa;
      color: #606266;
      font-weight: 600;
      text-align: center;
    }
  }
  
  .el-table__body {
    td {
      text-align: center;
    }
  }
}

:deep(.el-tag) {
  &.el-tag--success {
    background: rgba(107, 207, 127, 0.2);
    border-color: #6bcf7f;
    color: #67c23a;
  }
  
  &.el-tag--danger {
    background: rgba(255, 154, 158, 0.2);
    border-color: #ff9a9e;
    color: #f56c6c;
  }
}

:deep(.el-button) {
  &.el-button--primary {
    background: #a8d8ea;
    border-color: #a8d8ea;
    
    &:hover {
      background: #7fb3d3;
      border-color: #7fb3d3;
    }
  }
  
  &.el-button--danger {
    background: #ff9a9e;
    border-color: #ff9a9e;
    
    &:hover {
      background: #ff7875;
      border-color: #ff7875;
    }
  }
}

:deep(.el-radio-group) {
  .el-radio__input.is-checked .el-radio__inner {
    background: #a8d8ea;
    border-color: #a8d8ea;
  }
  
  .el-radio__input.is-checked + .el-radio__label {
    color: #a8d8ea;
  }
}

:deep(.el-input-number) {
  .el-input-number__increase,
  .el-input-number__decrease {
    &:hover {
      color: #a8d8ea;
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .table-container {
    padding: 12px;
    overflow-x: auto;
  }
  
  .action-bar {
    padding: 16px;
  }
}
</style>