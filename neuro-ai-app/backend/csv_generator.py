"""
Generador de reportes CSV para Neuro-AI
"""

import csv
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

def generate_csv_report(
    results: List[Dict[str, Any]],
    output_dir: Path = Path("exports")
) -> Path:
    """
    Generar un reporte CSV con los resultados del análisis
    
    Args:
        results: Lista de resultados de análisis
        output_dir: Directorio de salida
    
    Returns:
        Path: Ruta del archivo CSV generado
    """
    # Crear directorio de salida si no existe
    output_dir.mkdir(exist_ok=True)
    
    # Nombre del archivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = output_dir / f"neuro_ai_report_{timestamp}.csv"
    
    # Definir las columnas
    fieldnames = [
        'ID_Análisis',
        'Fecha_Hora',
        'Archivo',
        'Tipo_Análisis',
        'Éxito',
        'Diagnóstico',
        'Confianza_%',
        'Nivel_Prioridad',
        'Urgencia',
        'Título_Diagnóstico',
        'Descripción_Clínica',
        'Recomendaciones',
        'Probabilidad_Glioma_%',
        'Probabilidad_Meningioma_%',
        'Probabilidad_Normal_%',
        'Probabilidad_Pituitaria_%',
        'Probabilidad_Neumonía_%',
        'Probabilidad_COVID19_%',
        'Probabilidad_Tuberculosis_%',
        'Probabilidad_Opacidad_Pulmonar_%',
        'Error'
    ]
    
    # Escribir el archivo CSV
    with open(file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Escribir encabezados
        writer.writeheader()
        
        # Escribir datos
        for result in results:
            row = {
                'ID_Análisis': result.get('analysis_id', '')[:8] if result.get('analysis_id') else '',
                'Fecha_Hora': result.get('timestamp', ''),
                'Archivo': result.get('file_name', ''),
                'Tipo_Análisis': result.get('model_type', '').upper() if result.get('model_type') else '',
                'Éxito': 'Sí' if result.get('success', False) else 'No',
                'Diagnóstico': result.get('prediction', '').upper() if result.get('prediction') else '',
                'Confianza_%': f"{result.get('confidence', 0):.2f}" if result.get('confidence') else '0',
                'Error': result.get('error', '') if not result.get('success', False) else ''
            }
            
            # Agregar información médica si está disponible
            if result.get('medical_info'):
                medical_info = result['medical_info']
                row.update({
                    'Nivel_Prioridad': medical_info.get('nivel', ''),
                    'Urgencia': medical_info.get('urgencia', ''),
                    'Título_Diagnóstico': medical_info.get('titulo', ''),
                    'Descripción_Clínica': medical_info.get('descripcion', ''),
                    'Recomendaciones': medical_info.get('recomendaciones', '')
                })
            
            # Agregar probabilidades individuales
            if result.get('all_predictions'):
                predictions = result['all_predictions']
                
                # Mapeo de nombres de clases a columnas
                class_mapping = {
                    'glioma': 'Probabilidad_Glioma_%',
                    'meningioma': 'Probabilidad_Meningioma_%',
                    'normal': 'Probabilidad_Normal_%',
                    'pituitary': 'Probabilidad_Pituitaria_%',
                    'pneumonia': 'Probabilidad_Neumonía_%',
                    'covid19': 'Probabilidad_COVID19_%',
                    'tuberculosis': 'Probabilidad_Tuberculosis_%',
                    'lung_opacity': 'Probabilidad_Opacidad_Pulmonar_%'
                }
                
                for cls, column in class_mapping.items():
                    if cls in predictions:
                        row[column] = f"{predictions[cls]:.2f}"
            
            writer.writerow(row)
    
    # Crear archivo de resumen estadístico
    summary_path = output_dir / f"neuro_ai_summary_{timestamp}.csv"
    generate_summary_csv(results, summary_path)
    
    return file_path

def generate_summary_csv(results: List[Dict[str, Any]], file_path: Path):
    """
    Generar un archivo CSV con resumen estadístico
    
    Args:
        results: Lista de resultados
        file_path: Ruta del archivo de resumen
    """
    # Calcular estadísticas
    total = len(results)
    successful = sum(1 for r in results if r.get('success', False))
    failed = total - successful
    
    # Contar por tipo de análisis
    brain_count = sum(1 for r in results if r.get('model_type') == 'brain')
    chest_count = sum(1 for r in results if r.get('model_type') == 'chest')
    
    # Contar por nivel de prioridad
    high_priority = sum(1 for r in results 
                       if r.get('medical_info', {}).get('nivel') == 'ALTO')
    medium_priority = sum(1 for r in results 
                         if r.get('medical_info', {}).get('nivel') == 'MEDIO')
    low_priority = sum(1 for r in results 
                      if r.get('medical_info', {}).get('nivel') == 'BAJO')
    
    # Contar diagnósticos
    diagnosis_counts = {}
    for result in results:
        if result.get('prediction'):
            pred = result['prediction']
            diagnosis_counts[pred] = diagnosis_counts.get(pred, 0) + 1
    
    # Escribir resumen
    with open(file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile)
        
        # Encabezado del reporte
        writer.writerow(['RESUMEN ESTADÍSTICO - NEURO-AI'])
        writer.writerow(['Fecha de generación:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        writer.writerow([])
        
        # Estadísticas generales
        writer.writerow(['ESTADÍSTICAS GENERALES'])
        writer.writerow(['Métrica', 'Valor'])
        writer.writerow(['Total de análisis', total])
        writer.writerow(['Análisis exitosos', successful])
        writer.writerow(['Análisis con errores', failed])
        writer.writerow(['Tasa de éxito', f"{(successful/total*100 if total > 0 else 0):.1f}%"])
        writer.writerow([])
        
        # Por tipo de análisis
        writer.writerow(['POR TIPO DE ANÁLISIS'])
        writer.writerow(['Tipo', 'Cantidad', 'Porcentaje'])
        writer.writerow(['Cerebral', brain_count, f"{(brain_count/total*100 if total > 0 else 0):.1f}%"])
        writer.writerow(['Torácico', chest_count, f"{(chest_count/total*100 if total > 0 else 0):.1f}%"])
        writer.writerow([])
        
        # Por nivel de prioridad
        writer.writerow(['POR NIVEL DE PRIORIDAD'])
        writer.writerow(['Nivel', 'Cantidad', 'Porcentaje'])
        writer.writerow(['ALTO', high_priority, f"{(high_priority/total*100 if total > 0 else 0):.1f}%"])
        writer.writerow(['MEDIO', medium_priority, f"{(medium_priority/total*100 if total > 0 else 0):.1f}%"])
        writer.writerow(['BAJO', low_priority, f"{(low_priority/total*100 if total > 0 else 0):.1f}%"])
        writer.writerow([])
        
        # Distribución de diagnósticos
        writer.writerow(['DISTRIBUCIÓN DE DIAGNÓSTICOS'])
        writer.writerow(['Diagnóstico', 'Cantidad', 'Porcentaje'])
        
        for diagnosis, count in sorted(diagnosis_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count/total*100) if total > 0 else 0
            writer.writerow([diagnosis.upper(), count, f"{percentage:.1f}%"])
        
        writer.writerow([])
        
        # Confianza promedio
        confidences = [r.get('confidence', 0) for r in results if r.get('confidence')]
        if confidences:
            avg_confidence = sum(confidences) / len(confidences)
            min_confidence = min(confidences)
            max_confidence = max(confidences)
            
            writer.writerow(['ESTADÍSTICAS DE CONFIANZA'])
            writer.writerow(['Métrica', 'Valor'])
            writer.writerow(['Confianza promedio', f"{avg_confidence:.2f}%"])
            writer.writerow(['Confianza mínima', f"{min_confidence:.2f}%"])
            writer.writerow(['Confianza máxima', f"{max_confidence:.2f}%"])

def export_batch_csv(
    results_batches: List[List[Dict[str, Any]]],
    output_dir: Path = Path("exports")
) -> List[Path]:
    """
    Exportar múltiples lotes de resultados a archivos CSV separados
    
    Args:
        results_batches: Lista de lotes de resultados
        output_dir: Directorio de salida
    
    Returns:
        List[Path]: Lista de rutas de archivos generados
    """
    generated_files = []
    
    for i, batch in enumerate(results_batches, 1):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = output_dir / f"neuro_ai_batch_{i}_{timestamp}.csv"
        
        # Usar la función principal para cada lote
        generate_csv_report(batch, output_dir)
        generated_files.append(file_path)
    
    return generated_files

if __name__ == "__main__":
    # Prueba del generador
    test_results = [
        {
            'success': True,
            'file_name': 'brain_scan_001.jpg',
            'model_type': 'brain',
            'prediction': 'glioma',
            'confidence': 87.5,
            'all_predictions': {
                'glioma': 87.5,
                'meningioma': 8.2,
                'normal': 3.1,
                'pituitary': 1.2
            },
            'medical_info': {
                'titulo': 'Glioma Detectado',
                'descripcion': 'Se observan características compatibles con glioma cerebral.',
                'recomendaciones': 'Requiere evaluación urgente por neurocirugía.',
                'nivel': 'ALTO',
                'urgencia': 'URGENTE'
            },
            'timestamp': datetime.now().isoformat(),
            'analysis_id': 'abc123def456'
        },
        {
            'success': True,
            'file_name': 'chest_scan_002.jpg',
            'model_type': 'chest',
            'prediction': 'pneumonia',
            'confidence': 92.3,
            'all_predictions': {
                'normal': 5.2,
                'pneumonia': 92.3,
                'covid19': 1.5,
                'tuberculosis': 0.7,
                'lung_opacity': 0.3
            },
            'medical_info': {
                'titulo': 'Neumonía Detectada',
                'descripcion': 'Hallazgos radiológicos compatibles con proceso neumónico.',
                'recomendaciones': 'Tratamiento antibiótico según protocolo.',
                'nivel': 'MEDIO',
                'urgencia': 'PRIORITARIA'
            },
            'timestamp': datetime.now().isoformat(),
            'analysis_id': 'xyz789uvw012'
        }
    ]
    
    csv_path = generate_csv_report(test_results)
    print(f"CSV generado: {csv_path}")
