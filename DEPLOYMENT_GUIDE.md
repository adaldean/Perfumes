# 🚀 Guía de Deployment y Configuración - Aura Essence

**Fecha de Actualización**: 12 de mayo de 2026  
**Bugs Corregidos**: Carrito, S3, Email  
**Status**: Listo para Producción

---

## 📋 Tabla de Contenidos

1. [Variables de Entorno en Render](#variables-de-entorno)
2. [Verificación Pre-Deploy](#verificación-pre-deploy)
3. [Deploy a Render](#deploy-a-render)
4. [Post-Deploy Testing](#post-deploy-testing)
5. [Monitoreo y Troubleshooting](#monitoreo)

---

## 🔐 Variables de Entorno en Render {#variables-de-entorno}

Ir a: **Render Dashboard** → **Aura Essence Service** → **Environment**

### ✅ Requeridas (CRÍTICO)

```bash
# Seguridad y Configuración
SECRET_KEY=tu-django-secret-key-aqui-generate-uno-new
DEBUG=False
ALLOWED_HOSTS=aura-essence.onrender.com,www.aura-essence.onrender.com

# Base de Datos (Render PostgreSQL)
DATABASE_URL=postgres://user:password@host:port/dbname

# AWS S3 (PARA IMÁGENES - CRÍTICO)
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_STORAGE_BUCKET_NAME=aura-essence-prod
AWS_S3_REGION_NAME=us-east-1

# Email (Gmail SMTP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=app-password-google  # NO tu password de Google, genera uno en https://myaccount.google.com/apppasswords
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=noreply@auraessence.com

# Seguridad HTTPS
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000

# reCAPTCHA (Opcional pero recomendado)
RECAPTCHA_PUBLIC_KEY=tu-public-key-aqui
RECAPTCHA_PRIVATE_KEY=tu-private-key-aqui
```

### 📌 Notas Importantes

#### AWS S3 Setup
```
1. Crear bucket en S3: aura-essence-prod
2. Crear IAM User con permisos S3:
   - s3:GetObject
   - s3:PutObject
   - s3:PutObjectAcl
   - s3:DeleteObject
3. Copiar Access Key ID y Secret Access Key
4. Configurar CORS en bucket:

{
  "CORSRules": [
    {
      "AllowedOrigins": ["https://aura-essence.onrender.com"],
      "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
      "AllowedHeaders": ["*"],
      "MaxAgeSeconds": 3000
    }
  ]
}

5. Hacer bucket público para lectura (objeto por objeto en código)
```

#### Email con Gmail
```
1. Habilitar 2FA en Google Account
2. Ir a: https://myaccount.google.com/apppasswords
3. Generar "App Password" para "Mail"
4. Copiar la contraseña de 16 caracteres
5. Usar esa contraseña en EMAIL_HOST_PASSWORD
```

---

## 🔍 Verificación Pre-Deploy {#verificación-pre-deploy}

### ✅ Antes de pushear a Render

#### 1. Verificar cambios locales

```bash
git status
# Debe mostrar:
# - BUGFIXES_SUMMARY.md (nuevo)
# - templates/base.html (modificado)
# - templates/catalogo.html (modificado)
# - myproject/settings.py (modificado)
# - apps/orders/api_views.py (modificado)
```

#### 2. Ejecutar tests locales

```bash
# En terminal local
cd /home/jose/Escritorio/Perfumes

# Activar venv
source .venv/bin/activate

# Migrar BD local
python manage.py migrate

# Ejecutar servidor
python manage.py runserver

# Tests en otro terminal
python manage.py test apps.orders.tests  # Si existen
```

#### 3. Test manual - Carrito

```bash
1. Abrir http://localhost:8000/catalogo
2. Click en "Agregar al Carrito" en una card
3. Verificar:
   ✅ Spinner animado
   ✅ Checkmark verde
   ✅ Contador en header cambia a 1
   ✅ Button vuelve a normal en 1.5s
```

#### 4. Test manual - Registro y Email

```bash
1. Ir a http://localhost:8000/registro
2. Llenar formulario
3. Submit
4. Verificar:
   ✅ En consola Django, ver email de activación (console backend)
   ✅ Copiar link de activación
   ✅ Clic en link
   ✅ Mensaje "Cuenta activada exitosamente"
   ✅ Poder hacer login
```

#### 5. Sintaxis Python

```bash
python -m py_compile myproject/settings.py
python -m py_compile apps/orders/api_views.py
python -m py_compile templates/*.html  # No, no se compilan, solo verifica abajo

# O mejor:
python manage.py check
```

#### 6. Collectstatic

```bash
python manage.py collectstatic --noinput
# Debe completar sin errores
```

---

## 🚀 Deploy a Render {#deploy-a-render}

### Paso 1: Commit y Push

```bash
cd /home/jose/Escritorio/Perfumes

# Verificar cambios
git status

# Agregar archivos
git add BUGFIXES_SUMMARY.md
git add templates/base.html templates/catalogo.html
git add myproject/settings.py
git add apps/orders/api_views.py

# Commit con mensaje descriptivo
git commit -m "fix: Resolve critical bugs

- Fix cart counter hardcoding to 0 in header template
- Improve CSS selector for cart badge update in catalog
- Add cart count to API responses for proper UI updates
- Enhance AWS S3 configuration with proper validation
- Add missing S3 parameters (signature version, addressing style)

Fixes issues:
1. 🛒 Cart add-to-cart button from product cards now updates counter
2. 🔢 Cart badge counter now increases when products are added
3. 📸 Images now upload correctly to AWS S3 in production
4. ✉️ Email verification system validated and working"

# Push a origin
git push origin main
```

### Paso 2: Monitorear Deployment en Render

```
1. Ir a Render Dashboard
2. Seleccionar "Aura Essence" service
3. Ver logs en tiempo real
4. Esperar mensaje "Your service is live"
```

### Logs a Buscar (éxito):

```
✅ "Build started for branch main"
✅ "Building docker image"
✅ "running collectstatic"
✅ "running migrate"
✅ "Your service is live"
```

### Logs a Evitar (error):

```
❌ "OperationalError: FATAL: Ident authentication failed"
   → Verificar DATABASE_URL

❌ "ModuleNotFoundError: No module named 'storages'"
   → Verificar requirements.txt tiene django-storages

❌ "botocore.exceptions.NoCredentialsError"
   → Verificar AWS_* variables de entorno

❌ "SMTPAuthenticationError"
   → Verificar EMAIL_HOST_PASSWORD y EMAIL_HOST_USER
```

---

## 🧪 Post-Deploy Testing {#post-deploy-testing}

### Test 1: Website Loads

```bash
curl https://aura-essence.onrender.com
# Debe devolver HTML, no error 500
```

### Test 2: Catálogo Carga

```bash
1. Navegar a https://aura-essence.onrender.com/catalogo
2. Verificar:
   ✅ Productos carguen
   ✅ Imágenes visibles (desde S3)
   ✅ No hay error 500
```

### Test 3: Agregar Producto (Anónimo)

```bash
1. En /catalogo, click "Agregar al Carrito"
2. Verificar:
   ✅ Contador cambia de 0 a 1
   ✅ Spinner animado
   ✅ Checkmark verde
   ✅ Vuelve a icono normal
```

### Test 4: Registro y Email

```bash
1. Ir a /registro
2. Llenar formulario con email real (NO de prueba)
3. Verificar:
   ✅ Email llega en < 2 minutos
   ✅ Link de activación funciona
   ✅ Puede hacer login
```

### Test 5: Upload de Imagen

```bash
Admin:
1. Ir a /admin
2. Login
3. Add Producto with imagen
4. Verify:
   ✅ Imagen guardada en S3
   ✅ En /catalogo, imagen visible
   ✅ Inspeccionador: URL es HTTPS del S3
```

### Test 6: Carrito Persistente (Autenticado)

```bash
1. Login
2. Agregar 3 productos
3. Refreshear página (F5)
4. Verificar:
   ✅ Contador sigue en 3
   ✅ Ir a /carrito
   ✅ Los 3 productos están ahí
```

---

## 📊 Monitoreo {#monitoreo}

### Logs de Render

```bash
# Ver logs en tiempo real
Render Dashboard → Service → Logs

# Buscar errores:
- "error"
- "exception"
- "500"
- "S3"
- "email"
```

### Health Check

```bash
# Endpoint disponible?
curl -I https://aura-essence.onrender.com

# Status 200 = OK
# Status 50x = Error
```

### Monitoreo de S3

```
AWS Console → S3 → aura-essence-prod → Objects
- Ver que archivos se crean cuando subes imágenes
- Verificar tamaños
- Comprobar timestamps actuales
```

### Monitoreo de Email

```
Gmail Account:
- Ver que emails se envían desde noreply@auraessence.com
- Verificar "Sent" folder
- Si emails no llegan: Check spam folder
```

---

## 🔧 Troubleshooting

### Problema: Contador sigue en 0

**Causa Potencial**: JavaScript no actualiza

**Solución**:
```bash
1. Abrir DevTools (F12)
2. Console tab
3. Agregar producto
4. Ver si hay errores JavaScript
5. Verificar que ID "cart-badge" existe:
   document.getElementById('cart-badge')
   # Debe devolver el elemento, no null
```

### Problema: Imágenes no cargan

**Causa Potencial 1**: S3 no está configurado

```bash
# En Render Logs:
grep "S3" logs
# Si está vacío, S3 no se inicializó

# Solución: Verificar AWS_* variables
```

**Causa Potencial 2**: CORS bloqueado

```bash
# En DevTools Network tab:
# Ver si hay CORS error en imágenes
# Solución: Update S3 CORS rules (ver arriba)
```

### Problema: Email no llega

**Causa Potencial 1**: Credenciales incorrectas

```bash
# Test local:
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Test', 'noreply@auraessence.com', ['tu-email@gmail.com'])
1  # Si devuelve 1, OK. Si 0, error.
```

**Causa Potencial 2**: Gmail bloqueando

```
1. Ir a Google Account
2. "Less secure app access" → Allow (si aplica)
3. O usar App Password (recomendado)
```

### Problema: 500 Error

**Solución**:
```bash
1. Render Logs → Ver error exacto
2. Buscar "Traceback"
3. Leer mensaje de error
4. Si es BD: Verificar DATABASE_URL
5. Si es S3: Verificar AWS variables
6. Si es Email: Verificar EMAIL variables
```

---

## 🎯 Checklist Final

### Pre-Production
- [ ] Código local funciona perfectamente
- [ ] Todos los tests pasaron
- [ ] BUGFIXES_SUMMARY.md creado y agregado
- [ ] Cambios commiteados

### Deployment
- [ ] Push a main iniciado
- [ ] Render build inició
- [ ] Build completó sin errores
- [ ] Service está "live"

### Post-Deployment
- [ ] Website carga correctamente
- [ ] Contador carrito funciona
- [ ] Imágenes cargan desde S3
- [ ] Email de registro llega
- [ ] Login funciona
- [ ] Carrito persiste para usuarios autenticados

### Monitoreo Continuo
- [ ] Configurar alertas en Render
- [ ] Revisar logs diariamente primera semana
- [ ] Verificar S3 bucket storage
- [ ] Validar email delivery

---

## 📞 Contacto y Soporte

Si hay problemas:

1. **Revisar Logs**: Render Dashboard → Logs
2. **Revisar BUGFIXES_SUMMARY.md**: Este documento
3. **Verificar Variables**: Environment en Render
4. **Test Local**: Reproducir problema localmente

---

## 📝 Historial de Cambios

| Fecha | Cambio | Status |
|-------|--------|--------|
| 12/5/2026 | Corregir carrito, S3, email | ✅ Completado |
| - | Add to cart responses con cantidad_items | ✅ Completado |
| - | S3 configuration mejorada | ✅ Completado |

---

**Documento Generado por**: Senior Development Team  
**Última Actualización**: 12 de mayo de 2026  
**Versión**: 1.0

