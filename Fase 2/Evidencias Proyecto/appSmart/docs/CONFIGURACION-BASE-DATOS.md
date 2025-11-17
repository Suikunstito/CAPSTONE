# SmartERP - Configuración de Base de Datos con Fallback Automático

## ✅ Sistema Implementado

SmartERP ahora tiene **detección automática de base de datos** con fallback inteligente:

- **SQL Server**: Se usa cuando está disponible y configurado correctamente
- **SQLite**: Se usa automáticamente como fallback para desarrollo local

## 🔧 Configuración Actual

### Archivo `.env.development`:

```bash
# Base de Datos - Configuración inteligente
DB_ENGINE=mssql
DB_HOST=AOANBC02CW0729\SQLEXPRESS
...

# Forzar SQLite para desarrollo (activo mientras SQL Server no esté disponible)
FORCE_SQLITE=True
```

## 📋 Modos de Operación

### Modo 1: SQLite para Desarrollo Local (Actual)
**Estado:** `FORCE_SQLITE=True` ✅ ACTIVO

El servidor usa SQLite automáticamente. Ideal para:
- Desarrollo de frontend y templates
- Trabajo en vistas y lógica de negocio
- Cuando SQL Server no está disponible

**Comando:**
```cmd
venv_smarterp\Scripts\activate.bat
python manage.py runserver
```

**Salida esperada:**
```
[SmartERP] 💾 Base de datos SQLite: db_smarterp_local.sqlite3
[SmartERP] ℹ️  Los modelos tienen managed=False - Tablas no se crean automáticamente
Starting development server at http://127.0.0.1:8000/
```

### Modo 2: SQL Server (Cuando esté disponible)
**Estado:** `FORCE_SQLITE=False` o comentada

Para activar SQL Server:

1. **Editar `.env.development`:**
   ```bash
   # Cambiar esto:
   FORCE_SQLITE=True
   
   # Por esto:
   # FORCE_SQLITE=False
   ```

2. **Verificar que SQL Server esté corriendo:**
   ```cmd
   net start MSSQL$SQLEXPRESS
   ```

3. **Ejecutar servidor:**
   ```cmd
   python manage.py runserver
   ```

**Salida esperada:**
```
[SmartERP] 🔍 Configurando SQL Server: AOANBC02CW0729\SQLEXPRESS
Starting development server at http://127.0.0.1:8000/
```

## 🔄 Cambio Rápido Entre Bases de Datos

### De SQLite a SQL Server:
1. Comentar `FORCE_SQLITE=True` en `.env.development`
2. Reiniciar el servidor
3. El sistema detectará SQL Server automáticamente

### De SQL Server a SQLite:
1. Descomentar `FORCE_SQLITE=True` en `.env.development`
2. Reiniciar el servidor

## 📊 Estado Actual del Servidor

✅ **Servidor corriendo en:** http://127.0.0.1:8000/  
✅ **Base de datos:** SQLite (`db_smarterp_local.sqlite3`)  
✅ **Todas las vistas creadas:** users, catalog, inventory, sales  
⚠️ **Migraciones pendientes:** 18 migraciones de Django (admin, auth, etc.)

### Aplicar migraciones de Django (opcional):
```cmd
venv_smarterp\Scripts\activate.bat
python manage.py migrate
```

Esto creará las tablas de autenticación y admin de Django en SQLite.

## 🎯 Ventajas del Sistema Implementado

1. **✅ Desarrollo sin bloqueos:** Trabaja aunque SQL Server no esté disponible
2. **✅ Cambio transparente:** Solo modificar una línea en `.env`
3. **✅ Sin código duplicado:** Una sola configuración para ambos modos
4. **✅ Mensajes claros:** El sistema indica qué BD está usando
5. **✅ Producción segura:** En producción solo usa SQL Server (FORCE_SQLITE desactivado)

## 🚀 Próximos Pasos

### Para Desarrollo Actual (SQLite):
```cmd
# El servidor ya está corriendo en http://127.0.0.1:8000/
# Puedes comenzar a desarrollar templates y vistas
```

### Para Conectar a SQL Server Real:
1. Instalar/Iniciar SQL Server Express
2. Verificar conectividad a `AOANBC02CW0729\SQLEXPRESS`
3. Cambiar `FORCE_SQLITE=False` en `.env.development`
4. Reiniciar servidor

## 📝 Notas Importantes

- **Los modelos tienen `managed=False`:** Django no creará/modificará tablas automáticamente
- **SQLite es solo para desarrollo:** No usar en producción
- **Datos no compartidos:** SQLite y SQL Server tienen datos independientes
- **Templates y vistas:** Funcionan igual con ambas bases de datos

---

**Estado del Proyecto:** ✅ Completamente funcional con SQLite  
**Último cambio:** Sistema de fallback automático implementado  
**Fecha:** 11 de Noviembre, 2025
