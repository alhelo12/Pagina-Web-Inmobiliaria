/**
 * API: Autenticación
 * Cubre: login, registro de cliente, perfil actual,
 *        cambio de contraseña, validaciones.
 */
import api from './axios'

export const authApi = {
  /** Login — devuelve { access_token, token_type } */
  login(email, password) {
    // El backend espera multipart/form-data (OAuth2PasswordRequestForm)
    const form = new URLSearchParams()
    form.append('username', email)
    form.append('password', password)
    return api.post('/auth/login', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
  },

  /** Registro público de cliente */
  registerClient(data) {
    return api.post('/auth/register/client', data)
  },

  /** Perfil del usuario autenticado */
  me() {
    return api.get('/auth/me')
  },

  /** Cambio de contraseña */
  changePassword(currentPassword, newPassword) {
    return api.post('/auth/change-password', {
      current_password: currentPassword,
      new_password:     newPassword
    })
  },

  /** Verificar disponibilidad de email (POST, no GET) */
  checkEmail(email) {
    return api.post('/auth/check-email', { email })
  },

  /** Validar fortaleza de contraseña (POST) */
  validatePassword(password) {
    return api.post('/auth/validate-password', { password })
  }
}
