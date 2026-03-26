import axios from 'axios'

const api = axios.create({ baseURL: 'http://localhost:8000' })

export const getConfig   = ()       => api.get('/config').then(r => r.data)
export const saveConfig  = (data)   => api.post('/config', data).then(r => r.data)
export const getThemes   = ()       => api.get('/themes').then(r => r.data)
export const convertFile = (body)   => api.post('/convert', body).then(r => r.data)
export const convertFolder = (body) => api.post('/convert-folder', body).then(r => r.data)
export const previewUrl  = (path)   => `http://localhost:8000/preview?file_path=${encodeURIComponent(path)}`
