import apiClient from './axios'

export const postSaleApi = {
  getList(params = {}) {
    return apiClient.get('/post-sale/list', { params })
  },

  getById(followupId) {
    return apiClient.get(`/post-sale/${followupId}`)
  },

  getPending() {
    return apiClient.get('/post-sale/pending')
  },

  getOverdue() {
    return apiClient.get('/post-sale/overdue')
  },

  create(data) {
    return apiClient.post('/post-sale/create', data)
  },

  complete(followupId, data) {
    return apiClient.patch(`/post-sale/${followupId}/complete`, data)
  },

  skip(followupId, data) {
    return apiClient.patch(`/post-sale/${followupId}/skip`, data)
  },

  getStats() {
    return apiClient.get('/post-sale/stats')
  },

  getRanking(limit = 10) {
    return apiClient.get('/post-sale/ranking', { params: { limit } })
  }
}
