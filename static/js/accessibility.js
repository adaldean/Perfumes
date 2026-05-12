class AccessibilityManager {
    constructor() {
        this.textZoom = parseInt(localStorage.getItem('textZoom')) || 100;
        this.voiceReading = localStorage.getItem('voiceReading') === 'true';
        this.highContrast = localStorage.getItem('highContrast') === 'true';
        this.readingMode = localStorage.getItem('readingMode') === 'true';
        this.readingSpeed = parseFloat(localStorage.getItem('readingSpeed')) || 1.0;
        this.isReading = false;
        this.synth = window.speechSynthesis;
        this.currentUtterance = null;
        this.skipLinksAdded = false;
        this.userMoved = false; // whether user repositioned the panel

        this.init();
    }

    init() {
        this.createPanel();
        this.setupSkipLinks();
        this.improveSemanticHTML();
        this.addARIA();
        this.applyStoredSettings();
        this.setupKeyboardNavigation();
    }

    createPanel() {
        const panel = document.createElement('div');
        panel.className = 'accessibility-panel';
        panel.id = 'accessibility-panel';
        panel.innerHTML = `
            <button id="toggle-accessibility" class="accessibility-toggle" 
                    title="Abrir/Cerrar panel de accesibilidad" 
                    aria-label="Abrir panel de accesibilidad"
                    aria-expanded="false">
                <i class="fas fa-universal-access"></i>
                <span>Accesibilidad</span>
            </button>
            
            <div id="accessibility-menu" class="accessibility-menu" hidden>
                <div class="accessibility-menu-header">
                    <h3 class="accessibility-title">Opciones de Accesibilidad</h3>
                    <button id="close-accessibility" class="accessibility-close" 
                            title="Cerrar panel de accesibilidad"
                            aria-label="Cerrar panel de accesibilidad">
                        ✕
                    </button>
                </div>
                
                <!-- Zoom de Texto -->
                <div class="accessibility-option">
                    <label for="text-zoom">Tamaño de Texto</label>
                    <div class="zoom-controls">
                        <button id="zoom-decrease" class="zoom-btn" 
                                title="Reducir tamaño de texto"
                                aria-label="Reducir tamaño de texto">
                            <i class="fas fa-minus"></i>
                        </button>
                        <span id="zoom-level" class="zoom-display">100%</span>
                        <button id="zoom-increase" class="zoom-btn" 
                                title="Aumentar tamaño de texto"
                                aria-label="Aumentar tamaño de texto">
                            <i class="fas fa-plus"></i>
                        </button>
                        <button id="zoom-reset" class="zoom-btn reset" 
                                title="Resetear tamaño de texto"
                                aria-label="Resetear tamaño de texto">
                            Resetear
                        </button>
                    </div>
                </div>

                <!-- Lectura por Voz -->
                <div class="accessibility-option">
                    <label for="voice-reading-toggle">
                        <input type="checkbox" id="voice-reading-toggle" 
                               aria-label="Activar lectura por voz">
                        <span>Lectura por Voz</span>
                    </label>
                </div>

                <!-- Lectura Guiada -->
                <div class="accessibility-option">
                    <label for="reading-speed-select">Lectura y Velocidad</label>
                    <div class="speed-controls">
                        <button id="guided-reading-btn" class="control-btn" 
                                title="Activar lectura guiada"
                                aria-label="Iniciar lectura guiada del contenido">
                            <i class="fas fa-book"></i> Lectura Guiada
                        </button>
                        <select id="reading-speed-select" class="control-select" aria-label="Seleccionar velocidad de lectura">
                            <option value="0.7">Lenta</option>
                            <option value="1.0">Normal</option>
                            <option value="1.5">Rápida</option>
                        </select>
                    </div>
                </div>

                <!-- Contraste Alto -->
                <div class="accessibility-option">
                    <label for="high-contrast-toggle">
                        <input type="checkbox" id="high-contrast-toggle" 
                               aria-label="Activar contraste alto">
                        <span>Contraste Alto</span>
                    </label>
                </div>

                <!-- Modo Lectura -->
                <div class="accessibility-option">
                    <label for="reading-mode-toggle">
                        <input type="checkbox" id="reading-mode-toggle" 
                               aria-label="Activar modo lectura">
                        <span>Modo Lectura</span>
                    </label>
                </div>

                <!-- Anuncio Lector -->
                <div class="accessibility-option">
                    <button id="stop-reading-btn" class="control-btn danger" 
                            title="Detener lectura actual"
                            aria-label="Detener lectura por voz">
                        <i class="fas fa-stop"></i> Detener Lectura
                    </button>
                </div>

                <!-- Navegación rápida -->
                <div class="accessibility-option">
                    <label>Accesos Rápidos</label>
                    <div class="accessibility-shortcuts">
                        <a href="#main-content" class="skip-link">Ir al contenido principal</a>
                        <a href="#navigation" class="skip-link">Ir a navegación</a>
                        <a href="#footer" class="skip-link">Ir al pie de página</a>
                    </div>
                </div>

                <!-- Info Accesibilidad -->
                <div class="accessibility-info">
                    <p>💡 <strong>Atajo de teclado:</strong></p>
                    <ul>
                        <li>Tab: Navegar elementos</li>
                        <li>Enter: Activar botón</li>
                        <li>Alt + A: Abrir accesibilidad</li>
                        <li>Alt + R: Lectura por voz</li>
                    </ul>
                </div>
            </div>

            <!-- Anunciador ARIA para lectores de pantalla -->
            <div id="aria-announcer" class="sr-only" role="status" aria-live="polite" aria-atomic="true"></div>
        `;

        document.body.insertBefore(panel, document.body.firstChild);
        // Ensure panel position is appropriate for current viewport
        this.resetPanelPositionForViewport();
        this.attachEventListeners();
    }

    /**
     * Adjunta listeners a los controles
     */
    attachEventListeners() {
        const toggleBtn = document.getElementById('toggle-accessibility');
        const closeBtn = document.getElementById('close-accessibility');
        const menu = document.getElementById('accessibility-menu');
        const panel = document.getElementById('accessibility-panel');
        const recomputeMenuPlacement = () => this.updateMenuPlacement();
        
        // Variables para drag
        let isDragging = false;
        let dragStartX = 0;
        let dragStartY = 0;
        let dragStartPanelLeft = 0;
        let dragStartPanelTop = 0;
        let dragThreshold = 5; // píxeles mínimos para considerar un drag
        let dragDistance = 0;
        
        const toggleMenu = () => {
            const isExpanded = menu.hasAttribute('hidden');
            if (isExpanded) {
                menu.removeAttribute('hidden');
                toggleBtn.setAttribute('aria-expanded', 'true');
                this.updateMenuPlacement();
            } else {
                menu.setAttribute('hidden', '');
                toggleBtn.setAttribute('aria-expanded', 'false');
                menu.classList.remove('menu-open-up', 'menu-open-down', 'menu-open-left', 'menu-open-right');
            }
        };

        // Pointer events (unified for mouse/touch/pen)
        toggleBtn.addEventListener('pointerdown', (e) => {
            if (e.isPrimary === false) return;
            isDragging = true;
            dragStartX = e.clientX;
            dragStartY = e.clientY;
            dragDistance = 0;
            const rect = panel.getBoundingClientRect();
            dragStartPanelLeft = rect.left;
            dragStartPanelTop = rect.top;
            try { toggleBtn.setPointerCapture && toggleBtn.setPointerCapture(e.pointerId); } catch (err) {}
            e.preventDefault(); // Evita que se disparen mousedown/touchstart extras de forma predeterminada
        });

        document.addEventListener('pointermove', (e) => {
            if (!isDragging) return;
            if (e.isPrimary === false) return;
            const deltaX = e.clientX - dragStartX;
            const deltaY = e.clientY - dragStartY;
            dragDistance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
            if (dragDistance > dragThreshold) {
                let newLeft = dragStartPanelLeft + deltaX;
                let newTop = dragStartPanelTop + deltaY;
                const minMargin = 10;
                const btnW = toggleBtn.offsetWidth || 64;
                const btnH = toggleBtn.offsetHeight || 64;
                newLeft = Math.max(minMargin, Math.min(newLeft, window.innerWidth - minMargin - btnW));
                newTop = Math.max(minMargin, Math.min(newTop, window.innerHeight - minMargin - btnH));
                panel.style.left = newLeft + 'px';
                panel.style.top = newTop + 'px';
                panel.style.transform = 'none';
                panel.style.position = 'fixed';
            }
        });

        document.addEventListener('pointerup', (e) => {
            if (!isDragging) return;
            if (e.isPrimary === false) return;
            if (dragDistance <= dragThreshold) {
                toggleMenu();
            } else {
                this.userMoved = true;
            }
            isDragging = false;
            try { toggleBtn.releasePointerCapture && toggleBtn.releasePointerCapture(e.pointerId); } catch (err) {}
        });

        closeBtn.addEventListener('click', () => {
            menu.setAttribute('hidden', '');
            toggleBtn.setAttribute('aria-expanded', 'false');
            menu.classList.remove('menu-open-up', 'menu-open-down', 'menu-open-left', 'menu-open-right');
            toggleBtn.focus();
        });

        // Zoom de texto
        document.getElementById('zoom-increase').addEventListener('click', () => this.increaseZoom());
        document.getElementById('zoom-decrease').addEventListener('click', () => this.decreaseZoom());
        document.getElementById('zoom-reset').addEventListener('click', () => this.resetZoom());

        // Lectura por voz
        document.getElementById('voice-reading-toggle').addEventListener('change', (e) => {
            this.voiceReading = e.target.checked;
            localStorage.setItem('voiceReading', this.voiceReading);
            this.announce(this.voiceReading ? 'Lectura por voz activada' : 'Lectura por voz desactivada');
        });

        // Lectura guiada
        document.getElementById('guided-reading-btn').addEventListener('click', () => this.startGuidedReading());

        // Velocidad de lectura
        document.getElementById('reading-speed-select').addEventListener('change', (e) => {
            this.readingSpeed = parseFloat(e.target.value);
            localStorage.setItem('readingSpeed', this.readingSpeed.toString());
            const selectedOption = e.target.options[e.target.selectedIndex];
            this.announce(`Velocidad de lectura: ${selectedOption.text}`);
        });

        // Contraste alto
        document.getElementById('high-contrast-toggle').addEventListener('change', (e) => {
            this.highContrast = e.target.checked;
            localStorage.setItem('highContrast', this.highContrast);
            this.toggleHighContrast();
            this.announce(this.highContrast ? 'Contraste alto activado' : 'Contraste alto desactivado');
        });

        // Modo lectura
        document.getElementById('reading-mode-toggle').addEventListener('change', (e) => {
            this.readingMode = e.target.checked;
            localStorage.setItem('readingMode', this.readingMode);
            this.toggleReadingMode();
            this.announce(this.readingMode ? 'Modo lectura activado' : 'Modo lectura desactivado');
        });

        // Detener lectura
        document.getElementById('stop-reading-btn').addEventListener('click', () => this.stopReading());

        window.addEventListener('resize', recomputeMenuPlacement);
    }

    /**
     * Ajusta la posición del panel si el usuario no lo ha movido.
     */
    resetPanelPositionForViewport() {
        const panel = document.getElementById('accessibility-panel');
        if (!panel) return;
        
        // No sobrescribir la posición si el usuario la ha personalizado
        if (this.userMoved) return;
        
        // Posición inferior izquierda por defecto (evita colisión con chatbot)
        panel.style.position = 'fixed';
        panel.style.top = 'auto';
        panel.style.right = 'auto';
        panel.style.left = '20px';
        panel.style.bottom = '20px';
        panel.style.transform = 'none';

        // Permitimos que la lógica direccional (updateMenuPlacement)
        // se encargue de posicionar el menú.
        const menu = document.getElementById('accessibility-menu');
        if (menu) {
             menu.style.position = '';
             menu.style.left = '';
             menu.style.right = '';
             menu.style.top = '';
             menu.style.bottom = '';
             menu.style.transform = '';
        }
    }

    /**
     * Calcula la mejor dirección para abrir el panel según el espacio disponible.
     */
    updateMenuPlacement() {
        const panel = document.getElementById('accessibility-panel');
        const menu = document.getElementById('accessibility-menu');
        const toggleBtn = document.getElementById('toggle-accessibility');

        if (!panel || !menu || !toggleBtn || menu.hasAttribute('hidden')) {
            return;
        }

        // Remueve clases de dirección
        menu.classList.remove('menu-open-up', 'menu-open-down', 'menu-open-left', 'menu-open-right');

        // Para obtener el tamaño real sin que afecte el CSS actual o posiciones recortadas:
        menu.style.position = 'fixed';
        menu.style.top = '0px';
        menu.style.left = '0px';
        menu.style.transform = 'none';

        const margin = 12;
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;
        const toggleRect = toggleBtn.getBoundingClientRect();
        
        // Ahora medimos el menú
        const menuRect = menu.getBoundingClientRect();

        const spaceAbove = toggleRect.top - margin;
        const spaceBelow = viewportHeight - toggleRect.bottom - margin;
        const spaceLeft = toggleRect.left - margin;
        const spaceRight = viewportWidth - toggleRect.right - margin;

        const fitsBelow = spaceBelow >= menuRect.height;
        const fitsAbove = spaceAbove >= menuRect.height;
        const fitsRight = spaceRight >= menuRect.width;
        const fitsLeft = spaceLeft >= menuRect.width;

        let placement = 'up';

        if (fitsBelow && !fitsAbove) {
            placement = 'down';
        } else if (fitsAbove && !fitsBelow) {
            placement = 'up';
        } else if (fitsRight && !fitsLeft) {
            placement = 'right';
        } else if (fitsLeft && !fitsRight) {
            placement = 'left';
        } else {
            const roomAbove = spaceAbove - menuRect.height;
            const roomBelow = spaceBelow - menuRect.height;
            const roomLeft = spaceLeft - menuRect.width;
            const roomRight = spaceRight - menuRect.width;
            const candidate = [
                { side: 'up', room: roomAbove },
                { side: 'down', room: roomBelow },
                { side: 'left', room: roomLeft },
                { side: 'right', room: roomRight },
            ].sort((a, b) => b.room - a.room)[0];
            placement = candidate && candidate.room > -Infinity ? candidate.side : 'up';
        }

        menu.classList.add(`menu-open-${placement}`);

        const menuStyle = menu.style;
        menuStyle.position = 'fixed';
        menuStyle.right = '';
        menuStyle.bottom = '';
        menuStyle.transform = '';

        if (placement === 'down') {
            menuStyle.top = `${toggleRect.bottom + 10}px`;
            menuStyle.left = `${Math.max(margin, Math.min(toggleRect.left, viewportWidth - menuRect.width - margin))}px`;
        } else if (placement === 'left') {
            menuStyle.top = `${Math.max(margin, Math.min(toggleRect.top - (menuRect.height / 2), viewportHeight - menuRect.height - margin))}px`;
            menuStyle.left = `${Math.max(margin, toggleRect.left - menuRect.width - 10)}px`;
        } else if (placement === 'right') {
            menuStyle.top = `${Math.max(margin, Math.min(toggleRect.top - (menuRect.height / 2), viewportHeight - menuRect.height - margin))}px`;
            menuStyle.left = `${Math.min(viewportWidth - menuRect.width - margin, toggleRect.right + 10)}px`;
        } else {
            menuStyle.top = '';
            menuStyle.bottom = `${Math.max(margin, viewportHeight - toggleRect.top + 10)}px`;
            menuStyle.left = `${Math.max(margin, Math.min(toggleRect.left, viewportWidth - menuRect.width - margin))}px`;
        }
    }

    /**
     * Aumenta el zoom de texto
     */
    increaseZoom() {
        if (this.textZoom < 200) {
            this.textZoom += 10;
            this.applyZoom();
            this.announce(`Tamaño de texto: ${this.textZoom}%`);
        }
    }

    /**
     * Reduce el zoom de texto
     */
    decreaseZoom() {
        if (this.textZoom > 80) {
            this.textZoom -= 10;
            this.applyZoom();
            this.announce(`Tamaño de texto: ${this.textZoom}%`);
        }
    }

    /**
     * Resetea el zoom de texto
     */
    resetZoom() {
        this.textZoom = 100;
        this.applyZoom();
        this.announce('Tamaño de texto reiniciado');
    }

    /**
     * Aplica el zoom al documento
     */
    applyZoom() {
        const zoomFactor = this.textZoom / 100;
        document.documentElement.style.fontSize = (16 * zoomFactor) + 'px';
        document.getElementById('zoom-level').textContent = this.textZoom + '%';
        localStorage.setItem('textZoom', this.textZoom);
    }

    /**
     * Alterna el modo de contraste alto
     */
    toggleHighContrast() {
        if (this.highContrast) {
            document.body.classList.add('high-contrast');
        } else {
            document.body.classList.remove('high-contrast');
        }
    }

    /**
     * Alterna el modo lectura
     */
    toggleReadingMode() {
        if (this.readingMode) {
            document.body.classList.add('reading-mode');
        } else {
            document.body.classList.remove('reading-mode');
        }
    }

    /**
     * Inicia lectura por voz del contenido
     */
    startGuidedReading() {
        // Verificar disponibilidad de Web Speech API
        if (!window.speechSynthesis) {
            this.announce('La lectura por voz no está disponible en tu navegador.');
            console.error('Web Speech API no disponible');
            return;
        }

        if (this.isReading) {
            this.stopReading();
            return;
        }

        // Buscar contenido en varios lugares posibles
        let mainContent = document.querySelector('main') || 
                          document.querySelector('[role="main"]') ||
                          document.querySelector('article') || 
                          document.querySelector('.content') ||
                          document.querySelector('.container');
        
        // Si no encuentra nada, usa body pero excluye header y footer
        if (!mainContent) {
            mainContent = document.querySelector('body');
        }
        
        const text = this.extractReadableText(mainContent);
        
        if (!text || text.length < 10) {
            this.announce('No hay suficiente contenido para leer. Asegúrate de estar en una página con contenido.');
            console.warn('Contenido insuficiente:', text ? text.length : 0, 'caracteres');
            return;
        }

        console.log('Iniciando lectura de', text.length, 'caracteres');
        this.isReading = true;
        this.currentUtterance = new SpeechSynthesisUtterance(text);
        this.currentUtterance.lang = 'es-ES';
        this.currentUtterance.rate = this.readingSpeed;
        this.currentUtterance.pitch = 1;
        this.currentUtterance.volume = 1;

        this.currentUtterance.onend = () => {
            this.isReading = false;
            this.announce('Lectura completada');
        };

        this.currentUtterance.onerror = (event) => {
            console.error('Error en lectura por voz:', event);
            this.announce('Error en lectura por voz');
            this.isReading = false;
        };

        try {
            this.synth.speak(this.currentUtterance);
            this.announce('Iniciando lectura guiada');
        } catch (error) {
            console.error('Error al intentar leer:', error);
            this.announce('Error: La lectura por voz no está disponible en tu navegador.');
            this.isReading = false;
        }
    }

    /**
     * Extrae texto legible de un elemento
     */
    extractReadableText(element) {
        const clone = element.cloneNode(true);
        
        // Remover elementos no deseados más exhaustivamente
        const selectorsToRemove = [
            'script', 
            'style', 
            'nav', 
            'header',
            'footer',
            '.accessibility-panel', 
            '#accessibility-panel',
            '.chatbot',
            '.chat-widget',
            '[role="navigation"]',
            '[style*="display: none"]'
        ];
        
        selectorsToRemove.forEach(sel => {
            try {
                clone.querySelectorAll(sel).forEach(el => el.remove());
            } catch(e) {
                // Ignorar errores de selectores
            }
        });

        // Obtener el texto limpio
        let text = clone.innerText.trim();
        
        // Limpar espacios múltiples
        text = text.replace(/\s+/g, ' ');
        
        return text;
    }

    /**
     * Detiene la lectura actual
     */
    stopReading() {
        this.synth.cancel();
        this.isReading = false;
        this.announce('Lectura detenida');
    }

    /**
     * Anuncia un mensaje para lectores de pantalla
     */
    announce(message) {
        const announcer = document.getElementById('aria-announcer');
        if (announcer) {
            announcer.textContent = message;
        }
    }

    /**
     * Configura navegación por teclado mejorada
     */
    setupKeyboardNavigation() {
        document.addEventListener('keydown', (e) => {
            // Alt + A: Abrir panel de accesibilidad
            if (e.altKey && e.key === 'a') {
                e.preventDefault();
                document.getElementById('toggle-accessibility').click();
            }

            // Alt + R: Iniciar/Detener lectura
            if (e.altKey && e.key === 'r') {
                e.preventDefault();
                if (this.isReading) {
                    this.stopReading();
                } else {
                    document.getElementById('guided-reading-btn').click();
                }
            }

            // Alt + +: Aumentar zoom
            if (e.altKey && (e.key === '+' || e.key === '=')) {
                e.preventDefault();
                this.increaseZoom();
            }

            // Alt + -: Disminuir zoom
            if (e.altKey && e.key === '-') {
                e.preventDefault();
                this.decreaseZoom();
            }
        });

        // Mejorar tabulación
        this.makeElementsKeyboardAccessible();
    }

    /**
     * Hace elementos accesibles por teclado
     */
    makeElementsKeyboardAccessible() {
        document.addEventListener('click', (e) => {
            // Si la lectura por voz está activa, buscar el elemento interactivo más cercano.
            if (this.voiceReading) {
                const interactiveElement = e.target.closest('button, a, [role="button"], [role="link"]');
                if (interactiveElement) {
                    this.readElement(interactiveElement);
                }
            }
        });

        // Leer elemento al recibir foco con el tabulador
        document.addEventListener('focusin', (e) => {
            if (this.voiceReading && e.target && e.target !== document.body) {
                // Llama a la función de lectura para el elemento que acaba de recibir el foco.
                this.readElement(e.target);
            }
        });

        // Hacer divs clicables navegables
        const interactiveElements = document.querySelectorAll('[role="button"], [onclick]');
        interactiveElements.forEach(el => {
            if (!el.hasAttribute('tabindex')) {
                el.setAttribute('tabindex', '0');
            }
        });
    }

    /**
     * Lee un elemento específico
     */
    readElement(element) {
        // Priorizar aria-label, luego title, y finalmente el texto visible.
        const textToRead = element.getAttribute('aria-label') || element.getAttribute('title') || element.innerText || element.textContent;

        if (textToRead && textToRead.trim()) {
            // Crear el audio que se va a reproducir.
            const utterance = new SpeechSynthesisUtterance(textToRead.trim());
            utterance.lang = 'es-ES';
            utterance.rate = this.readingSpeed;
            utterance.onerror = (event) => {
                console.error('Error en lectura por voz de elemento:', event);
                this.announce('Error al leer el elemento.');
            };

            // Asignar a la propiedad de la clase para evitar que sea eliminado por el recolector de basura.
            this.currentUtterance = utterance;

            // Lógica diferenciada: si está hablando, hay que interrumpir. Si no, solo hablar.
            if (this.synth.speaking) {
                this.synth.cancel();
                // WORKAROUND: Esperar un momento después de cancelar. Es un bug conocido de los navegadores.
                setTimeout(() => this.synth.speak(this.currentUtterance), 100);
            } else {
                this.synth.speak(this.currentUtterance);
            }
        }
    }

    /**
     * Agrega enlaces de salto (skip links)
     */
    setupSkipLinks() {
        this.skipLinksAdded = true;
    }

    /**
     * Mejora la semántica HTML
     */
    improveSemanticHTML() {
        // Asegurar que main content tenga ID
        const main = document.querySelector('main');
        if (main && !main.id) {
            main.id = 'main-content';
        }

        // Asegurar que nav tenga ID
        const nav = document.querySelector('nav');
        if (nav && !nav.id) {
            nav.id = 'navigation';
        }

        // Asegurar que footer tenga ID
        const footer = document.querySelector('footer');
        if (footer && !footer.id) {
            footer.id = 'footer';
        }

        // Agregar roles a elementos importantes
        document.querySelectorAll('.product-card, [class*="card"]').forEach(el => {
            if (!el.hasAttribute('role')) {
                el.setAttribute('role', 'article');
            }
        });
    }

    /**
     * Agrega atributos ARIA
     */
    addARIA() {
        // Agregar alt text a imágenes sin él
        document.querySelectorAll('img:not([alt])').forEach((img, index) => {
            const altText = img.getAttribute('title') || `Imagen ${index + 1}`;
            img.setAttribute('alt', altText);
        });

        // Agregar aria-label a botones sin texto
        document.querySelectorAll('button:not([aria-label])').forEach(btn => {
            const text = btn.innerText || btn.title;
            if (text) {
                btn.setAttribute('aria-label', text.trim());
            }
        });

        // Agregar aria-label a enlaces sin texto
        document.querySelectorAll('a:not([aria-label])').forEach(link => {
            const text = link.innerText || link.title;
            if (text) {
                link.setAttribute('aria-label', text.trim());
            }
        });
    }

    /**
     * Aplica configuración guardada
     */
    applyStoredSettings() {
        this.applyZoom();
        this.toggleHighContrast();
        this.toggleReadingMode();

        // Actualizar checkboxes
        document.getElementById('voice-reading-toggle').checked = this.voiceReading;
        document.getElementById('high-contrast-toggle').checked = this.highContrast;
        document.getElementById('reading-mode-toggle').checked = this.readingMode;

        // Actualizar velocidad de lectura
        document.getElementById('reading-speed-select').value = this.readingSpeed.toString();
    }
}

// Inicializar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.accessibilityManager = new AccessibilityManager();
        // Ajustar al cambiar el tamaño
        window.addEventListener('resize', () => window.accessibilityManager.resetPanelPositionForViewport());
    });
} else {
    window.accessibilityManager = new AccessibilityManager();
    window.addEventListener('resize', () => window.accessibilityManager.resetPanelPositionForViewport());
}
