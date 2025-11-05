"""
Generador de reportes PDF para Neuro-AI
"""

from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import io
import base64

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image,
    Table, TableStyle, PageBreak, KeepTogether,
    Frame, PageTemplate, BaseDocTemplate
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.pdfgen import canvas
from PIL import Image as PILImage

class NumberedCanvas(canvas.Canvas):
    """Canvas personalizado con números de página"""
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []
        self.page_num = 0

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()
        self.page_num += 1

    def save(self):
        """Agregar números de página a cada página"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        """Dibujar número de página"""
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.grey)
        self.drawRightString(
            letter[0] - inch * 0.5,
            inch * 0.5,
            f"Página {self.page_num} de {page_count}"
        )
        # Línea decorativa
        self.setStrokeColor(colors.HexColor('#e5e7eb'))
        self.line(inch * 0.5, inch * 0.6, letter[0] - inch * 0.5, inch * 0.6)

def generate_pdf_report(
    results: List[Dict[str, Any]],
    include_images: bool = True,
    output_dir: Path = Path("exports")
) -> Path:
    """
    Generar un reporte PDF profesional con los resultados del análisis
    """
    # Crear directorio de salida si no existe
    output_dir.mkdir(exist_ok=True)
    
    # Nombre del archivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = output_dir / f"neuro_ai_report_{timestamp}.pdf"
    
    # Crear documento
    doc = SimpleDocTemplate(
        str(file_path),
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=1*inch,
        bottomMargin=1*inch
    )
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading1_style = ParagraphStyle(
        'CustomHeading1',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#2563eb'),
        spaceBefore=20,
        spaceAfter=12,
        keepWithNext=True
    )
    
    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#475569'),
        spaceBefore=12,
        spaceAfter=8
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=11,
        textColor=colors.HexColor('#334155'),
        alignment=TA_JUSTIFY,
        spaceAfter=8
    )
    
    warning_style = ParagraphStyle(
        'Warning',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#dc2626'),
        backColor=colors.HexColor('#fef2f2'),
        borderColor=colors.HexColor('#dc2626'),
        borderWidth=1,
        borderPadding=10,
        alignment=TA_CENTER
    )
    
    # Construir el contenido
    story = []
    
    # Portada
    story.append(Spacer(1, 1.5*inch))
    story.append(Paragraph("NEURO-AI", title_style))
    story.append(Paragraph("Sistema de Diagnóstico Asistido por Inteligencia Artificial", heading2_style))
    story.append(Spacer(1, 0.5*inch))
    
    # Logo o imagen decorativa (si existe)
    logo_path = Path("public/icons/logo.png")
    if logo_path.exists():
        logo = Image(str(logo_path), width=2*inch, height=2*inch)
        logo.hAlign = 'CENTER'
        story.append(logo)
        story.append(Spacer(1, 0.5*inch))
    
    # Información del reporte
    report_info = f"""
    <para align="center">
    <b>REPORTE DE ANÁLISIS DE IMÁGENES MÉDICAS</b><br/>
    <br/>
    Fecha de generación: {datetime.now().strftime('%d de %B de %Y')}<br/>
    Hora: {datetime.now().strftime('%H:%M:%S')}<br/>
    Total de estudios analizados: {len(results)}<br/>
    </para>
    """
    story.append(Paragraph(report_info, body_style))
    
    story.append(PageBreak())
    
    # Advertencia legal
    story.append(Paragraph("ADVERTENCIA IMPORTANTE", heading1_style))
    warning_text = """
    Este reporte ha sido generado por un sistema de inteligencia artificial y tiene 
    carácter exclusivamente orientativo. NO constituye un diagnóstico médico definitivo.
    
    Los resultados DEBEN ser revisados y validados por un profesional médico calificado 
    antes de tomar cualquier decisión clínica. Este documento es EDITABLE para permitir 
    correcciones y anotaciones médicas.
    
    La precisión del sistema puede variar y no garantiza la detección de todas las 
    condiciones médicas. Siempre consulte con un especialista para un diagnóstico definitivo.
    """
    story.append(Paragraph(warning_text, warning_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Resumen ejecutivo
    story.append(Paragraph("RESUMEN EJECUTIVO", heading1_style))
    
    # Estadísticas generales
    stats_data = calculate_statistics(results)
    
    summary_table_data = [
        ['Métrica', 'Valor'],
        ['Total de análisis', str(len(results))],
        ['Análisis exitosos', str(stats_data['successful'])],
        ['Análisis con errores', str(stats_data['failed'])],
        ['Tipo predominante', stats_data['predominant_type']],
        ['Hallazgos críticos', str(stats_data['critical'])],
        ['Hallazgos normales', str(stats_data['normal'])]
    ]
    
    summary_table = Table(summary_table_data, colWidths=[3*inch, 3*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')])
    ]))
    
    story.append(summary_table)
    story.append(PageBreak())
    
    # Resultados detallados
    story.append(Paragraph("RESULTADOS DETALLADOS", heading1_style))
    
    for idx, result in enumerate(results, 1):
        # Encabezado del estudio
        story.append(Paragraph(f"ESTUDIO #{idx}", heading2_style))
        
        if result.get('success', False):
            # Información básica
            basic_info = [
                ['Campo', 'Valor'],
                ['Archivo', result.get('file_name', 'Sin nombre')],
                ['Fecha de análisis', result.get('timestamp', 'No disponible')],
                ['Tipo de análisis', result.get('model_type', 'No especificado').upper()],
                ['ID de análisis', result.get('analysis_id', 'No disponible')[:8] + '...']
            ]
            
            basic_table = Table(basic_info, colWidths=[2*inch, 4*inch])
            basic_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#64748b')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')])
            ]))
            
            story.append(basic_table)
            story.append(Spacer(1, 0.2*inch))
            
            # Diagnóstico principal
            medical_info = result.get('medical_info', {})
            diagnosis_data = [
                ['DIAGNÓSTICO PRINCIPAL', medical_info.get('titulo', 'No disponible')],
                ['Confianza del modelo', f"{result.get('confidence', 0):.1f}%"],
                ['Nivel de prioridad', medical_info.get('nivel', 'No especificado')],
                ['Urgencia', medical_info.get('urgencia', 'No especificada')]
            ]
            
            # Aplicar color según el nivel
            bg_color = get_priority_color(medical_info.get('nivel', 'BAJO'))
            
            diagnosis_table = Table(diagnosis_data, colWidths=[2*inch, 4*inch])
            diagnosis_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, 0), bg_color),
                ('TEXTCOLOR', (0, 0), (0, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (1, 0), 12),
                ('SPAN', (1, 0), (1, 0)),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8)
            ]))
            
            story.append(diagnosis_table)
            story.append(Spacer(1, 0.2*inch))
            
            # Descripción clínica
            story.append(Paragraph("<b>Descripción Clínica:</b>", body_style))
            story.append(Paragraph(
                medical_info.get('descripcion', 'No disponible'),
                body_style
            ))
            story.append(Spacer(1, 0.1*inch))
            
            # Recomendaciones
            story.append(Paragraph("<b>Recomendaciones:</b>", body_style))
            story.append(Paragraph(
                medical_info.get('recomendaciones', 'No disponible'),
                body_style
            ))
            story.append(Spacer(1, 0.2*inch))
            
            # Distribución de probabilidades
            story.append(Paragraph("<b>Análisis Detallado de Probabilidades:</b>", body_style))
            
            all_predictions = result.get('all_predictions', {})
            if all_predictions:
                prob_data = [['Clasificación', 'Probabilidad', 'Interpretación']]
                
                for cls, prob in sorted(all_predictions.items(), key=lambda x: x[1], reverse=True):
                    interpretation = get_probability_interpretation(prob)
                    prob_data.append([
                        cls.upper(),
                        f"{prob:.2f}%",
                        interpretation
                    ])
                
                prob_table = Table(prob_data, colWidths=[2*inch, 1.5*inch, 2.5*inch])
                prob_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#475569')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')])
                ]))
                
                story.append(prob_table)
            
            # Espacio para notas médicas
            story.append(Spacer(1, 0.3*inch))
            story.append(Paragraph("<b>ESPACIO PARA OBSERVACIONES MÉDICAS:</b>", body_style))
            
            notes_data = [['', '']] * 5  # 5 filas vacías para notas
            notes_table = Table(notes_data, colWidths=[6*inch], rowHeights=[0.4*inch]*5)
            notes_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fafafa'))
            ]))
            story.append(notes_table)
            
        else:
            # Mostrar error
            error_msg = f"""
            <para>
            <font color="red"><b>ERROR EN EL ANÁLISIS</b></font><br/>
            Archivo: {result.get('file_name', 'Sin nombre')}<br/>
            Error: {result.get('error', 'Error desconocido')}<br/>
            </para>
            """
            story.append(Paragraph(error_msg, body_style))
        
        # Salto de página entre estudios
        if idx < len(results):
            story.append(PageBreak())
    
    # Página de firma
    story.append(PageBreak())
    story.append(Paragraph("VALIDACIÓN MÉDICA", heading1_style))
    story.append(Spacer(1, 0.5*inch))
    
    signature_text = """
    Este documento requiere validación y firma de un profesional médico calificado 
    para su uso en decisiones clínicas.
    """
    story.append(Paragraph(signature_text, body_style))
    story.append(Spacer(1, 1*inch))
    
    # Campos para firma
    signature_data = [
        ['Nombre del Médico:', '_' * 40],
        ['Especialidad:', '_' * 40],
        ['Número de Colegiado:', '_' * 40],
        ['Fecha de Revisión:', '_' * 40],
        ['Firma:', ''],
        ['', ''],
        ['', ''],
        ['', '_' * 40]
    ]
    
    signature_table = Table(signature_data, colWidths=[2*inch, 4*inch])
    signature_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM')
    ]))
    
    story.append(signature_table)
    
    # Generar PDF con canvas personalizado
    doc.build(story, canvasmaker=NumberedCanvas)
    
    return file_path

def calculate_statistics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calcular estadísticas de los resultados"""
    stats = {
        'successful': 0,
        'failed': 0,
        'critical': 0,
        'normal': 0,
        'predominant_type': 'No determinado',
        'model_types': {}
    }
    
    for result in results:
        if result.get('success', False):
            stats['successful'] += 1
            
            # Contar por tipo de modelo
            model_type = result.get('model_type', 'unknown')
            stats['model_types'][model_type] = stats['model_types'].get(model_type, 0) + 1
            
            # Contar niveles críticos
            level = result.get('medical_info', {}).get('nivel', 'BAJO')
            if level == 'ALTO':
                stats['critical'] += 1
            elif result.get('prediction') == 'normal':
                stats['normal'] += 1
        else:
            stats['failed'] += 1
    
    # Determinar tipo predominante
    if stats['model_types']:
        stats['predominant_type'] = max(stats['model_types'], key=stats['model_types'].get).upper()
    
    return stats

def get_priority_color(level: str) -> colors.Color:
    """Obtener color según el nivel de prioridad"""
    colors_map = {
        'ALTO': colors.HexColor('#dc2626'),    # Rojo
        'MEDIO': colors.HexColor('#f59e0b'),   # Naranja
        'BAJO': colors.HexColor('#10b981')     # Verde
    }
    return colors_map.get(level, colors.HexColor('#64748b'))  # Gris por defecto

def get_probability_interpretation(probability: float) -> str:
    """Interpretar el valor de probabilidad"""
    if probability >= 80:
        return "Muy alta probabilidad"
    elif probability >= 60:
        return "Alta probabilidad"
    elif probability >= 40:
        return "Probabilidad moderada"
    elif probability >= 20:
        return "Baja probabilidad"
    else:
        return "Muy baja probabilidad"

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
            'analysis_id': 'abc123'
        }
    ]
    
    pdf_path = generate_pdf_report(test_results)
    print(f"PDF generado: {pdf_path}")
