import { api } from './request'

// 文件上传API
export const uploadApi = {
  // 上传图片（不设置 Content-Type，由浏览器自动添加 multipart/form-data 及 boundary）
  uploadImage(file: File, type: string = 'food') {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('type', type)
    
    return api.post<{ path: string; url: string }>('/upload/image', formData)
  }
}