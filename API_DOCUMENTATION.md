# Documentación de API

Este proyecto incluye una API REST implementada con Django REST Framework. A continuación se detallan los endpoints disponibles.

## Base URL

```
http://127.0.0.1:8000/api
```

## Endpoints disponibles

### Productos

#### 1. Listar todos los productos

**Endpoint:** `GET /api/productos/`

**Respuesta:**
```json
{
  "count": 0,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "nombre": "Producto de Ejemplo",
      "descripcion": "Descripción del producto",
      "precio": "99.99",
      "activo": true,
      "creado_en": "2025-02-18T10:30:00Z",
      "actualizado_en": "2025-02-18T10:30:00Z"
    }
  ]
}
```

---

#### 2. Obtener un producto específico

**Endpoint:** `GET /api/productos/{id}/`

**Parámetros:**
- `id` (path): ID del producto

**Respuesta:**
```json
{
  "id": 1,
  "nombre": "Producto de Ejemplo",
  "descripcion": "Descripción del producto",
  "precio": "99.99",
  "activo": true,
  "creado_en": "2025-02-18T10:30:00Z",
  "actualizado_en": "2025-02-18T10:30:00Z"
}
```

---

#### 3. Crear un nuevo producto

**Endpoint:** `POST /api/productos/`

**Body (JSON):**
```json
{
  "nombre": "Nuevo Producto",
  "descripcion": "Descripción del nuevo producto",
  "precio": "199.99",
  "activo": true
}
```

**Respuesta (Código 201):**
```json
{
  "id": 2,
  "nombre": "Nuevo Producto",
  "descripcion": "Descripción del nuevo producto",
  "precio": "199.99",
  "activo": true,
  "creado_en": "2025-02-18T11:00:00Z",
  "actualizado_en": "2025-02-18T11:00:00Z"
}
```

---

#### 4. Actualizar un producto (completo)

**Endpoint:** `PUT /api/productos/{id}/`

**Parámetros:**
- `id` (path): ID del producto

**Body (JSON):**
```json
{
  "nombre": "Producto Actualizado",
  "descripcion": "Nueva descripción",
  "precio": "249.99",
  "activo": true
}
```

**Respuesta:**
```json
{
  "id": 1,
  "nombre": "Producto Actualizado",
  "descripcion": "Nueva descripción",
  "precio": "249.99",
  "activo": true,
  "creado_en": "2025-02-18T10:30:00Z",
  "actualizado_en": "2025-02-18T11:15:00Z"
}
```

---

#### 5. Actualizar un producto (parcial)

**Endpoint:** `PATCH /api/productos/{id}/`

**Parámetros:**
- `id` (path): ID del producto

**Body (JSON):**
```json
{
  "precio": "299.99"
}
```

**Respuesta:**
```json
{
  "id": 1,
  "nombre": "Producto Actualizado",
  "descripcion": "Nueva descripción",
  "precio": "299.99",
  "activo": true,
  "creado_en": "2025-02-18T10:30:00Z",
  "actualizado_en": "2025-02-18T11:30:00Z"
}
```

---

#### 6. Eliminar un producto

**Endpoint:** `DELETE /api/productos/{id}/`

**Parámetros:**
- `id` (path): ID del producto

**Respuesta:** Código 204 (sin contenido)

---

## Códigos de Estado HTTP

| Código | Significado |
|--------|-------------|
| 200 | OK - Solicitud exitosa |
| 201 | Created - Recurso creado exitosamente |
| 204 | No Content - Recurso eliminado |
| 400 | Bad Request - Datos inválidos |
| 404 | Not Found - Recurso no encontrado |
| 500 | Internal Server Error - Error del servidor |

---

## Pruebas con curl

### Listar productos
```bash
curl http://127.0.0.1:8000/api/productos/
```

### Crear un producto
```bash
curl -X POST http://127.0.0.1:8000/api/productos/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Mi Producto",
    "descripcion": "Mi descripción",
    "precio": "99.99",
    "activo": true
  }'
```

### Obtener un producto
```bash
curl http://127.0.0.1:8000/api/productos/1/
```

### Actualizar un producto
```bash
curl -X PATCH http://127.0.0.1:8000/api/productos/1/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Producto Actualizado"
  }'
```

### Eliminar un producto
```bash
curl -X DELETE http://127.0.0.1:8000/api/productos/1/
```

---

## Pruebas con Postman

Puedes usar Postman para probar la API:

1. Descarga [Postman](https://www.postman.com/downloads/)
2. Crea una nueva colección llamada "Django API"
3. Agrega las siguientes solicitudes con los métodos HTTP y URLs correspondientes
4. Prueba cada endpoint

---

## Autenticación

Actualmente, la API no requiere autenticación. Para agregar autenticación por token, sigue estos pasos:

1. Instala: `pip install djangorestframework-simplejwt`
2. Configura en `settings.py`:
   ```python
   REST_FRAMEWORK = {
       'DEFAULT_AUTHENTICATION_CLASSES': [
           'rest_framework_simplejwt.authentication.JWTAuthentication',
       ]
   }
   ```
3. Incluye las URLs de autenticación en `urls.py`

---

## Recursos Útiles

- [Django REST Framework Documentation](https://www.django-rest-framework.org/)
- [Django QuerySet API](https://docs.djangoproject.com/en/4.2/ref/models/querysets/)
- [Postman Collections](https://www.postman.com/features/api-management/)

