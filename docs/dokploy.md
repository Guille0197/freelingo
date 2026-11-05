# FreeLingo personal: inglés en Dokploy

Esta variante usa cuatro contenedores: Next.js, FastAPI, PostgreSQL 16 y Redis 7. Compila el frontend
y backend del fork; no utiliza imágenes precompiladas de artcc ni modelos locales ni GPU.
El texto usa OpenRouter; STT/TTS usan los adaptadores externos OpenAI existentes.

## Preparar VM 105 sin modificar Proxmox

En Ubuntu revisa `free -h`, `lsblk`, `df -h` y el almacenamiento mostrado por Dokploy. Los 12 GB de RAM
y 100 GB de disco configurados en Proxmox no demuestran la memoria reconocida ni el tamaño del sistema
de archivos. Si falta espacio, resuélvelo por separado antes de compilar; este proyecto no modifica
particiones, volúmenes ni recursos de Proxmox.

Usa Docker Compose en Dokploy, no Docker Stack/Swarm: este último no compila directivas build.
Reserva espacio para una compilación y una versión anterior. No asignes límites de RAM hasta medir.

## Instalación

1. Crea un proyecto y un servicio Docker Compose con origen GitHub `Guille0197/freelingo`.
   Selecciona `feat/english-only-dokploy` para revisar esta propuesta, o la rama aprobada después de
   integrarla. Ruta del archivo: `docker-compose.dokploy.yml`.
2. Copia `.env.dokploy.example` a Environment de Dokploy y completa los campos vacíos. No pegues
   secretos en Git ni en capturas. Genera PostgreSQL, Redis y SECRET_KEY de forma independiente con
   `openssl rand -hex 32`. Los passwords deben ser hexadecimales o estar codificados para URLs; el
   Compose construye DATABASE_URL/REDIS_URL. No cambies credenciales existentes sin rotarlas en el servicio.
3. Configura un dominio que resuelva al proxy de Dokploy. APP_HOST es solo el host, sin https ni ruta.
   Este Compose incluye etiquetas Traefik: no añadas rutas duplicadas en Domains. Usa un ROUTER_PREFIX
   único y comprueba el nombre real del resolver TLS; el valor habitual es letsencrypt.
4. Usa la red externa `dokploy-network` existente de Dokploy. No actives Isolated Deployments sobre
   este archivo sin adaptar sus etiquetas y redes. Las bases solo están en la red interna `data`;
   frontend/backend comparten `app` y se conectan al proxy. No hay puertos publicados en el host.
5. Revisa Preview Compose. Frontend/backend deben conservar ambas redes; postgres/redis nunca deben
   recibir dokploy-network ni puertos públicos. Despliega. La primera compilación descarga dependencias.
6. Backend espera a las bases saludables. FastAPI aplica las migraciones ya versionadas durante su
   arranque. El Compose evita ejecutarlas otra vez en el comando. Mantén un worker inicialmente.
7. En la terminal del contenedor backend ejecuta `python -m app.create_private_invite`. Solo funciona
   con cero usuarios, registro cerrado y primer usuario administrador habilitado. Genera una invitación
   de un uso que caduca a los 15 minutos. Ábrela en HTTPS, regístrate y guarda tus credenciales. El
   registro público permanece cerrado. Si ya hay usuarios, inicia sesión con tu cuenta y usa las
   invitaciones de administración. El enlace temporal es un secreto.
8. En perfil selecciona español como idioma nativo, inglés US si deseas esa variante y objetivo trabajo.
   La interfaz empieza en español; cookies o preferencias existentes conservan su idioma. El valor
   predeterminado de aprendizaje sigue siendo en-GB; en-US se puede elegir sin migrar datos automáticamente.
9. Completa la evaluación y crea un plan A2/B1 hacia B2/C1. El plan y las seis competencias existentes
   se conservan. En el tutor puedes pedir entrevistas, daily standups, code reviews, reuniones con
   clientes o explicaciones de arquitecturas. El tutor adapta la dificultad y permite aclaraciones
   breves en español. No es un servicio de generación de código.

## HTTPS y voz

Traefik dirige `/ws/` al backend:8000 con prioridad 100 y las demás rutas al frontend:3000.
No elimina el prefijo. El cliente deriva `wss://APP_HOST/ws/conversation` del origen; no hace falta
NEXT_PUBLIC_API_URL. Las rutas HTTP `/api/*` pasan por Next.js al backend. El micrófono requiere HTTPS.
HTTP redirige a HTTPS y las cookies de renovación usan Secure/HttpOnly/SameSite=Lax.

No uses una clave OpenRouter como OPENAI_API_KEY. Las claves se inyectan exclusivamente al backend.
El modelo OpenRouter se selecciona en ejecución, sin recompilar. Necesita Chat Completions, streaming
y respuestas JSON fiables; las herramientas son opcionales y el adaptador conserva su fallback.
Consulta modelos y precios actuales en [OpenRouter](https://openrouter.ai/models); no se presupone que
un ID DeepSeek o Qwen esté siempre disponible. Revisa también su ventana de contexto; esta integración
no aplica un presupuesto automático de tokens por petición.

Los ejercicios de repetición comparan la transcripción con una frase. No miden fonemas, acento,
entonación ni pronunciación acústica. Los prompts y el feedback de respaldo declaran esta limitación.

## Variables del despliegue

Todas las variables aceptadas por este Compose están en `.env.dokploy.example`:

- APP_HOST: dominio único; también fija APP_BASE_URL y CORS al origen HTTPS exacto.
- ROUTER_PREFIX: prefijo único para rutas/servicios Traefik. TRAEFIK_CERT_RESOLVER: resolver ya
  configurado en tu Dokploy; no instala certificados ni cambia el proxy por fuera de sus rutas.
- DATA_PATH: ruta absoluta y estable de la VM para datos. Debe existir en disco persistente con
  permisos para PostgreSQL, Redis y backend. No uses una carpeta temporal del checkout de Dokploy.
- POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD: base y credenciales. Los dos primeros por defecto
  son freelingo. Conserva los valores previos si conectas almacenamiento existente.
- REDIS_PASSWORD: contraseña Redis; se usa también en su healthcheck sin argumentos visibles.
- SECRET_KEY: valor aleatorio de 32 caracteres como mínimo. Cambiarlo invalida tokens de acceso.
- OPENROUTER_API_KEY, OPENROUTER_MODEL: obligatorios para texto. OPENROUTER_BASE_URL por defecto
  https://openrouter.ai/api/v1, sin añadir /chat/completions. Usa solo un endpoint de confianza.
- OPENAI_API_KEY: clave independiente obligatoria para voz; OPENAI_TTS_MODEL, OPENAI_TTS_VOICE,
  OPENAI_TTS_SPEED y OPENAI_STT_MODEL permiten configurar los modelos/voz soportados por esa cuenta.
- UVICORN_WORKERS: 1 inicialmente; aumentar multiplica memoria y puede ejecutar migraciones en paralelo.
- EXERCISE_GENERATION_TIMEOUT_SECONDS: 600 por defecto; límite total para generación de recursos.
- LOG_LEVEL: INFO por defecto. No uses DEBUG permanentemente.

El archivo fija idiomas a en-GB/en-US, registro cerrado, cookies seguras, Stripe desactivado, pruebas
comerciales desactivadas, correo desactivado y analítica sin configuración. No hay suscripciones
necesarias cuando Stripe está desactivado. Se mantienen los límites de uso actuales para controlar
costes: consulta administración si necesitas ajustarlos; cambiar valores por defecto no modifica
automáticamente las cuotas de cuentas ya creadas.

El build del frontend fija NEXT_PUBLIC_ENGLISH_ONLY=true para limitar selectores y presentación.
Cambiar esta variable requiere compilar; UI_DEFAULT_LOCALE=es se configura en ejecución y respeta
la elección del usuario. Las claves de proveedor nunca son NEXT_PUBLIC_*.

Los proveedores anteriores siguen disponibles con LLM_PROVIDER en los Compose generales. La plantilla
Dokploy elige OpenRouter y OpenAI para mantener una configuración pequeña; usar otros proveedores
requiere adaptar explícitamente sus variables en esa plantilla.

## Datos existentes y almacenamiento

Antes de reutilizar una instalación: copia la base y los directorios persistentes. Conserva exactamente
DATA_PATH y POSTGRES_DB/USER/PASSWORD. Verifica que la carpeta postgres corresponde a PostgreSQL 16.
No ejecutes la instalación vieja y la nueva contra el mismo directorio PostgreSQL simultáneamente.
Detén la aplicación anterior de forma controlada antes de iniciar la nueva, sin eliminar sus datos.

Se reutilizan los bind mounts postgres, redis, avatars, audio y tts_previews. No hay migraciones nuevas
en esta propuesta ni conversión/borrado de idiomas. Los idiomas no ingleses antiguos siguen almacenados;
no se pueden añadir ni seleccionar nuevos fuera de la lista habilitada. Revisarlos o retirarlos es una
decisión separada; no borres sus filas manualmente ni cambies sus códigos para convertir su historial.

- Logs: json-file limita cada servicio a 3 archivos de 10 MB (aprox. 120 MB entre cuatro servicios).
- Imagen backend: compiladores quedan en una etapa de build, fuera de la imagen final.
- Contextos: .dockerignore excluye secretos, toolchains, caches, tests y artefactos de build. VAD se
  reconstruye desde las dependencias en el frontend, preservando los assets necesarios para hablar.
- Audio de lecciones: persiste y puede crecer. No lo borres por fecha: está referenciado desde la base.
- Cachés tour y previews: regenerables, pero esta versión no borra automáticamente archivos existentes.
  Revisa tamaño mensualmente en la VM y conserva solo cachés vigentes mediante mantenimiento
  planificado; cualquier limpieza debe excluir audio de lecciones, avatares y bases.
- Redis conserva el formato de snapshots RDB existente y guarda al apagarse de forma ordenada. Un
  apagado abrupto puede perder sesiones recientes; copiar o restaurar snapshots tampoco garantiza
  que todos los tokens sigan siendo válidos. No se cambia automáticamente a AOF sobre datos existentes.
- Conserva la versión anterior de las imágenes y su caché de build hasta terminar la aceptación.
  Limpia solo imágenes/cachés identificados y sin uso desde Dokploy. Nunca limpies volúmenes.

## Presupuesto de recursos: estimaciones, no mediciones

Para una sola persona, un worker y sin modelos locales:

- Frontend en ejecución: aproximadamente 150–400 MB RAM; imagen de unos 250–700 MB.
- Backend: aproximadamente 250–800 MB RAM; imagen de unos 300–900 MB.
- PostgreSQL: aproximadamente 100–400 MB RAM con pocos datos; datos iniciales unos 100–300 MB más
  crecimiento, WAL y espacio temporal de mantenimiento.
- Redis: aproximadamente 20–100 MB RAM; datos iniciales pequeños, variables según sesiones/cachés/RDB.
- Total orientativo de servicios: 0.5–1.7 GB en uso ligero; reserva margen para audio y concurrencia.
  No incluye Ubuntu, Dokploy, Traefik ni otros proyectos de la VM.
- Compilación: picos adicionales de unos 2–5 GB RAM y varios GB de disco. No es el consumo estable.
  Las imágenes, versiones anteriores y cachés pueden ocupar 2–6 GB o más según builds.
- MP3: a 64–128 kbit/s, 10 horas equivalen aproximadamente a 300–600 MB. El bitrate real depende del
  proveedor. Las copias de seguridad necesitan espacio adicional independiente.

Son rangos de planificación sin medición en VM 105. Mide desde Dokploy durante reposo, una sesión de
voz y una generación de listening; observa RAM de cada contenedor, RAM disponible y uso de disco.
Después ajusta concurrencia, cuotas y políticas de mantenimiento. No se fijan límites arbitrarios.

## Aceptación en tu servidor

No hay acceso al servidor ni credenciales de proveedores en este trabajo. En Dokploy verifica:

1. Preview Compose válido, solo cuatro servicios, sin GPU ni puertos públicos de bases.
2. Build, migraciones y healthchecks correctos; certificado y redirección HTTPS válidos.
3. Invitación inicial, login, renovación de sesión y logout; /register sin invitación debe rechazar.
4. Perfil y onboarding solo ofrecen inglés; petición manual para otro idioma debe devolver 422.
5. Conversación de texto con correcciones, explicación en español y escenario profesional.
6. Micrófono, transcripción, respuesta hablada y WebSocket 101 sobre HTTPS, también tras reconexión.
7. Crear plan y ejercicio, guardar progreso, reiniciar desde Dokploy y comprobar que persisten.
8. Revisar /api/admin/health autenticado: bases y servicios de voz. /health comprueba respuesta HTTP;
   no garantiza saldo, capacidad del LLM ni disponibilidad de todos los proveedores.
9. Probar errores de proveedor/red sin perder el progreso previamente guardado.

## Actualización, backup y rollback

Antes de actualizar, registra el commit y las imágenes que funcionan, exporta las variables de forma
segura, realiza un backup lógico PostgreSQL desde Dokploy y copia avatars/audio/tts_previews. Para una
copia consistente evita escrituras mientras respaldas. Conserva backups fuera del disco de la VM y
prueba restauración en otra instalación. Una instantánea Proxmox no reemplaza un backup externo.

Despliega el commit aprobado desde Git, sin cambiar DATA_PATH ni el nombre/ruta del proyecto.
Comprueba migraciones y ejecuta la aceptación anterior. Mantén una copia previa y una diaria durante
7 días más 4 semanales como política inicial, ajustada al espacio real. No automatizamos borrado de
backups existentes en este cambio.

Para volver atrás en esta propuesta, selecciona el commit anterior en Dokploy y recompila/reutiliza
sus imágenes conservadas, con las mismas credenciales, datos y redes. No hay cambios nuevos de esquema.
En actualizaciones futuras revisa compatibilidad del esquema antes de revertir binarios: si cambió
de forma incompatible, restaura el backup en una ubicación/base separada, verifica y cambia de forma
controlada. No ejecutes alembic downgrade ni sobrescribas la base actual a ciegas. Nunca uses down -v,
prune --volumes ni elimines DATA_PATH para actualizar o retroceder.

Referencias: [Dominios Compose de Dokploy](https://docs.dokploy.com/docs/core/docker-compose/domains),
[API Chat Completions de OpenRouter](https://openrouter.ai/docs/api/api-reference/chat/send-chat-completion-request).
