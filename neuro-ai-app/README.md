# Neuro-AI v2.0.0

Sistema de Diagnóstico Asistido por Inteligencia Artificial para Análisis de Tomografías Cerebrales y Torácicas

![Neuro-AI](./public/banner.png)

## Descripción

Neuro-AI es una aplicación de escritorio moderna que utiliza inteligencia artificial y redes neuronales para analizar tomografías cerebrales y de tórax, proporcionando diagnósticos preliminares para asistir a profesionales médicos.

## ✨ Características Principales

### Funcionalidades Core
- **Análisis con IA**: Procesamiento de tomografías usando modelos de deep learning
- **Múltiples Modalidades**: Soporte para imágenes cerebrales y torácicas
- **Procesamiento Batch**: Análisis simultáneo de múltiples imágenes
- **Historial Completo**: Registro detallado de todos los análisis realizados
- **Exportación Profesional**: Generación de reportes en PDF y CSV editables

### Interfaz de Usuario
- **Diseño Moderno**: Interfaz minimalista siguiendo estándares de diseño actuales
- **Visualización Previa**: Vista previa de imágenes y diagnósticos en tiempo real
- **Animaciones Fluidas**: Indicadores visuales para retroalimentación del usuario
- **Modo Pantalla Completa**: Opción de visualización sin distracciones
- **Tema Claro/Oscuro**: Soporte para preferencias de tema del usuario

### Precisión y Confiabilidad
- **Alta Precisión**: Objetivo de >90% de precisión en clasificación
- **Advertencias Claras**: Disclaimers sobre la fiabilidad de IA
- **Reportes Editables**: PDFs modificables para correcciones médicas

## Instalación

### Requisitos Previos
- Node.js 18+ 
- Python 3.8+
- npm o yarn
- Git

### Pasos de Instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/neuro-ai/desktop-app.git
cd neuro-ai-app
```

2. **Instalar dependencias de Node.js**
```bash
npm install
```

3. **Instalar dependencias de Python**
```bash
cd backend
pip install -r requirements.txt
cd ..
```

4. **Descargar los modelos de IA**

Descarga los modelos pre-entrenados desde los siguientes datasets:
- [Brain CT Scans](https://www.kaggle.com/datasets/trainingdatapro/computed-tomography-ct-of-the-brain)
- [NIH Chest X-rays](https://www.kaggle.com/datasets/nih-chest-xrays/data/data)
- [Chest CT Scans](https://www.kaggle.com/datasets/mohamedhanyyy/chest-ctscan-images)

Coloca los archivos `.h5` en la carpeta `data/models/`:
- `data/models/brain_model.h5`
- `data/models/chest_model.h5`

## Uso

### Modo Desarrollo
```bash
npm run dev
```
Esto iniciará:
- Proceso principal de Electron
- Servidor de desarrollo React (puerto 3000)
- API Backend Python (puerto 5000)

### Compilación
```bash
# Para Windows
npm run dist:win

# Para macOS
npm run dist:mac

# Para Linux
npm run dist:linux
```

## Estructura del Proyecto

```
neuro-ai-app/
├── src/
│   ├── main/              # Proceso principal de Electron
│   │   ├── main.ts        # Entrada principal
│   │   └── preload.ts     # Script de precarga
│   └── renderer/          # Aplicación React
│       ├── components/    # Componentes reutilizables
│       ├── pages/         # Páginas de la aplicación
│       ├── hooks/         # Custom React hooks
│       ├── services/      # Servicios y APIs
│       ├── store/         # Estado global (Redux)
│       ├── styles/        # Estilos globales
│       ├── types/         # TypeScript types
│       └── utils/         # Utilidades
├── backend/               # API Python
│   ├── app.py            # Servidor FastAPI
│   ├── models/           # Lógica de modelos de IA
│   ├── services/         # Servicios de backend
│   └── utils/            # Utilidades
├── public/               # Assets públicos
│   ├── assets/          # Imágenes y recursos
│   └── icons/           # Iconos de la aplicación
├── data/
│   ├── models/          # Modelos de IA (.h5)
│   └── logs/            # Logs de la aplicación
├── tests/               # Tests
├── docs/                # Documentación
└── scripts/             # Scripts de utilidad
```

##  Configuración

### Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
# Backend
FLASK_PORT=5000
FLASK_ENV=development

# Modelos
MODEL_BRAIN_PATH=./data/models/brain_model.h5
MODEL_CHEST_PATH=./data/models/chest_model.h5

# Configuración
MAX_FILE_SIZE=52428800  # 50MB
CACHE_DIR=./cache
```

## Testing

```bash
# Ejecutar todos los tests
npm test

# Tests con coverage
npm run test:coverage

# Tests del backend
cd backend && python -m pytest
```

## Modelos de IA

### Clases de Diagnóstico

**Cerebro:**
- Glioma
- Meningioma
- Normal
- Adenoma Pituitario

**Tórax:**
- Normal
- Neumonía
- COVID-19
- Tuberculosis
- Opacidad Pulmonar

### Entrenamiento de Modelos

Para entrenar tus propios modelos, consulta la documentación en `docs/training.md`.

## Advertencia Legal

**IMPORTANTE**: Esta aplicación es una herramienta de asistencia y NO reemplaza el diagnóstico médico profesional. Todos los resultados deben ser revisados y validados por un profesional médico calificado antes de tomar decisiones clínicas.

## Contribución

Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## Autores

- **Equipo Neuro-AI** - Desarrollo inicial

## Agradecimientos

- Datasets de Kaggle por proporcionar las imágenes de entrenamiento
- Comunidad de TensorFlow por las herramientas de ML
- Electron y React por el framework de aplicación

## Contacto

Para soporte o consultas: support@neuro-ai.com

---

**Nota**: Esta aplicación está en desarrollo activo. Para la última versión estable, consulta las [releases](https://github.com/neuro-ai/desktop-app/releases).
