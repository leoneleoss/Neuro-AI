"""
Neuro-AI Backend API
Sistema de procesamiento de imágenes médicas con IA
"""

import os
import sys
import json
import traceback
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
import uvicorn
import numpy as np
from PIL import Image
import io
import base64
import hashlib
import uuid

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Intentar importar TensorFlow y modelos
try:
    import tensorflow as tf
    from tensorflow.keras.models import load_model
    from tensorflow.keras.preprocessing.image import img_to_array
    TF_AVAILABLE = True
except ImportError:
    logger.warning("TensorFlow no está disponible. Usando modo simulación.")
    TF_AVAILABLE = False

# Configuración
class Config:
    MODEL_BRAIN_PATH = Path("models/brain_model.h5")
    MODEL_CHEST_PATH = Path("models/chest_model.h5")
    IMG_SIZE = (224, 224)
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".bmp", ".dcm"}
    CACHE_DIR = Path("cache")
    HISTORY_FILE = Path("data/history.json")
    PORT = int(os.environ.get("FLASK_PORT", "5000"))

config = Config()

# Crear directorios necesarios
config.CACHE_DIR.mkdir(exist_ok=True)
config.HISTORY_FILE.parent.mkdir(exist_ok=True, parents=True)

# Inicializar FastAPI
app = FastAPI(
    title="Neuro-AI API",
    description="API para análisis de tomografías cerebrales y torácicas",
    version="2.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos de datos
class AnalysisRequest(BaseModel):
    image_data: str  # Base64 encoded image
    image_name: str
    analysis_type: str = Field(default="auto", pattern="^(auto|brain|chest)$")

class AnalysisResult(BaseModel):
    success: bool
    file_name: str
    model_type: Optional[str] = None
    prediction: Optional[str] = None
    confidence: Optional[float] = None
    all_predictions: Optional[Dict[str, float]] = None
    medical_info: Optional[Dict[str, Any]] = None
    timestamp: str
    analysis_id: str
    error: Optional[str] = None

class BatchAnalysisRequest(BaseModel):
    images: List[AnalysisRequest]

class ExportRequest(BaseModel):
    results: List[Dict[str, Any]]
    format: str = Field(default="pdf", pattern="^(pdf|csv)$")
    include_images: bool = True

# Clasificaciones y reportes médicos
BRAIN_CLASSES = ['glioma', 'meningioma', 'normal', 'pituitary']
CHEST_CLASSES = ['normal', 'pneumonia', 'covid19', 'tuberculosis', 'lung_opacity']

MEDICAL_REPORTS = {
    'glioma': {
        'titulo': 'Glioma Detectado',
        'descripcion': 'Se observan características compatibles con glioma cerebral. Los gliomas son tumores que se originan en las células gliales del cerebro.',
        'recomendaciones': 'Requiere evaluación urgente por neurocirugía. Se recomienda RMN con contraste y biopsia para clasificación histológica. Consulta con oncología.',
        'nivel': 'ALTO',
        'urgencia': 'URGENTE'
    },
    'meningioma': {
        'titulo': 'Meningioma Detectado',
        'descripcion': 'Lesión compatible con meningioma, tumor generalmente benigno que surge de las meninges.',
        'recomendaciones': 'Evaluación por neurocirugía. Monitoreo con estudios de imagen periódicos según tamaño y localización.',
        'nivel': 'MEDIO',
        'urgencia': 'PROGRAMADA'
    },
    'normal': {
        'titulo': 'Estudio Normal',
        'descripcion': 'No se observan hallazgos patológicos significativos en el estudio de imagen.',
        'recomendaciones': 'Continuar con seguimiento clínico rutinario según indicación médica.',
        'nivel': 'BAJO',
        'urgencia': 'RUTINA'
    },
    'pituitary': {
        'titulo': 'Adenoma Hipofisario',
        'descripcion': 'Lesión en región selar compatible con adenoma hipofisario. Estos tumores son generalmente benignos.',
        'recomendaciones': 'Evaluación por endocrinología y neurocirugía. Perfil hormonal completo y campimetría visual.',
        'nivel': 'MEDIO',
        'urgencia': 'PRIORITARIA'
    },
    'pneumonia': {
        'titulo': 'Neumonía Detectada',
        'descripcion': 'Hallazgos radiológicos compatibles con proceso neumónico activo.',
        'recomendaciones': 'Tratamiento antibiótico según protocolo. Control radiológico en 48-72 horas. Evaluación clínica inmediata.',
        'nivel': 'MEDIO',
        'urgencia': 'PRIORITARIA'
    },
    'covid19': {
        'titulo': 'Hallazgos Compatibles con COVID-19',
        'descripcion': 'Patrón de opacidades en vidrio esmerilado bilateral compatible con neumonía viral por SARS-CoV-2.',
        'recomendaciones': 'Aislamiento inmediato. Tratamiento según protocolo COVID-19. Monitoreo de saturación de oxígeno y signos de alarma.',
        'nivel': 'ALTO',
        'urgencia': 'URGENTE'
    },
    'tuberculosis': {
        'titulo': 'Hallazgos Sugestivos de Tuberculosis',
        'descripcion': 'Patrón radiológico compatible con tuberculosis pulmonar activa.',
        'recomendaciones': 'Aislamiento respiratorio. Baciloscopia y cultivo urgente. Iniciar tratamiento antituberculoso según protocolo DOTS.',
        'nivel': 'ALTO',
        'urgencia': 'URGENTE'
    },
    'lung_opacity': {
        'titulo': 'Opacidad Pulmonar',
        'descripcion': 'Presencia de opacidades pulmonares inespecíficas que requieren correlación clínica.',
        'recomendaciones': 'Evaluación clínica completa. Considerar TC de tórax para mejor caracterización. Seguimiento según evolución.',
        'nivel': 'MEDIO',
        'urgencia': 'PROGRAMADA'
    }
}

# Cargar modelos
class ModelManager:
    def __init__(self):
        self.brain_model = None
        self.chest_model = None
        self.models_loaded = False
        
        if TF_AVAILABLE:
            self.load_models()
    
    def load_models(self):
        """Cargar modelos de IA"""
        try:
            if config.MODEL_BRAIN_PATH.exists():
                self.brain_model = load_model(str(config.MODEL_BRAIN_PATH))
                logger.info("Modelo cerebral cargado exitosamente")
            else:
                logger.warning(f"Modelo cerebral no encontrado en {config.MODEL_BRAIN_PATH}")
            
            if config.MODEL_CHEST_PATH.exists():
                self.chest_model = load_model(str(config.MODEL_CHEST_PATH))
                logger.info("Modelo torácico cargado exitosamente")
            else:
                logger.warning(f"Modelo torácico no encontrado en {config.MODEL_CHEST_PATH}")
            
            self.models_loaded = (self.brain_model is not None or self.chest_model is not None)
        except Exception as e:
            logger.error(f"Error cargando modelos: {e}")
            self.models_loaded = False
    
    def predict(self, image: np.ndarray, model_type: str) -> Dict[str, Any]:
        """Realizar predicción en una imagen"""
        if not TF_AVAILABLE or not self.models_loaded:
            # Modo simulación
            return self._simulate_prediction(model_type)
        
        try:
            model = self.brain_model if model_type == 'brain' else self.chest_model
            classes = BRAIN_CLASSES if model_type == 'brain' else CHEST_CLASSES
            
            if model is None:
                return self._simulate_prediction(model_type)
            
            # Preprocesar imagen
            image = image.astype('float32') / 255.0
            image = np.expand_dims(image, axis=0)
            
            # Predicción
            predictions = model.predict(image, verbose=0)[0]
            
            # Procesar resultados
            results = {}
            max_idx = 0
            max_prob = 0
            
            for i, cls in enumerate(classes):
                prob = float(predictions[i]) * 100
                results[cls] = prob
                if prob > max_prob:
                    max_prob = prob
                    max_idx = i
            
            return {
                'success': True,
                'prediction': classes[max_idx],
                'confidence': max_prob,
                'all_predictions': results
            }
            
        except Exception as e:
            logger.error(f"Error en predicción: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _simulate_prediction(self, model_type: str) -> Dict[str, Any]:
        """Simulación de predicción para desarrollo"""
        classes = BRAIN_CLASSES if model_type == 'brain' else CHEST_CLASSES
        
        # Generar probabilidades aleatorias pero realistas
        probs = np.random.dirichlet(np.ones(len(classes)) * 0.5)
        results = {cls: float(prob * 100) for cls, prob in zip(classes, probs)}
        
        # Encontrar la clase con mayor probabilidad
        max_class = max(results, key=results.get)
        
        return {
            'success': True,
            'prediction': max_class,
            'confidence': results[max_class],
            'all_predictions': results
        }

# Instancia del gestor de modelos
model_manager = ModelManager()

# Funciones auxiliares
def decode_base64_image(base64_string: str) -> Image.Image:
    """Decodificar imagen desde base64"""
    try:
        # Remover el prefijo data:image/xxx;base64, si existe
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        image_data = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(image_data))
        
        # Convertir a RGB si es necesario
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        return image
    except Exception as e:
        raise ValueError(f"Error decodificando imagen: {e}")

def preprocess_image(image: Image.Image) -> np.ndarray:
    """Preprocesar imagen para el modelo"""
    # Redimensionar
    image = image.resize(config.IMG_SIZE, Image.Resampling.LANCZOS)
    
    # Convertir a array
    img_array = img_to_array(image) if TF_AVAILABLE else np.array(image)
    
    return img_array

def determine_model_type(image: np.ndarray, requested_type: str = "auto") -> str:
    """Determinar el tipo de modelo a usar"""
    if requested_type != "auto":
        return requested_type
    
    # Lógica simple: usar análisis de histograma para determinar el tipo
    # En producción, esto debería ser más sofisticado
    mean_intensity = np.mean(image)
    
    if mean_intensity > 100:  # Imágenes más claras tienden a ser de tórax
        return "chest"
    else:
        return "brain"

def save_to_history(result: AnalysisResult):
    """Guardar resultado en el historial"""
    try:
        history = []
        if config.HISTORY_FILE.exists():
            with open(config.HISTORY_FILE, 'r') as f:
                history = json.load(f)
        
        history.append(result.dict())
        
        # Mantener solo los últimos 1000 registros
        if len(history) > 1000:
            history = history[-1000:]
        
        with open(config.HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        logger.error(f"Error guardando historial: {e}")

# Endpoints de la API
@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "name": "Neuro-AI API",
        "version": "2.0.0",
        "status": "running",
        "tensorflow": TF_AVAILABLE,
        "models_loaded": model_manager.models_loaded
    }

@app.get("/health")
async def health_check():
    """Verificación de salud del servicio"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "models": {
            "brain": model_manager.brain_model is not None,
            "chest": model_manager.chest_model is not None
        }
    }

@app.post("/analyze", response_model=AnalysisResult)
async def analyze_image(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks
):
    """Analizar una imagen médica"""
    try:
        # Decodificar imagen
        image = decode_base64_image(request.image_data)
        
        # Preprocesar
        img_array = preprocess_image(image)
        
        # Determinar tipo de modelo
        model_type = determine_model_type(img_array, request.analysis_type)
        
        # Realizar predicción
        prediction_result = model_manager.predict(img_array, model_type)
        
        if not prediction_result['success']:
            raise HTTPException(status_code=500, detail=prediction_result.get('error', 'Error en predicción'))
        
        # Obtener información médica
        medical_info = MEDICAL_REPORTS.get(
            prediction_result['prediction'],
            MEDICAL_REPORTS['normal']
        )
        
        # Crear resultado
        result = AnalysisResult(
            success=True,
            file_name=request.image_name,
            model_type=model_type,
            prediction=prediction_result['prediction'],
            confidence=prediction_result['confidence'],
            all_predictions=prediction_result['all_predictions'],
            medical_info=medical_info,
            timestamp=datetime.now().isoformat(),
            analysis_id=str(uuid.uuid4())
        )
        
        # Guardar en historial en segundo plano
        background_tasks.add_task(save_to_history, result)
        
        return result
        
    except Exception as e:
        logger.error(f"Error analizando imagen: {e}")
        return AnalysisResult(
            success=False,
            file_name=request.image_name,
            timestamp=datetime.now().isoformat(),
            analysis_id=str(uuid.uuid4()),
            error=str(e)
        )

@app.post("/analyze/batch")
async def analyze_batch(
    request: BatchAnalysisRequest,
    background_tasks: BackgroundTasks
):
    """Analizar múltiples imágenes"""
    results = []
    
    for img_request in request.images:
        result = await analyze_image(img_request, background_tasks)
        results.append(result)
    
    return {"results": results, "total": len(results)}

@app.get("/history")
async def get_history(
    limit: int = 100,
    offset: int = 0
):
    """Obtener historial de análisis"""
    try:
        if not config.HISTORY_FILE.exists():
            return {"history": [], "total": 0}
        
        with open(config.HISTORY_FILE, 'r') as f:
            history = json.load(f)
        
        # Aplicar paginación
        total = len(history)
        history = history[offset:offset + limit]
        
        return {"history": history, "total": total}
    except Exception as e:
        logger.error(f"Error obteniendo historial: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/history/{analysis_id}")
async def delete_history_item(analysis_id: str):
    """Eliminar un elemento del historial"""
    try:
        if not config.HISTORY_FILE.exists():
            raise HTTPException(status_code=404, detail="Historial no encontrado")
        
        with open(config.HISTORY_FILE, 'r') as f:
            history = json.load(f)
        
        # Filtrar el elemento a eliminar
        history = [h for h in history if h.get('analysis_id') != analysis_id]
        
        with open(config.HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
        
        return {"message": "Elemento eliminado exitosamente"}
    except Exception as e:
        logger.error(f"Error eliminando del historial: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/export")
async def export_results(request: ExportRequest):
    """Exportar resultados a PDF o CSV"""
    try:
        if request.format == "pdf":
            # Generar PDF
            from .pdf_generator import generate_pdf_report
            file_path = generate_pdf_report(request.results, request.include_images)
        else:
            # Generar CSV
            from .csv_generator import generate_csv_report
            file_path = generate_csv_report(request.results)
        
        return FileResponse(
            file_path,
            media_type='application/octet-stream',
            filename=file_path.name
        )
    except Exception as e:
        logger.error(f"Error exportando resultados: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models/info")
async def get_models_info():
    """Obtener información sobre los modelos disponibles"""
    return {
        "brain": {
            "available": model_manager.brain_model is not None,
            "classes": BRAIN_CLASSES,
            "path": str(config.MODEL_BRAIN_PATH),
            "exists": config.MODEL_BRAIN_PATH.exists()
        },
        "chest": {
            "available": model_manager.chest_model is not None,
            "classes": CHEST_CLASSES,
            "path": str(config.MODEL_CHEST_PATH),
            "exists": config.MODEL_CHEST_PATH.exists()
        }
    }

@app.post("/models/reload")
async def reload_models():
    """Recargar modelos de IA"""
    try:
        model_manager.load_models()
        return {"success": True, "message": "Modelos recargados exitosamente"}
    except Exception as e:
        logger.error(f"Error recargando modelos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Manejo de errores global
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Error no manejado: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor", "error": str(exc)}
    )

# Inicializar servidor
if __name__ == "__main__":
    port = config.PORT
    logger.info(f"Iniciando Neuro-AI API en puerto {port}")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
        reload=False
    )
