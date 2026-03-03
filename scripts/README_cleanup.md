### Cambios realizados:

1. **Consolidación de scripts**:
   - Se eliminó el script `create_admin_user.py` ya que su funcionalidad estaba cubierta por `create_initial_users.py`.

2. **Actualización de `render.yaml`**:
   - Se cambió el script ejecutado en `releaseCommand` para usar `create_initial_users.py`.

3. **Variables de entorno**:
   - Se agregaron `ADMIN_USERNAME`, `ADMIN_EMAIL` y `ADMIN_PASSWORD` en `render.yaml` para la creación de usuarios administradores en Render.

### Próximos pasos:
- Verificar que las variables de entorno estén configuradas correctamente en Render.
- Probar el despliegue para confirmar que el usuario administrador se crea exitosamente.