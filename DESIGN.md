---
name: JAKEDA Inmobiliaria
description: Plataforma inmobiliaria mexicana con acompañamiento integral, del catálogo moderado a la postventa.
colors:
  brass: "#b9945f"
  brass-deep: "#97773f"
  petrol: "#102d2d"
  ink: "#071b1c"
  ivory: "#f3eee4"
  ivory-deep: "#ece6d8"
  card: "#fffdf8"
  line: "#ddd5c3"
  muted: "#6b7268"
  charcoal: "#232a2a"
  error: "#991b1b"
typography:
  display:
    fontFamily: "'Cormorant Garamond', Georgia, serif"
    fontSize: "clamp(52px, 8.5vw, 116px)"
    fontWeight: 500
    lineHeight: 1.02
    letterSpacing: "-0.01em"
  headline:
    fontFamily: "'Cormorant Garamond', Georgia, serif"
    fontSize: "clamp(28px, 4vw, 56px)"
    fontWeight: 500
    lineHeight: 1.05
  body:
    fontFamily: "'Poppins', system-ui, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.8
  label:
    fontFamily: "'Poppins', system-ui, sans-serif"
    fontSize: "11px"
    fontWeight: 700
    letterSpacing: "0.18em"
rounded:
  sharp: "0px"
  card: "12px"
  field: "8px"
  action: "7px"
  pill: "999px"
spacing:
  container: "1280px"
  pad: "clamp(16px, 3vw, 32px)"
  grid-gap: "16px"
components:
  button-brass:
    backgroundColor: "{colors.brass}"
    textColor: "#ffffff"
    rounded: "{rounded.sharp}"
    padding: "14px 26px"
  button-brass-hover:
    backgroundColor: "{colors.brass-deep}"
    textColor: "#ffffff"
    rounded: "{rounded.sharp}"
    padding: "14px 26px"
  button-ink:
    backgroundColor: "{colors.petrol}"
    textColor: "#ffffff"
    rounded: "{rounded.sharp}"
    padding: "14px 22px"
  button-ghost:
    backgroundColor: "transparent"
    textColor: "#ffffff"
    rounded: "{rounded.sharp}"
    padding: "14px 26px"
  input-underline:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    rounded: "{rounded.sharp}"
  card-flat:
    backgroundColor: "{colors.card}"
    textColor: "{colors.ink}"
    rounded: "{rounded.card}"
    padding: "16px"
---

# Design System: JAKEDA Inmobiliaria

## Overview

**Creative North Star: "The Accompanied House"**

La casa nunca se vende sola; el sistema acompaña cada paso. JAKEDA se ve como una asesoría bien llevada con ojo cinematográfico: marketing fotográfico a pantalla completa donde la arquitectura es protagonista, y paneles de trabajo serenos sobre marfil donde cada dato respira. La voz es cálida y confiable, nunca ruidosa; el latón aparece solo en momentos decisivos —un CTA, un estado activo, una métrica— porque su rareza es el punto.

El sistema vive en dos mundos con una sola identidad: tinta de selva profunda para navegación y superficies de autoridad, papel de casa cálido para contenido, y oro tranquilo como único acento. Nada brilla sin motivo y nada grita.

**Key Characteristics:**
- Editorial cinematográfico en público, serenidad operativa en privado.
- Un solo acento (latón); todo lo demás es tinta, marfil y línea.
- Tipografía con contraste extremo: serif expresiva para display, sans geométrica para interfaz.
- Capas suaves: la profundidad se siente en la atmósfera, no en sombras duras.

## Colors

Un acento cálido sobre un mundo tinta-marfil; la paleta nunca cambia de temperatura a mitad de página.

### Primary
- **Oro Tranquilo** (#b9945f): El único acento. CTAs primarios, estados activos, reglas de énfasis, numerales destacados y detalles de marca. Su rareza es el punto.

### Neutral
- **Tinta de Selva** (#102d2d): Superficies de autoridad —navegación sólida, sidebars de workspace, botones de acción principal, overlays fotográficos.
- **Tinta Profunda** (#071b1c): Texto principal, footer, fondos de máxima profundidad.
- **Papel de Casa** (#f3eee4): Fondo de contenido en claro; la página respira sobre marfil, nunca sobre blanco puro.
- **Marfil Hondo** (#ece6d8): Superficie secundaria —fondos de métricas, filas alternas, pozos de imagen.
- **Tarjeta** (#fffdf8): Superficie elevada en claro, apenas más luminosa que el fondo.
- **Línea** (#ddd5c3): Divisores, bordes de tarjeta y reglas editoriales; siempre fina (1px).
- **Gris Salvia** (#6b7268): Texto secundario y descripciones.
- **Carbón** (#232a2a): Texto de apoyo en contextos densos.
- **Rojo Tierra** (#991b1b): Solo errores y acciones destructivas confirmadas.

### Named Rules (optional, powerful)
**The One Voice Rule.** El latón se usa en ≤10% de cualquier pantalla. Si todo brilla, nada brilla.
**The Warm Lock Rule.** Nunca mezclar grises fríos con la escala cálida marfil-línea-salvia; todos los neutros llevan el mismo matiz cálido.

## Typography

**Display Font:** Cormorant Garamond (con Georgia, serif)
**Body Font:** Poppins (con system-ui, sans-serif)

**Character:** Contraste deliberado entre una serif editorial de alto contraste para momentos de persuasión y una sans geométrica contenida para todo lo operativo. La serif nunca aparece en datos densos; la sans nunca protagoniza un hero.

### Hierarchy
- **Display** (500, clamp(52px, 8.5vw, 116px), 1.02): Solo heroes y portadas. Alineado a la izquierda sobre fotografía, máximo 2 líneas.
- **Headline** (500, clamp(28px, 4vw, 56px), 1.05): Títulos de sección y de página en claro y en paneles.
- **Body** (400, 0.875rem, 1.8): Texto corrido y descripciones; párrafos con ancho cómodo de lectura.
- **Label** (700, 11px, 0.18em, uppercase): Eyebrows, etiquetas de campo, encabezados de tabla y estados. Siempre mayúsculas con tracking amplio.

### Named Rules (optional)
**The Two-Voice Rule.** Serif persuade, sans opera. Ninguna pantalla mezcla ambas voces en el mismo nivel jerárquico.

## Layout

Modelo editorial con contenedor máximo de 1280px y padding fluido (clamp(16px, 3vw, 32px)). Ritmo de grilla base de 16px; catálogos en 3/2/1 columnas, dashboards en filas de métricas divididas por reglas finas en lugar de tarjetas separadas. En marketing se permite asimetría editorial (bloques 7/5, elementos desplazados); en workspaces, disciplina estricta de una columna por debajo de 768px y navegación que colapsa a bloque superior bajo 900px. El hero habita el primer viewport completo (min-height 100dvh) con la navegación superpuesta transparente; el resto de las páginas reserva el espacio bajo la barra sólida de 72px.

## Elevation & Depth

El sistema usa capas suaves: la profundidad se construye con atmósfera —overlays tinta sobre fotografía, superficies marfil escalonadas y sombras ambientales tenues— en lugar de elevaciones duras.

### Shadow Vocabulary (if applicable)
- **Suave ambiental** (`box-shadow: 0 18px 45px rgba(7, 27, 28, 0.12)`): Respiración bajo paneles y tarjetas en claro.
- **Fuerte de capa** (`box-shadow: 0 20px 50px rgba(16, 45, 45, 0.18)`): Modales, dropdowns y elementos flotantes; reservada a overlays, nunca a contenido en flujo.

### Named Rules (optional)
**The Atmosphere Rule.** La profundidad se siente, no se ve: primero overlay y tono, la sombra es el último recurso y siempre teñida de tinta.

## Shapes

Lenguaje de forma dual y disciplinado: lo decisivo es recto, lo contenedor es suave. CTAs primarios, navegación y divisores usan radio 0 —la nitidez comunica decisión. Tarjetas y paneles usan 12px, campos y controles pequeños 8px, acciones de tabla 7px. Filtros, etiquetas y contadores usan pastilla completa (999px); avatares y spinners son círculos (50%). Los estados (aprobada, pendiente, vendida) son texto en mayúsculas con un punto de 6px del color actual, nunca pastillas sólidas.

## Components

### Buttons
- **Shape:** Recto (0px); el filo es la firma del sistema.
- **Primary:** Oro Tranquilo con texto blanco, padding 14px 26px, etiquetas en mayúsculas 12px con tracking amplio.
- **Hover / Focus:** Fondo a latón profundo con elevación de 1px; `:active` con presión física (translateY + escala 0.99); foco visible con anillo latón de 2px.
- **Secondary / Ghost / Tertiary (if applicable):** Fantasma claro (borde marfil translúcido sobre fotografía) y sólido tinta (botón principal en superficies claras).

### Chips (if used)
- **Style:** Fondo transparente o marfil hondo, texto salvia, borde fino de línea en pastilla.
- **State:** Activo en sólido tinta con texto marfil; nunca compiten con el CTA primario.

### Cards / Containers
- **Corner Style:** 12px suaves.
- **Background:** Tarjeta (#fffdf8) sobre fondo marfil; imagen full-bleed con overlay tinta en catálogo.
- **Shadow Strategy:** Suave ambiental; ver Elevation.
- **Border:** 1px de línea (#ddd5c3) siempre presente en claro.
- **Internal Padding:** Escala 16px base; paneles densos hasta 30px.

### Inputs / Fields
- **Style:** Subrayado editorial —fondo transparente, sin bordes laterales, solo regla inferior de línea; radio 0.
- **Focus:** La regla inferior cambia a tinta de selva; sin resplandores.
- **Error / Disabled:** Mensaje en Rojo Tierra bajo el campo; deshabilitado en salvia sin contraste fingido.

### Navigation
- **Style, typography, default/hover/active states, mobile treatment.** Barra fija de 72px: transparente con texto marfil sobre heroes, sólida marfil con texto tinta en el resto (la transparencia vive solo en inicio). Enlaces en mayúsculas 11px con tracking 0.18em; subrayado latón de 1px que crece al hover; activo en latón. Botón de acceso en outline. En móvil (<900px), menú hamburguesa a panel sólido tinta apilado.

### Metric Row
Fila de métricas dividida por reglas finas (no tarjetas separadas): numeral grande en serif, etiqueta small-caps encima, contexto en salvia debajo.

## Do's and Don'ts

### Do:
- **Do** reservar el latón a momentos decisivos (CTA, activo, métrica clave).
- **Do** alinear display serif a la izquierda sobre fotografía con overlay tinta legible.
- **Do** usar reglas de 1px en línea (#ddd5c3) para dividir en lugar de encajonar.
- **Do** expresar estados como texto en mayúsculas con punto de 6px.
- **Do** mantener una sola columna bajo 768px con acciones táctiles de ≥44px.

### Don't:
- **Don't** usar degradados morados/azules, brillos neón ni ninguna estética AI genérica.
- **Don't** poner CTA primario redondeado o con sombra dura.
- **Don't** centrar headlines simétricos en cada sección; variar la composición.
- **Don't** mezclar grises fríos en la escala cálida marfil.
- **Don't** usar el hero para más de 4 elementos de texto (etiqueta, titular, apoyo, CTAs).
