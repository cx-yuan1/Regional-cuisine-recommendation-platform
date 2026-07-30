<template>
  <div class="merchant-comments">
    <h2>评价回复</h2>
    
    <el-table v-loading="loading" :data="commentList" style="margin-top: 20px">
      <el-table-column label="序号" width="80" align="center">
        <template #default="{ $index }">
          {{ (pagination.page - 1) * pagination.per_page + $index + 1 }}
        </template>
      </el-table-column>
      <el-table-column prop="food.name" label="美食" width="120" />
      <el-table-column prop="user.username" label="用户" width="100" />
      <el-table-column prop="content" label="评论内容" min-width="200" show-overflow-tooltip />
      <el-table-column prop="rating" label="评分" width="80" />
      <el-table-column label="商家回复" min-width="200">
        <template #default="{ row }">
          <span v-if="row.reply_content">{{ row.reply_content }}</span>
          <el-button v-else size="small" type="primary" @click="openReply(row)">回复</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <el-pagination
      v-model:current-page="pagination.page"
      v-model:page-size="pagination.per_page"
      :total="pagination.total"
      layout="total, prev, pager, next"
      style="margin-top: 20px"
      @current-change="load"
    />
    
    <el-dialog v-model="replyVisible" title="回复评论" width="500px">
      <el-input v-model="replyContent" type="textarea" :rows="4" placeholder="请输入回复内容" />
      <template #footer>
        <el-button @click="replyVisible = false">取消</el-button>
        <el-button type="primary" :loading="replying" @click="submitReply">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { merchantApi } from '@/api/merchant'
import type { Comment } from '@/types'

const loading = ref(false)
const commentList = ref<Comment[]>([])
const pagination = reactive({ page: 1, per_page: 10, total: 0 })
const replyVisible = ref(false)
const replyContent = ref('')
const replying = ref(false)
const replyingComment = ref<Comment | null>(null)

const load = async () => {
  try {
    loading.value = true
    const res = await merchantApi.getMyComments({
      page: pagination.page,
      per_page: pagination.per_page
    })
    commentList.value = res.data.items || []
    pagination.total = res.data.pagination?.total ?? 0
  } catch (e) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const openReply = (row: Comment) => {
  replyingComment.value = row
  replyContent.value = ''
  replyVisible.value = true
}

const submitReply = async () => {
  if (!replyContent.value.trim() || replyContent.value.length < 2) {
    ElMessage.warning('回复内容至少2个字符')
    return
  }
  if (!replyingComment.value) return
  try {
    replying.value = true
    await merchantApi.replyComment(replyingComment.value.id, replyContent.value)
    ElMessage.success('回复成功')
    replyVisible.value = false
    load()
  } catch (e: any) {
    ElMessage.error(e?.message || '回复失败')
  } finally {
    replying.value = false
  }
}

onMounted(load)
</script>

<style scoped lang="scss">
.merchant-comments h2 { margin: 0; font-size: 20px; color: #303133; }
</style>
