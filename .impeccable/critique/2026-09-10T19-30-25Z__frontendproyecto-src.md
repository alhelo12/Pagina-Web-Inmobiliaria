---
target: frontend rediseñado (frontendProyecto/src)
total_score: 20
max_score: 40
na_heuristics: 
p0_count: 2
p1_count: 2
timestamp: 2026-09-10T19-30-25Z
slug: frontendproyecto-src
---
# Critique — frontend rediseñado (frontendProyecto/src)

## Design Health Score

| # | Heuristic | Score | Key Issue |
|---|-----------|-------|-----------|
| 1 | Visibility of System Status | 2 | Favorito invitado silencioso; sin estado offline en chat |
| 2 | Match System / Real World | 2 | Wizard sin acentos; jerga "Tomar"; tab Fachada = square_meters |
| 3 | User Control and Freedom | 2 | Autoplay sin pausa; blur de ciudad borra datos |
| 4 | Consistency and Standards | 1 | Dos geometrías; Georgia vs Cormorant; pills vs texto; dos homes admin |
| 5 | Error Prevention | 3 | Mejor heurística; validación por paso; resta borrado silencioso |
| 6 | Recognition Rather Than Recall | 2 | Búsqueda solo-placeholder; avatares de una inicial |
| 7 | Flexibility and Efficiency | 1 | Sin búsquedas guardadas, bulk ni teclado; reset fuerza reescribir |
| 8 | Aesthetic and Minimalist Design | 2 | Hero con 7 interactivos; dashboard denso |
| 9 | Error Recovery | 2 | Retry/empty bien; wizard con alerta única arriba |
| 10 | Help and Documentation | 1 | Sin onboarding ni explicadores; copy de asesor mal dirigido |
| **Total** | | **20/40** | **Acceptable** |

## Design Specificity Verdict

**Veredicto: piel art-directed sobre esqueleto intercambiable (~65% propio).** Coherente en marketing (tinta/marfil/latón, Cormorant izquierda, reglas finas, grilla asimétrica, contact-card sticky). Genérico debajo: landing estándar premium-real-estate, workspaces SaaS redondeados que contradicen la regla dual de formas, y el diferenciador (moderación humana) sin un solo píxel público.

**Scan determinista:** 7 warnings, 0 fallos. 6 side-tab son marcadores de estado intencionales (no-leído/pendiente/alerta) — exentos con nota. 1 bounce-easing es falso positivo defendido (keyframes solo scale/opacity con ease-in-out; solo el nombre dice "bounce").

**Overlays en vivo (build actual):** texto de logo a 9px bajo el piso, chip-eyebrow sobre el H1, botón BUSCAR blanco-sobre-latón 2.8:1 (real: estilo scoped que el fix global no alcanzó), kickers repetidos ×3, líneas de ~85 caracteres.

## Overall Impression

El sistema de piel más sólido hasta ahora; los finales más débiles. Publicar termina en redirect arrancado, contactar en salto a chat sin ceremonia, catálogo en "nada". La mayor oportunidad: darle píxeles al foso (moderación y reserva de visita).

## What's Working

1. **Profundidad por atmósfera.** Overlays duales + Cormorant abajo-izquierda + eyebrow latón; legibilidad óptica, no sombras duras. La firma del sistema.
2. **Jerarquía del detalle.** Price-card con regla latón → specs → descripción → mapa → contact-card sticky: único operate que raciona bien el latón.
3. **Modelo de fotos del wizard.** Subida una-a-una con orden elegible + insignia Principal + compresión WebP invisible: control percibido con craft oculto.

## Priority Issues

- **[P0] Señales de confianza fabricadas** (HomeView rating-card 4.9/5 + teléfono). Viola PRODUCT.md y el principio #2. **Fix:** quitar o reemplazar por promesa de moderación verificable. **Suggested command:** `/impeccable clarify`
- **[P0] Agujero del funnel: sin reserva de visita** (PropertyDetailView solo abre chat). El paso `visitar (cita)` nunca aparece en el punto de decisión. **Fix:** captura de fecha/disponibilidad junto a Contactar, no en vez de. **Suggested command:** `/impeccable shape`
- **[P1] Favorito invitado silencioso** (PropertyCard toggle). El control más tocado enseña que está roto. **Fix:** redirigir a login con retorno a la propiedad. **Suggested command:** `/impeccable polish`
- **[P1] Hero sobrecargado + búsqueda frágil** (HomeView: 7 interactivos, ciudad free-text, hero rehén del último upload; overlay confirma BUSCAR con contraste 2.8:1). **Fix:** 1 CTA + búsqueda compacta, arte fijo, datalist cableado, BUSCAR a tinta-sobre-latón. **Suggested command:** `/impeccable layout`
- **[P2] Deriva de consistencia** (geometrías, Georgia vs Cormorant, pills vs texto+ punto, dos homes admin, kicker "Panel Admin" en ruta cliente, `:show-cta` vs `:showCta`). **Fix:** barrido de normalización a DESIGN.md. **Suggested command:** `/impeccable polish`

## Persona Red Flags

**Sam (dependiente de accesibilidad):** autoplay sin pausa ni guard de movimiento; lightbox sin foco atrapado ni `role=dialog`; mapa Leaflet sin teclado ni alternativa; `RouterLink` envolviendo `fav-btn` (interactivos anidados); thumbs con `aria-selected` sin tablist.
**Jordan (publica por primera vez):** kicker "Panel Admin" en su ruta; ciudad custom sin teclado que borra entradas; file inputs invisibles sin label; errores en alerta única arriba; éxito que redirige a los 1800ms sin folio ni timeline.
**Casey (móvil distraído):** hero 100dvh empuja resultados varios scrolls; chips glass sobre foto se lavan al sol; contacto bajo el fold; `take-btn` y `x` de error bajo 44px; menú móvil sin `aria-expanded`.

## Minor Observations

Enlace muerto `/favoritos` vs `/cliente/favoritos`; "Tuxtla Gutiérrez" vs "Tuxtla Gutierrez" (dos identidades); lista MEXICO_CITIES con estados, duplicados y typos; corazón `#d64545` fuera del token; header de PropertiesView centrado (spec: display izquierda); badges gold blanco-sobre-latón; CTA login que fusiona signup con publicar; filtros de chat apagados por defecto + chip gold vs spec petrol; skeletons en grises fríos; `console.log` de geocoding en producción; logo a 9px; kickers repetidos ×3.

## Questions to Consider

1. Si la moderación humana es el foso, ¿por qué ningún píxel público la muestra?
2. Si la venta no termina en el cierre, ¿qué se demote para darle casa a postventa?
3. ¿Qué cambiaría más allá del color si JAKEDA se comprometiera con materialidad Chiapas/Tuxtla?
