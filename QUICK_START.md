# 🚀 Guía Rápida - Django Web Project

## Estado Actual ✅

Tu proyecto Django está **100% configurado y listo para usar**.

```
✅ Entorno Python (venv) configurado
✅ Dependencias instaladas
✅ Base de datos migrada (SQLite)
✅ Aplicación de ejemplo (API con modelo Producto)
✅ Django REST Framework integrado
✅ CORS configurado
✅ Panel de administración disponible
```

---

## 1. Inicia el Servidor 🎯

### Opción A: Desde VS Code (Recomendado)
1. Presiona `Ctrl+Shift+B` (o `Cmd+Shift+B` en Mac)
2. Selecciona **"Django: Ejecutar servidor"**
3. El servidor estará en: http://127.0.0.1:8000

### Opción B: Desde Terminal
```bash
cd /home/adal-dean/Documentos/Teck
source .venv/bin/activate  # Linux/Mac
python manage.py runserver
```

### Opción C: Usando el script
```bash
bash start.sh
```

---

## 2. Accede a los Servicios 🌐

| Servicio | URL |
|----------|-----|
| **Inicio** | http://127.0.0.1:8000 |
| **Panel Admin** | http://127.0.0.1:8000/admin |
| **API REST** | http://127.0.0.1:8000/api/productos/ |
| **Interfaz BrowsableAPI** | http://127.0.0.1:8000/api/productos/ |

---

## 3. Crea tu Primer Superusuario (Admin) 👤

```bash
python manage.py createsuperuser
```

Completa los datos que pide y luego accede a:
http://127.0.0.1:8000/admin

---

## 4. Prueba la API 🔧

### Con curl
```bash
# Listar productos
curl http://127.0.0.1:8000/api/productos/

# Crear producto
curl -X POST http://127.0.0.1:8000/api/productos/ \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Mi Producto","precio":"99.99","activo":true}'
```

### Con Postman
1. Descarga [Postman](https://www.postman.com/)
2. Crea una solicitud `GET` a `http://127.0.0.1:8000/api/productos/`
3. ¡Prueba los diferentes endpoints!

---

## 5. Crear una Nueva Aplicación 📦

Si necesitas crear una nueva aplicación:

```bash
python manage.py startapp miapp apps/miapp
```

Luego, registra la aplicación en `myproject/settings.py`:
```python
INSTALLED_APPS = [
    ...
    'apps.miapp',  # Agrega esta línea
]
```

---

## 6. Archivos Importantes 📄

| Archivo | Propósito |
|---------|-----------|
| `myproject/settings.py` | Configuración principal del proyecto |
| `myproject/urls.py` | Rutas principales |
| `apps/api/models.py` | Modelos de datos |
| `apps/api/views.py` | Lógica de la API |
| `apps/api/serializers.py` | Conversión de datos para la API |
| `requirements.txt` | Dependencias del proyecto |
| `manage.py` | Script de gestión de Django |

---

## 7. Migraciones 🗄️

Cuando cambies modelos:

```bash
# Crea migraciones
python manage.py makemigrations

# Aplica migraciones
python manage.py migrate
```

O desde VS Code presiona `Ctrl+Shift+B` y selecciona la tarea.

---

## 8. Estructura del Proyecto 📁

```
Teck/
├── .venv/                  # Entorno virtual
├── .github/
│   └── copilot-instructions.md
├── .vscode/
│   ├── tasks.json          # Tareas de VS Code
│   └── launch.json         # Configuración del debugger
├── myproject/              # Configuración principal
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── __init__.py
├── apps/                   # Aplicaciones del proyecto
│   ├── api/
│   │   ├── models.py       # Modelo Producto de ejemplo
│   │   ├── views.py        # ViewSet de API
│   │   ├── serializers.py  # Serializador
│   │   ├── urls.py         # Rutas de la app
│   │   ├── admin.py        # Configuración admin
│   │   └── migrations/
│   └── __init__.py
├── templates/              # Plantillas HTML
├── static/                 # Archivos estáticos (CSS, JS, imágenes)
├── media/                  # Archivos subidos por usuarios
├── manage.py               # Script de gestión
├── requirements.txt        # Dependencias
├── .env.example            # Ejemplo de variables de entorno
├── .gitignore              # Archivos a ignorar en git
├── README.md               # Documentación completa
├── API_DOCUMENTATION.md    # Documentación API
├── QUICK_START.md          # Este archivo
└── start.sh                # Script para iniciar el servidor
```

---

## 9. Próximos Pasos 🎯

1. **Crea un superusuario**: `python manage.py createsuperuser`
2. **Inicia el servidor**: `python manage.py runserver`
3. **Accede al admin**: http://127.0.0.1:8000/admin
4. **Prueba la API**: http://127.0.0.1:8000/api/productos/
5. **Lee la documentación completa**: [README.md](README.md)
6. **Consulta la API**: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

---

## 10. Variables de Entorno 🔐

Para cambiar la configuración según el entorno:

1. Copia `.env.example` a `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edita `.env` con tus valores:
   ```
   DEBUG=False
   SECRET_KEY=tu-clave-secreta-aqui
   ```

3. Actualiza `settings.py` para usar las variables

---

## ¿Necesitas Ayuda? 🆘

- **Documentación oficial**: https://docs.djangoproject.com/
- **Django REST Framework**: https://www.django-rest-framework.org/
- **Comunidad**: https://www.djangoproject.com/community/

---

## Comandos Útiles en VS Code ⌨️

| Atajo | Acción |
|-------|--------|
| `Ctrl+Shift+B` | Ejecutar tarea por defecto |
| `Ctrl+K Ctrl+J` | Mostrar terminal |
| `Ctrl+Shift+D` | Modo debug |
| `Ctrl+Shift+P` | Paleta de comandos |

---

**¡Felicidades! Ya tienes un proyecto Django completamente funcional. 🎉**

Ahora es momento de:
- Crear nuevas aplicaciones
- Definir tus modelos
- Construir tu API
- ¡Crear algo increíble!

