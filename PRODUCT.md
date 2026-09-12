# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

JAKEDA es una plataforma de tres lados donde ningún rol es secundario: cliente, asesor y administrador tienen la misma importancia.

- **Cliente:** persona en México que busca comprar o rentar vivienda, publica sus propias propiedades, guarda favoritas, agenda visitas o inspecciones, conversa con asesores y responde encuestas postventa.
- **Asesor:** agente inmobiliario que gestiona inventario asignado (aprueba, rechaza, marca vendidas, reclama disponibles), atiende citas, conversa con clientes, administra su cartera y ejecuta seguimientos postventa.
- **Administrador:** quien modera todo el inventario de la plataforma, gestiona usuarios de los tres roles y supervisa la operación.

## Product Purpose

Plataforma inmobiliaria integral que acompaña la transacción completa: publicación moderada de propiedades, descubrimiento y contacto, agendamiento de visitas, comunicación en tiempo real y seguimiento postventa, todo en una sola aplicación instalable (PWA). El éxito es cerrar operaciones con confianza y mantener la relación después de la venta.

## Positioning

Acompañamiento integral, no portal de anuncios: inventario moderado por humanos (flujo pendiente → aprobado/rechazado/vendido), chat directo cliente-asesor en tiempo real y seguimiento postventa estructurado dentro de la misma app. Un portal genérico vecino no podría copiar verazmente la combinación de moderación + conversación + postventa en un solo flujo.

## Operating Context

- Flujo principal: publicar → moderar → visitar (cita) → cerrar → seguimiento postventa.
- Entornos: navegadores de escritorio y móvil; PWA instalable en ambos. La web móvil sigue siendo `web`.
- Sesiones JWT con expiración; layouts y permisos separados por rol.
- Mapas Leaflet para ubicación de propiedades; notificaciones y chat por WebSocket unificado (`/ws` con subprotocolo `bearer.<JWT>`).
- Idioma de producto: español (México).

## Capabilities and Constraints

Capacidades confirmadas: catálogo público solo con propiedades aprobadas; publicación y edición de propiedades con imágenes; favoritos; citas (visita/inspección) con confirmación y cancelación; chat en tiempo real; notificaciones y preferencias; postventa con encuestas y seguimiento; formulario público de contacto; administración de propiedades, usuarios y asignaciones cliente-asesor.

Restricciones técnicas confirmadas: auth JWT HS256; layouts/vistas separados por rol (`client/`, `advisor/`, `admin/`); enums del sistema con fuente de verdad en backend (`GET /constants`); un solo WebSocket gestionado por `useWebSocket.js`; migraciones Alembic como única vía de esquema; no subir `.env` ni secretos.

Hechos deliberadamente no decididos: ninguno pendiente a nivel producto; las decisiones abiertas futuras se registran aquí cuando aparezcan.

## Brand Commitments

Nombre: JAKEDA Inmobiliaria (wordmark "JAKEDA / REAL ESTATE"). Voz del producto en español (México). Sin otros compromisos de identidad confirmados en este registro.

## Evidence on Hand

- `README.md`: stack, arquitectura, instalación y variables de entorno.
- `AGENTS.md`: convenciones de trabajo (roles, enums, WebSocket, commits).
- Código y rutas reales en `backend/app/` y `frontendProyecto/src/`.
- Ausencias que el trabajo futuro no debe fabricar: no hay testimonios, clientes nombrados, métricas públicas, precios ni claims de despliegue confirmados.

## Product Principles

1. Los tres roles son ciudadanos de primera clase; ningún flujo sacrifica a uno por otro.
2. La confianza se construye con moderación humana, no con volumen de anuncios.
3. La venta no termina en el cierre: la postventa es parte del producto.
4. México y español primero; cada decisión de contenido y formato pasa por ese filtro.
