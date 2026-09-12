---
target: frontend rediseñado (frontendProyecto/src)
total_score: 20
max_score: 40
na_heuristics: 
p0_count: 1
p1_count: 2
timestamp: 2026-09-10T22-40-22Z
slug: frontendproyecto-src
---
# Critique re-run — frontend rediseñado (frontendProyecto/src)

## Design Health Score

| # | Heuristic | Score | Key Issue |
|---|-----------|-------|-----------|
| 1 | Visibility of System Status | 2 | Sin feedback en búsqueda home; take sin estado por fila |
| 2 | Match System / Real World | 3 | Fuerte es-MX; resta fecha cruda y ruta `/client` fugada |
| 3 | User Control and Freedom | 2 | Sin undo de favorito; sin cancelar/reprogramar junto a booking |
| 4 | Consistency and Standards | 1 | Georgia residual; pills vs texto; `/cliente` vs `/client` |
| 5 | Error Prevention | 2 | Horas fijas admiten pasado-hoy; ciudad free-text garantiza error tardío |
| 6 | Recognition Rather Than Recall | 2 | Acciones advisor sin verbo inline; hilos sin contexto de propiedad |
| 7 | Flexibility and Efficiency | 2 | Sin guardados, bulk ni atajos; un Asignarme por fila |
| 8 | Aesthetic and Minimalist Design | 3 | Mejor eje; resta triple uso de destacadas en home |
| 9 | Error Recovery | 2 | Dashboards sin retry; uploads agregados sin reintento |
| 10 | Help and Documentation | 1 | Sin ETA de moderación, sin política de reserva, sin SLA de chat |
| **Total** | | **20/40** | **Acceptable** |

## Design Specificity Verdict

**LLM:** A medio camino de intercambiable a propio. El foso declarado (moderación en 3 pasos, honesto) pero sin recibos; booking cableado pero sin ceremonia; barrido parcial (dos tipografías, dos lenguajes de estado y tres radios conviven).

**Deterministic scan:** 1 warning, 0 fallos — `bounce-easing` falso positivo defendido (keyframes solo scale/opacity con ease-in-out). Side-tabs: 0 (eliminados).

**Overlays en vivo (build fresco):** 3 hallazgos — contraste 1.2:1 blanco-sobre-marfil (localizar; posible elemento sobre foto clara), chip-eyebrow sobre H1 (patrón aceptado, anotado), fondo crema (marca comprometida, no violación). BUSCAR, kickers ×3 y líneas largas: resueltos.

## Overall Impression

El esqueleto ya es JAKEDA; lo que falta es hospitalidad en los picos de ansiedad (publicar, reservar) y terminar el barrido (tipografía, estados, ruta). La mayor oportunidad sigue siendo darle recibos al foso.

## What's Working

1. Split editorial-operativo real y disciplinado en el path inspeccionado.
2. Copy de confianza honesto (moderación en 3 pasos, gate de email, pending).
3. Hardening estructural (trampa de foco, autoplay con pausa, errores anclados, retry, 44px).

## Priority Issues

- **[P0] Ruta de contacto rota** (PropertyDetailView.vue:243 → `/client/mensajes`; no existe ruta `/client`). **Fix:** unificar a `/cliente|/advisor/mensajes` según rol. **Suggested command:** `/impeccable polish`
- **[P1] Pills de estado en detalle** (PropertyDetailView.vue:711-737) vs texto+punto del resto. **Fix:** tratamiento dot 6px. **Suggested command:** `/impeccable polish`
- **[P1] Booking sin ceremonia** (sin identidad del asesor, duración, SLA, fecha localizada, disponibilidad ni cancelación). **Fix:** bloque de confirmación con resumen. **Suggested command:** `/impeccable shape`
- **[P2] Georgia residual** (15+ declaraciones en shells admin/advisor). **Fix:** `var(--serif)`. **Suggested command:** `/impeccable polish`
- **[P2] Éxito de publicación abandona** (redirect 1.8s sin ETA ni next-steps). **Fix:** tarjeta persistente con enlaces. **Suggested command:** `/impeccable clarify`

## Persona Red Flags

**Jordan (compra):** búsqueda sin feedback; pills duplicadas sobre foto; hora fija que admite pasado-hoy; éxito con fecha cruda.
**Sam (vende):** ciudad que conserva texto inválido y bloquea; "Principal" implícito sin control; éxito sin ETA que lo arranca; dashboard que oculta estados.
**Casey (asesor):** 6 métricas sin verbos; filas sin acción inline; Asignarme sin estado por fila y lista que se desactualiza; panel de relación con vacíos hardcodeados.

## Minor Observations

Subtítulo con declaración muerta; convención showCta mixta; geo-fence silencioso a Tuxtla; tab que mezcla conteo con fotos; login con dos primarias iguales; dropdown sin Esc/foco; aria-describedby permanente; lógica mobile-hide a verificar; `/cliente/citas` para advisors sin recovery.

## Questions to Consider

1. ¿Por qué ninguna superficie guest muestra recibos de moderación si es el foso?
2. ¿Por qué la visita —lo más acompañado— tiene menos hospitalidad que el lightbox?
3. ¿Qué le pide el dashboard al asesor en 10 minutos entre visitas?
