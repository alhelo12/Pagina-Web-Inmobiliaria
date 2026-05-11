import apiClient from './axios'

export const appointmentsApi = {
  getByClient(params = {}) {
    return apiClient.get('/appointments', { params })
  },

  getByAdvisor(params = {}) {
    return apiClient.get('/appointments/advisor/my-appointments', { params })
  },

  getById(appointmentId) {
    return apiClient.get(`/appointments/${appointmentId}`)
  },

  create(data) {
    return apiClient.post('/appointments', data, { params: { client_id: data.client_id } })
  },

  update(appointmentId, data) {
    return apiClient.put(`/appointments/${appointmentId}`, data)
  },

  updateStatus(appointmentId, status) {
    return apiClient.patch(`/appointments/${appointmentId}`, { status })
  },

  delete(appointmentId) {
    return apiClient.delete(`/appointments/${appointmentId}`)
  }
}