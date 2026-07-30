<template>
  <div class="user-manage">
    <!-- 搜索和操作栏 -->
    <div class="search-bar">
      <div class="search-left">
        <el-input
          v-model="searchForm.keyword"
          placeholder="搜索用户名或邮箱"
          style="width: 300px"
          clearable
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-select
          v-model="searchForm.role"
          placeholder="选择角色"
          style="width: 120px; margin-left: 16px"
          clearable
        >
          <el-option label="用户" value="user" />
          <el-option label="商家" value="merchant" />
          <el-option label="管理员" value="admin" />
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
    </div>

    <!-- 用户表格 -->
    <div class="table-container">
      <el-table
        v-loading="loading"
        :data="userList"
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" align="center" />
        
        <el-table-column label="序号" width="80" align="center">
          <template #default="{ $index }">
            {{ (pagination.page - 1) * pagination.per_page + $index + 1 }}
          </template>
        </el-table-column>
        
        <el-table-column prop="username" label="用户名" align="center" />
        
        <el-table-column prop="email" label="邮箱" align="center" />
        
        <el-table-column prop="role" label="角色" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : row.role === 'merchant' ? 'success' : 'primary'">
              {{ row.role === 'admin' ? '管理员' : row.role === 'merchant' ? '商家' : '用户' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="注册时间" width="180" align="center">
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
              :disabled="row.role === 'admin'"
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

    <!-- 编辑用户对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      :title="editForm.id ? '编辑用户' : '添加用户'"
      width="500px"
    >
      <el-form
        ref="editFormRef"
        :model="editForm"
        :rules="editRules"
        label-width="80px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="editForm.username" :disabled="!!editForm.id" />
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="editForm.email" />
        </el-form-item>
        
        <el-form-item label="角色" prop="role">
          <el-select v-model="editForm.role" style="width: 100%" disabled>
            <el-option label="用户" value="user" />
            <el-option label="商家" value="merchant" />
            <el-option label="管理员" value="admin" />
          </el-select>
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
import { Search, Refresh } from '@element-plus/icons-vue'
import { getUsers, updateUser, deleteUser } from '@/api/admin'
import type { User } from '@/types'

// 响应式数据
const loading = ref(false)
const saveLoading = ref(false)
const userList = ref<User[]>([])
const selectedUsers = ref<User[]>([])

// 搜索表单
const searchForm = reactive({
  keyword: '',
  role: ''
})

// 分页数据
const pagination = reactive({
  page: 1,
  per_page: 20,
  total: 0
})

// 编辑表单
const editDialogVisible = ref(false)
const editFormRef = ref<FormInstance>()
const editForm = reactive({
  id: 0,
  username: '',
  email: '',
  role: 'user'
})

// 表单验证规则
const editRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ]
}

// 获取用户列表
const getUserList = async () => {
  try {
    loading.value = true
    const params = {
      ...searchForm,
      page: pagination.page,
      per_page: pagination.per_page
    }
    
    const response = await getUsers(params)
    if (response.code === 200) {
      userList.value = response.data.items || []
      pagination.total = response.data.pagination?.total || 0
    }
  } catch (error) {
    console.error('获取用户列表失败:', error)
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  getUserList()
}

// 重置搜索
const handleReset = () => {
  searchForm.keyword = ''
  searchForm.role = ''
  pagination.page = 1
  getUserList()
}
// 分页处理
const handleSizeChange = (size: number) => {
  pagination.per_page = size
  pagination.page = 1
  getUserList()
}

const handleCurrentChange = (page: number) => {
  pagination.page = page
  getUserList()
}

// 选择处理
const handleSelectionChange = (selection: User[]) => {
  selectedUsers.value = selection
}

// 编辑用户
const handleEdit = (row: User) => {
  editForm.id = row.id
  editForm.username = row.username
  editForm.email = row.email || ''
  editForm.role = row.role
  editDialogVisible.value = true
}

// 保存用户
const handleSave = async () => {
  if (!editFormRef.value) return
  
  try {
    await editFormRef.value.validate()
    saveLoading.value = true
    
    const data = {
      email: editForm.email
    }
    
    await updateUser(editForm.id, data)
    ElMessage.success('保存成功')
    editDialogVisible.value = false
    getUserList()
  } catch (error) {
    console.error('保存失败:', error)
  } finally {
    saveLoading.value = false
  }
}

// 删除用户
const handleDelete = async (row: User) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 "${row.username}" 吗？\n\n注意：删除后该用户的评论、收藏等数据也将被清除，此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        dangerouslyUseHTMLString: false
      }
    )
    
    await deleteUser(row.id)
    ElMessage.success('删除成功')
    getUserList()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      // 检查是否是关联数据错误
      if (error.message && error.message.includes('关联')) {
        ElMessage.warning('该用户存在关联数据，请先处理相关评论和收藏后再删除')
      } else {
        ElMessage.error(error.message || '删除失败，请稍后重试')
      }
    }
  }
}

// 格式化时间
const formatTime = (timeStr: string) => {
  return new Date(timeStr).toLocaleString('zh-CN')
}

// 页面初始化
onMounted(() => {
  getUserList()
})
</script>
<style scoped lang="scss">
.user-manage {
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
    
    &:disabled {
      background: #f5f7fa;
      border-color: #e4e7ed;
      color: #c0c4cc;
    }
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