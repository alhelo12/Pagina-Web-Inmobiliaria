<template>
  <section class="nosotros">
    <div class="contenido">
      <h1 class="animar">JAKEDA <span>Inmobiliaria</span></h1>

      <p class="funcion animar">
        <strong>Función principal:</strong>
        Brindar un servicio profesional que combine experiencia inmobiliaria y respaldo jurídico,
        asegurando que cada operación de compraventa o arrendamiento se realice dentro del marco
        legal y con plena seguridad para nuestros clientes.
      </p>

      <div class="bloque animar">
        <h2>Misión</h2>
        <p>
          Ofrecer soluciones inmobiliarias confiables, transparentes y seguras, garantizando la
          protección del patrimonio de nuestros clientes mediante un acompañamiento legal especializado.
        </p>
      </div>

      <div class="bloque animar">
        <h2>Visión</h2>
        <p>
          Consolidarnos como una inmobiliaria joven para todas aquellas personas que deseen vender o
          rentar, reconocida por su profesionalismo, ética y seguridad jurídica, siendo la primera
          opción para quienes buscan asesoría integral en el sector inmobiliario.
        </p>
      </div>

      <!-- MÉTRICAS -->
      <div class="metricas">
        <div class="item animar">
          <span class="numero">{{ seguridad }}%</span>
          <p>Seguridad Jurídica</p>
        </div>

        <div class="item animar">
          <span class="numero">+{{ clientes }}</span>
          <p>Clientes Satisfechos</p>
        </div>

        <div class="item animar">
          <span class="numero">{{ transparencia }}%</span>
          <p>Transparencia</p>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'NosotrosView',
  data() {
    return {
      seguridad: 0,
      clientes: 0,
      transparencia: 0,
      animado: false
    }
  },
  mounted() {
    const elementos = document.querySelectorAll('.animar')

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible')

            if (!this.animado) {
              this.animarContadores()
              this.animado = true
            }
          }
        })
      },
      { threshold: 0.3 }
    )

    elementos.forEach(el => observer.observe(el))
  },
  methods: {
    animarContadores() {
      const intervalo = setInterval(() => {
        if (this.seguridad < 100) this.seguridad++
        if (this.clientes < 50) this.clientes++
        if (this.transparencia < 100) this.transparencia++

        if (
          this.seguridad === 100 &&
          this.clientes === 50 &&
          this.transparencia === 100
        ) {
          clearInterval(intervalo)
        }
      }, 20)
    }
  }
}
</script>

<style scoped>

.nosotros {
  background: linear-gradient(180deg, #f7f9fc, #ffffff);
  padding: 90px 20px;
}

.contenido {
  max-width: 1100px;
  margin: auto;
}

/* TITULO */
h1 {
  font-size: 44px;
  font-weight: 700;
  color: #0a2a66;
  margin-bottom: 30px;
}

h1 span {
  color: #cfa335;
}

/* TEXTO */
.funcion {
  font-size: 16px;
  color: #5f6f88;
  margin-bottom: 45px;
}

.bloque {
  margin-bottom: 35px;
}

h2 {
  color: #0a2a66;
  margin-bottom: 10px;
}

p {
  line-height: 1.8;
  color: #5f6f88;
}

/* MÉTRICAS */
.metricas {
  display: flex;
  justify-content: space-between;
  margin-top: 80px;
  text-align: center;
  flex-wrap: wrap;
}

.item {
  flex: 1;
  min-width: 220px;
  padding: 20px;
}

.numero {
  font-size: 42px;
  font-weight: 700;
  color: #cfa335;
  display: block;
}

.item p {
  margin-top: 10px;
  font-weight: 500;
}

/* ANIMACIONES */
.animar {
  opacity: 0;
  transform: translateY(25px);
  transition: all 0.9s ease;
}

.animar.visible {
  opacity: 1;
  transform: translateY(0);
}
</style>
