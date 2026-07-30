<template>
  <div class="category-manage">
    <!-- 操作栏 -->
    <div class="action-bar">
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>
        添加分类
      </el-button>
    </div>

    <!-- 分类表格 -->
    <div class="table-container">
      <el-table
        v-loading="loading"
        :data="categoryList"
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" align="center" />
        
        <el-table-column prop="icon" label="图标" width="100" align="center">
          <template #default="{ row }">
            <el-image
              v-if="row.icon"
              :src="getImageUrl(row.icon)"
              :preview-src-list="[getImageUrl(row.icon)]"
              style="width: 50px; height: 50px; border-radius: 4px"
              fit="cover"
            />
            <span v-else class="no-image">无图标</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="name" label="分类名称" align="center" />
        
        <el-table-column prop="description" label="描述" align="center">
          <template #default="{ row }">
            <span>{{ row.description || '-' }}</span>
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
    
    <!-- 添加/编辑分类对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      :close-on-click-modal="false"
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="分类名称" prop="name">
          <el-input
            v-model="formData.name"
            placeholder="请输入分类名称"
            maxlength="50"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="分类图标">
          <ImageUpload
            v-model="formData.icon"
            upload-type="category"
            placeholder="点击上传分类图标"
          />
        </el-form-item>
        
        <el-form-item label="描述">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入分类描述"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="排序" prop="sort_order">
          <el-input-number
            v-model="formData.sort_order"
            :min="0"
            :max="999"
            style="width: 100%"
          />
          <span style="margin-left: 12px; color: #909399; font-size: 12px;">
            数值越小，排序越靠前
          </span>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          :loading="submitLoading"
          @click="handleSubmit"
        >
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getAdminCategories, createCategory, updateCategory, deleteCategory } from '@/api/admin'
import ImageUpload from '@/components/common/ImageUpload.vue'
import type { FoodCategory } from '@/types'

// 响应式数据
const loading = ref(false)
const categoryList = ref<FoodCategory[]>([])
const dialogVisible = ref(false)
const submitLoading = ref(false)
const formRef = ref<FormInstance>()

// 表单数据
const formData = reactive({
  id: 0,
  name: '',
  icon: '',
  description: '',
  sort_order: 0
})

// 对话框标题
const dialogTitle = computed(() => {
  return formData.id ? '编辑分类' : '添加分类'
})

// 表单验证规则
const formRules: FormRules = {
  name: [
    { required: true, message: '请输入分类名称', trigger: 'blur' },
    { min: 2, max: 50, message: '名称长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  sort_order: [
    { required: true, message: '请输入排序值', trigger: 'blur' }
  ]
}

// 获取分类列表
const getCategoryList = async () => {
  try {
    loading.value = true
    const response = await getAdminCategories()
    if (response.code === 200) {
      categoryList.value = response.data || []
    }
  } catch (error) {
    console.error('获取分类列表失败:', error)
    ElMessage.error('获取分类列表失败')
  } finally {
    loading.value = false
  }
}

// 添加分类
const handleAdd = () => {
  resetForm()
  dialogVisible.value = true
}

// 编辑分类
const handleEdit = (row: FoodCategory) => {
  resetForm()
  formData.id = row.id
  formData.name = row.name
  formData.icon = row.icon || ''
  formData.description = row.description || ''
  formData.sort_order = row.sort_order
  dialogVisible.value = true
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    submitLoading.value = true
    
    if (formData.id) {
      // 编辑
      await updateCategory(formData.id, formData)
      ElMessage.success('更新成功')
    } else {
      // 添加
      await createCategory(formData)
      ElMessage.success('添加成功')
    }
    
    dialogVisible.value = false
    getCategoryList()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('提交失败:', error)
      ElMessage.error(error.message || '操作失败')
    }
  } finally {
    submitLoading.value = false
  }
}

// 删除分类
const handleDelete = async (row: FoodCategory) => {
  try {
    // 检查是否有关联美食
    if (row.food_count && row.food_count > 0) {
      await ElMessageBox.confirm(
        `分类 "${row.name}" 下还有 ${row.food_count} 个美食。\n\n删除分类后，这些美食将失去分类关联。是否继续删除？`,
        '删除确认',
        {
          confirmButtonText: '确定删除',
          cancelButtonText: '取消',
          type: 'warning',
          dangerouslyUseHTMLString: false
        }
      )
    } else {
      await ElMessageBox.confirm(
        `确定要删除分类 "${row.name}" 吗？\n\n此操作不可恢复。`,
        '删除确认',
        {
          confirmButtonText: '确定删除',
          cancelButtonText: '取消',
          type: 'warning',
          dangerouslyUseHTMLString: false
        }
      )
    }
    
    await deleteCategory(row.id)
    ElMessage.success('删除成功')
    getCategoryList()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error(error.message || '删除失败，请稍后重试')
    }
  }
}

// 重置表单
const resetForm = () => {
  formData.id = 0
  formData.name = ''
  formData.icon = ''
  formData.description = ''
  formData.sort_order = 0
  
  if (formRef.value) {
    formRef.value.clearValidate()
  }
}

// 对话框关闭
const handleDialogClose = () => {
  resetForm()
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
  getCategoryList()
})
</script>

<style scoped lang="scss">
.category-manage {
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
