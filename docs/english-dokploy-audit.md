# Auditoría: inglés personal en Dokploy

## Alcance e inventario

Revisión del árbol completo y de los contratos de despliegue, configuración, autenticación,
idiomas, tutor, voz, persistencia y validación. No es una revisión de seguridad exhaustiva de cada
línea del repositorio.

- Frontend: Next.js 16, React, next-intl, Zustand y VAD en navegador. Ya produce una imagen standalone.
- Backend: FastAPI, SQLAlchemy async y Alembic. Centraliza LLM, STT y TTS; las claves permanecen aquí.
- PostgreSQL 16: usuarios, planes, historial, ejercicios, progreso y uso de IA. Conservar esquema y
  cadena de migraciones completos, incluidos los campos de idiomas y sus relaciones.
- Redis 7: tokens de renovación, invitaciones, límites y estado transitorio. Es necesario para la
  autenticación actual; eliminarlo requeriría rediseñarla.
- IA: adaptador común para Ollama, OpenAI Responses, Anthropic y DeepSeek Chat Completions.
  OpenRouter puede reutilizar Chat Completions, streaming, JSON y herramientas sin nuevas dependencias.
- Voz: servicios intercambiables locales u OpenAI; conservar captura, VAD, transcripción y audio.
  Los ejercicios llamados pronunciation reciben una transcripción, no una evaluación acústica.
- Compose original: imágenes del upstream, cuatro servicios de aplicación y dos servicios GPU.
  No tiene rotación explícita de logs. El frontend publica 3000; las bases no publican puertos.
- Persistencia: bind mounts de PostgreSQL, Redis, avatares, audio y previews bajo DATA_PATH.
- Calidad: pytest con SQLite/Redis/LLM simulados; Vitest, ESLint y TypeScript; scripts locales fijan
  runtimes y dependencias. Las pruebas SQLite no verifican actualizaciones reales de PostgreSQL.

## Decisiones antes de modificar

- Conservar tutor, planes A2/B1/B2/C1, vocabulario, gramática, reading, listening, speaking, writing,
  repasos, progreso, sesiones y recuperación de datos.
- Limitar idiomas disponibles a en-GB/en-US en el despliegue personal. Validar también registro y
  edición de perfil para que no eludan la configuración. Conservar los registros antiguos intactos.
- Mantener traducciones y preferencia de interfaz; configurar español como valor inicial en Dokploy.
- Desactivar Stripe, pruebas comerciales, analítica y registro público en el despliegue personal.
- Excluir Kokoro, Whisper y Ollama de la nueva topología. El Compose original permanece disponible.
- Mantener proveedores alternativos sin duplicar servicios ni añadir paquetes.
- Añadir escenarios profesionales al tutor para practicar inglés sobre Java, Spring Boot, Node.js,
  NestJS y APIs, sin convertirlo en un generador de código.
- No eliminar recursos, dependencias ni tablas por su nombre: Three.js/modelos se usan en la interfaz;
  VAD/ONNX se usan para voz. Hay archivos generados grandes, pero retirarlos del historial o del árbol
  debe tratarse como limpieza independiente, con confirmación previa.
- No borrar audio educativo por antigüedad: hay referencias persistidas. Limitar solamente cachés
  regenerables y mantener un procedimiento de copia de seguridad.

## Fases

1. Este inventario y diagnóstico antes de cambios funcionales.
2. Restricción de idiomas, interfaz inicial española, práctica profesional y feedback de voz honesto.
3. OpenRouter mediante variables de entorno y adaptador existente.
4. Compose específico: cuatro contenedores, compilación del fork, almacenamiento existente,
   red privada para bases, HTTPS/WebSocket en Dokploy, healthchecks y logs acotados.
5. Pruebas disponibles, documentación operativa y PR. Las pruebas de proveedores con credenciales y
   el despliegue real quedan sujetos a disponer de esos recursos; sus resultados no se presuponen.

No se prevén migraciones nuevas ni eliminación de funcionalidades o datos. Los cambios se hacen en
feat/english-only-dokploy. No se aplican migraciones, rollbacks ni cambios en Proxmox desde este trabajo.
