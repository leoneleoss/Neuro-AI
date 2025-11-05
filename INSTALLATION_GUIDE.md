# Guía de Instalación y Configuración - Neuro-AI v2.0.0

## 📋 Requisitos del Sistema

### Hardware Mínimo
- **Procesador**: Intel Core i5 o AMD Ryzen 5 (4 núcleos)
- **RAM**: 8 GB (16 GB recomendado)
- **Almacenamiento**: 10 GB de espacio libre
- **GPU**: Opcional pero recomendado para mejor rendimiento (NVIDIA con CUDA 11.0+)

### Software Requerido
- **Sistema Operativo**: Windows 10/11, macOS 10.14+, Ubuntu 20.04+
- **Node.js**: Versión 18.0.0 o superior
- **Python**: Versión 3.8 a 3.11
- **npm**: Versión 8.0.0 o superior
- **Git**: Última versión estable

## 🚀 Instalación Paso a Paso

### Paso 1: Preparar el Entorno

#### Windows
```powershell
# Instalar Chocolatey (gestor de paquetes)
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Instalar dependencias
choco install nodejs python git -y
```

#### macOS
```bash
# Instalar Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Instalar dependencias
brew install node python@3.11 git
```

#### Linux (Ubuntu/Debian)
```bash
# Actualizar repositorios
sudo apt update && sudo apt upgrade -y

# Instalar dependencias
sudo apt install nodejs npm python3 python3-pip git build-essential -y
```

### Paso 2: Descargar y Extraer el Proyecto

```bash
# Crear directorio de trabajo
mkdir ~/neuro-ai-workspace
cd ~/neuro-ai-workspace

# Extraer el archivo (si tienes el .tar.gz)
tar -xzf neuro-ai-app.tar.gz
cd neuro-ai-app

# O clonar desde repositorio (cuando esté disponible)
# git clone https://github.com/neuro-ai/desktop-app.git neuro-ai-app
# cd neuro-ai-app
```

### Paso 3: Instalar Dependencias de Node.js

```bash
# Instalar dependencias del proyecto
npm install

# Si hay errores de permisos en Linux/macOS
sudo npm install --unsafe-perm=true --allow-root

# Verificar instalación
npm list --depth=0
```

### Paso 4: Configurar el Backend Python

```bash
# Navegar al directorio backend
cd backend

# Crear entorno virtual (recomendado)
python -m venv venv

# Activar entorno virtual
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

# Para soporte GPU (opcional)
pip install tensorflow-gpu==2.15.0

# Volver al directorio raíz
cd ..
```

### Paso 5: Configurar los Modelos de IA

#### Opción A: Usar Modelos Pre-entrenados
```bash
# Crear directorio para modelos
mkdir -p data/models

# Descargar modelos (enlaces de ejemplo)
# Necesitarás descargar los modelos desde Kaggle o entrenar los tuyos propios
# Colócalos en data/models/ con los nombres:
# - brain_model.h5
# - chest_model.h5
```

#### Opción B: Entrenar Modelos Propios
```python
# Script básico de entrenamiento (train_model.py)
import tensorflow as tf
from tensorflow.keras import layers, models

# Configurar modelo para cerebro
brain_model = models.Sequential([
    layers.Conv2D(32, (3, 3), activation='relu', input_shape=(224, 224, 3)),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(64, (3, 3), activation='relu'),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(128, (3, 3), activation='relu'),
    layers.MaxPooling2D((2, 2)),
    layers.Flatten(),
    layers.Dense(512, activation='relu'),
    layers.Dropout(0.5),
    layers.Dense(4, activation='softmax')  # 4 clases para cerebro
])

brain_model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# Entrenar con tus datos...
# brain_model.fit(...)

# Guardar modelo
brain_model.save('data/models/brain_model.h5')
```

### Paso 6: Configuración de Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```env
# Backend Configuration
FLASK_PORT=5000
FLASK_ENV=development
API_KEY=tu-api-key-segura

# Model Paths
MODEL_BRAIN_PATH=./data/models/brain_model.h5
MODEL_CHEST_PATH=./data/models/chest_model.h5

# Application Settings
MAX_FILE_SIZE=52428800
BATCH_SIZE=10
CONFIDENCE_THRESHOLD=0.7

# Database (opcional)
DATABASE_URL=sqlite:///data/neuro_ai.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=./data/logs/app.log
```

### Paso 7: Primera Ejecución

```bash
# Modo desarrollo (recomendado para primera vez)
npm run dev

# Esto iniciará:
# - Backend Python en http://localhost:5000
# - Frontend React en http://localhost:3000
# - Aplicación Electron
```

## 🔧 Configuración Adicional

### Configurar HTTPS (Producción)

```javascript
// backend/config/ssl.js
const https = require('https');
const fs = require('fs');

const options = {
  key: fs.readFileSync('path/to/private.key'),
  cert: fs.readFileSync('path/to/certificate.crt')
};

https.createServer(options, app).listen(443);
```

### Configurar Base de Datos (Opcional)

```python
# backend/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgresql://user:password@localhost/neuro_ai')
Session = sessionmaker(bind=engine)
```

### Configurar Caché Redis (Opcional)

```python
# backend/cache.py
import redis

redis_client = redis.Redis(
    host='localhost',
    port=6379,
    decode_responses=True
)
```

## 📦 Compilación para Distribución

### Windows (.exe)
```bash
npm run build
npm run dist:win

# El instalador estará en dist/
```

### macOS (.dmg)
```bash
npm run build
npm run dist:mac

# Firmar la aplicación (requerido para distribución)
codesign --deep --force --verify --verbose --sign "Developer ID" dist/mac/Neuro-AI.app
```

### Linux (.AppImage)
```bash
npm run build
npm run dist:linux

# Hacer ejecutable
chmod +x dist/Neuro-AI-*.AppImage
```

## 🐛 Solución de Problemas Comunes

### Error: "Python/Node no encontrado"
```bash
# Verificar instalaciones
python --version  # o python3 --version
node --version
npm --version

# Agregar al PATH si es necesario
export PATH=$PATH:/usr/local/bin
```

### Error: "TensorFlow no se puede importar"
```bash
# Reinstalar TensorFlow
pip uninstall tensorflow
pip install tensorflow==2.15.0

# Para M1/M2 Macs
pip install tensorflow-macos tensorflow-metal
```

### Error: "Puerto 5000 ya en uso"
```bash
# Encontrar proceso usando el puerto
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/macOS
lsof -i :5000
kill -9 <PID>
```

### Error: "Modelos no encontrados"
```bash
# Verificar rutas
ls -la data/models/

# Crear modelos dummy para pruebas
python scripts/create_dummy_models.py
```

## 🧪 Verificación de la Instalación

### Test Rápido del Backend
```bash
# Activar entorno virtual
source backend/venv/bin/activate  # Linux/macOS
# o
backend\venv\Scripts\activate  # Windows

# Test de la API
python -c "from backend.app import app; print('Backend OK')"

# Test de endpoints
curl http://localhost:5000/health
```

### Test de la Aplicación
```bash
# Ejecutar tests automatizados
npm test

# Test de integración
npm run test:e2e
```

## 📱 Configuración para Desarrollo

### VS Code
Instalar extensiones recomendadas:
- ESLint
- Prettier
- Python
- TypeScript

Configuración `.vscode/settings.json`:
```json
{
  "editor.formatOnSave": true,
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "typescript.tsdk": "node_modules/typescript/lib"
}
```

### Debugging
```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Electron: Main",
      "type": "node",
      "request": "launch",
      "protocol": "inspector",
      "runtimeExecutable": "${workspaceFolder}/node_modules/.bin/electron",
      "args": [".", "--remote-debugging-port=9223"],
      "env": {
        "NODE_ENV": "development"
      }
    },
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["backend.app:app", "--reload", "--port", "5000"]
    }
  ]
}
```

## 🔐 Seguridad

### Configuraciones Importantes
1. **Nunca** subir modelos o datos sensibles a repositorios públicos
2. Usar HTTPS en producción
3. Implementar autenticación para acceso remoto
4. Validar y sanitizar todas las entradas
5. Mantener dependencias actualizadas

### Actualizaciones de Seguridad
```bash
# Verificar vulnerabilidades
npm audit
pip check

# Actualizar dependencias
npm audit fix
pip install --upgrade -r requirements.txt
```

## 📞 Soporte

Si encuentras problemas durante la instalación:
1. Revisa los logs en `data/logs/`
2. Consulta la documentación en `docs/`
3. Abre un issue en GitHub
4. Contacta al equipo: support@neuro-ai.com

## ✅ Checklist Post-Instalación

- [ ] Node.js y Python instalados correctamente
- [ ] Todas las dependencias instaladas sin errores
- [ ] Modelos de IA descargados y ubicados en `data/models/`
- [ ] Backend responde en http://localhost:5000
- [ ] Aplicación se abre sin errores
- [ ] Puede cargar y analizar una imagen de prueba
- [ ] Puede generar un reporte PDF
- [ ] Los logs se están generando en `data/logs/`

---

¡Felicitaciones! Si has completado todos los pasos, Neuro-AI está listo para usar. 🎉
