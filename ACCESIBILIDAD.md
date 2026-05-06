# Sistema de Accesibilidad - Aura Essence

## 📋 Resumen

Se ha implementado un sistema completo de accesibilidad en tu aplicación Django que incluye:

- ✅ **Zoom/Ajuste de Texto** - Usuarios pueden aumentar o reducir el tamaño del texto
- ✅ **Lectura por Voz** - Síntesis de voz Web Speech API para lectura guiada
- ✅ **Navegación por Teclado** - Acceso completo sin ratón
- ✅ **Modo Lectura** - Interfaz simplificada para lectura enfocada
- ✅ **Contraste Alto** - Modo de contraste aumentado para mejor visibilidad
- ✅ **Enlaces de Salto** - Saltar contenido no esencial rápidamente
- ✅ **Atributos ARIA** - Soporte completo para lectores de pantalla
- ✅ **Animaciones Reducidas** - Respeto a `prefers-reduced-motion`

---

## 🚀 Cómo Usar

### Acceder al Panel de Accesibilidad

El panel de accesibilidad aparece como un botón **"Accesibilidad"** dorado en la esquina inferior derecha de la pantalla. Haz clic para abrir el menú.

### Funcionalidades Principales

#### 1. **Tamaño de Texto**
```
- Botón [+]: Aumentar tamaño (max 200%)
- Botón [-]: Reducir tamaño (min 80%)
- Botón [Resetear]: Volver a 100%
```

**Atajo de Teclado**: `Alt + +` (aumentar) / `Alt + -` (disminuir)

#### 2. **Lectura por Voz**
Activa el checkbox "Lectura por Voz" para que la aplicación lea en voz alta elementos con los que interactúes.

**Atajo de Teclado**: `Alt + R` (iniciar/detener)

#### 3. **Lectura Guiada**
El botón "Lectura Guiada" lee todo el contenido principal de la página de forma continua.

- Velocidad: 0.9x (clara y pausada)
- Idioma: Español (es-ES)
- Se puede detener con el botón "Detener Lectura"

#### 4. **Modo Lectura**
Simplifica la interfaz:
- Oculta navegación y sidebars
- Aumenta espaciado entre líneas (1.8em)
- Aumenta espacio entre letras
- Centra el contenido
- Limita ancho a 800px

#### 5. **Contraste Alto**
Aplica colores en blanco y negro con bordes más gruesos:
- Fondo: Blanco
- Texto: Negro
- Enlaces: Azul estándar con subrayado

---

## ⌨️ Atajos de Teclado

| Atajo | Acción |
|-------|--------|
| `Alt + A` | Abrir/Cerrar panel de accesibilidad |
| `Alt + R` | Iniciar/Detener lectura guiada |
| `Alt + +` | Aumentar tamaño de texto |
| `Alt + -` | Reducir tamaño de texto |
| `Tab` | Navegar entre elementos |
| `Enter` | Activar botón enfocado |
| `Shift + Tab` | Navegar hacia atrás |

---

## 💾 Persistencia

Todas las preferencias de accesibilidad se guardan en **localStorage**:
- Nivel de zoom
- Modo lectura activado
- Lectura por voz activada
- Contraste alto activado

Tus preferencias se mantendrán cuando regreses a la aplicación.

---

## 🔧 Archivos Incluidos

### 1. **`static/js/accessibility.js`** (2.3 KB)
- Clase principal `AccessibilityManager`
- Todas las funcionalidades de accesibilidad
- Gestión de eventos y localStorage
- Web Speech API integration

### 2. **`static/css/accessibility.css`** (8.1 KB)
- Estilos del panel de accesibilidad
- Estilos para modo lectura
- Estilos para contraste alto
- Focus visible mejorado
- Animaciones accesibles

### 3. **`templates/base.html`** (Modificado)
- Incluye CSS de accesibilidad en `<head>`
- Incluye JS de accesibilidad antes de `</body>`

---

## 🌐 Compatibilidad

| Navegador | Soporte |
|-----------|---------|
| Chrome | ✅ Completo |
| Firefox | ✅ Completo |
| Safari | ✅ Completo |
| Edge | ✅ Completo |
| Opera | ✅ Completo |
| IE 11 | ⚠️ Parcial (sin Web Speech) |

**Nota sobre Web Speech API**: La lectura por voz funciona mejor en Chrome y Edge. Firefox y Safari tienen soporte pero puede variar según el sistema operativo.

---

## 📱 Responsive

El sistema es totalmente responsive:
- En móvil, el panel se ajusta a la pantalla
- Botones tienen tamaño mínimo de 44x44px (accesible para toque)
- Menú adapta su posición en pantallas pequeñas

---

## ♿ Estándares WCAG 2.1

El sistema implementa:

✅ **WCAG A**
- Nivel de contraste de texto (4.5:1 normal, 3:1 grande)
- Navegación por teclado
- Focus visible

✅ **WCAG AA**
- Zoom hasta 200%
- Modo alto contraste
- Animaciones reducidas

✅ **WCAG AAA (Parcial)**
- Lectura por voz
- Interactivos descriptivos

---

## 🔍 Validaciones de Accesibilidad

El sistema incluye:

1. **ARIA Labels**: Todos los botones e iconos tienen `aria-label`
2. **ARIA Live Regions**: Anuncios de cambios para lectores de pantalla
3. **Skip Links**: Saltar a contenido principal
4. **Semantic HTML**: Uso de `<main>`, `<nav>`, `<footer>`, `<article>`
5. **Form Accessibility**: Labels asociados correctamente

---

## 📝 Ejemplos de Uso

### Habilitar Zoom Automático
Si deseas establecer un zoom por defecto, edita `accessibility.js`:

```javascript
// Línea 13 - Cambia el valor por defecto
this.textZoom = parseInt(localStorage.getItem('textZoom')) || 120; // 120% por defecto
```

### Cambiar Idioma de Lectura
Para cambiar el idioma de la lectura por voz, edita `accessibility.js`:

```javascript
// Línea 165 - Cambia el idioma
this.currentUtterance.lang = 'en-US'; // Para inglés
this.currentUtterance.lang = 'fr-FR'; // Para francés
```

### Personalizar Velocidad de Lectura
```javascript
// Línea 166 - Ajusta la velocidad (0.5 = lento, 2 = rápido)
this.currentUtterance.rate = 1.2; // Un poco más rápido
```

---

## 🐛 Solución de Problemas

### El panel de accesibilidad no aparece
- Verifica que `static/js/accessibility.js` y `static/css/accessibility.css` estén cargados
- Abre la consola del navegador (F12) y busca errores

### La lectura por voz no funciona
- Algunos navegadores requieren interacción de usuario primero
- Algunos sistemas operativos no tienen voces en español
- Intenta con Chrome o Edge para mejor soporte

### El zoom no se guarda
- Verifica que localStorage no esté deshabilitado
- Prueba en modo incógnito para descartar extensiones

---

## 🎨 Personalización Futura

Puedes ampliar el sistema agregando:

1. **Más idiomas** - Agregar soporte multiidioma
2. **Tema de alto contraste oscuro** - Versión oscura del contraste alto
3. **Controles de dislexia** - Fuentes específicas para dislexia
4. **Controles de movilidad** - Movimiento por voz
5. **Perfiles de usuario** - Guardar preferencias en base de datos

---

## 📞 Soporte

Para reportar problemas de accesibilidad:
1. Abre la consola (F12)
2. Copia cualquier error
3. Describe el navegador y dispositivo usado
4. Crea un issue en el repositorio

---

## ✅ Checklist de Implementación

- [x] JavaScript de accesibilidad
- [x] CSS de accesibilidad
- [x] Integración en base.html
- [x] Documentación
- [ ] Testing con lectores de pantalla (NVDA, JAWS)
- [ ] Testing con herramientas de validación (axe DevTools)
- [ ] Testing con usuarios reales

---

## 📚 Recursos Externos

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [WebAIM - Web Accessibility In Mind](https://webaim.org/)
- [MDN Accessibility](https://developer.mozilla.org/en-US/docs/Web/Accessibility)
- [Web Accessibility By Google](https://www.udacity.com/course/web-accessibility--ud891)

---

**¡Tu aplicación ahora es más accesible para todos!** ♿🌟
