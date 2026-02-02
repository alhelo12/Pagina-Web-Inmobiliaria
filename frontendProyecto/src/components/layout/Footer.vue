<template>
  <footer class="footer">
    <div class="footer-container">

      <!-- BRAND -->
      <div class="brand">
        <h3>JAKEDA Inmobiliaria</h3>
        <p>
          Asesoría integral con respaldo jurídico para compra, venta y renta
          de inmuebles.
        </p>

        <!-- REDES -->
        <div class="socials">
          <a href="https://facebook.com" target="_blank" aria-label="Facebook">
            <i class="fab fa-facebook-f"></i>
          </a>
          <a href="https://instagram.com" target="_blank" aria-label="Instagram">
            <i class="fab fa-instagram"></i>
          </a>
          <a href="https://wa.me/5210000000000" target="_blank" aria-label="WhatsApp">
            <i class="fab fa-whatsapp"></i>
          </a>
          <a href="https://linkedin.com" target="_blank" aria-label="LinkedIn">
            <i class="fab fa-linkedin-in"></i>
          </a>
        </div>
      </div>

      <!-- LINKS -->
      <div class="links">
        <h4>Enlaces</h4>
        <ul>
          <li>Inicio</li>
          <li>Propiedades</li>
          <li>Servicios</li>
          <li>Contacto</li>
        </ul>
      </div>

      <!-- CONTACTO -->
      <div class="contact">
        <h4>Contacto</h4>
        <p><i class="fas fa-location-dot"></i> México</p>
        <p><i class="fas fa-phone"></i> 55 0000 0000</p>
        <p><i class="fas fa-envelope"></i> contacto@jakeda.com</p>
      </div>

    </div>

    <div class="footer-bottom">
      © 2025 JAKEDA Inmobiliaria
    </div>
  </footer>
</template>

<style scoped>
.footer {
  background: #0f2a44;
  color: white;
  padding: 3rem 1.5rem 1.5rem;
}

/* GRID CONTAINER */
.footer-container {
  max-width: 1200px;
  margin: auto;
  display: grid;
  grid-template-columns: 1fr;
  gap: 40px;
}

/* ANIMACIÓN */
.footer-container > div {
  opacity: 0;
  transform: translateY(30px);
  animation: fadeUp 0.8s ease forwards;
}

.footer-container > div:nth-child(2) {
  animation-delay: 0.2s;
}
.footer-container > div:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes fadeUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* BRAND */
.brand h3 {
  color: #facc15;
  margin-bottom: 0.5rem;
}

.brand p {
  font-size: 0.95rem;
  line-height: 1.6;
  opacity: 0.9;
}

/* LINKS & CONTACT */
.links h4,
.contact h4 {
  color: #facc15;
  margin-bottom: 0.6rem;
}

.links ul {
  list-style: none;
  padding: 0;
}

.links li {
  margin-bottom: 0.4rem;
  font-size: 0.9rem;
}

.contact p {
  font-size: 0.9rem;
  margin-bottom: 0.4rem;
}

/* REDES SOCIALES */
.socials {
  display: flex;
  gap: 14px;
  margin-top: 16px;
}

.socials a {
  width: 40px;
  height: 40px;
  background: #1e3a5f;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  color: white;
  font-size: 16px;
  transition: transform 0.2s, background 0.2s;
}

.socials a:hover {
  transform: translateY(-3px);
  background: #f59e0b;
}

/* FOOTER BOTTOM */
.footer-bottom {
  text-align: center;
  margin-top: 2rem;
  font-size: 0.8rem;
  opacity: 0.7;
  border-top: 1px solid rgba(255,255,255,.15);
  padding-top: 1rem;
}

/* 💻 DESKTOP */
@media (min-width: 768px) {
  .footer-container {
    grid-template-columns: 2fr 1fr 1fr;
  }
}

/* 📱 MOBILE */
@media (max-width: 768px) {
  .footer-container {
    text-align: center;
  }

  .socials {
    justify-content: center;
  }
}
</style>
