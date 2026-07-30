<template>
  <div class="announcement-manage">
    <!-- 搜索和操作栏 -->
    <div class="search-bar">
      <div class="search-left">
        <el-input
          v-model="searchForm.keyword"
          placeholder="搜索公告标题"
          style="width: 300px"
          clearable
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-select
          v-model="searchForm.type"
          placeholder="选择类型"
          style="width: 120px; margin-left: 16px"
          clearable
        >
          <el-option label="通知" value="notice" />
          <el-option label="活动" value="event" />
          <el-option label="系统" value="system" />
        </el-select>
        
        <el-select
          v-model="searchForm.status"
          placeholder="选择状态"
          style="width: 120px; margin-left: 16px"
          clearable
        >
          <el-option label="启用" :value="1" />
          <el-option label="禁用" :value="0" />
        </el-select>
        
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
          添加公告
        </el-button>
      </div>
    </div>

    <!-- 公告表格 -->
    <div class="table-container">
      <el-table
        v-loading="loading"
        :data="announcementList"
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
        
        <el-table-column prop="title" label="标题" align="center" />
        
        <el-table-column prop="type" label="类型" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getTypeTagType(row.type)">
              {{ getTypeText(row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="priority" label="优先级" width="100" align="center">
          <template #default="{ row }">
            <el-rate
              v-model="row.priority"
              disabled
              size="small"
              :max="5"
            />
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'">
              {{ row.status === 1 ? '启用' : '禁用' }}
            </el-tag>
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
    
    <!-- 添加/编辑公告对话框 -->
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
        <el-form-item label="公告标题" prop="title">
          <el-input
            v-model="formData.title"
            placeholder="请输入公告标题"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="公告类型" prop="type">
          <el-select v-model="formData.type" placeholder="请选择公告类型">
            <el-option label="通知" value="notice" />
            <el-option label="活动" value="event" />
            <el-option label="系统" value="system" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="优先级" prop="priority">
          <el-rate v-model="formData.priority" :max="5" />
          <span style="margin-left: 12px; color: #909399;">
            优先级越高，展示越靠前
          </span>
        </el-form-item>
        
        <el-form-item label="公告图片">
          <ImageUpload
            v-model="formData.image"
            upload-type="announcement"
            placeholder="点击上传公告图片"
          />
        </el-form-item>
        
        <el-form-item label="公告内容" prop="content">
          <RichTextEditor
            v-model="formData.content"
            height="400px"
            placeholder="请输入公告内容..."
          />
        </el-form-item>
        
        <el-form-item label="有效期">
          <el-date-picker
            v-model="timeRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>
        
        <el-form-item label="状态">
          <el-switch
            v-model="formData.status"
            :active-value="1"
            :inactive-value="0"
            active-text="启用"
            inactive-text="禁用"
          />
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
import { Search, Refresh, Plus } from '@element-plus/icons-vue'
import { getAdminAnnouncements, createAnnouncement, updateAnnouncement, deleteAnnouncement } from '@/api/admin'
import RichTextEditor from '@/components/common/RichTextEditor.vue'
import ImageUpload from '@/components/common/ImageUpload.vue'
import type { Announcement } from '@/types'

// 响应式数据
const loading = ref(false)
const announcementList = ref<Announcement[]>([])
const dialogVisible = ref(false)
const submitLoading = ref(false)
const formRef = ref<FormInstance>()

// 搜索表单
const searchForm = reactive({
  keyword: '',
  type: '',
  status: null as number | null
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
  title: '',
  content: '',
  type: 'notice' as 'notice' | 'event' | 'system',
  priority: 3,
  image: '',
  status: 1,
  start_time: '',
  end_time: ''
})

// 时间范围
const timeRange = ref<[string, string] | null>(null)

// 对话框标题
const dialogTitle = computed(() => {
  return formData.id ? '编辑公告' : '添加公告'
})

// 表单验证规则
const formRules: FormRules = {
  title: [
    { required: true, message: '请输入公告标题', trigger: 'blur' },
    { min: 2, max: 100, message: '标题长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择公告类型', trigger: 'change' }
  ],
  content: [
    { required: true, message: '请输入公告内容', trigger: 'blur' },
    { min: 10, message: '内容至少10个字符', trigger: 'blur' }
  ],
  priority: [
    { required: true, message: '请选择优先级', trigger: 'change' }
  ]
}

// 获取公告列表
const getAnnouncementList = async () => {
  try {
    loading.value = true
    const params = {
      ...searchForm,
      page: pagination.page,
      per_page: pagination.per_page
    }
    
    const response = await getAdminAnnouncements(params)
    if (response.code === 200) {
      announcementList.value = response.data.items || []
      pagination.total = response.data.pagination?.total || 0
    }
  } catch (error) {
    console.error('获取公告列表失败:', error)
    ElMessage.error('获取公告列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  getAnnouncementList()
}

// 重置搜索
const handleReset = () => {
  searchForm.keyword = ''
  searchForm.type = ''
  searchForm.status = null
  pagination.page = 1
  getAnnouncementList()
}

// 分页处理
const handleSizeChange = (size: number) => {
  pagination.per_page = size
  pagination.page = 1
  getAnnouncementList()
}

const handleCurrentChange = (page: number) => {
  pagination.page = page
  getAnnouncementList()
}

// 添加公告
const handleAdd = () => {
  resetForm()
  dialogVisible.value = true
}

// 编辑公告
const handleEdit = (row: Announcement) => {
  resetForm()
  formData.id = row.id
  formData.title = row.title
  formData.content = row.content
  formData.type = row.type
  formData.priority = row.priority
  formData.image = row.image || ''
  formData.status = row.status
  formData.start_time = row.start_time || ''
  formData.end_time = row.end_time || ''
  
  // 设置时间范围
  if (row.start_time && row.end_time) {
    timeRange.value = [row.start_time, row.end_time]
  }
  
  dialogVisible.value = true
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    // 处理时间范围
    if (timeRange.value) {
      formData.start_time = timeRange.value[0]
      formData.end_time = timeRange.value[1]
    } else {
      formData.start_time = ''
      formData.end_time = ''
    }
    
    submitLoading.value = true
    
    if (formData.id) {
      // 编辑
      await updateAnnouncement(formData.id, formData)
      ElMessage.success('更新成功')
    } else {
      // 添加
      await createAnnouncement(formData)
      ElMessage.success('添加成功')
    }
    
    dialogVisible.value = false
    getAnnouncementList()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('提交失败:', error)
      ElMessage.error(error.message || '操作失败')
    }
  } finally {
    submitLoading.value = false
  }
}

// 删除公告
const handleDelete = async (row: Announcement) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除公告 "${row.title}" 吗？\n\n删除后用户将无法查看此公告内容，此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        dangerouslyUseHTMLString: false
      }
    )
    
    await deleteAnnouncement(row.id)
    ElMessage.success('删除成功')
    getAnnouncementList()
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
  formData.title = ''
  formData.content = ''
  formData.type = 'notice'
  formData.priority = 3
  formData.image = ''
  formData.status = 1
  formData.start_time = ''
  formData.end_time = ''
  timeRange.value = null
  
  if (formRef.value) {
    formRef.value.clearValidate()
  }
}

// 对话框关闭
const handleDialogClose = () => {
  resetForm()
}

// 获取类型标签类型
const getTypeTagType = (type: string) => {
  const typeMap: Record<string, string> = {
    notice: 'primary',
    event: 'success',
    system: 'warning'
  }
  return typeMap[type] || 'primary'
}

// 获取类型文本
const getTypeText = (type: string) => {
  const typeMap: Record<string, string> = {
    notice: '通知',
    event: '活动',
    system: '系统'
  }
  return typeMap[type] || type
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
  getAnnouncementList()
})
</script>
<style scoped lang="scss">
.announcement-manage {
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
  
  .no-image {
    color: #c0c4cc;
    font-size: 12px;
  }
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
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
  &.el-tag--primary {
    background: rgba(168, 216, 234, 0.2);
    border-color: #a8d8ea;
    color: #409eff;
  }
  
  &.el-tag--success {
    background: rgba(107, 207, 127, 0.2);
    border-color: #6bcf7f;
    color: #67c23a;
  }
  
  &.el-tag--warning {
    background: rgba(255, 217, 61, 0.2);
    border-color: #ffd93d;
    color: #e6a23c;
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