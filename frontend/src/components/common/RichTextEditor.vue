<template>
  <div class="rich-text-editor">
    <QuillEditor
      v-model:content="content"
      :options="editorOptions"
      :style="{ height: height }"
      content-type="html"
      theme="snow"
      @update:content="handleContentChange"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'

interface Props {
  modelValue: string
  height?: string
  placeholder?: string
  /** 是否去除 p 标签，输出纯文本（适用于美食描述等简单文本场景） */
  stripParagraphTags?: boolean
}

interface Emits {
  (e: 'update:modelValue', value: string): void
}

const props = withDefaults(defineProps<Props>(), {
  height: '300px',
  placeholder: '请输入内容...',
  stripParagraphTags: false
})

const emit = defineEmits<Emits>()

// 编辑器内容
const content = ref(props.modelValue)

// 编辑器配置
const editorOptions = {
  modules: {
    toolbar: [
      ['bold', 'italic', 'underline', 'strike'],        // 加粗、斜体、下划线、删除线
      ['blockquote', 'code-block'],                     // 引用、代码块
      [{ 'header': 1 }, { 'header': 2 }],               // 标题
      [{ 'list': 'ordered'}, { 'list': 'bullet' }],     // 有序列表、无序列表
      [{ 'script': 'sub'}, { 'script': 'super' }],      // 下标、上标
      [{ 'indent': '-1'}, { 'indent': '+1' }],          // 缩进
      [{ 'direction': 'rtl' }],                         // 文本方向
      [{ 'size': ['small', false, 'large', 'huge'] }],  // 字体大小
      [{ 'header': [1, 2, 3, 4, 5, 6, false] }],        // 标题
      [{ 'color': [] }, { 'background': [] }],          // 字体颜色、背景颜色
      [{ 'font': [] }],                                 // 字体
      [{ 'align': [] }],                                // 对齐方式
      ['clean'],                                        // 清除格式
      ['link', 'image']                                 // 链接、图片
    ]
  },
  placeholder: props.placeholder,
  theme: 'snow'
}

// 去除 p 标签，保留换行
const stripPTags = (html: string): string => {
  if (!html || !html.trim()) return ''
  return html
    .replace(/<p><br><\/p>/gi, '\n')
    .replace(/<p><\/p>/gi, '\n')
    .replace(/<\/p>\s*<p>/gi, '\n')
    .replace(/<p>/gi, '')
    .replace(/<\/p>/gi, '\n')
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/\n{2,}/g, '\n')
    .trim()
}

// 监听内容变化
const handleContentChange = (value: string) => {
  const output = props.stripParagraphTags ? stripPTags(value) : value
  emit('update:modelValue', output)
}

// 监听外部值变化
watch(() => props.modelValue, (newValue) => {
  if (newValue !== content.value) {
    content.value = newValue
  }
})
</script>

<style lang="scss" scoped>
.rich-text-editor {
  :deep(.ql-container) {
    min-height: 200px;
    font-size: 14px;
  }
  
  :deep(.ql-editor) {
    min-height: 200px;
    
    &.ql-blank::before {
      color: #c0c4cc;
      font-style: normal;
    }
  }
  
  :deep(.ql-toolbar) {
    background: #f8f9fa;
    border-color: #dcdfe6;
    border-radius: 4px 4px 0 0;
  }
  
  :deep(.ql-container) {
    border-color: #dcdfe6;
    border-radius: 0 0 4px 4px;
  }
  
  :deep(.ql-snow .ql-stroke) {
    stroke: #606266;
  }
  
  :deep(.ql-snow .ql-fill) {
    fill: #606266;
  }
  
  :deep(.ql-snow .ql-picker-label) {
    color: #606266;
  }
  
  :deep(.ql-toolbar.ql-snow .ql-picker-label:hover),
  :deep(.ql-toolbar.ql-snow .ql-picker-label.ql-active),
  :deep(.ql-toolbar.ql-snow button:hover),
  :deep(.ql-toolbar.ql-snow button.ql-active) {
    color: #a8d8ea;
    
    .ql-stroke {
      stroke: #a8d8ea;
    }
    
    .ql-fill {
      fill: #a8d8ea;
    }
  }
}
</style>
