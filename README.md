# 🏥 Censo Hospitalario — Dashboard Streamlit

Dashboard interactivo para el análisis del censo hospitalario, construido con **Streamlit** y **Plotly**. Desarrollado siguiendo la metodología de proyectos de ciencia de datos: definición de objetivos, fuentes de datos, preparación, modelo de datos, diseño de interfaz e implementación técnica.

---

## 📁 Estructura del proyecto

```
censo_dashboard/
├── app.py                    # Aplicación principal Streamlit
├── requirements.txt          # Dependencias Python
├── README.md                 # Este archivo
├── areas.csv                 # Catálogo de áreas hospitalarias
├── camas.csv                 # Inventario de camas y estado actual
├── hospitalizacion.csv       # Registros de hospitalizaciones
├── paciente_ingreso.csv      # Datos demográficos de pacientes
└── pisos.csv                 # Catálogo de pisos
```

---

## 🚀 Instalación y ejecución

### 1. Crear entorno virtual (recomendado)

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Ejecutar la aplicación

```bash
streamlit run app.py
```

La app abrirá automáticamente en `http://localhost:8501`.

---

## 📊 Módulos del Dashboard

| Módulo | Descripción |
|---|---|
| **Resumen General** | KPIs clave, ingresos por mes, distribución por área y sexo |
| **Ocupación de Camas** | Estado actual, % ocupación por área, tabla de camas |
| **Ingresos y Egresos** | Tendencia mensual, motivos de ingreso, estancia hospitalaria |
| **Pacientes** | Perfil demográfico, pirámide poblacional, tipo de derechohabiencia |
| **Urgencias** | Comparativa urgencias vs. programados, análisis por área |
| **Mortalidad** | Tasa de mortalidad, distribución por área, edad y sexo |

---

## 🎨 Paleta de colores institucional

| Color | HEX | Pantone |
|---|---|---|
| Neutral Black | `#161a1d` | Neutral Black C |
| Cool Gray | `#98989a` | Cool Gray 7 C |
| Dorado | `#a57f2c` | 1255 C |
| Vino | `#9b2247` | 7420 C |
| Verde oscuro | `#002f2a` | 627 C |
| Verde medio | `#1e5b4f` | — |

---

## 🔗 Fuentes de datos

| Archivo | Descripción | Registros |
|---|---|---|
| `pisos.csv` | Catálogo de pisos (4 pisos) | 4 |
| `areas.csv` | Áreas clínicas por piso (347 camas totales) | 9 |
| `camas.csv` | Inventario individual de camas | 347 |
| `hospitalizacion.csv` | Hospitalizaciones dic 2025 – abr 2026 | 713 |
| `paciente_ingreso.csv` | Derechohabientes registrados | 687 |

---

## ⚙️ Requisitos del sistema

- Python **3.10+**
- Navegador moderno (Chrome, Firefox, Edge)
- Los archivos CSV deben estar en el mismo directorio que `app.py`

---

## 📝 Notas técnicas

- Los datos se cargan con `@st.cache_data` para optimizar rendimiento.
- Las tablas se unen mediante claves foráneas (`area_id`, `piso_id`, `cama_id`, `paciente_id`).
- La variable `estancia_d` se calcula como `(fecha_egreso - fecha_ingreso)` en días.
- Los filtros del sidebar se aplican globalmente a todos los módulos.
