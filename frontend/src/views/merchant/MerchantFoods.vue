<template>
  <div class="merchant-foods">
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
            v-for="c in categories"
            :key="c.id"
            :label="c.name"
            :value="c.id"
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
      
      <div class="search-right">
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          发布美食
        </el-button>
      </div>
    </div>

    <!-- 美食表格 -->
    <div class="table-container">
      <el-table
        v-loading="loading"
        :data="foodList"
        stripe
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
              :src="getFoodImage(row.image)"
              :preview-src-list="[getFoodImage(row.image)]"
              style="width: 60px; height: 60px; border-radius: 4px"
              fit="cover"
            />
            <span v-else class="no-image">无图片</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="name" label="美食名称" min-width="150" align="center" show-overflow-tooltip />
        
        <el-table-column prop="region" label="地域" width="100" align="center" />
        
        <el-table-column prop="category_name" label="分类" width="120" align="center" />
        
        <el-table-column prop="price_range" label="价格区间" width="120" align="center" />
        
        <el-table-column prop="rating" label="评分" width="100" align="center">
          <template #default="{ row }">
            <el-rate
              :model-value="row.rating"
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
            <el-button type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">删除</el-button>
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
    
    <!-- 发布/编辑美食对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingId ? '编辑美食' : '发布美食'"
      width="900px"
      :close-on-click-modal="false"
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="美食名称" prop="name">
          <el-input
            v-model="form.name"
            placeholder="请输入美食名称"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="所属分类" prop="category_id">
          <el-select v-model="form.category_id" placeholder="请选择分类" style="width: 100%">
            <el-option
              v-for="c in categories"
              :key="c.id"
              :label="c.name"
              :value="c.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="地域" prop="region">
          <el-input
            v-model="form.region"
            placeholder="请输入地域，如：四川、广东"
            maxlength="50"
          />
        </el-form-item>
        
        <el-form-item label="价格区间" prop="price_range">
          <el-input
            v-model="form.price_range"
            placeholder="如：20-50元"
            maxlength="50"
          />
        </el-form-item>
        
        <el-form-item label="美食图片">
          <ImageUpload
            v-model="form.image"
            upload-type="food"
            placeholder="点击上传美食图片"
          />
        </el-form-item>
        
        <el-form-item label="美食描述" prop="description">
          <RichTextEditor
            v-model="form.description"
            height="300px"
            placeholder="请输入美食详细描述..."
            strip-paragraph-tags
          />
        </el-form-item>
        
        <el-form-item label="口味标签">
          <el-select
            v-model="form.taste_tags"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="选择或输入口味标签"
            style="width: 100%"
          >
            <el-option
              v-for="t in defaultTags"
              :key="t"
              :label="t"
              :value="t"
            />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Search, Refresh, Plus } from '@element-plus/icons-vue'
import { merchantApi } from '@/api/merchant'
import { foodCategoryApi } from '@/api/foodCategory'
import RichTextEditor from '@/components/common/RichTextEditor.vue'
import ImageUpload from '@/components/common/ImageUpload.vue'
import type { Food, FoodCategory } from '@/types'

const loading = ref(false)
const foodList = ref<Food[]>([])
const categories = ref<FoodCategory[]>([])
const pagination = reactive({ page: 1, per_page: 20, total: 0 })
const dialogVisible = ref(false)
const editingId = ref<number | null>(null)
const submitting = ref(false)
const formRef = ref<FormInstance>()

const searchForm = reactive({
  keyword: '',
  category_id: null as number | null,
  region: ''
})

const defaultTags = [
  '麻辣', '香辣', '微辣', '酸辣', '清淡',
  '鲜美', '香甜', '咸鲜', '酸甜', '酥脆',
  '经典', '传统', '创新', '特色', '地道'
]

const form = reactive({
  name: '',
  category_id: null as number | null,
  region: '',
  price_range: '',
  image: '',
  description: '',
  taste_tags: [] as string[]
})

const formRules: FormRules = {
  name: [
    { required: true, message: '请输入美食名称', trigger: 'blur' },
    { min: 2, max: 100, message: '名称长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  category_id: [{ required: true, message: '请选择分类', trigger: 'change' }],
  region: [{ required: true, message: '请输入地域', trigger: 'blur' }]
}

const load = async () => {
  try {
    loading.value = true
    const res = await merchantApi.getMyFoods({
      page: pagination.page,
      per_page: pagination.per_page,
      keyword: searchForm.keyword || undefined,
      category_id: searchForm.category_id || undefined,
      region: searchForm.region || undefined
    })
    foodList.value = res.data.items || []
    pagination.total = res.data.pagination?.total ?? 0
  } catch (e) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const loadCategories = async () => {
  try {
    const res = await foodCategoryApi.getActiveCategories()
    categories.value = res.data || []
  } catch (e) {
    console.error(e)
  }
}

const handleSearch = () => {
  pagination.page = 1
  load()
}

const handleReset = () => {
  searchForm.keyword = ''
  searchForm.category_id = null
  searchForm.region = ''
  pagination.page = 1
  load()
}

const handleSizeChange = () => {
  pagination.page = 1
  load()
}

const handleCurrentChange = () => {
  load()
}

const resetForm = () => {
  editingId.value = null
  Object.assign(form, {
    name: '',
    category_id: null,
    region: '',
    price_range: '',
    image: '',
    description: '',
    taste_tags: []
  })
  formRef.value?.clearValidate()
}

const handleAdd = () => {
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row: Food) => {
  editingId.value = row.id
  Object.assign(form, {
    name: row.name,
    category_id: row.category_id ?? null,
    region: row.region,
    price_range: row.price_range || '',
    image: row.image || '',
    description: (row.description as string) || '',
    taste_tags: row.taste_tags || []
  })
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
    submitting.value = true
    if (editingId.value) {
      await merchantApi.updateFood(editingId.value, form)
      ElMessage.success('更新成功')
    } else {
      await merchantApi.createFood(form)
      ElMessage.success('发布成功')
    }
    dialogVisible.value = false
    load()
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error(e?.message || '操作失败')
  } finally {
    submitting.value = false
  }
}

const handleDialogClose = () => {
  resetForm()
}

const getFoodImage = (path?: string) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return path.startsWith('/') ? path : `/${path}`
}

const formatTime = (timeStr?: string) => {
  if (!timeStr) return ''
  return new Date(timeStr).toLocaleString('zh-CN')
}

const handleDelete = async (row: Food) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除美食「${row.name}」吗？删除后相关评论、收藏等数据也将清除。`,
      '删除确认',
      { confirmButtonText: '确定删除', cancelButtonText: '取消', type: 'warning' }
    )
    await merchantApi.deleteFood(row.id)
    ElMessage.success('删除成功')
    load()
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error(e?.message || '删除失败')
  }
}

onMounted(() => {
  loadCategories()
  load()
})
</script>

<style scoped lang="scss">
.merchant-foods {
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

:deep(.el-table) {
  .el-table__header th {
    background: #f8f9fa;
    color: #606266;
    font-weight: 600;
    text-align: center;
  }
  .el-table__body td {
    text-align: center;
  }
}

:deep(.el-table__cell) {
  vertical-align: middle;
}

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
    .el-input, .el-select {
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
