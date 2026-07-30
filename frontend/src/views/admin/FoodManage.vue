<template>
  <div class="food-manage">
    <!-- 搜索和操作栏 -->
    <div class="search-bar">
      <div class="search-left">
        <el-input
          v-model="searchForm.keyword"
          placeholder="搜索美食名称"
          style="width: 300px"
          clearable
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-select
          v-model="searchForm.category_id"
          placeholder="选择分类"
          style="width: 150px; margin-left: 16px"
          clearable
        >
          <el-option
            v-for="category in categoryList"
            :key="category.id"
            :label="category.name"
            :value="category.id"
          />
        </el-select>
        
        <el-input
          v-model="searchForm.region"
          placeholder="地域"
          style="width: 120px; margin-left: 16px"
          clearable
        />
        
        <el-button type="primary" @click="handleSearch" style="margin-left: 16px">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
        
        <el-button @click="handleReset">
          <el-icon><Refresh /></el-icon>
          重置
        </el-button>
      </div>
    </div>

    <!-- 美食表格 -->
    <div class="table-container">
      <el-table
        v-loading="loading"
        :data="foodList"
        style="width: 100%"
      >
        <el-table-column label="序号" width="80" align="center">
          <template #default="{ $index }">
            {{ (pagination.page - 1) * pagination.per_page + $index + 1 }}
          </template>
        </el-table-column>
        
        <el-table-column prop="image" label="图片" width="100" align="center">
          <template #default="{ row }">
            <el-image
              v-if="row.image"
              :src="getImageUrl(row.image)"
              :preview-src-list="[getImageUrl(row.image)]"
              style="width: 60px; height: 60px; border-radius: 4px"
              fit="cover"
            />
            <span v-else class="no-image">无图片</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="name" label="美食名称" align="center" />
        
        <el-table-column prop="region" label="地域" width="100" align="center" />
        
        <el-table-column prop="category_name" label="分类" width="120" align="center" />
        
        <el-table-column prop="price_range" label="价格区间" width="120" align="center" />
        
        <el-table-column prop="rating" label="评分" width="100" align="center">
          <template #default="{ row }">
            <el-rate
              v-model="row.rating"
              disabled
              size="small"
              :max="5"
              :precision="0.1"
            />
          </template>
        </el-table-column>
        
        <el-table-column prop="view_count" label="浏览量" width="100" align="center" />
        
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

    <!-- 分页 -->
    <div class="pagination-container">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.per_page"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
    
    <!-- 添加/编辑美食对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="900px"
      :close-on-click-modal="false"
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="美食名称" prop="name">
          <el-input
            v-model="formData.name"
            placeholder="请输入美食名称"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="所属分类" prop="category_id">
          <el-select v-model="formData.category_id" placeholder="请选择分类" style="width: 100%">
            <el-option
              v-for="category in categoryList"
              :key="category.id"
              :label="category.name"
              :value="category.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="地域" prop="region">
          <el-input
            v-model="formData.region"
            placeholder="请输入地域，如：四川、广东"
            maxlength="50"
          />
        </el-form-item>
        
        <el-form-item label="价格区间" prop="price_range">
          <el-input
            v-model="formData.price_range"
            placeholder="如：20-50元"
            maxlength="50"
          />
        </el-form-item>
        
        <el-form-item label="美食图片">
          <ImageUpload
            v-model="formData.image"
            upload-type="food"
            placeholder="点击上传美食图片"
          />
        </el-form-item>
        
        <el-form-item label="美食描述" prop="description">
          <RichTextEditor
            v-model="formData.description"
            height="300px"
            placeholder="请输入美食详细描述..."
            strip-paragraph-tags
          />
        </el-form-item>
        
        <el-form-item label="口味标签">
          <el-select
            v-model="formData.taste_tags"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="选择或输入口味标签，如：麻辣、香辣、经典"
            style="width: 100%"
          >
            <el-option
              v-for="tag in defaultTasteTags"
              :key="tag"
              :label="tag"
              :value="tag"
            />
          </el-select>
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
import { Search, Refresh } from '@element-plus/icons-vue'
import { getAdminFoods, createFood, updateFood, deleteFood } from '@/api/admin'
import { foodCategoryApi } from '@/api/foodCategory'
import RichTextEditor from '@/components/common/RichTextEditor.vue'
import ImageUpload from '@/components/common/ImageUpload.vue'
import type { Food, FoodCategory } from '@/types'

// 响应式数据
const loading = ref(false)
const foodList = ref<Food[]>([])
const categoryList = ref<FoodCategory[]>([])
const dialogVisible = ref(false)
const submitLoading = ref(false)
const formRef = ref<FormInstance>()

// 搜索表单
const searchForm = reactive({
  keyword: '',
  category_id: null as number | null,
  region: ''
})

// 分页数据
const pagination = reactive({
  page: 1,
  per_page: 20,
  total: 0
})

// 表单数据
const formData = reactive({
  id: 0,
  name: '',
  category_id: null as number | null,
  region: '',
  price_range: '',
  image: '',
  description: '',
  taste_tags: [] as string[]
})

// 默认口味标签选项
const defaultTasteTags = [
  '麻辣', '香辣', '微辣', '酸辣', '清淡',
  '鲜美', '香甜', '咸鲜', '酸甜', '苦涩',
  '经典', '传统', '创新', '特色', '地道'
]

// 对话框标题
const dialogTitle = computed(() => {
  return formData.id ? '编辑美食' : '添加美食'
})

// 表单验证规则
const formRules: FormRules = {
  name: [
    { required: true, message: '请输入美食名称', trigger: 'blur' },
    { min: 2, max: 100, message: '名称长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  category_id: [
    { required: true, message: '请选择分类', trigger: 'change' }
  ],
  region: [
    { required: true, message: '请输入地域', trigger: 'blur' }
  ],
  price_range: [
    { required: true, message: '请输入价格区间', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入美食描述', trigger: 'blur' }
  ]
}

// 获取美食列表
const getFoodList = async () => {
  try {
    loading.value = true
    const params = {
      ...searchForm,
      page: pagination.page,
      per_page: pagination.per_page
    }
    
    const response = await getAdminFoods(params)
    if (response.code === 200) {
      foodList.value = response.data.items || []
      pagination.total = response.data.pagination?.total || 0
    }
  } catch (error) {
    console.error('获取美食列表失败:', error)
    ElMessage.error('获取美食列表失败')
  } finally {
    loading.value = false
  }
}

// 获取分类列表
const getCategoryList = async () => {
  try {
    const response = await foodCategoryApi.getActiveCategories()
    if (response.code === 200) {
      categoryList.value = response.data || []
    }
  } catch (error) {
    console.error('获取分类列表失败:', error)
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  getFoodList()
}

// 重置搜索
const handleReset = () => {
  searchForm.keyword = ''
  searchForm.category_id = null
  searchForm.region = ''
  pagination.page = 1
  getFoodList()
}

// 分页处理
const handleSizeChange = (size: number) => {
  pagination.per_page = size
  pagination.page = 1
  getFoodList()
}

const handleCurrentChange = (page: number) => {
  pagination.page = page
  getFoodList()
}

// 编辑美食
const handleEdit = (row: Food) => {
  resetForm()
  formData.id = row.id
  formData.name = row.name
  formData.category_id = row.category_id
  formData.region = row.region
  formData.price_range = row.price_range
  formData.image = row.image || ''
  formData.description = row.description || ''
  formData.taste_tags = row.taste_tags || []
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
      await updateFood(formData.id, formData)
      ElMessage.success('更新成功')
    } else {
      // 添加
      await createFood(formData)
      ElMessage.success('添加成功')
    }
    
    dialogVisible.value = false
    getFoodList()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('提交失败:', error)
      ElMessage.error(error.message || '操作失败')
    }
  } finally {
    submitLoading.value = false
  }
}

// 重置表单
const resetForm = () => {
  formData.id = 0
  formData.name = ''
  formData.category_id = null
  formData.region = ''
  formData.price_range = ''
  formData.image = ''
  formData.description = ''
  formData.taste_tags = []
  
  if (formRef.value) {
    formRef.value.clearValidate()
  }
}

// 对话框关闭
const handleDialogClose = () => {
  resetForm()
}

// 删除美食
const handleDelete = async (row: Food) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除美食 "${row.name}" 吗？\n\n注意：删除后相关的评论、收藏等数据也将被清除，此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        dangerouslyUseHTMLString: false
      }
    )
    
    await deleteFood(row.id)
    ElMessage.success('删除成功')
    getFoodList()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      // 检查是否是关联数据错误
      if (error.message && error.message.includes('关联')) {
        ElMessage.warning('该美食存在关联数据，请先处理相关评论和收藏后再删除')
      } else {
        ElMessage.error(error.message || '删除失败，请稍后重试')
      }
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
  getCategoryList()
  getFoodList()
})
</script>
<style scoped lang="scss">
.food-manage {
  padding: 0;
}

.search-bar {
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-left {
  display: flex;
  align-items: center;
}

.table-container {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
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

:deep(.el-rate) {
  .el-rate__icon {
    font-size: 14px;
    color: #ffd93d;
  }
}

:deep(.el-pagination) {
  .el-pager li.is-active {
    background: #a8d8ea;
    color: white;
  }
  
  .btn-next,
  .btn-prev {
    &:hover {
      color: #a8d8ea;
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .search-bar {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }
  
  .search-left {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
    
    .el-input,
    .el-select {
      width: 100% !important;
      margin-left: 0 !important;
    }
    
    .el-button {
      margin-left: 0 !important;
    }
  }
  
  .table-container {
    padding: 12px;
    overflow-x: auto;
  }
}
</style>