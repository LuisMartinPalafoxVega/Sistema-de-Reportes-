# Práctica 09: API serverless de La Costeña

## Funcionalidad elegida

Se implementa una consulta de solo lectura que lista hasta 20 reportes recientes
de `ReportesColoniasP07` mediante AWS Lambda y DynamoDB. Es breve, esporádica y
se dispara por una petición HTTP, por lo que evita mantener un servidor activo
para una consulta ocasional.

## Candidatas descartadas

1. Crear o actualizar reportes: no se expone públicamente porque sería una
   operación destructiva o modificadora sin autenticación.
2. Eliminar reportes: se descarta por el riesgo de pérdida de datos y porque no
   es una operación apropiada para un endpoint público de la práctica.

## Configuración prevista

- Función: `P09-LaCostena-Reportes`
- Runtime: Python 3.12
- Memoria inicial: 128 MB
- Tiempo de espera inicial: 10 s
- Variable `TABLE_NAME`: `ReportesColoniasP07`
- Permiso: `dynamodb:Scan` únicamente sobre la tabla de prácticas
- Interfaz: API Gateway HTTP API, método `GET /reportes`

## Prueba

La respuesta esperada es JSON con `ok`, `table`, `count` e `items`. El parámetro
opcional `limit` acepta valores de 1 a 20. El endpoint no acepta cuerpo de
escritura ni métodos POST, PUT o DELETE.
