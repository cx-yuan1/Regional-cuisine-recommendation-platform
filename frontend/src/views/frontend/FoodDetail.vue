<template>
  <div class="food-detail-page">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-button 
        class="back-btn-loading"
        :icon="ArrowLeft"
        @click="router.back()"
      >
        返回
      </el-button>
      <el-skeleton animated>
        <template #template>
          <div class="skeleton-content">
            <el-skeleton-item variant="image" style="width: 100%; height: 400px;" />
            <div style="padding: 24px;">
              <el-skeleton-item variant="h1" style="width: 60%;" />
              <el-skeleton-item variant="text" style="width: 80%; margin: 16px 0;" />
              <el-skeleton-item variant="text" style="width: 40%;" />
            </div>
          </div>
        </template>
      </el-skeleton>
    </div>

    <!-- 美食详情内容 -->
    <div v-else-if="food" class="food-detail-content">
      <!-- 美食头图 -->
      <div class="food-hero">
        <el-button 
          class="back-btn"
          :icon="ArrowLeft"
          @click="router.back()"
        >
          返回
        </el-button>
        <img 
          :src="getFoodImage(food.image)" 
          :alt="food.name"
          class="hero-image"
          @error="handleImageError"
        />
        <div class="hero-overlay">
          <div class="hero-content">
            <h1 class="food-title">{{ food.name }}</h1>
            <div class="food-meta">
              <div class="meta-item" v-if="food.merchant_name">
                <el-icon><Shop /></el-icon>
                <span>{{ food.merchant_name }}</span>
              </div>
              <div class="meta-item">
                <el-icon><Location /></el-icon>
                <span>{{ food.region }}</span>
              </div>
              <div class="meta-item" v-if="food.category_name">
                <el-icon><Food /></el-icon>
                <span>{{ food.category_name }}</span>
              </div>
              <div class="meta-item" v-if="food.rating > 0">
                <el-icon><Star /></el-icon>
                <span>{{ food.rating.toFixed(1) }}分</span>
              </div>
            </div>
          </div>
          <div class="hero-actions">
            <el-button 
              :type="isFavorite ? 'danger' : 'primary'"
              :icon="Collection"
              @click="toggleFavorite"
              :loading="favoriteLoading"
            >
              {{ isFavorite ? '取消收藏' : '收藏美食' }}
            </el-button>
          </div>
        </div>
      </div>

      <!-- 详情信息 -->
      <div class="detail-container">
        <div class="detail-main">
          <!-- 美食描述 -->
          <div class="detail-section">
            <h3 class="section-title">美食介绍</h3>
            <p class="food-description">
              {{ food.description || '暂无详细介绍' }}
            </p>
          </div>

          <!-- 口味标签 -->
          <div class="detail-section" v-if="food.taste_tags && food.taste_tags.length > 0">
            <h3 class="section-title">口味特色</h3>
            <div class="taste-tags">
              <el-tag 
                v-for="tag in food.taste_tags" 
                :key="tag"
                type="info"
                effect="plain"
                size="large"
              >
                {{ tag }}
              </el-tag>
            </div>
          </div>

          <!-- 评论区域 -->
          <div class="detail-section">
            <div class="section-header">
              <h3 class="section-title">用户评价</h3>
              <el-button 
                v-if="userStore.isLoggedIn"
                type="primary" 
                @click="showCommentDialog = true"
              >
                写评价
              </el-button>
            </div>
            
            <!-- 评论列表 -->
            <div class="comments-list">
              <div v-if="comments.length === 0" class="empty-comments">
                <el-empty description="暂无评价，快来写第一条评价吧！" />
              </div>
              <div v-else>
                <div 
                  v-for="comment in comments" 
                  :key="comment.id"
                  class="comment-item"
                >
                  <div class="comment-header">
                    <div class="user-info">
                      <img 
                        :src="getUserAvatar(comment.user?.avatar)" 
                        :alt="comment.user?.username"
                        class="user-avatar"
                      />
                      <span class="username">{{ comment.user?.username || '匿名用户' }}</span>
                    </div>
                    <div class="comment-rating">
                      <el-rate 
                        v-model="comment.rating" 
                        disabled 
                        size="small"
                        show-score
                      />
                    </div>
                  </div>
                  <p class="comment-content">{{ comment.content }}</p>
                  <div class="comment-time">
                    {{ formatTime(comment.created_at) }}
                  </div>
                  <!-- 商家回复 -->
                  <div v-if="comment.reply_content" class="comment-reply">
                    <div class="reply-label">商家回复：</div>
                    <p class="reply-content">{{ comment.reply_content }}</p>
                    <div class="reply-time" v-if="comment.reply_at">
                      {{ formatTime(comment.reply_at) }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 侧边栏 -->
        <div class="detail-sidebar">
          <!-- 基本信息 -->
          <div class="info-card">
            <h4 class="card-title">基本信息</h4>
            <div class="info-list">
              <div class="info-item" v-if="food.merchant_name">
                <span class="label">店家：</span>
                <span class="value">{{ food.merchant_name }}</span>
              </div>
              <div class="info-item">
                <span class="label">价格区间：</span>
                <span class="value">{{ food.price_range || '暂无' }}</span>
              </div>
              <div class="info-item">
                <span class="label">浏览次数：</span>
                <span class="value">{{ formatCount(food.view_count) }}</span>
              </div>
              <div class="info-item" v-if="food.comment_count">
                <span class="label">评价数量：</span>
                <span class="value">{{ food.comment_count }}条</span>
              </div>
            </div>
          </div>

          <!-- 相似推荐 -->
          <div class="info-card" v-if="similarFoods.length > 0">
            <h4 class="card-title">相似美食</h4>
            <div class="similar-foods">
              <div 
                v-for="similarFood in similarFoods" 
                :key="similarFood.id"
                class="similar-item"
                @click="goToFood(similarFood.id)"
              >
                <img 
                  :src="getFoodImage(similarFood.image)" 
                  :alt="similarFood.name"
                  class="similar-image"
                />
                <div class="similar-info">
                  <h5 class="similar-name">{{ similarFood.name }}</h5>
                  <p class="similar-region">{{ similarFood.region }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 错误状态 -->
    <div v-else class="error-container">
      <el-result
        icon="error"
        title="美食不存在"
        sub-title="抱歉，您访问的美食信息不存在或已被删除"
      >
        <template #extra>
          <el-button type="primary" @click="$router.push('/')">
            返回首页
          </el-button>
        </template>
      </el-result>
    </div>

    <!-- 评论对话框 -->
    <el-dialog
      v-model="showCommentDialog"
      title="写评价"
      width="500px"
      :before-close="handleCommentDialogClose"
    >
      <el-form 
        ref="commentFormRef"
        :model="commentForm" 
        :rules="commentRules"
        label-width="80px"
      >
        <el-form-item label="评分" prop="rating">
          <el-rate 
            v-model="commentForm.rating" 
            :texts="['极差', '失望', '一般', '满意', '非常满意']"
            show-text 
          />
        </el-form-item>
        <el-form-item label="评价内容" prop="content">
          <el-input
            v-model="commentForm.content"
            type="textarea"
            :rows="4"
            placeholder="请分享您的用餐体验..."
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCommentDialog = false">取消</el-button>
        <el-button 
          type="primary" 
          :loading="commentSubmitting"
          @click="submitComment"
        >
          提交评价
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { 
  Location, 
  Food, 
  Star, 
  Shop,
  Collection,
  ArrowLeft
} from '@element-plus/icons-vue'
import { foodApi } from '@/api/food'
import { favoriteApi } from '@/api/favorite'
import { commentApi } from '@/api/comment'
import { recommendApi } from '@/api/recommend'
import type { Food as FoodType, Comment, CommentForm } from '@/types'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// 响应式数据
const loading = ref(true)
const food = ref<FoodType | null>(null)
const comments = ref<Comment[]>([])
const similarFoods = ref<FoodType[]>([])
const isFavorite = ref(false)
const favoriteLoading = ref(false)
const imageError = ref(false)

// 评论相关
const showCommentDialog = ref(false)
const commentSubmitting = ref(false)
const commentFormRef = ref<FormInstance>()
const commentForm = reactive<CommentForm>({
  food_id: 0,
  content: '',
  rating: 5
})

// 评论表单验证规则
const commentRules: FormRules = {
  rating: [
    { required: true, message: '请选择评分', trigger: 'change' }
  ],
  content: [
    { required: true, message: '请输入评价内容', trigger: 'blur' },
    { min: 10, message: '评价内容至少10个字符', trigger: 'blur' }
  ]
}

// 获取美食ID
const foodId = computed(() => {
  return parseInt(route.params.id as string)
})

// 获取美食详情
const getFoodDetail = async () => {
  try {
    loading.value = true
    const response = await foodApi.getFoodDetail(foodId.value)
    food.value = response.data
    commentForm.food_id = foodId.value
    
    // 并行获取相关数据
    await Promise.all([
      getComments(),
      getSimilarFoods(),
      checkFavoriteStatus()
    ])
  } catch (error) {
    console.error('获取美食详情失败:', error)
    food.value = null
  } finally {
    loading.value = false
  }
}

// 获取评论列表
const getComments = async () => {
  try {
    const response = await commentApi.getFoodComments(foodId.value)
    comments.value = response.data.items || []
  } catch (error) {
    console.error('获取评论失败:', error)
  }
}

// 获取相似美食
const getSimilarFoods = async () => {
  try {
    const response = await recommendApi.getSimilarFoods(foodId.value, 4)
    similarFoods.value = response.data
  } catch (error) {
    console.error('获取相似美食失败:', error)
  }
}

// 检查收藏状态
const checkFavoriteStatus = async () => {
  if (!userStore.isLoggedIn) return
  
  try {
    const response = await favoriteApi.checkFavorite(foodId.value)
    isFavorite.value = response.data.is_favorited
  } catch (error) {
    console.error('检查收藏状态失败:', error)
  }
}

// 切换收藏状态
const toggleFavorite = async () => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    router.push({ name: 'Login', query: { redirect: route.fullPath } })
    return
  }

  try {
    favoriteLoading.value = true
    
    if (isFavorite.value) {
      await favoriteApi.deleteFavoriteByFood(foodId.value)
      isFavorite.value = false
      ElMessage.success('已取消收藏')
    } else {
      await favoriteApi.addFavorite(foodId.value)
      isFavorite.value = true
      ElMessage.success('收藏成功')
    }
  } catch (error) {
    console.error('收藏操作失败:', error)
  } finally {
    favoriteLoading.value = false
  }
}

// 提交评论
const submitComment = async () => {
  if (!commentFormRef.value) return
  
  try {
    await commentFormRef.value.validate()
    
    commentSubmitting.value = true
    await commentApi.addComment(commentForm)
    
    ElMessage.success('评价提交成功')
    showCommentDialog.value = false
    
    // 重新获取评论列表
    await getComments()
    
    // 重置表单
    commentForm.content = ''
    commentForm.rating = 5
  } catch (error) {
    console.error('提交评价失败:', error)
  } finally {
    commentSubmitting.value = false
  }
}

// 处理评论对话框关闭
const handleCommentDialogClose = (done: () => void) => {
  if (commentSubmitting.value) {
    ElMessage.warning('正在提交评价，请稍候...')
    return
  }
  done()
}

// 跳转到其他美食
const goToFood = (id: number) => {
  router.push({ name: 'FoodDetail', params: { id } })
}

// 工具函数
const getFoodImage = (imagePath?: string) => {
  if (imageError.value) return '/placeholder-food.jpg'
  if (!imagePath) return '/placeholder-food.jpg'
  if (imagePath.startsWith('http')) return imagePath
  return `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'}${imagePath}`
}

const handleImageError = () => {
  imageError.value = true
}

const getUserAvatar = (avatarPath?: string) => {
  if (!avatarPath) return '/default-avatar.png'
  if (avatarPath.startsWith('http')) return avatarPath
  return `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'}${avatarPath}`
}

const formatCount = (count: number) => {
  if (count >= 10000) {
    return `${(count / 10000).toFixed(1)}万`
  } else if (count >= 1000) {
    return `${(count / 1000).toFixed(1)}k`
  }
  return count.toString()
}

const formatTime = (timeStr: string) => {
  const date = new Date(timeStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  const minutes = Math.floor(diff / (1000 * 60))
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (minutes < 60) {
    return `${minutes}分钟前`
  } else if (hours < 24) {
    return `${hours}小时前`
  } else if (days < 30) {
    return `${days}天前`
  } else {
    return date.toLocaleDateString()
  }
}

// 页面初始化
onMounted(() => {
  getFoodDetail()
})
</script>

<style scoped lang="scss">
.food-detail-page {
  min-height: 100vh;
  background: #f8f9fa;
}

.loading-container {
  padding: 20px;
  position: relative;
}

.back-btn-loading {
  position: absolute;
  top: 20px;
  left: 20px;
  z-index: 10;
}

.skeleton-content {
  max-width: 1200px;
  margin: 0 auto;
  background: white;
  border-radius: 12px;
  overflow: hidden;
}

.food-hero {
  position: relative;
  height: 400px;
  overflow: hidden;
}

.back-btn {
  position: absolute;
  top: 20px;
  left: 20px;
  z-index: 10;
  background: rgba(255, 255, 255, 0.9);
  border: none;
  color: #303133;
  
  &:hover {
    background: #fff;
    color: #409eff;
  }
}

.hero-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.hero-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.7));
  padding: 40px;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
}

.hero-content {
  color: white;
}

.food-title {
  font-size: 36px;
  font-weight: 600;
  margin: 0 0 16px 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
}

.food-meta {
  display: flex;
  gap: 24px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 16px;
  
  .el-icon {
    font-size: 18px;
  }
}

.hero-actions {
  .el-button {
    height: 48px;
    padding: 0 24px;
    font-size: 16px;
  }
}

.detail-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 20px;
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 32px;
}

.detail-main {
  background: white;
  border-radius: 12px;
  padding: 32px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.detail-section {
  margin-bottom: 40px;
  
  &:last-child {
    margin-bottom: 0;
  }
}

.section-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 16px 0;
  padding-bottom: 8px;
  border-bottom: 2px solid #a8d8ea;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.food-description {
  font-size: 16px;
  line-height: 1.8;
  color: #606266;
  margin: 0;
  white-space: pre-line; /* 保留换行显示 */
}

.taste-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.comments-list {
  .empty-comments {
    text-align: center;
    padding: 40px 0;
  }
}

.comment-item {
  padding: 20px 0;
  border-bottom: 1px solid #f0f0f0;
  
  &:last-child {
    border-bottom: none;
  }
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.username {
  font-weight: 500;
  color: #303133;
}

.comment-content {
  font-size: 15px;
  line-height: 1.6;
  color: #606266;
  margin: 0 0 8px 0;
}

.comment-time {
  font-size: 13px;
  color: #909399;
}

.comment-reply {
  margin-top: 12px;
  padding: 12px 16px;
  background: #f5f7fa;
  border-radius: 8px;
  border-left: 3px solid #409eff;
}

.reply-label {
  font-size: 13px;
  color: #409eff;
  font-weight: 500;
  margin-bottom: 6px;
}

.reply-content {
  font-size: 14px;
  line-height: 1.5;
  color: #606266;
  margin: 0 0 6px 0;
}

.reply-time {
  font-size: 12px;
  color: #909399;
}

.detail-sidebar {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.info-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 16px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f0f0;
}

.info-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  
  .label {
    color: #909399;
    font-size: 14px;
  }
  
  .value {
    color: #303133;
    font-weight: 500;
  }
}

.similar-foods {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.similar-item {
  display: flex;
  gap: 12px;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  transition: background-color 0.3s ease;
  
  &:hover {
    background: #f8f9fa;
  }
}

.similar-image {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  object-fit: cover;
}

.similar-info {
  flex: 1;
}

.similar-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin: 0 0 4px 0;
  line-height: 1.4;
}

.similar-region {
  font-size: 12px;
  color: #909399;
  margin: 0;
}

.error-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
}

@media (max-width: 768px) {
  .food-hero {
    height: 250px;
  }
  
  .hero-overlay {
    padding: 20px;
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .food-title {
    font-size: 24px;
  }
  
  .food-meta {
    gap: 16px;
    flex-wrap: wrap;
  }
  
  .detail-container {
    grid-template-columns: 1fr;
    padding: 20px 16px;
    gap: 24px;
  }
  
  .detail-main {
    padding: 20px;
  }
}
</style>