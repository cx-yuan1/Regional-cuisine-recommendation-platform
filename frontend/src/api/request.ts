import axios, { type AxiosRequestConfig, type AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import type { ApiResponse } from '@/types'

// 创建axios实例
const request = axios.create({
  baseURL: '/api',
  timeout: 10000,
  withCredentials: true, // 携带cookie（session）
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  (config: AxiosRequestConfig) => {
    // FormData 上传时移除 Content-Type，让浏览器自动添加 multipart/form-data 及 boundary
    if (config.data instanceof FormData && config.headers) {
      delete (config.headers as Record<string, unknown>)['Content-Type']
    }
    return config
  },
  (error) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    const { data } = response
    
    // 检查业务状态码
    if (data.code === 200) {
      return data
    } else {
      // 业务错误
      ElMessage.error(data.message || '请求失败')
      return Promise.reject(new Error(data.message || '请求失败'))
    }
  },
  (error) => {
    console.error('响应错误:', error)
    
    // 处理HTTP状态码错误
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 401:
          // 登录、注册页面不提示，用户本就是来登录/注册的
          const path = window.location.pathname
          if (!path.includes('/login') && !path.includes('/register')) {
            ElMessage.error('未登录或登录已过期')
          }
          break
        case 403:
          ElMessage.error('无权访问')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error('服务器内部错误')
          break
        default:
          ElMessage.error(data?.message || `请求失败 (${status})`)
      }
    } else if (error.request) {
      ElMessage.error('网络连接失败，请检查网络')
    } else {
      ElMessage.error('请求配置错误')
    }
    
    return Promise.reject(error)
  }
)

// 封装常用请求方法
export const api = {
  get<T = any>(url: string, params?: any): Promise<ApiResponse<T>> {
    return request.get(url, { params })
  },
  
  post<T = any>(url: string, data?: any): Promise<ApiResponse<T>> {
    return request.post(url, data)
  },
  
  put<T = any>(url: string, data?: any): Promise<ApiResponse<T>> {
    return request.put(url, data)
  },
  
  delete<T = any>(url: string): Promise<ApiResponse<T>> {
    return request.delete(url)
  },
  
  // 文件上传（FormData 由拦截器自动处理 Content-Type）
  upload<T = any>(url: string, formData: FormData): Promise<ApiResponse<T>> {
    return request.post(url, formData)
  }
}

export default request