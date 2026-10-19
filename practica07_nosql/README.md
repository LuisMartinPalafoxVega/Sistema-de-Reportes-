# Práctica 07: CRUD NoSQL con DynamoDB

Este ejemplo adapta el modelo del Sistema Web de Reportes de Colonias a DynamoDB. Está escrito en Python con boto3 y usa las credenciales temporales del rol de instancia EC2; no contiene llaves AWS.

## Patrones de acceso

1. Obtener un reporte por `id_reporte`, usando `GetItem` sobre la clave primaria.
2. Consultar los reportes de una persona, más recientes primero, con `Query` en `usuario_id-fecha_creacion-index`.
3. Consultar reportes por estado, más recientes primero, con `Query` en `estado-fecha_creacion-index`.

La partición primaria `id_reporte` identifica un reporte de forma única y habilita una lectura directa. Los dos índices globales cubren las consultas por usuario y estado; `fecha_creacion` como sort key permite ordenar cronológicamente sin escanear toda la tabla.

## Tabla requerida

- Tabla: `ReportesColoniasP07`; clave de partición `id_reporte` (String), sin sort key primaria.
- Índice `usuario_id-fecha_creacion-index`: PK `usuario_id` (String), SK `fecha_creacion` (String), proyección `ALL`.
- Índice `estado-fecha_creacion-index`: PK `estado` (String), SK `fecha_creacion` (String), proyección `ALL`.
- Capacidad: bajo demanda (`PAY_PER_REQUEST`); etiquetas del equipo/proyecto.

## Ejecución

El perfil de instancia debe conceder solo las acciones CRUD necesarias sobre esta tabla y sus índices. Con `boto3` instalado en la EC2:

```bash
export AWS_REGION=us-east-1
export P07_TABLE_NAME=ReportesColoniasP07
python3 -m pip install -r requirements.txt
python3 crud_reportes.py demo
```

La demostración inserta un registro ficticio con ID aleatorio, lo lee por clave y por índice, actualiza su estado, compara `Query` con un `Scan` limitado a 100 elementos y borra el registro temporal.

## `Query` frente a `Scan` y costos

`Query` restringe la lectura a una partición conocida. `Scan` evalúa elementos de la tabla y luego aplica el filtro; al crecer a un millón de elementos puede leer mucho más de lo que devuelve. La prueba limita el `Scan` a 100 elementos para acotar costo y permite observar `ScannedCount` y capacidad consumida. Bajo demanda factura solicitudes y almacenamiento, mientras que la capacidad provisionada reserva unidades de lectura/escritura por tiempo.

## Comparación con RDS/MySQL

RDS/MySQL se ajusta mejor al sistema de reportes existente: usuario, categoría, estado, reporte y comentario tienen relaciones y restricciones, y las consultas combinan entidades mediante joins. DynamoDB escala lecturas por claves conocidas y evita administrar capacidad de lectura/escritura, pero requiere diseñar índices a partir de patrones de acceso y puede duplicar atributos. Para este proyecto se recomienda mantener RDS como base principal; DynamoDB sirve como comparación o como complemento si aparece una carga de lecturas muy específica.
