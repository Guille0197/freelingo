# Validación de la propuesta

## Comprobado localmente

- Entorno reconstruido con scripts/bootstrap.sh y las versiones exactas de scripts/toolchain.env,
  sin modificar dependencias ni lockfiles.
- scripts/format.sh: correcto; Ruff, Black, ESLint y Prettier mediante las herramientas locales.
- Backend dirigido: 173 pruebas correctas sobre OpenRouter/configuración personal, adaptador LLM,
  autenticación y ejercicios. Esta ejecución precedió a las dos pruebas finales de invitaciones.
- Backend completo: 2350 correctas, 26 omitidas; cobertura 89.24 %, superior al umbral del 70 %.
  La suite completa incluye las pruebas de invitaciones. Las omitidas son variantes PostgreSQL de
  ciclo de analítica, concurrencia de juegos y recompensas; no había PostgreSQL de integración.
- Frontend: ESLint y TypeScript correctos; 103 archivos y 1436 pruebas correctas con Vitest.
- Frontend de producción: compilación Webpack correcta con NEXT_PUBLIC_ENGLISH_ONLY=true y los
  catálogos copiados temporalmente a frontend/messages, como hace el Dockerfile. La copia temporal se
  eliminó después de comprobar que coincidía exactamente con los originales.
- YAML de los tres Compose analizado correctamente. Se comprobó la topología personal de cuatro
  servicios, builds desde código, healthchecks, reinicio, logs acotados, ausencia de puertos publicados
  y bases solo en la red interna. Redis conserva el formato de snapshots existente.
- git diff --check correcto.

Las pruebas del backend utilizan SQLite y dobles de Redis/proveedores. No representan un despliegue
real de PostgreSQL, Redis o servicios externos. Se observaron advertencias de deprecación heredadas.

## Límites encontrados

El primer build local falló por acceso de red a Google Fonts y por no tener la copia de catálogos que
normalmente prepara Docker. Después de preparar esa copia, Turbopack no pudo abrir un puerto interno
por restricciones del entorno. La compilación con Webpack y acceso de red terminó correctamente,
con advertencias existentes de middleware y dependencias WASM/VAD. Esto no equivale a haber construido
las imágenes Docker ni a haber probado el bundler Turbopack en la VM.

## Pendiente en Dokploy

- Validación efectiva de interpolación/compatibilidad con Docker Compose y Preview Compose.
- Build de las imágenes Linux y arranque completo del backend con migraciones y bases reales.
- Migraciones sobre una copia de los datos existentes y aceptación de persistencia tras reinicio.
- Dominio, resolver TLS, redes y enrutamiento WebSocket con el proxy real de Dokploy.
- Login/refresh/logout y acceso privado en navegador sobre HTTPS.
- Conversación OpenRouter, calidad educativa y reconocimiento/reproducción de voz con credenciales
  reales. No se disponía de claves de prueba y no se realizaron llamadas pagadas.
- Medición de RAM, almacenamiento y picos de compilación en VM 105.

No se aplicaron migraciones en servidores, no se borraron datos ni volúmenes y no se modificó Proxmox.
La lista de aceptación y los procedimientos operativos están en dokploy.md.
