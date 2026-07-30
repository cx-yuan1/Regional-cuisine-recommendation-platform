<template>
  <div class="merchant-manage">
    <!-- 搜索和筛选 -->
    <div class="search-bar">
      <div class="search-left">
        <el-select
          v-model="searchForm.status"
          placeholder="申请状态"
          style="width: 140px"
          clearable
        >
          <el-option label="待审核" value="pending" />
          <el-option label="已通过" value="approved" />
          <el-option label="已拒绝" value="rejected" />
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

    <!-- 商家列表表格 -->
    <div class="table-container">
      <el-table
        v-loading="loading"
        :data="merchantList"
        style="width: 100%"
      >
        <el-table-column label="序号" width="80" align="center">
          <template #default="{ $index }">
            {{ (pagination.page - 1) * pagination.per_page + $index + 1 }}
          </template>
        </el-table-column>
        
        <el-table-column prop="name" label="店铺名称" min-width="140" />
        
        <el-table-column label="申请人" width="120" align="center">
          <template #default="{ row }">
            {{ row.user?.username || '-' }}
          </template>
        </el-table-column>
        
        <el-table-column label="联系方式" width="130" align="center">
          <template #default="{ row }">
            {{ row.contact_phone || '-' }}
          </template>
        </el-table-column>
        
        <el-table-column prop="address" label="地址" min-width="160" show-overflow-tooltip />
        
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)">
              {{ statusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="申请时间" width="180" align="center">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="200" align="center" fixed="right">
          <template #default="{ row }">
            <template v-if="row.status === 'pending'">
              <el-button type="success" size="small" @click="handleApprove(row)">
                通过
              </el-button>
              <el-button type="danger" size="small" @click="handleReject(row)">
                拒绝
              </el-button>
            </template>
            <template v-else>
              <el-tag type="info">已处理</el-tag>
            </template>
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
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 拒绝原因对话框 -->
    <el-dialog
      v-model="rejectDialogVisible"
      title="拒绝入驻申请"
      width="450px"
    >
      <el-form :model="rejectForm" label-width="80px">
        <el-form-item label="拒绝原因">
          <el-input
            v-model="rejectForm.reject_reason"
            type="textarea"
            :rows="4"
            placeholder="请输入拒绝原因（选填，默认：不符合入驻条件）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="rejectDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="confirmReject" :loading="rejectLoading">
          确认拒绝
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh } from '@element-plus/icons-vue'
import { getMerchantApplications, approveMerchant, rejectMerchant } from '@/api/admin'
import type { Merchant } from '@/types'

const loading = ref(false)
const merchantList = ref<Merchant[]>([])

const searchForm = reactive({
  status: ''
})

const pagination = reactive({
  page: 1,
  per_page: 20,
  total: 0
})

const rejectDialogVisible = ref(false)
const rejectLoading = ref(false)
const rejectForm = reactive({
  merchantId: 0,
  reject_reason: ''
})

const statusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '待审核',
    approved: '已通过',
    rejected: '已拒绝'
  }
  return map[status] || status
}

const statusTagType = (status: string) => {
  const map: Record<string, string> = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger'
  }
  return map[status] || 'info'
}

const formatTime = (time?: string) => {
  if (!time) return '-'
  return time.replace('T', ' ').slice(0, 19)
}

const getMerchantList = async () => {
  try {
    loading.value = true
    const params: Record<string, any> = {
      page: pagination.page,
      per_page: pagination.per_page
    }
    if (searchForm.status) params.status = searchForm.status

    const response = await getMerchantApplications(params)
    if (response.code === 200) {
      merchantList.value = response.data?.items || []
      pagination.total = response.data?.pagination?.total || 0
    }
  } catch (error) {
    console.error('获取商家列表失败:', error)
    ElMessage.error('获取商家列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  getMerchantList()
}

const handleReset = () => {
  searchForm.status = ''
  pagination.page = 1
  getMerchantList()
}

const handleSizeChange = (size: number) => {
  pagination.per_page = size
  pagination.page = 1
  getMerchantList()
}

const handleCurrentChange = (page: number) => {
  pagination.page = page
  getMerchantList()
}

const handleApprove = async (row: Merchant) => {
  try {
    await ElMessageBox.confirm(`确定通过「${row.name}」的入驻申请吗？`, '确认通过', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'success'
    })

    const res = await approveMerchant(row.id)
    if (res.code === 200) {
      ElMessage.success('审核通过')
      getMerchantList()
    }
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

const handleReject = (row: Merchant) => {
  rejectForm.merchantId = row.id
  rejectForm.reject_reason = ''
  rejectDialogVisible.value = true
}

const confirmReject = async () => {
  try {
    rejectLoading.value = true
    const res = await rejectMerchant(
      rejectForm.merchantId,
      rejectForm.reject_reason || undefined
    )
    if (res.code === 200) {
      ElMessage.success('已拒绝')
      rejectDialogVisible.value = false
      getMerchantList()
    }
  } catch (error) {
    ElMessage.error('操作失败')
  } finally {
    rejectLoading.value = false
  }
}

onMounted(() => {
  getMerchantList()
})
</script>

<style scoped lang="scss">
.merchant-manage {
  .search-bar {
    margin-bottom: 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .table-container {
    background: white;
    padding: 16px;
    border-radius: 8px;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  }

  .pagination-container {
    margin-top: 16px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>
