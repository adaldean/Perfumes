# Django Perfumes Project - Comprehensive Feature Analysis

**Analysis Date:** May 12, 2026  
**Project:** Aura Essence - Perfume E-commerce Platform

---

## Table of Contents
1. [Shopping Cart Functionality](#1-shopping-cart-functionality)
2. [Email Verification Code System](#2-email-verification-code-system)
3. [AWS S3 Image Upload Configuration](#3-aws-s3-image-upload-configuration)

---

## 1. Shopping Cart Functionality

### Overview
The shopping cart implements a **dual-system architecture** supporting both anonymous and authenticated users:
- **Anonymous Users:** Session-based cart (temporary, browser-only)
- **Authenticated Users:** Database-backed cart (persistent)

### 1.1 Data Models

**Location:** `apps/orders/models.py` (lines 46-113)

#### Carrito Model
```python
class Carrito(models.Model):
    """Persistent cart for authenticated users"""
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='carrito')
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    @property
    def total(self):
        """Total cart value"""
        return sum(item.subtotal for item in self.items.all())
    
    @property
    def cantidad_items(self):
        """Total item count"""
        return sum(item.cantidad for item in self.items.all())
```

#### ItemCarrito Model
```python
class ItemCarrito(models.Model):
    """Individual items in cart"""
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    @property
    def subtotal(self):
        """Line item total (price × quantity)"""
        return self.producto.precio * self.cantidad
    
    class Meta:
        unique_together = ('carrito', 'producto')  # One product per cart
```

### 1.2 Cart Session Logic

**Location:** `apps/api/auth_views.py` (lines 161-243)

#### Session Storage Functions
```python
def obtener_carrito_sesion(request):
    """Retrieve cart from session: {'producto_id': cantidad, ...}"""
    return request.session.get('carrito', {})

def guardar_carrito_sesion(request, carrito_dict):
    """Save cart to session and mark as modified"""
    request.session['carrito'] = carrito_dict
    request.session.modified = True

def migrar_carrito_sesion(request, user):
    """
    Migrate session cart to database on login/registration.
    - Executed after authentication
    - Uses atomic transaction
    - Sums quantities if product already exists
    """
    carrito_sesion = obtener_carrito_sesion(request)
    if not carrito_sesion:
        return
    
    try:
        carrito_user = Carrito.objects.get(usuario=user)
        with transaction.atomic():
            for producto_id, cantidad in carrito_sesion.items():
                try:
                    producto = Producto.objects.get(id=int(producto_id))
                    item, created = ItemCarrito.objects.get_or_create(
                        carrito=carrito_user,
                        producto=producto,
                        defaults={'cantidad': 0}
                    )
                    item.cantidad += int(cantidad)
                    item.save()
                except Producto.DoesNotExist:
                    continue
        guardar_carrito_sesion(request, {})
    except Carrito.DoesNotExist:
        pass
```

### 1.3 API Endpoints

**Location:** `apps/orders/api_views.py` (lines 23-155)

#### GET /api/carrito/ - Retrieve Cart
**Function:** `obtener_carrito(request)`

**Response (Authenticated):**
```json
{
    "exito": true,
    "items": [
        {
            "id": 1,
            "producto_id": 5,
            "nombre": "Chanel No. 5",
            "precio": 150.00,
            "cantidad": 2,
            "subtotal": 300.00,
            "imagen": "https://bucket.s3.amazonaws.com/productos/image.jpg"
        }
    ],
    "total": 300.00,
    "cantidad_items": 2
}
```

**Response (Anonymous):**
```json
{
    "exito": true,
    "items": [...],
    "total": 0,
    "cantidad_items": 0
}
```

#### POST /api/carrito/ - Add Product
**Function:** `agregar_carrito(request)`

**Request Body:**
```json
{
    "producto_id": 5,
    "cantidad": 2
}
```

**Response:**
```json
{
    "exito": true,
    "mensaje": "Producto agregado"
}
```

**Logic:**
- If authenticated: Creates/updates `ItemCarrito` record
- If anonymous: Updates session dict and increments quantity
- If product exists in cart: Adds to existing quantity

#### DELETE /api/carrito/ - Remove Product
**Function:** `eliminar_de_carrito(request)`

**Request Body:**
```json
{
    "producto_id": 5
}
```

**Response:**
```json
{
    "exito": true,
    "mensaje": "Producto eliminado"
}
```

### 1.4 Frontend Implementation

#### Add to Cart Button
**Location:** `templates/catalogo/detalle.html` (lines 171-229)

```html
<!-- Quantity selector -->
<div class="flex items-center border rounded-full w-max">
    <button onclick="updateQuantity(-1)">
        <i class="fa-solid fa-minus"></i>
    </button>
    <input type="number" id="quantity" value="1" min="1" max="{{ producto.stock }}" readonly>
    <button onclick="updateQuantity(1)">
        <i class="fa-solid fa-plus"></i>
    </button>
</div>

<!-- Add to cart button -->
<button onclick="addToCart({{ producto.id }})" id="add-to-cart-btn"
    class="flex-1 bg-brand-dark hover:bg-brand-gold text-white font-bold py-3 px-8 rounded-full">
    <i class="fa-solid fa-cart-shopping"></i>
    <span>Agregar al Carrito</span>
</button>
```

#### JavaScript Cart Function
**Location:** `templates/catalogo/detalle.html` (lines 231-262)

```javascript
async function addToCart(productoId) {
    const btn = document.getElementById('add-to-cart-btn');
    const originalContent = btn.innerHTML;
    const cantidad = parseInt(document.getElementById('quantity').value);

    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Agregando...';

    try {
        const response = await fetch('/api/carrito/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                producto_id: productoId,
                cantidad: cantidad
            })
        });

        const data = await response.json();

        if (data.exito) {
            // Success feedback
            btn.innerHTML = '<i class="fa-solid fa-check"></i> ¡Agregado!';
            btn.classList.replace('bg-brand-dark', 'bg-green-600');
            
            // Update cart badge
            const badge = document.querySelector('.fa-bag-shopping + span');
            if (badge) badge.textContent = data.cantidad_items;

            setTimeout(() => {
                btn.innerHTML = originalContent;
                btn.classList.replace('bg-green-600', 'bg-brand-dark');
                btn.disabled = false;
            }, 2000);
        } else {
            alert('Error: ' + data.error);
            btn.innerHTML = originalContent;
            btn.disabled = false;
        }
    } catch (error) {
        console.error(error);
        alert('Error al conectar con el servidor.');
        btn.innerHTML = originalContent;
        btn.disabled = false;
    }
}
```

#### Cart Counter Badge
**Location:** `templates/header.html` (lines 34-37)

```html
<a href="{% url 'auth:carrito' %}" title="Carrito" class="action-icon cart-trigger">
    <i class="fa-solid fa-cart-shopping"></i>
    <span class="cart-badge">{{ carrito_items_count|default:0 }}</span>
</a>
```

**Updated dynamically via JavaScript after cart operations**

### 1.5 Cart Page
**Location:** `templates/carrito.html`

**Features:**
- Shows all cart items with images, quantities, and prices
- Ability to modify quantities or remove items
- Cart summary with subtotal, shipping (free), and total
- Mercado Pago payment integration
- Login prompt for anonymous users

**Key JavaScript:**
```javascript
async function cargarCarrito() {
    const response = await fetch('/api/carrito/');
    const data = await response.json();
    // Render items and update totals...
}

async function eliminarProducto(productoId) {
    const response = await fetch('/api/carrito/', {
        method: 'DELETE',
        body: JSON.stringify({ producto_id: productoId })
    });
    // Reload cart display...
}
```

### 1.6 Cart Creation on Registration/Login

**Location:** `apps/api/auth_views.py` (lines 104-145), `apps/users/views.py` (lines 179-181)

```python
# On registration
Carrito.objects.get_or_create(usuario=user)
migrar_carrito_sesion(request, user)

# On login
login(request, user)
Carrito.objects.get_or_create(usuario=user)
migrar_carrito_sesion(request, user)
```

### 1.7 URL Configuration
**Location:** `apps/orders/urls.py`

```python
urlpatterns = [
    path('carrito/', views.carrito_view, name='carrito'),  # HTML page
    path('api/carrito/', api_views.carrito_api, name='carrito_api'),  # API endpoints
    path('api/carrito/actualizar/', api_views.carrito_api, name='actualizar_carrito'),
]
```

---

## 2. Email Verification Code System

### Overview
The project uses a **two-layer email verification system**:
1. **Token-based activation** (Django built-in)
2. **OTP backup system** (custom EmailOTP model)
3. **Allauth integration** (EmailAddress verification)

### 2.1 Email Verification Models

**Location:** `apps/users/models.py` (lines 12-21)

#### EmailOTP Model
```python
class EmailOTP(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='otps')
    code = models.CharField(max_length=6)  # 6-digit code
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()  # Set to now + 3 minutes
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"OTP({self.user.username} - {self.code})"
```

#### UserProfile Model
```python
class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    must_change_password = models.BooleanField(default=False)
    # Auto-created on user registration via signal
```

### 2.2 OTP Generation and Sending

**Location:** `apps/users/views.py` (lines 36-103)

#### Generate OTP Code
```python
def _generate_otp_code(length=6):
    """Generate random 6-digit code"""
    return ''.join(random.choices('0123456789', k=length))
```

#### Send OTP Email
```python
def _send_otp_email(user, code):
    """Send OTP code via email"""
    subject = 'Aura Essence: Código temporal de acceso'
    message = (
        f'Tu código de verificación es: {code}\n\n'
        'El código expira en 3 minutos. No compartas este código con nadie.'
    )
    from_email = settings.DEFAULT_FROM_EMAIL
    send_mail(subject, message, from_email, [user.email], fail_silently=False)
```

#### Create Pending OTP
```python
def _create_pending_otp(request, user, next_url):
    """
    Create and send OTP to user.
    - Marks previous unused OTPs as used
    - Stores user ID and next URL in session
    - OTP expires in 3 minutes
    """
    # Mark old OTPs as used
    EmailOTP.objects.filter(
        user=user, 
        is_used=False, 
        expires_at__gte=timezone.now()
    ).update(is_used=True)
    
    # Create new OTP
    code = _generate_otp_code()
    EmailOTP.objects.create(
        user=user,
        code=code,
        expires_at=timezone.now() + timedelta(minutes=3)
    )
    
    # Send email
    _send_otp_email(user, code)
    
    # Store in session
    request.session['otp_user_id'] = user.id
    request.session['otp_next_url'] = next_url
    request.session.modified = True
```

### 2.3 Registration Flow

**Location:** `apps/users/views.py` (lines 278-330)

```python
def signup_view(request):
    """Registration with email activation"""
    if request.method == 'POST':
        # Validate form...
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        # Account starts as inactive
        user.is_active = False
        user.save()
        
        # Send activation email
        _send_activation_email(request, user)
        
        messages.success(request, 'Te enviamos un correo de activación.')
        return redirect('auth:login')
    
    return render(request, 'auth/registro.html')
```

### 2.4 Email Activation Token

**Location:** `apps/users/views.py` (lines 334-362)

#### Send Activation Email
```python
def _send_activation_email(request, user):
    """Send email with activation token link"""
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    activation_link = request.build_absolute_uri(
        reverse('auth:activate', kwargs={'uidb64': uid, 'token': token})
    )
    
    subject = 'Aura Essence: Activa tu cuenta'
    message = f"""
    ¡Hola {user.first_name}!

    Gracias por registrarte en Aura Essence. Para activar tu cuenta, haz clic:

    {activation_link}

    Si no creaste esta cuenta, ignora este mensaje.
    """
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
```

#### Activate Account (Token Verification)
**Location:** `apps/users/views.py` (lines 300-327)

```python
def activate_view(request, uidb64, token):
    """
    Verify activation token and activate account.
    - Decodes user ID from token
    - Checks token validity
    - Sets is_active = True
    - Marks email as verified in Allauth
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()

        # Sync with Allauth
        from allauth.account.models import EmailAddress
        email_obj, created = EmailAddress.objects.get_or_create(
            user=user, 
            email=user.email,
            defaults={'primary': True}
        )
        email_obj.verified = True
        email_obj.save()

        messages.success(request, 'Tu cuenta ha sido activada exitosamente.')
        return redirect('auth:login')
    else:
        messages.error(request, 'El enlace de activación es inválido o ha expirado.')
        return redirect('auth:login')
```

### 2.5 Login Verification

**Location:** `apps/users/views.py` (lines 113-180)

```python
def _email_verified(user):
    """Check if email is verified in Allauth"""
    from allauth.account.models import EmailAddress
    return EmailAddress.objects.filter(
        user=user, 
        email__iexact=user.email, 
        verified=True
    ).exists()

def login_view(request):
    """
    Login with email verification requirement.
    - Checks if email is verified (except admin/staff)
    - Checks if account is active
    """
    if request.method == 'POST':
        user = _authenticate_username_or_email(request, identifier, password)
        
        if user is not None:
            # Check email verification
            if not user.is_staff and not user.is_superuser:
                if not _email_verified(user):
                    return render(request, 'auth/login.html', {
                        'error': 'Tu cuenta aún no ha sido verificada. Por favor, revisa tu correo.'
                    })
            
            # Check if active
            if not user.is_active:
                return render(request, 'auth/login.html', {
                    'error': 'Tu cuenta está pendiente de verificación.'
                })
            
            login(request, user)
            Carrito.objects.get_or_create(usuario=user)
            return redirect('frontend:catalogo')
    
    return render(request, 'auth/login.html')
```

### 2.6 URL Routes

**Location:** `apps/users/urls.py`

```python
urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/', views.signup_view, name='registro'),
    path('activate/<uidb64>/<token>/', views.activate_view, name='activate'),
    # ...
]
```

### 2.7 Email Settings

**Location:** `myproject/settings.py`

```python
# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@aurassentence.com')
```

---

## 3. AWS S3 Image Upload Configuration

### Overview
Images are optionally stored in AWS S3 during production deployment. Falls back to local filesystem if S3 is not configured.

### 3.1 Settings Configuration

**Location:** `myproject/settings.py` (lines 131-171)

#### Conditional S3 Setup
```python
if not DEBUG:
    # Production settings...
    if os.getenv('AWS_ACCESS_KEY_ID'):
        # ===== AWS S3 Configuration =====
        AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
        AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
        AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
        AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
        AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
        AWS_QUERYSTRING_AUTH = False  # Public URLs without signatures
        AWS_S3_FILE_OVERWRITE = False  # Keep versioned files
        AWS_DEFAULT_ACL = None  # Use bucket policy instead
        
        STORAGES = {
            'default': {
                'BACKEND': 'storages.backends.s3boto3.S3Boto3Storage',
            },
            'staticfiles': {
                'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
            },
        }
        
        STATIC_URL = '/static/'
        MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/'
    else:
        # Fallback: Local filesystem storage
        STORAGES = {
            'default': {
                'BACKEND': 'django.core.files.storage.FileSystemStorage',
            },
            'staticfiles': {
                'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
            },
        }
```

### 3.2 Product Image Model

**Location:** `apps/catalog/models.py` (lines 40-72)

```python
class Producto(models.Model):
    """Product model with image upload to S3"""
    # ... other fields ...
    imagen = models.ImageField(
        upload_to='productos/',  # S3 path prefix
        null=True, 
        blank=True
    )
    # ... other fields ...
```

**Image Upload Path:**
- S3: `https://bucket-name.s3.amazonaws.com/productos/image-name.jpg`
- Local: `/media/productos/image-name.jpg`

### 3.3 Image Upload Mixin

**Location:** `apps/orders/models.py` (lines 7-12)

```python
class ImageUploadMixin:
    """Mixin to slugify image names before upload"""
    def save(self, *args, **kwargs):
        if self.imagen:
            self.imagen.name = slugify(self.imagen.name)
        super().save(*args, **kwargs)

# Applied to Pago model
class Pago(models.Model, ImageUploadMixin):
    # ... model fields ...
```

**Purpose:**
- Converts image filenames to URL-safe format
- Prevents special characters in S3 paths
- Example: "My Photo (1).jpg" → "my-photo-1.jpg"

### 3.4 Image Display in Templates

**Location:** `templates/catalogo/detalle.html` (lines 31-44)

```html
<!-- Display product image with fallback -->
{% if producto.imagen %}
    <img src="{{ producto.imagen.url }}" 
         alt="{{ producto.nombre }}"
         class="w-full h-full object-cover">
{% else %}
    <!-- Fallback to Unsplash placeholder -->
    <img src="https://source.unsplash.com/random/800x800/?perfume&sig={{ producto.id }}"
         alt="{{ producto.nombre }}"
         class="w-full h-full object-cover opacity-90">
{% endif %}
```

**In Cart API Response:**
```python
'imagen': item.producto.imagen.url if item.producto.imagen else None
```

### 3.5 S3 Bucket Configuration

**Required AWS S3 Bucket Settings:**

1. **CORS Configuration** (Allow image loading from web)
   ```json
   [
     {
       "AllowedHeaders": ["*"],
       "AllowedMethods": ["GET", "HEAD"],
       "AllowedOrigins": ["https://yourdomain.com"],
       "ExposeHeaders": []
     }
   ]
   ```

2. **Bucket Policy** (Public read access for images)
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Sid": "PublicReadGetObject",
         "Effect": "Allow",
         "Principal": "*",
         "Action": "s3:GetObject",
         "Resource": "arn:aws:s3:::bucket-name/productos/*"
       }
     ]
   }
   ```

3. **Block Public Access Settings:**
   - Block public ACLs: OFF
   - Ignore public ACLs: OFF
   - Block public bucket policies: OFF
   - Restrict public bucket policies: OFF

### 3.6 Media File Management

**Location:** `apps/core/management/commands/migrate_media_to_s3.py`

**Purpose:**
- Command to migrate existing local media files to S3
- Useful when transitioning from local storage to S3
- Updates database file paths

**Usage:**
```bash
python manage.py migrate_media_to_s3
```

### 3.7 Environment Variables Required

```env
# Production S3 Configuration
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_STORAGE_BUCKET_NAME=perfumes-bucket
AWS_S3_REGION_NAME=us-east-1

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@aurassentence.com

# Other essentials
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,*.onrender.com
```

### 3.8 Local Development

**For local development (DEBUG=True):**
- Images stored in `MEDIA_ROOT` (default: `/media/`)
- S3 storage is disabled
- No AWS credentials needed
- Images accessible at `/media/productos/image.jpg`

### 3.9 Production Deployment (Render)

**Why S3 is Required on Render:**
- Render doesn't persist local filesystem between deployments
- Each deploy creates fresh ephemeral storage
- S3 provides persistent media storage across deployments

**Configuration on Render:**
1. Set all AWS environment variables in Render dashboard
2. Django automatically detects and uses S3
3. Images persist across deployments
4. CDN speeds up image delivery

### 3.10 Django Admin Image Upload

**Location:** `apps/catalog/admin.py`

```python
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'precio', 'marca', 'stock', 'activo']
    # Image upload handled automatically through Django Admin
    # Files uploaded directly to S3 or local storage based on configuration
```

---

## Summary

### Shopping Cart
- **Dual-system:** Session for anonymous, database for authenticated
- **API endpoints:** GET, POST, DELETE on `/api/carrito/`
- **Persistence:** Session-to-database migration on login
- **Frontend:** Real-time updates with cart badge counter
- **Integration:** Mercado Pago for checkout

### Email Verification
- **Token-based:** Django token generator + urlsafe encoding
- **OTP backup:** 6-digit code, 3-minute expiration
- **Allauth sync:** EmailAddress verified flag integration
- **Requirements:** Admin users exempt from email verification
- **Flow:** Registration → Email sent → Link click → Account activated

### S3 Image Upload
- **Conditional:** Enabled in production if AWS credentials present
- **Path:** `productos/` prefix in bucket
- **Fallback:** Local FileSystemStorage if no S3
- **Persistence:** Required for platforms like Render
- **Management:** Migration command available for bulk uploads

---

**Last Updated:** May 12, 2026
