# 🚀 Guía de Inicio Rápido - SmartERP

## Tabla de Contenidos
- [Inicio Rápido (30 segundos)](#inicio-rápido)
- [Comandos Principales](#comandos-principales)
- [Desarrollo Diario](#desarrollo-diario)
- [Solución de Problemas](#solución-de-problemas)

---

## 🏃 Inicio Rápido

### 1️⃣ Primera Vez - Configurar Entorno

```cmd
setup-dev.bat
```

Este comando:
- ✅ Crea el entorno virtual Python (`venv_smarterp`)
- ✅ Instala todas las dependencias
- ✅ Configura archivos de entorno
- ✅ Verifica la configuración de Django

### 2️⃣ Ejecutar Servidor de Desarrollo

```cmd
dev.bat
```

El servidor se iniciará en: **http://127.0.0.1:8000/**

---

## 📋 Comandos Principales

### Scripts Disponibles

#### Scripts Principales (Raíz del Proyecto)
| Comando | Descripción | Cuándo Usar |
|---------|-------------|-------------|
| `setup-dev.bat` | ⚙️ Configurar entorno | **Solo la primera vez** |
| `dev.bat` | 🚀 Iniciar desarrollo | **Uso diario** |

#### Scripts Auxiliares (Carpeta `scripts/`)
| Comando | Descripción | Cuándo Usar |
|---------|-------------|-------------|
| `scripts\dev-local.bat` | 💻 Forzar modo local | Sin Docker |
| `scripts\prod.bat` | 🏭 Modo producción | Deploy con Docker |
| `scripts\test.bat` | 🧪 Ejecutar tests | Verificar código |
| `scripts\clean.bat` | 🧹 Limpiar entorno | Reset completo |
| `scripts\quick-setup.bat` | 🔧 Setup alternativo | (legacy, usar setup-dev.bat) |

### Descripción Detallada

#### `setup-dev.bat` - Configuración Inicial
```cmd
setup-dev.bat
```
**Ejecutar solo la primera vez o después de `clean.bat`**

**Qué hace:**
- Verifica Python instalado
- Crea entorno virtual
- Instala dependencias de `requirements/development.txt`
- Configura `.env.development` si no existe
- Verifica configuración de Django

#### `dev.bat` - Desarrollo con Auto-Detección
```cmd
dev.bat
```
**Comando principal para desarrollo diario**

**Detección automática:**
- ✅ **Docker disponible** → Usa `docker-compose up`
- ✅ **Docker no disponible** → Usa entorno local Python
- ✅ **Sin configuración manual** → Todo automático

#### `dev-local.bat` - Forzar Modo Local
```cmd
scripts\dev-local.bat
```
**Usar cuando:**
- Prefieres trabajar sin Docker
- Docker está instalado pero no quieres usarlo
- Desarrollo de frontend/templates sin contenedores

#### `test.bat` - Ejecutar Tests
```cmd
scripts\test.bat
```
**Ejecuta la suite de tests del proyecto**

#### `prod.bat` - Modo Producción
```cmd
scripts\prod.bat
```
**Solo para deployment con Docker Compose en producción**

#### `clean.bat` - Limpiar Todo
```cmd
scripts\clean.bat
```
**⚠️ CUIDADO: Elimina todo y requiere reconfiguración**

Elimina:
- Entorno virtual
- Base de datos SQLite local
- Archivos `__pycache__`
- Archivos compilados `.pyc`

---

## 💻 Desarrollo Diario

### Flujo de Trabajo Típico

```cmd
# 1. Activar entorno (ya hecho por dev.bat)
venv_smarterp\Scripts\activate.bat

# 2. Iniciar servidor
dev.bat

# 3. Abrir navegador
# http://127.0.0.1:8000/
```

### Trabajando con la Base de Datos

#### Usando SQLite (por defecto)
El sistema usa SQLite automáticamente si SQL Server no está disponible.

**Archivo:** `db_smarterp_local.sqlite3`

#### Cambiar a SQL Server
Editar `.env.development`:
```bash
# Comentar esta línea:
# FORCE_SQLITE=True
```

Reiniciar el servidor.

### Comandos Django Útiles

```cmd
# Activar entorno primero
venv_smarterp\Scripts\activate.bat

# Verificar configuración
python manage.py check

# Crear superusuario
python manage.py createsuperuser

# Shell interactivo
python manage.py shell

# Aplicar migraciones (solo tablas de Django)
python manage.py migrate
```

---

## 🎯 Tareas VSCode

Si usas VSCode, presiona `Ctrl+Shift+P` → `Tasks: Run Task`:

### Tareas Disponibles

- 🚀 **SmartERP: Desarrollo (Auto-detecta)** - Ejecutar dev.bat
- ⚙️ **SmartERP: Configurar Desarrollo** - Ejecutar setup-dev.bat
- 💻 **SmartERP: Desarrollo (Solo Local)** - Ejecutar dev-local.bat
- 🧪 **SmartERP: Ejecutar Tests** - Ejecutar test.bat
- 🏭 **SmartERP: Producción** - Ejecutar prod.bat
- 🧹 **SmartERP: Limpiar Entorno** - Ejecutar clean.bat

---

## 🔧 Solución de Problemas

### Error: "Python no encontrado"
```cmd
# Verificar instalación de Python
python --version

# Si no está instalado, descargar desde:
# https://www.python.org/downloads/
```

### Error: "venv_smarterp no encontrado"
```cmd
# Ejecutar configuración inicial
setup-dev.bat
```

### Error: "Puerto 8000 en uso"
```cmd
# Opción 1: Matar proceso
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Opción 2: Usar otro puerto
python manage.py runserver 8001
```

### Error: Base de datos no conecta
```cmd
# Forzar uso de SQLite para desarrollo
# Editar .env.development:
FORCE_SQLITE=True

# Reiniciar servidor
```

### Reinstalar desde Cero
```cmd
# 1. Limpiar todo
clean.bat

# 2. Reconfigurar
setup-dev.bat

# 3. Ejecutar
dev.bat
```

---

## 📚 Documentación Adicional

- **[Configuración de Base de Datos](CONFIGURACION-BASE-DATOS.md)** - SQLite vs SQL Server
- **[README Principal](../README.md)** - Arquitectura del proyecto
- **[Instrucciones GitHub Copilot](../.github/copilot-instructions.md)** - Guía para desarrollo con Copilot

---

## 🆘 Soporte

### Verificar Estado del Sistema
```cmd
# Ver configuración actual
python manage.py check

# Ver ambiente configurado
echo %DJANGO_ENVIRONMENT%

# Ver base de datos en uso
# Buscar en salida del servidor:
# [SmartERP] 💾 Base de datos SQLite: ...
# o
# [SmartERP] 🔍 Configurando SQL Server: ...
```

### Logs y Debugging
```cmd
# Ejecutar con más detalle
set DJANGO_DEBUG=True
python manage.py runserver

# Ver logs en tiempo real
# (Los logs aparecen en la consola del servidor)
```

---

**¿Problemas?** Consulta `CONFIGURACION-BASE-DATOS.md` para configuración avanzada de BD.

**🎉 ¡Listo para desarrollar!** El servidor debería estar corriendo en http://127.0.0.1:8000/
