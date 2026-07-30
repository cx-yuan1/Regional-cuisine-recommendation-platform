<template>
  <div class="merchant-store">
    <h2>店铺信息</h2>
    <el-row :gutter="24" style="margin-top: 24px">
      <el-col :span="24">
        <el-card v-loading="loading" class="form-card">
          <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
            <el-form-item label="店铺名称" prop="name">
              <el-input v-model="form.name" placeholder="店铺名称" maxlength="100" show-word-limit />
            </el-form-item>
            <el-form-item label="店铺描述">
              <el-input v-model="form.description" type="textarea" :rows="4" placeholder="店铺描述" />
            </el-form-item>
            <el-form-item label="联系电话">
              <el-input v-model="form.contact_phone" placeholder="联系电话" />
            </el-form-item>
            <el-form-item label="店铺地址">
              <el-input v-model="form.address" placeholder="店铺地址" />
            </el-form-item>
            <el-form-item label="店铺Logo">
              <ImageUpload v-model="form.logo" upload-type="merchant" placeholder="上传Logo" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { merchantApi } from '@/api/merchant'
import ImageUpload from '@/components/common/ImageUpload.vue'

const formRef = ref<FormInstance>()
const loading = ref(false)
const saving = ref(false)
const form = reactive({
  name: '',
  description: '',
  contact_phone: '',
  address: '',
  logo: ''
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入店铺名称', trigger: 'blur' }]
}

const load = async () => {
  try {
    loading.value = true
    const res = await merchantApi.getMyStore()
    Object.assign(form, {
      name: res.data.name || '',
      description: res.data.description || '',
      contact_phone: res.data.contact_phone || '',
      address: res.data.address || '',
      logo: res.data.logo || ''
    })
  } catch (e) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const handleSave = async () => {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
    saving.value = true
    await merchantApi.updateStore(form)
    ElMessage.success('保存成功')
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error(e?.message || '保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<style scoped lang="scss">
.merchant-store h2 { margin: 0; font-size: 20px; color: #303133; }

.form-card {
  width: 100%;
}
</style>
