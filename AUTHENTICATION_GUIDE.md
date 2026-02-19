# 🛒 SISTEMA DE AUTENTICACIÓN Y CARRITO PERSISTENTE

## 📋 Resumen

Tu sistema ahora tiene:

✅ **Autenticación Frontend**: Login y Registro con interfaz premium
✅ **Carrito Persistente Híbrido**: 
  - Usuarios anónimos → Sesión del navegador
  - Usuarios autenticados → Base de datos
  - Migración automática al login

✅ **API JSON**: Endpoints para gestionar carrito dinámicamente
✅ **Validaciones**: Email, contraseña, usuario duplicado

---

## 🔑 RUTAS DE AUTENTICACIÓN

### 1. **Registro de Usuario**
```
GET  /registro/
POST /registro/
```

**Template**: `templates/auth/registro.html`

**POST Body**:
```json
{
  "username": "juan_perfume",
  "email": "juan@example.com",
  "password": "MiContraseña123",
  "password2": "MiContraseña123"
}
```

**Respuesta**:
- Si es exitoso → Redirige a login
- Si hay error → Muestra errores en el formulario

**Validaciones**:
- Usuario: 3+ caracteres, único
- Email: válido y único
- Contraseña: 6+ caracteres, coincidentes
- Al registrarse → Crea carrito automáticamente

---

### 2. **Iniciar Sesión**
```
GET  /login/
POST /login/
```

**Template**: `templates/auth/login.html`

**POST Body**:
```json
{
  "username": "juan_perfume",
  "password": "MiContraseña123"
}
```

**Flujo**:
1. Autentica usuario
2. Crea carrito si no existe
3. **Migra carrito de sesión a BD** ← IMPORTANTE
4. Redirige a siguiente página (por default catálogo)

---

### 3. **Cerrar Sesión**
```
GET /logout/
```
- Cierra sesión
- Limpia cookies
- Redirige a login

---

## 🛒 RUTAS DE CARRITO

### **1. Ver Carrito (Frontend)**
```
GET /carrito/
```

**Template**: `templates/carrito.html`

Renderiza página completa del carrito con:
- Lista de productos
- Controles de cantidad
- Resumen de precios
- Botón de pago
- Sugerencia de login si es anónimo

---

### **2. API: Obtener Carrito (JSON)**
```
GET /api/carrito/
```

**Respuesta**:
```json
{
  "exito": true,
  "items": [
    {
      "producto_id": 1,
      "nombre": "Eau de Parfum Oriental",
      "precio": 89.99,
      "cantidad": 2,
      "subtotal": 179.98
    }
  ],
  "total": 179.98,
  "cantidad_items": 2
}
```

---

### **3. API: Agregar al Carrito**
```
POST /api/carrito/
Content-Type: application/json

{
  "producto_id": 1,
  "cantidad": 2
}
```

**Comportamiento**:
- **Anónimo** → Se guarda en `request.session['carrito']`
- **Autenticado** → Se guarda en modelo `ItemCarrito` de BD
- Si ya existe → Suma cantidades
- Retorna carrito actualizado (JSON)

---

### **4. API: Actualizar Cantidad**
```
POST /api/carrito/actualizar/
Content-Type: application/json

{
  "producto_id": 1,
  "cantidad": 5
}
```

**Casos**:
- Cantidad > 0 → Actualizar
- Cantidad = 0 → Usar `/eliminar/`
- Retorna carrito actualizado

---

### **5. API: Eliminar del Carrito**
```
POST /api/carrito/eliminar/
Content-Type: application/json

{
  "producto_id": 1
}
```

**Resultado**:
- Elimina producto del carrito
- Retorna carrito actualizado
- Si carrito queda vacío → La página se recarga

---

## 💾 BASE DE DATOS

### Modelo: **Carrito**
```python
class Carrito(models.Model):
    usuario = OneToOneField(User)  # Un carrito por usuario
    creado_en = DateTimeField(auto_now_add=True)
    actualizado_en = DateTimeField(auto_now=True)
    
    @property
    def total(self):
        """Suma de todos los items"""
    
    @property
    def cantidad_items(self):
        """Total de items en carrito"""
```

### Modelo: **ItemCarrito**
```python
class ItemCarrito(models.Model):
    carrito = ForeignKey(Carrito)
    producto = ForeignKey(Producto)
    cantidad = IntegerField(default=1)
    
    @property
    def subtotal(self):
        """producto.precio * cantidad"""
    
    class Meta:
        unique_together = ('carrito', 'producto')  # Un producto una sola vez
```

---

## 🔄 LÓGICA: Migración de Carrito

### Momento 1: Usuario Anónimo Agrega al Carrito
```
GET  /
POST /api/carrito/ → Guarda en request.session
{
  "carrito": {
    "1": 2,  # producto_id: cantidad
    "5": 1
  }
}
```

### Momento 2: Usuario Hace Click en Login
```
GET /login/
```

### Momento 3: Usuario Submite Credenciales
```
POST /login/
→ Autentica
→ Crea sesión Django
→ Llama migrar_carrito_sesion(request, user)
  ├── Lee carrito de sesión
  ├── Crea items en ItemCarrito
  ├── Limpia sesión
  └── Redirige a índice
```

### Resultado Final
```python
carrito_user = Carrito.objects.get(usuario=user)
carrito_user.items.all()  # Ya contiene los productos
```

---

## 🎯 CASO DE USO: Compra Completa

### Escenario: Cliente Anónimo → Autenticado → Compra

```
1. Cliente llega a tienda
   ↓
2. Navega catálogo sin cuenta
   ↓
3. Agrega 3 perfumes al carrito (sesión)
   ↓
4. Hace click en "Proceder al Pago"
   ↓
5. Redirecciona a login (carrito se mantiene)
   ↓
6. Se registra/inicia sesión
   ↓
7. Carrito se migra automáticamente a BD
   ↓
8. Cliente es redirigido a su carrito
   ↓
9. Ve sus 3 productos en el carrito guardado
   ↓
10. Procede al pago
```

---

## 🔐 Validaciones y Seguridad

### Registro
- ✅ Username mínimo 3 caracteres
- ✅ Username único
- ✅ Email válido y único
- ✅ Contraseña mínimo 6 caracteres
- ✅ Contraseña y confirmación coinciden

### Login
- ✅ Valida credenciales contra BD
- ✅ Solo usuarios activos pueden iniciar sesión
- ✅ Crea sesión segura con Django

### Carrito
- ✅ Producto debe existir en BD
- ✅ Cantidad debe ser positiva
- ✅ Productos antiguos se limpian al logout
- ✅ CSRF protection en todos los POST

---

## 🚀 Frontend: JavaScript para Carrito Dinámico

En `templates/carrito.html` hay funciones JS para:

```javascript
// Incrementar cantidad: /api/carrito/actualizar/
incrementQuantity(btn)

// Decrementar cantidad: /api/carrito/actualizar/
decrementQuantity(btn)

// Eliminar producto: /api/carrito/eliminar/
removeItem(btn)

// Actualizar display
updateCartDisplay(data)
```

Todas usan `fetch()` con CSRF token automático.

---

## ⚙️ Configuración en settings.py

```python
# Sesión
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 1209600  # 2 semanas
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Carrito anónimo usa request.session
# Datos de sesión en tabla: django_session
```

---

## 📝 Próximos Pasos (FASE 3)

1. Integrar Stripe para pagos
2. Crear orden desde carrito
3. Enviar confirmación por email
4. Historial de pedidos

---

## 🐛 Troubleshooting

### Error: "Carrito no encontrado"
```python
# Solución: Crear carrito si no existe
carrito, _ = Carrito.objects.get_or_create(usuario=user)
```

### Error: CSRF token faltante
```javascript
// Usar getCookie('csrftoken') en fetch
headers: {
  'X-CSRFToken': getCookie('csrftoken'),
}
```

### Carrito no migra al login
```python
# Verificar que migrar_carrito_sesion() se llama en login_view
# Debe estar ANTES de return redirect()
```

---

## 📞 Soporte

Para problemas:
1. Revisar logs: `python manage.py runserver`
2. Verificar BD: `python manage.py dbshell`
3. Check migrations: `python manage.py showmigrations`
