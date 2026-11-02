# Práctica 10: contenerizar la aplicación de reportes

Esta carpeta contiene la unidad de despliegue del Sistema Web de Reportes de Colonias.
La aplicación expone `GET /reportes` y `GET /health` mediante Flask y puede consultar
la tabla DynamoDB `ReportesColoniasP07` cuando se ejecuta con `DEMO_MODE=false`.

## Archivo de definición

El `Dockerfile` usa `python:3.12-slim`, instala dependencias antes de copiar el código,
ejecuta Gunicorn en el puerto 8080 y cambia a un usuario sin privilegios. El archivo
`.dockerignore` evita incluir credenciales, archivos `.env`, dependencias locales,
repositorios Git y evidencias.

## Variables de entorno

| Variable | Requerida | Uso |
| --- | --- | --- |
| `TABLE_NAME` | No | Tabla DynamoDB; valor predeterminado `ReportesColoniasP07`. |
| `AWS_REGION` | No | Región AWS; valor predeterminado `us-east-1`. |
| `DEMO_MODE` | No | `true` usa un registro de demostración para probar el contenedor; `false` consulta DynamoDB. |
| `PORT` | No | Puerto HTTP interno; valor predeterminado `8080`. |

## Reducción propuesta

La imagen puede reducirse aún más usando un builder multi-stage y un wheelhouse
para separar herramientas de compilación del runtime. También se puede fijar un
archivo de hashes para dependencias y eliminar paquetes que no sean necesarios.
La imagen final implementada conserva `python:3.12-slim` por su claridad y tamaño
razonable para esta práctica.
