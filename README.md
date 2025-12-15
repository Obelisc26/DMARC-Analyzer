# Analizador de Reportes DMARC

Una herramienta completa en Python para analizar reportes DMARC (Domain-based Message Authentication, Reporting & Conformance). Soporta reportes **RUA (agregados)** y **RUF (forenses/fallos)** de múltiples proveedores, incluyendo soporte nativo para archivos de Microsoft Outlook (`.msg`).

## 🎯 Características

### Pipeline Completo de 3 Etapas

1.  **🔧 PARTE 1: Extracción de Archivos**
    * Extrae automáticamente archivos HTML/XML de varios formatos comprimidos (ZIP, GZ, TAR).
    * **¡NUEVO!** Soporte nativo para archivos **.msg de Outlook**: extrae automáticamente los reportes adjuntos (XML/ZIP) dentro de los correos guardados.
    * Procesa archivos EML con adjuntos anidados.
    * Detecta automáticamente los tipos de archivo.

2.  **🔧 PARTE 2: Clasificación de Reportes**
    * Clasifica inteligentemente los reportes como RUA o RUF.
    * Analiza contenido XML y HTML.
    * Utiliza coincidencia de palabras clave y heurística.
    * Organiza los reportes en directorios separados.

3.  **🔧 PARTE 3: Análisis y Reportes**
    * **Análisis RUA**: Reportes agregados con estadísticas de IP y métricas de autenticación.
    * **Análisis RUF**: Reportes forenses con información detallada de fallos.
    * Genera archivos Excel profesionales con múltiples hojas, resúmenes y estadísticas.

### Características Adicionales

* **Soporte Multi-Formato**: Reportes XML, HTML y correos .MSG/.EML.
* **Soporte Multi-Proveedor**: Microsoft 365, Google Workspace, y todos los proveedores compatibles con DMARC.
* **Ejecución Flexible**: Ejecuta el pipeline completo o pasos individuales.
* **Interfaz de Línea de Comandos**: CLI fácil de usar.

## 📋 Requisitos

* Python 3.7+
* Librerías requeridas (ver `requirements.txt`):
    * `pandas`
    * `openpyxl`
    * `beautifulsoup4`
    * `extract-msg` (para soporte de Outlook)
    * Nativas: `xml.etree.ElementTree`, `zipfile`, `gzip`, `tarfile`, `email`

## 🚀 Instalación

```bash
# Clonar el repositorio
git clone https://github.com/Obelisc26/DMARC-Analyzer.git
cd DMARC-Analyzer

# Instalar dependencias
pip install -r requirements.txt
```

## 📁 Estructura del Proyecto

```text
DMARC-Analyzer/
├── main.py                      # Script principal - integra las 3 partes
├── requirements.txt             # Dependencias del proyecto
├── README.md                    # Documentación
│
├── extractors/                  # PARTE 1: Extracción de archivos
│   ├── __init__.py
│   └── file_extractor.py        # Lógica de extracción (ZIP, GZ, MSG, EML)
│
├── classifiers/                 # PARTE 2: Clasificación de reportes
│   ├── __init__.py
│   └── report_classifier.py
│
├── analyzers/                   # PARTE 3: Análisis
│   ├── __init__.py
│   ├── rua_analyzer.py          # Reportes RUA (agregados)
│   └── ruf_analyzer.py          # Reportes RUF (forenses)
│
└── reports/
    ├── raw/                     # ¡Pon tus archivos aquí! (ZIP, MSG, XML, etc.)
    ├── extracted/               # Archivos HTML/XML extraídos
    ├── rua/                     # Reportes clasificados como RUA
    └── ruf/                     # Reportes clasificados como RUF
```

## 💡 Uso

### Inicio Rápido: Pipeline Completo

La forma más fácil de analizar tus reportes:

1.  Coloca tus archivos (ZIP, MSG de Outlook, GZ, XML) en la carpeta `reports/raw`.
2.  Ejecuta:

    ```bash
    python main.py --input reports/raw
    ```

    Esto realizará automáticamente:
    * **Extracción de archivos** (incluyendo adjuntos dentro de `.msg` de Outlook).
    * **Clasificación** en RUA o RUF.
    * **Generación de Excel** con el análisis.

    **Salida:**
    * `rua_analysis.xlsx`: Análisis de reportes agregados.
    * `ruf_analysis.xlsx`: Análisis de reportes forenses.

### Uso Avanzado

#### Ejecutar Pasos Individuales

```bash
# PARTE 1: Solo extraer archivos
python main.py --extract --input reports/raw

# PARTE 2: Solo clasificar (después de extraer)
python main.py --classify --input reports/extracted

# PARTE 3: Solo analizar reportes RUA
python main.py --analyze rua --input reports/rua --output mi_reporte_rua.xlsx
```

#### Archivos de Salida Personalizados

```bash
python main.py --input reports/raw \
  --output-rua reporte_cliente_A.xlsx \
  --output-ruf reporte_forense_A.xlsx
```

## 📊 Contenido del Reporte (Excel)

### Análisis RUA (Reportes Agregados)

El archivo Excel contiene:
1.  **Resumen**: Estadísticas generales (tasa de éxito, total de mensajes, IPs únicas).
2.  **Todos los Registros**: Dataset completo.
3.  **Fallos de Auth**: Registros donde falló SPF o DKIM (¡Crítico para depurar!).
4.  **Estadísticas por IP**: Datos agregados por dirección IP de origen.
5.  **Fallos SPF/DKIM**: Detalles específicos de por qué falló cada validación.

### Análisis RUF (Reportes Forenses)

1.  **Resumen**: IPs y dominios únicos con fallos.
2.  **Detalle Forense**: Cabeceras originales (From, To, Subject), resultados de entrega y razones del fallo.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Si encuentras un error o quieres mejorar el soporte para Outlook, por favor abre un Issue o envía un Pull Request.

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo LICENSE para más detalles.

---

**Nota:** Esta herramienta es para analizar reportes DMARC. Asegúrate siempre de tener permiso para analizar los datos de autenticación de correo electrónico y maneja las cabeceras de correo de manera responsable.
