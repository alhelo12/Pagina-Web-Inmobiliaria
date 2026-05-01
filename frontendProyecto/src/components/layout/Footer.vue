<template>
  <footer class="footer">
    <div class="footer-container">
      <div class="brand">
        <h3>JAKEDA Inmobiliaria</h3>
        <p>
          Plataforma inmobiliaria con enfoque profesional para compra, venta,
          renta y administracion de propiedades.
        </p>
      </div>

      <div>
        <h4>Explorar</h4>
        <RouterLink to="/">Home</RouterLink>
        <RouterLink to="/servicios">Servicios</RouterLink>
        <RouterLink to="/propiedades">Proyectos</RouterLink>
        <RouterLink to="/contacto">Contacto</RouterLink>
      </div>

      <div>
        <h4>Contacto</h4>
        <p>Mexico</p>
        <p>55 0000 0000</p>
        <p>contacto@jakeda.com</p>
      </div>
    </div>

    <div class="footer-bottom">
      <span>© 2026 JAKEDA Inmobiliaria</span>
      <span>Diseno corporativo moderno</span>
    </div>
  </footer>
</template>

<script setup>
import { RouterLink } from 'vue-router'
</script>

<style scoped>
.footer {
  background:
    linear-gradient(90deg, rgba(7,23,45,.98), rgba(16,46,79,.96)),
    #07172d;
  color: white;
  padding: 64px 24px 24px;
}

.footer-container {
  max-width: 1180px;
  margin: auto;
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: 42px;
}

.brand h3,
h4 {
  color: #f2c46d;
  margin-bottom: 14px;
}

.brand h3 {
  font-family: Georgia, 'Times New Roman', serif;
  font-size: 28px;
}

p,
a {
  display: block;
  color: rgba(255,255,255,.74);
  line-height: 1.8;
  font-size: 14px;
}

a {
  transition: color .2s ease, transform .2s ease;
}

a:hover {
  color: #f2c46d;
  transform: translateX(3px);
}

.footer-bottom {
  max-width: 1180px;
  margin: 42px auto 0;
  padding-top: 18px;
  border-top: 1px solid rgba(255,255,255,.13);
  display: flex;
  justify-content: space-between;
  gap: 16px;
  color: rgba(255,255,255,.58);
  font-size: 13px;
}

@media (max-width: 760px) {
  .footer-container {
    grid-template-columns: 1fr;
  }
  .footer-bottom {
    flex-direction: column;
  }
}
</style>
