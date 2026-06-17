import api from './axios'

export const authApi = {
  login(email, password) {
    const form = new URLSearchParams()
    form.append('username', email)
    form.append('password', password)
    return api.post('/auth/login', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
  },

  registerClient(data) {
    return api.post('/auth/register/client', data)
  },

  register(data) {
    return api.post('/auth/register', data)
  },

  me() {
    return api.get('/auth/me')
  },

  changePassword(currentPassword, newPassword) {
    return api.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword
    })
  },

  checkEmail(email) {
    return api.post('/auth/check-email', { email })
  },

  validatePassword(password) {
    return api.post('/auth/validate-password', { password })
  },

  sendVerification(email) {
    return api.post('/auth/send-verification', { email })
  },

  verifyEmail(token) {
    return api.get(`/auth/verify-email/${token}`)
  },

  forgotPassword(email) {
    return api.post('/auth/forgot-password', { email })
  },

  resetPassword(token, newPassword) {
    return api.post('/auth/reset-password', { token, new_password: newPassword })
  }
}
