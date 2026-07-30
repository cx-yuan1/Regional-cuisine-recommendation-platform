<template>
  <div class="merchant-apply">
    <div class="apply-card" v-if="!applyStatus?.has_applied || applyStatus?.merchant?.status !== 'approved'">
      <!-- 入驻失败 -->
      <div v-if="applyStatus?.merchant?.status === 'rejected' && !showReapplyForm" class="status-box rejected-box">
        <el-result icon="error" title="入驻失败" :sub-title="rejectSubTitle">
          <template #extra>
            <el-button type="primary" @click="showReapplyForm = true">重新申请</el-button>
          </template>
        </el-result>
      </div>
      
      <!-- 首次申请或重新申请表单 -->
      <template v-if="!applyStatus?.has_applied || (applyStatus?.merchant?.status === 'rejected' && showReapplyForm)">
        <h2>商家入驻申请</h2>
        <p class="tip">填写店铺信息，提交后等待平台审核。审核通过后即可发布美食、管理店铺。</p>
        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-width="100px"
          style="max-width: 500px; margin-top: 24px"
        >
          <el-form-item label="店铺名称" prop="name">
            <el-input v-model="form.name" placeholder="请输入店铺名称" maxlength="100" show-word-limit />
          </el-form-item>
          <el-form-item label="店铺描述" prop="description">
            <el-input v-model="form.description" type="textarea" :rows="4" placeholder="简要描述您的店铺" />
          </el-form-item>
          <el-form-item label="联系电话" prop="contact_phone">
            <el-input v-model="form.contact_phone" placeholder="请输入联系电话" />
          </el-form-item>
          <el-form-item label="店铺地址" prop="address">
            <el-input v-model="form.address" placeholder="请输入店铺地址" />
          </el-form-item>
          <el-form-item label="店铺Logo" prop="logo">
            <ImageUpload v-model="form.logo" upload-type="merchant" placeholder="点击上传店铺Logo" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="submitting" @click="handleSubmit">
              {{ applyStatus?.merchant?.status === 'rejected' ? '重新申请' : '提交申请' }}
            </el-button>
          </el-form-item>
        </el-form>
      </template>
      
      <!-- 审核中 -->
      <div v-else-if="applyStatus?.merchant?.status === 'pending'" class="status-box">
        <el-result icon="info" title="审核中" sub-title="您的入驻申请已提交，请耐心等待平台审核。审核通过后即可发布美食、管理店铺。" />
      </div>
    </div>
    
    <div v-else class="already-merchant">
      <el-result icon="success" title="您已是商家" sub-title="入驻申请已通过，可以管理您的店铺了">
        <template #extra>
          <el-button type="primary" @click="$router.push('/merchant/dashboard')">进入商家中心</el-button>
        </template>
      </el-result>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { merchantApi } from '@/api/merchant'
import { useUserStore } from '@/stores/user'
import type { Merchant } from '@/types'
import ImageUpload from '@/components/common/ImageUpload.vue'

const formRef = ref<FormInstance>()
const applyStatus = ref<{ has_applied: boolean; merchant: Merchant | null; status?: string } | null>(null)
const submitting = ref(false)
const showReapplyForm = ref(false)

const rejectSubTitle = computed(() => {
  const reason = applyStatus.value?.merchant?.reject_reason
  return reason ? `拒绝原因：${reason}` : '您的入驻申请未通过审核，请修改后重新申请。'
})

const form = reactive({
  name: '',
  description: '',
  contact_phone: '',
  address: '',
  logo: ''
})

const rules: FormRules = {
  name: [
    { required: true, message: '请输入店铺名称', trigger: 'blur' },
    { min: 2, max: 100, message: '长度在 2 到 100 个字符', trigger: 'blur' }
  ]
}

const userStore = useUserStore()

const loadStatus = async () => {
  try {
    const res = await merchantApi.getApplyStatus()
    applyStatus.value = res.data
    if (res.data?.status === 'approved') {
      await userStore.getUserInfo()
    }
  } catch (e) {
    console.error(e)
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
    submitting.value = true
    await merchantApi.apply(form)
    ElMessage.success('申请已提交，请等待审核')
    showReapplyForm.value = false
    await loadStatus()
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error(e?.message || '提交失败')
  } finally {
    submitting.value = false
  }
}

onMounted(loadStatus)
</script>

<style scoped lang="scss">
.merchant-apply {
  max-width: 600px;
  margin: 0 auto;
}
.apply-card {
  background: white;
  border-radius: 12px;
  padding: 32px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  h2 { margin: 0 0 8px 0; font-size: 24px; color: #303133; }
  .tip { color: #909399; margin: 0; font-size: 14px; }
}
.status-box, .rejected-box, .already-merchant {
  background: white;
  border-radius: 12px;
  padding: 48px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}
</style>
