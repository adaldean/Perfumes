# 🧪 GUÍA DE VALIDACIÓN LOCAL - Antes del Deploy

**Tiempo Estimado**: 10 minutos  
**Requisitos**: Local environment funcionando + navegador

---

## ✅ Test 1: Iniciar Servidor

```bash
cd /home/jose/Escritorio/Perfumes

# Activar entorno
source .venv/bin/activate

# Migrar BD
python manage.py migrate

# Iniciar servidor
python manage.py runserver

# En otro terminal:
# python manage.py test (si tienes tests)
```

**Esperado**: Server corriendo en http://localhost:8000

---

## ✅ Test 2: Verificar Contador Inicial

**URL**: http://localhost:8000

**Pasos**:
1. Abrir DevTools (F12)
2. Console tab
3. Ejecutar:
```javascript
document.getElementById('cart-badge').textContent
// Debe retornar: "0"
```

**Si no funciona**: Verificar que exista el elemento
```javascript
document.getElementById('cart-badge')
// Debe retornar: <span id="cart-badge">0</span>
```

---

## ✅ Test 3: Agregar Producto desde Catálogo

**URL**: http://localhost:8000/catalogo

**Pasos**:
1. Ver productos en grid
2. Pasar mouse sobre una card
3. Debe aparecer overlay con dos iconos:
   - 👁️ Ver detalles
   - 🛒 Agregar al carrito

**Esperado en Carrito**:
```
1. Click en 🛒 (Agregar al carrito)
2. Botón muestra spinner (fa-spinner animado)
3. Petición se envía a /api/carrito/
4. Respuesta con 'exito': true y 'cantidad_items': 1
5. Contador en header cambia de 0 → 1
6. Botón muestra checkmark (fa-check) en verde
7. Después 1.5s vuelve a icono original 🛒
```

**Verificar en DevTools** (Network tab):
```
POST /api/carrito/

Request:
{
  "producto_id": 5,
  "cantidad": 1
}

Response:
{
  "exito": true,
  "mensaje": "Producto agregado",
  "cantidad_items": 1
}
```

---

## ✅ Test 4: Contador Actualiza Múltiples Veces

**Pasos**:
1. Desde /catalogo, agregar 3 productos diferentes
2. Después de cada click, verificar:
   - Contador aumenta: 0 → 1 → 2 → 3
   - Feedback visual funciona

**Esperado**:
```
Click 1: Contador 0 → 1 ✅
Click 2: Contador 1 → 2 ✅
Click 3: Contador 2 → 3 ✅
```

---

## ✅ Test 5: Carrito Persiste (Anónimo)

**Pasos**:
1. Agregar 2 productos en /catalogo
2. Contador debe mostrar 2
3. Refrescar página (F5)
4. Contador debe SEGUIR en 2
5. Ir a /carrito
6. Deben verse los 2 productos

**Por qué funciona**: Sesión (cookie) en el navegador

---

## ✅ Test 6: Carrito Persiste (Autenticado)

**Pasos**:
1. Ir a /registro
2. Llenar formulario con datos:
   - Username: testuser123
   - Email: tu-email@gmail.com (necesita ser real para recibir email)
   - Password: Test@1234
   - First Name: Test
   - Last Name: User

3. Submit

**Esperado**:
```
Mensaje: "Cuenta creada exitosamente. Revisa tu correo para activar tu cuenta."
Redirección a /login
Revisar email → Debe haber email de Aura Essence
Click en link → Debe ir a /auth/activate/...
Mensaje: "Tu cuenta ha sido activada exitosamente"
Poder hacer login
```

**Después de Login**:
1. Ir a /catalogo
2. Agregar 3 productos
3. Ir a /carrito
4. Verificar que vea los 3 productos
5. Refrescar página (F5)
6. Los 3 productos siguen ahí (BD)

---

## ✅ Test 7: Upload de Imagen (Admin)

**Pasos**:
1. Ir a /admin
2. Login con superuser (si tienes)
3. Ir a Catalog > Productos
4. Crear producto o editar uno existente
5. Subir una imagen (JPG pequeño, <5MB)
6. Guardar

**En local (Django)**: 
- Imagen se guarda en `/media/productos/`

**Esperado**:
```
✅ Imagen guardada localmente
✅ En /catalogo, imagen visible
✅ URL es /media/productos/imagen.jpg
```

---

## ✅ Test 8: Email de Verificación

**Pasos**:
1. Ir a /registro
2. Llenar con email real (Gmail, etc)
3. Submit

**Esperado**:
```
En consola Django:
- Ver email content (console backend)
- Link de activación visible

EN REALIDAD:
- Email debe llegar en < 1 min
- Link de activación funciona
- Cuenta se activa
```

**Cómo verificar email en local**:
```bash
# En consola del servidor Django, verás:

Subject: Aura Essence: Activa tu cuenta
From: noreply@auraessence.com
To: tu-email@gmail.com

Content:
¡Hola Test!

Gracias por registrarte...
http://localhost:8000/auth/activate/MTg=/c5k-abcdef123/

Click en el link
```

---

## ✅ Test 9: Verificar Selector CSS del Contador

**En DevTools Console**:
```javascript
// Test 1: ¿Existe el ID?
const badge = document.getElementById('cart-badge')
// Debe devolver: <span id="cart-badge">3</span>

// Test 2: ¿Puede cambiar el texto?
badge.textContent = '99'
// Badge debe mostrar 99 ahora

// Test 3: Restore
badge.textContent = '3'
```

---

## ✅ Test 10: Verificar API Response Completa

**URL en navegador**: 
```
GET http://localhost:8000/api/carrito/
```

**Esperado (Anónimo)**:
```json
{
  "exito": true,
  "items": [
    {
      "producto_id": 5,
      "nombre": "Perfume XYZ",
      "precio": 150.0,
      "cantidad": 2,
      "subtotal": 300.0,
      "imagen": "/media/productos/image.jpg"
    }
  ],
  "total": 300.0,
  "cantidad_items": 2
}
```

**Esperado (Autenticado)**:
```json
{
  "exito": true,
  "items": [...],
  "total": 300.0,
  "cantidad_items": 2
}
```

---

## 🐛 Troubleshooting

### Problema: Contador no cambia

**Verificar**:
```javascript
// 1. ¿Existe el elemento?
document.getElementById('cart-badge')
// Si retorna null, problema en base.html

// 2. ¿Tiene listener el botón?
document.querySelector('.add-to-cart-btn[data-id]')
// Click y check Network tab
```

### Problema: Error 404 en /api/carrito/

**Verificar**:
- URLs están configuradas en `apps/orders/urls.py`
- Ruta está incluida en `myproject/urls.py`

```bash
grep -r "api/carrito" myproject/urls.py apps/orders/urls.py
```

### Problema: CSRF Token Error

**Verificar**:
```javascript
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Test
getCookie('csrftoken')
// Debe retornar un token
```

---

## 📋 Checklist Pre-Deploy

Marcar todo ✅ antes de hacer push

```bash
# Verificar código
[ ] python manage.py check

# Verificar sintaxis
[ ] python -m py_compile myproject/settings.py
[ ] python -m py_compile apps/orders/api_views.py

# Verificar migraciones
[ ] python manage.py migrate

# Tests locales
[ ] Test 1: Contador inicial (0)
[ ] Test 2: Agregar productos (contador actualiza)
[ ] Test 3: Persistencia anónimo (refresh)
[ ] Test 4: Persistencia autenticado (BD)
[ ] Test 5: Email llega
[ ] Test 6: API devuelve cantidad_items

# Limpiar
[ ] python manage.py collectstatic --noinput
[ ] Revisar que no hay errores

# Commit
[ ] git add cambios
[ ] git commit
[ ] git push origin main
```

---

## ✅ Si Todo Funciona Localmente

**Entonces está listo para Render**:

```bash
1. Variables de entorno en Render configuradas ✅
2. Código local funciona perfecto ✅
3. Push a main ✅
4. Render auto-deploy 1-2 minutos ✅
5. Validar en producción con Testing Checklist ✅
```

---

## 📞 Si Algo Falla Localmente

1. Revisar console error en DevTools (F12)
2. Revisar server console (terminal del runserver)
3. Revisar logs: `python manage.py runserver`
4. Check BUGFIXES_SUMMARY.md para troubleshooting

---

**Generado**: 12/5/2026  
**Version**: 1.0

