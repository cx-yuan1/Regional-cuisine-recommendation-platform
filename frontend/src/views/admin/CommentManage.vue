<template>
  <div class="comment-manage">
    <!-- 搜索栏 -->
    <div class="search-bar">
      <div class="search-left">
        <el-input
          v-model="searchForm.keyword"
          placeholder="搜索评论内容"
          style="width: 300px"
          clearable
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
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

    <!-- 评论表格 -->
    <div class="table-container">
      <el-table
        v-loading="loading"
        :data="commentList"
        style="width: 100%"
      >
        <el-table-column label="序号" width="80" align="center">
          <template #default="{ $index }">
            {{ (pagination.page - 1) * pagination.per_page + $index + 1 }}
          </template>
        </el-table-column>
        
        <el-table-column prop="user.username" label="用户" width="120" align="center">
          <template #default="{ row }">
            <span>{{ row.user?.username || '-' }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="food.name" label="美食" width="150" align="center">
          <template #default="{ row }">
            <span>{{ row.food?.name || '-' }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="content" label="评论内容" align="center">
          <template #default="{ row }">
            <div class="comment-content">
              {{ row.content }}
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="rating" label="评分" width="120" align="center">
          <template #default="{ row }">
            <el-rate
              v-model="row.rating"
              disabled
              size="small"
              :max="5"
            />
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="评论时间" width="180" align="center">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="120" align="center">
          <template #default="{ row }">
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
  </div>
</template>
<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh } from '@element-plus/icons-vue'
import { getAdminComments, deleteComment } from '@/api/admin'
import type { Comment } from '@/types'

// 响应式数据
const loading = ref(false)
const commentList = ref<Comment[]>([])

// 搜索表单
const searchForm = reactive({
  keyword: ''
})

// 分页数据
const pagination = reactive({
  page: 1,
  per_page: 20,
  total: 0
})

// 获取评论列表
const getCommentList = async () => {
  try {
    loading.value = true
    const params = {
      ...searchForm,
      page: pagination.page,
      per_page: pagination.per_page
    }
    
    const response = await getAdminComments(params)
    if (response.code === 200) {
      commentList.value = response.data.items || []
      pagination.total = response.data.pagination?.total || 0
    }
  } catch (error) {
    console.error('获取评论列表失败:', error)
    ElMessage.error('获取评论列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  getCommentList()
}

// 重置搜索
const handleReset = () => {
  searchForm.keyword = ''
  pagination.page = 1
  getCommentList()
}

// 分页处理
const handleSizeChange = (size: number) => {
  pagination.per_page = size
  pagination.page = 1
  getCommentList()
}

const handleCurrentChange = (page: number) => {
  pagination.page = page
  getCommentList()
}

// 删除评论
const handleDelete = async (row: Comment) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 "${row.user?.username || '未知用户'}" 的这条评论吗？\n\n删除后将无法恢复，此操作不可撤销。`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        dangerouslyUseHTMLString: false
      }
    )
    
    await deleteComment(row.id)
    ElMessage.success('删除成功')
    getCommentList()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error(error.message || '删除失败，请稍后重试')
    }
  }
}

// 格式化时间
const formatTime = (timeStr: string) => {
  return new Date(timeStr).toLocaleString('zh-CN')
}

// 页面初始化
onMounted(() => {
  getCommentList()
})
</script>
<style scoped lang="scss">
.comment-manage {
  padding: 0;
}

.search-bar {
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
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

.comment-content {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  text-align: left;
  margin: 0 auto;
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
  .search-left {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
    
    .el-input {
      width: 100% !important;
    }
    
    .el-button {
      margin-left: 0 !important;
    }
  }
  
  .table-container {
    padding: 12px;
    overflow-x: auto;
  }
  
  .comment-content {
    max-width: 200px;
  }
}
</style>