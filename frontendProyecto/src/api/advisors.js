import api from './axios'

export const advisorsApi = {
  create(userId, data) {
    return api.post('/advisors', data, { params: { user_id: userId } })
  },

  update(advisorId, data) {
    return api.put(`/advisors/${advisorId}`, data)
  },

  getById(advisorId) {
    return api.get(`/advisors/${advisorId}`)
  }
}
