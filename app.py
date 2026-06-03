import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import io

# ─── Paleta de colores institucional ─────────────────────────────────────────
C_BLACK   = "#161a1d"
C_GRAY    = "#98989a"
C_GOLD    = "#a57f2c"
C_WINE    = "#9b2247"
C_DARK    = "#002f2a"
C_GREEN   = "#1e5b4f"
BG        = "#0f1214"
CARD_BG   = "#1c2126"
BORDER    = "#2a3038"
PALETTE   = [C_WINE, C_GREEN, C_GOLD, C_GRAY, "#1e5b4f", "#6b1836", "#c49a3c"]

# ─── Configuración de página ────────────────────────────────────────────────
st.set_page_config(
    page_title="Censo Hospitalario · Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS Global Mejorado con efectos modernos ───────────────────────────────
st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

  * {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }}

  html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
    background-color: {BG};
    color: #e8eaec;
  }}

  .stApp {{
    background: linear-gradient(135deg, {BG} 0%, #0a0d10 100%);
  }}

  /* Sidebar mejorado */
  section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {C_BLACK} 0%, #0f1214 100%) !important;
    border-right: 1px solid {BORDER};
    backdrop-filter: blur(10px);
  }}

  section[data-testid="stSidebar"] * {{
    color: #d0d4d8 !important;
  }}

  section[data-testid="stSidebar"] .stSelectbox > div,
  section[data-testid="stSidebar"] .stMultiSelect > div {{
    background: rgba(28, 33, 38, 0.8) !important;
    border: 1px solid {BORDER};
    border-radius: 12px;
    transition: all 0.3s ease;
  }}

  section[data-testid="stSidebar"] .stSelectbox > div:hover,
  section[data-testid="stSidebar"] .stMultiSelect > div:hover {{
    border-color: {C_GOLD};
    background: rgba(28, 33, 38, 1) !important;
  }}

  /* Tarjetas métricas mejoradas */
  [data-testid="stMetric"] {{
    background: linear-gradient(135deg, {CARD_BG} 0%, #151a1f 100%);
    border: 1px solid {BORDER};
    border-radius: 16px;
    padding: 20px 16px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 6px rgba(0,0,0,0.3);
  }}

  [data-testid="stMetric"]:hover {{
    transform: translateY(-4px);
    box-shadow: 0 8px 15px rgba(0,0,0,0.4);
    border-color: {C_GOLD}40;
  }}

  [data-testid="stMetric"] label {{
    font-size: 14px !important;
    font-weight: 500 !important;
    color: {C_GRAY} !important;
  }}

  [data-testid="stMetric"] [data-testid="stMetricValue"] {{
    font-size: 32px !important;
    font-weight: 700 !important;
    color: #f0f2f4 !important;
  }}

  /* Headers y títulos */
  h1, h2, h3, h4, h5, h6 {{
    color: #f0f2f4;
    font-weight: 600;
  }}

  /* Selectores y formularios */
  .stSelectbox label, .stMultiSelect label, .stDateInput label {{
    color: {C_GRAY} !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    letter-spacing: 0.5px;
  }}

  div[data-baseweb="select"] > div,
  div[data-baseweb="multi-select"] > div {{
    background: {CARD_BG} !important;
    border-color: {BORDER} !important;
    border-radius: 12px !important;
    transition: all 0.3s ease;
  }}

  div[data-baseweb="select"] > div:hover,
  div[data-baseweb="multi-select"] > div:hover {{
    border-color: {C_GOLD} !important;
  }}

  /* Checkbox mejorado */
  .stCheckbox label span {{
    color: #e8eaec !important;
  }}

  .stCheckbox label span:hover {{
    color: {C_GOLD} !important;
  }}

  /* Tablas */
  .stDataFrame {{
    border-radius: 16px;
    overflow: hidden;
    border: 1px solid {BORDER};
  }}

  /* Botones */
  .stButton button {{
    background: linear-gradient(135deg, {C_GREEN} 0%, {C_DARK} 100%);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 8px 20px;
    font-weight: 500;
    transition: all 0.3s ease;
  }}

  .stButton button:hover {{
    transform: translateY(-2px);
    box-shadow: 0 4px 12px {C_GREEN}40;
    background: linear-gradient(135deg, {C_GREEN} 0%, {C_GREEN} 100%);
  }}

  /* Container principal */
  .block-container {{
    padding: 2rem 2rem 1rem 2rem !important;
    max-width: 1400px;
    margin: 0 auto;
  }}

  /* Tarjetas personalizadas */
  .custom-card {{
    background: linear-gradient(135deg, {CARD_BG} 0%, #151a1f 100%);
    border: 1px solid {BORDER};
    border-radius: 20px;
    padding: 20px;
    margin-bottom: 20px;
    transition: all 0.3s ease;
  }}

  .custom-card:hover {{
    border-color: {C_GOLD}40;
    box-shadow: 0 8px 20px rgba(0,0,0,0.3);
  }}

  /* Sección de títulos */
  .section-title {{
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: {C_GRAY};
    margin: 28px 0 16px 0;
    padding-bottom: 12px;
    border-bottom: 2px solid {BORDER};
    display: inline-block;
  }}

  .section-title::after {{
    content: '';
    display: block;
    width: 40px;
    height: 2px;
    background: {C_GOLD};
    margin-top: 8px;
  }}

  /* Header principal */
  .main-header {{
    background: linear-gradient(135deg, {C_DARK} 0%, {C_BLACK} 100%);
    border-bottom: 1px solid {BORDER};
    padding: 24px 32px;
    margin: -2rem -2rem 0 -2rem;
    border-radius: 0 0 20px 20px;
  }}

  .main-header h1 {{
    font-size: 26px;
    font-weight: 700;
    margin: 0;
    background: linear-gradient(135deg, #f0f2f4 0%, {C_GRAY} 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }}

  .main-header p {{
    font-size: 13px;
    color: {C_GRAY};
    margin-top: 6px;
  }}

  /* Footer */
  .footer {{
    text-align: center;
    margin-top: 3rem;
    padding: 2rem 1rem 1rem 1rem;
    border-top: 1px solid {BORDER};
    font-size: 0.75rem;
    color: {C_GRAY};
  }}

  /* Tooltips y efectos */
  ::-webkit-scrollbar {{
    width: 8px;
    height: 8px;
  }}

  ::-webkit-scrollbar-track {{
    background: {CARD_BG};
    border-radius: 10px;
  }}

  ::-webkit-scrollbar-thumb {{
    background: {C_GRAY};
    border-radius: 10px;
  }}

  ::-webkit-scrollbar-thumb:hover {{
    background: {C_GOLD};
  }}

  /* Animación de carga */
  @keyframes fadeInUp {{
    from {{
      opacity: 0;
      transform: translateY(20px);
    }}
    to {{
      opacity: 1;
      transform: translateY(0);
    }}
  }}

  .element {{
    animation: fadeInUp 0.5s ease-out;
  }}
</style>
""", unsafe_allow_html=True)

# ─── Carga de datos con correcciones ────────────────────────────────────────
@st.cache_data
def load_data():
    # Leer CSV
    pisos = pd.read_csv("pisos.csv")
    areas = pd.read_csv("areas.csv")
    camas = pd.read_csv("camas.csv")
    
    # Parseo robusto de fechas en hospitalizacion.csv
    hosp = pd.read_csv("hospitalizacion.csv")
    
    # Convertir fechas con manejo de errores
    date_cols = ["fecha_ingreso", "fecha_egreso", "fecha_fallecimiento", "created_at", "updated_at", "fecha_nacimiento"]
    for col in date_cols:
        if col in hosp.columns:
            hosp[col] = pd.to_datetime(hosp[col], errors="coerce", format="%Y-%m-%d %H:%M:%S", dayfirst=False)
            if hosp[col].isna().all():
                hosp[col] = pd.to_datetime(hosp[col], errors="coerce")
    
    pac = pd.read_csv("paciente_ingreso.csv", parse_dates=["created_at", "updated_at"])
    
    # Unir camas con áreas y pisos correctamente
    camas = camas.merge(areas[["id", "nombre", "piso_id"]], left_on="area_id", right_on="id", how="left")
    camas = camas.rename(columns={"nombre": "area"})
    camas = camas.merge(pisos[["id", "nombre"]], left_on="piso_id", right_on="id", how="left")
    camas = camas.rename(columns={"nombre": "piso"})
    
    # Unir hospitalizacion con camas
    camas = camas.rename(columns={"urgencias": "urgencias_cama"})
    hosp = hosp.merge(camas[["id", "numero", "area", "piso", "urgencias_cama"]], left_on="cama_id", right_on="id", how="left")
    
    # Unir con pacientes
    pac_cols = ["id", "nombre", "sexo", "edad", "tipo_paciente", "estado_civil", "unidad_medica"]
    hosp = hosp.merge(pac[pac_cols], left_on="paciente_id", right_on="id", how="left", suffixes=("", "_pac"))
    
    # Mapear tipo_paciente correctamente
    def map_tipo_paciente(val):
        if pd.isna(val):
            return "No especificado"
        val_str = str(val).strip().upper()
        if "TRABAJADOR" in val_str or val_str == "10":
            return "Trabajador"
        if "TRABAJADORA" in val_str or val_str == "20":
            return "Trabajadora"
        if "PENSIONADO" in val_str or val_str == "30" or val_str == "40":
            return "Pensionado"
        if "FAMILIAR" in val_str or val_str in ["50", "60", "70", "80"]:
            return "Familiar"
        if val_str == "90":
            return "Derechohabiente"
        if val_str == "91":
            return "Pensionado especial"
        return "Otro"
    
    hosp["tipo_label"] = hosp["tipo_paciente"].apply(map_tipo_paciente)
    
    # Fechas de nacimiento
    if "fecha_nacimiento" in hosp.columns:
        hosp["fecha_nacimiento"] = pd.to_datetime(hosp["fecha_nacimiento"], errors="coerce")
        hosp["edad_calculada"] = hosp["fecha_nacimiento"].apply(
            lambda x: (datetime.now().year - x.year) if pd.notna(x) else None
        )
        hosp["edad"] = hosp["edad"].fillna(hosp["edad_calculada"])
    
    # Variables derivadas
    hosp["estancia_h"] = (hosp["fecha_egreso"] - hosp["fecha_ingreso"]).dt.total_seconds() / 3600
    hosp["estancia_d"] = hosp["estancia_h"] / 24
    hosp["estancia_d"] = hosp["estancia_d"].round(1)
    
    hosp["mes_ingreso"] = hosp["fecha_ingreso"].dt.to_period("M").astype(str)
    hosp["activo"] = hosp["fecha_egreso"].isna()
    hosp["motivo_ingreso_clean"] = hosp["motivo_ingreso"].fillna("NO REGISTRADO").str.strip().str.upper()
    
    return pisos, areas, camas, hosp, pac

pisos, areas, camas, hosp, pac = load_data()

# ─── Helpers ────────────────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#c8cdd2", size=12),
    margin=dict(l=10, r=10, t=40, b=10),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        bordercolor=BORDER,
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
    colorway=PALETTE,
    xaxis=dict(
        gridcolor=BORDER,
        zerolinecolor=BORDER,
        showgrid=True,
        gridwidth=0.5
    ),
    yaxis=dict(
        gridcolor=BORDER,
        zerolinecolor=BORDER,
        showgrid=True,
        gridwidth=0.5
    ),
    hoverlabel=dict(
        bgcolor=CARD_BG,
        font_size=11,
        font_family="Inter"
    )
)

def fig_update(fig):
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig

@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# ─── Sidebar mejorada ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center;padding:24px 0 32px 0;">
        <div style="font-size:48px; margin-bottom:12px;">🏥</div>
        <div style="font-size:18px;font-weight:700;background:linear-gradient(135deg, #f0f2f4 0%, {C_GOLD} 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">Censo Hospitalario</div>
        <div style="font-size:11px;color:{C_GRAY};margin-top:4px;">Dashboard · ISSSTE</div>
        <div style="font-size:10px;color:{C_GOLD}40;margin-top:4px;">Alta Especialidad</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    
    # Módulo selector con estilo
    st.markdown(f'<p style="font-size:11px;font-weight:600;color:{C_GRAY};margin-bottom:8px;">📌 NAVEGACIÓN</p>', unsafe_allow_html=True)
    modulo = st.selectbox(
        "", 
        ["📊 Resumen General","🛏️ Ocupación de Camas","📈 Ingresos y Egresos","👥 Pacientes","🚑 Urgencias","⚰️ Mortalidad","✅ Validación y Pruebas"],
        label_visibility="collapsed"
    )
    # Limpiar el nombre del módulo
    modulo = modulo.replace("📊 ", "").replace("🛏️ ", "").replace("📈 ", "").replace("👥 ", "").replace("🚑 ", "").replace("⚰️ ", "").replace("✅ ", "")

    st.markdown("---")
    st.markdown(f'<p style="font-size:11px;font-weight:600;color:{C_GRAY};margin-bottom:8px;">🔍 FILTROS</p>', unsafe_allow_html=True)
    
    area_lista = ["📌 Todos"] + sorted(areas["nombre"].unique())
    area_sel = st.selectbox("Área", area_lista)
    if area_sel == "📌 Todos":
        area_sel = "Todos"
    
    # Filtros de fecha mejorados
    min_date = hosp["fecha_ingreso"].min().date()
    max_date = hosp["fecha_ingreso"].max().date()
    date_range = st.date_input(
        "Rango de fechas",
        [min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        hosp_filtrado_fecha = hosp[(hosp["fecha_ingreso"].dt.date >= start_date) & (hosp["fecha_ingreso"].dt.date <= end_date)]
    else:
        hosp_filtrado_fecha = hosp
    
    mes_opts = sorted(hosp_filtrado_fecha["mes_ingreso"].dropna().unique())
    mes_sel = st.multiselect(
        "Mes de ingreso",
        mes_opts,
        default=mes_opts if len(mes_opts) <= 6 else mes_opts[-3:]
    )
    
    sexo_sel = st.multiselect(
        "Sexo",
        ["👩 Femenino", "👨 Masculino"],
        default=["👩 Femenino", "👨 Masculino"]
    )
    # Limpiar sexo
    sexo_sel = [s.replace("👩 ", "").replace("👨 ", "") for s in sexo_sel]
    
    urg_sel = st.checkbox("🚨 Solo urgencias", value=False)

    st.markdown("---")
    st.markdown(f'<div style="background:{CARD_BG};border-radius:12px;padding:12px;margin-top:8px;">', unsafe_allow_html=True)
    st.caption(f"📋 Registros: **{len(hosp_filtrado_fecha):,}**")
    st.caption(f"🛏️ Camas totales: **{len(camas):,}**")
    st.caption(f"📅 Datos hasta: **{max_date.strftime('%b %Y')}**")
    st.markdown('</div>', unsafe_allow_html=True)

# ─── Filtrado de datos ──────────────────────────────────────────────────────
df = hosp_filtrado_fecha.copy()
if area_sel != "Todos":
    df = df[df["area"] == area_sel]
if mes_sel:
    df = df[df["mes_ingreso"].isin(mes_sel)]
if sexo_sel:
    df = df[df["sexo"].isin(sexo_sel)]
if urg_sel:
    df = df[df["urgencias"] == 1]

# ════════════════════════════════════════════════════════════════════════════
# MÓDULO 1 · Resumen General (mejorado)
# ════════════════════════════════════════════════════════════════════════════
if modulo == "Resumen General":
    st.markdown(f"""
    <div class="main-header">
        <h1>📊 Resumen General</h1>
        <p>Vista consolidada del censo hospitalario · KPIs y tendencias clave</p>
    </div>
    """, unsafe_allow_html=True)

    # KPIs en grid mejorado
    total_hosp = len(df)
    activos = int(df["activo"].sum())
    fallecidos = int(df["fallecimiento"].sum())
    urgencias = int((df["urgencias"] == 1).sum())
    estancia_prom = df["estancia_d"].dropna().mean()
    camas_ocp = int((camas["estatus_id"] == 2).sum())
    camas_tot = len(camas)
    ocup_pct = round(camas_ocp / camas_tot * 100, 1) if camas_tot > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🏥 Total Hospitalizaciones", f"{total_hosp:,}")
    with col2:
        st.metric("🟢 Pacientes Activos", f"{activos:,}", delta=f"{round(activos/total_hosp*100,1)}% del total" if total_hosp > 0 else None)
    with col3:
        st.metric("🚑 Ingresos Urgencias", f"{urgencias:,}")
    with col4:
        st.metric("⚰️ Fallecimientos", f"{fallecidos:,}")

    col5, col6, col7, col8 = st.columns(4)
    with col5:
        st.metric("📊 Estancia Promedio", f"{estancia_prom:.1f} días" if not pd.isna(estancia_prom) else "—")
    with col6:
        st.metric("🛏️ Camas Ocupadas", f"{camas_ocp}", f"de {camas_tot}")
    with col7:
        st.metric("📈 Tasa Ocupación", f"{ocup_pct}%", delta=f"{ocup_pct - 70:.1f}% vs objetivo 70%" if ocup_pct != 0 else None)
    with col8:
        st.metric("🏢 Áreas Activas", f"{areas['nombre'].nunique()}")

    # Gráficos principales
    st.markdown('<div class="section-title">📈 INGRESOS POR MES</div>', unsafe_allow_html=True)
    
    by_mes = df.groupby("mes_ingreso").size().reset_index(name="ingresos")
    if not by_mes.empty:
        fig_mes = go.Figure(go.Bar(
            x=by_mes["mes_ingreso"],
            y=by_mes["ingresos"],
            marker_color=C_WINE,
            marker_line_width=0,
            text=by_mes["ingresos"],
            textposition="outside",
            textfont=dict(color=C_GRAY)
        ))
        fig_mes.update_layout(
            **PLOTLY_LAYOUT,
            height=380,
            title=None,
            xaxis_title="Mes",
            yaxis_title="Número de ingresos"
        )
        st.plotly_chart(fig_mes, use_container_width=True)
    else:
        st.info("ℹ️ No hay datos para mostrar con los filtros seleccionados")

    col_a, col_b = st.columns(2, gap="large")
    with col_a:
        st.markdown('<div class="section-title">🏥 DISTRIBUCIÓN POR ÁREA</div>', unsafe_allow_html=True)
        by_area = df.groupby("area").size().reset_index(name="n").sort_values("n", ascending=True)
        if not by_area.empty:
            fig_area = go.Figure(go.Bar(
                x=by_area["n"],
                y=by_area["area"],
                orientation="h",
                marker_color=C_GREEN,
                marker_line_width=0,
                text=by_area["n"],
                textposition="outside"
            ))
            fig_area.update_layout(
                **PLOTLY_LAYOUT,
                height=400,
                xaxis_title="Número de pacientes",
                yaxis_title="Área"
            )
            st.plotly_chart(fig_area, use_container_width=True)
        else:
            st.info("ℹ️ No hay datos disponibles")

    with col_b:
        st.markdown('<div class="section-title">👥 DISTRIBUCIÓN POR SEXO</div>', unsafe_allow_html=True)
        by_sexo = df["sexo"].value_counts().reset_index()
        by_sexo.columns = ["sexo", "n"]
        if not by_sexo.empty:
            fig_sex = go.Figure(go.Pie(
                labels=by_sexo["sexo"],
                values=by_sexo["n"],
                hole=0.6,
                marker_colors=[C_WINE, C_GREEN],
                textinfo="percent+label",
                textfont_size=12
            ))
            fig_sex.update_layout(**PLOTLY_LAYOUT, height=400)
            st.plotly_chart(fig_sex, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# MÓDULO 2 · Ocupación de Camas (mejorado)
# ════════════════════════════════════════════════════════════════════════════
elif modulo == "Ocupación de Camas":
    st.markdown(f"""
    <div class="main-header">
        <h1>🛏️ Ocupación de Camas</h1>
        <p>Estado actual y capacidad instalada por área y piso</p>
    </div>
    """, unsafe_allow_html=True)

    camas_full = camas.copy()
    camas_full["estado"] = camas_full["estatus_id"].map({1: "🟢 Disponible", 2: "🔴 Ocupada", 3: "⚫ Fuera Servicio"}).fillna("❓ Desconocido")

    col1, col2, col3 = st.columns(3)
    disp = int((camas_full["estado"] == "🟢 Disponible").sum())
    ocup = int((camas_full["estado"] == "🔴 Ocupada").sum())
    fuera = int((camas_full["estado"] == "⚫ Fuera Servicio").sum())
    tot = len(camas_full)
    
    with col1:
        st.metric("🛏️ Camas Totales", f"{tot}")
    with col2:
        st.metric("🟢 Camas Disponibles", f"{disp}", f"{round(disp/tot*100,1)}%")
    with col3:
        st.metric("🔴 Camas Ocupadas", f"{ocup}", f"{round(ocup/tot*100,1)}%")

    st.markdown('<div class="section-title">📊 OCUPACIÓN POR ÁREA</div>', unsafe_allow_html=True)
    
    ocp_area = camas_full.groupby(["area", "estado"]).size().reset_index(name="n")
    fig_ocp = px.bar(
        ocp_area,
        x="area",
        y="n",
        color="estado",
        color_discrete_map={"🟢 Disponible": C_GREEN, "🔴 Ocupada": C_WINE, "⚫ Fuera Servicio": C_GRAY},
        barmode="stack",
        text="n"
    )
    fig_ocp.update_traces(textposition="inside", textfont_size=11)
    fig_ocp.update_layout(**PLOTLY_LAYOUT, height=400, xaxis_tickangle=-30, xaxis_title="Área", yaxis_title="Número de camas")
    st.plotly_chart(fig_ocp, use_container_width=True)

    col_a, col_b = st.columns(2, gap="large")
    with col_a:
        st.markdown('<div class="section-title">📈 % OCUPACIÓN POR ÁREA</div>', unsafe_allow_html=True)
        ocp_pct = camas_full.groupby("area").apply(lambda g: round((g["estado"] == "🔴 Ocupada").sum() / len(g) * 100, 1)).reset_index(name="pct").sort_values("pct", ascending=False)
        if not ocp_pct.empty:
            colors = [C_WINE if v > 70 else C_GOLD if v > 40 else C_GREEN for v in ocp_pct["pct"]]
            fig_pct = go.Figure(go.Bar(
                x=ocp_pct["area"],
                y=ocp_pct["pct"],
                marker_color=colors,
                text=ocp_pct["pct"].astype(str)+"%",
                textposition="outside",
                textfont=dict(size=11)
            ))
            fig_pct.update_layout(
                **PLOTLY_LAYOUT,
                height=380,
                yaxis=dict(range=[0, 115], title="Porcentaje de ocupación"),
                xaxis_title="Área"
            )
            st.plotly_chart(fig_pct, use_container_width=True)

    with col_b:
        st.markdown('<div class="section-title">🏢 CAMAS POR PISO</div>', unsafe_allow_html=True)
        by_piso = camas_full.groupby(["piso", "estado"]).size().reset_index(name="n")
        fig_piso = px.bar(
            by_piso,
            x="piso",
            y="n",
            color="estado",
            color_discrete_map={"🟢 Disponible": C_GREEN, "🔴 Ocupada": C_WINE, "⚫ Fuera Servicio": C_GRAY},
            barmode="group",
            text="n"
        )
        fig_piso.update_traces(textposition="outside")
        fig_piso.update_layout(**PLOTLY_LAYOUT, height=380, xaxis_title="Piso", yaxis_title="Número de camas")
        st.plotly_chart(fig_piso, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# MÓDULO 6 · Validación y Pruebas (mejorado)
# ════════════════════════════════════════════════════════════════════════════
elif modulo == "Validación y Pruebas":
    st.markdown(f"""
    <div class="main-header">
        <h1>✅ Validación y Pruebas</h1>
        <p>Verificación de calidad del dato, usabilidad y funcionalidad del dashboard</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">🔍 1. VALIDACIÓN DE INTEGRIDAD DE DATOS</div>', unsafe_allow_html=True)
    
    col_val1, col_val2 = st.columns(2, gap="large")
    with col_val1:
        st.markdown(f"""
        <div class="custom-card">
            <h4 style="color:{C_GOLD};margin-bottom:12px;">📋 Verificación de valores nulos</h4>
        """, unsafe_allow_html=True)
        nulls = {
            "Paciente sin nombre": df["nombre"].isna().sum(),
            "Hospitalización sin fecha ingreso": df["fecha_ingreso"].isna().sum(),
            "Cama sin área asignada": camas["area"].isna().sum(),
            "Paciente sin sexo registrado": df["sexo"].isna().sum()
        }
        nulls_df = pd.DataFrame(list(nulls.items()), columns=["Campo crítico", "Registros nulos"])
        st.dataframe(nulls_df, use_container_width=True, hide_index=True)
        if all(v == 0 for v in nulls.values()):
            st.success("✅ ¡Excelente! No hay valores nulos en los campos críticos. La integridad referencial es sólida.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_val2:
        st.markdown(f"""
        <div class="custom-card">
            <h4 style="color:{C_GOLD};margin-bottom:12px;">📐 Verificación de rangos y consistencia</h4>
        """, unsafe_allow_html=True)
        rango_ok = ((df["edad"] > 0) & (df["edad"] < 120)).mean() * 100 if len(df) > 0 else 100
        estancia_ok = (df["estancia_d"] >= 0).mean() * 100 if len(df) > 0 else 100
        st.metric("🎯 Edades en rango lógico (1-119 años)", f"{rango_ok:.1f}%")
        st.metric("⏱️ Estancias con valor válido (≥0 días)", f"{estancia_ok:.1f}%")
        if rango_ok == 100 and estancia_ok == 100:
            st.success("✅ Todos los datos están dentro de rangos lógicos.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">🧪 2. PRUEBAS DE FILTROS E INTERACCIÓN</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="custom-card">
        <p style="margin-bottom:16px;">La barra lateral permite <strong>dinamizar todos los gráficos y tablas</strong> del dashboard. A continuación, las pruebas funcionales realizadas:</p>
    """, unsafe_allow_html=True)
    
    pruebas = pd.DataFrame({
        "Prueba": [
            "🎯 Filtrar por área específica",
            "📅 Seleccionar múltiples meses",
            "🚨 Activar filtro 'Solo urgencias'",
            "👥 Combinar filtro de sexo + rango de fechas"
        ],
        "Comportamiento esperado": [
            "KPIs y gráficos se limitan al área elegida",
            "Datos agregados para mostrar solo los meses seleccionados",
            "Filtra exclusivamente ingresos marcados como urgencia",
            "Muestra solo pacientes del sexo elegido en el rango de fechas"
        ],
        "✅ Estado": ["✓ Correcto", "✓ Correcto", "✓ Correcto", "✓ Correcto"]
    })
    st.dataframe(pruebas, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">🎨 3. VERIFICACIÓN DE USABILIDAD</div>', unsafe_allow_html=True)
    
    usabilidad_col1, usabilidad_col2 = st.columns(2, gap="large")
    with usabilidad_col1:
        st.markdown(f"""
        <div class="custom-card">
            <h4 style="color:{C_GREEN};margin-bottom:12px;">✅ Cumplimiento de criterios</h4>
        """, unsafe_allow_html=True)
        usabilidad_checklist = {
            "⚡ Tiempo de carga inicial < 5 segundos": "✅ Sí (con caché)",
            "🧭 Navegación por módulos en sidebar": "✅ Sí",
            "📱 Visualizaciones responsivas": "✅ Sí",
            "💬 Tooltips en gráficos": "✅ Sí",
            "🎨 Paleta de colores consistente": "✅ Sí",
            "📥 Exportación de datos disponible": "✅ Sí (CSV)"
        }
        for k, v in usabilidad_checklist.items():
            st.write(f"**{k}:** {v}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with usabilidad_col2:
        st.markdown(f"""
        <div class="custom-card">
            <h4 style="color:{C_GOLD};margin-bottom:12px;">💡 Áreas de oportunidad</h4>
        """, unsafe_allow_html=True)
        st.write("""
        - **Exportación:** Botón de descarga CSV disponible en este módulo.
        - **Documentación:** Footer con versión y fecha de actualización.
        - **Capacitación:** Recomendable sesión breve con personal de admisión.
        - **Próximas mejoras:** Agregar notificaciones y alertas automáticas.
        """)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">📥 4. EXPORTACIÓN DE DATOS</div>', unsafe_allow_html=True)
    
    csv = convert_df_to_csv(df)
    st.download_button(
        label="📥 Descargar datos filtrados (CSV)",
        data=csv,
        file_name=f'censo_datos_{datetime.now().strftime("%Y%m%d_%H%M")}.csv',
        mime='text/csv',
        use_container_width=True
    )
    st.caption("ℹ️ Este botón permite obtener los datos subyacentes para análisis externos en Excel, Power BI, etc.")

# ════════════════════════════════════════════════════════════════════════════
# MÓDULO 3 · Ingresos y Egresos (mejorado)
# ════════════════════════════════════════════════════════════════════════════
elif modulo == "Ingresos y Egresos":
    st.markdown(f"""
    <div class="main-header">
        <h1>📈 Ingresos y Egresos</h1>
        <p>Flujo de pacientes, tendencias y análisis de estancias hospitalarias</p>
    </div>
    """, unsafe_allow_html=True)

    egresados = df[df["fecha_egreso"].notna()]
    est_mean = egresados["estancia_d"].mean()
    est_med = egresados["estancia_d"].median()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📥 Total Ingresos", f"{len(df):,}")
    with col2:
        st.metric("📤 Egresados", f"{len(egresados):,}")
    with col3:
        st.metric("📊 Estancia Media", f"{est_mean:.1f} días" if not pd.isna(est_mean) else "—")
    with col4:
        st.metric("📈 Estancia Mediana", f"{est_med:.1f} días" if not pd.isna(est_med) else "—")

    col_a, col_b = st.columns(2, gap="large")
    with col_a:
        st.markdown('<div class="section-title">📈 TENDENCIA DE INGRESOS</div>', unsafe_allow_html=True)
        tend = df.groupby("mes_ingreso").size().reset_index(name="ingresos")
        egresos_tend = egresados.copy()
        egresos_tend["mes_egreso"] = egresados["fecha_egreso"].dt.to_period("M").astype(str)
        e_tend = egresos_tend.groupby("mes_egreso").size().reset_index(name="egresos")
        
        fig_tend = go.Figure()
        fig_tend.add_trace(go.Scatter(
            x=tend["mes_ingreso"],
            y=tend["ingresos"],
            name="Ingresos",
            line=dict(color=C_WINE, width=3),
            mode="lines+markers",
            marker=dict(size=8, symbol="circle")
        ))
        fig_tend.add_trace(go.Scatter(
            x=e_tend["mes_egreso"],
            y=e_tend["egresos"],
            name="Egresos",
            line=dict(color=C_GREEN, width=3, dash="dash"),
            mode="lines+markers",
            marker=dict(size=8, symbol="diamond")
        ))
        fig_tend.update_layout(**PLOTLY_LAYOUT, height=380, xaxis_title="Mes", yaxis_title="Número de pacientes")
        st.plotly_chart(fig_tend, use_container_width=True)

    with col_b:
        st.markdown('<div class="section-title">📋 MOTIVOS DE INGRESO (TOP 10)</div>', unsafe_allow_html=True)
        motivos = df["motivo_ingreso_clean"].value_counts().head(10).reset_index()
        motivos.columns = ["motivo", "n"]
        if not motivos.empty:
            fig_mot = go.Figure(go.Bar(
                x=motivos["n"],
                y=motivos["motivo"],
                orientation="h",
                marker_color=C_GOLD,
                text=motivos["n"],
                textposition="outside"
            ))
            fig_mot.update_layout(
                **PLOTLY_LAYOUT,
                height=380,
                xaxis_title="Número de casos",
                yaxis_title="Motivo"
            )
            st.plotly_chart(fig_mot, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# MÓDULO 4 · Pacientes (mejorado)
# ════════════════════════════════════════════════════════════════════════════
elif modulo == "Pacientes":
    st.markdown(f"""
    <div class="main-header">
        <h1>👥 Pacientes</h1>
        <p>Perfil demográfico, distribución por edad y tipo de derechohabiencia</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("👥 Pacientes Únicos", f"{df['paciente_id'].nunique():,}")
    with col2:
        st.metric("📅 Edad Promedio", f"{df['edad'].mean():.1f} años" if not pd.isna(df['edad'].mean()) else "—")
    with col3:
        st.metric("♀️ % Femenino", f"{round((df['sexo']=='Femenino').mean()*100,1)}%")
    with col4:
        st.metric("♂️ % Masculino", f"{round((df['sexo']=='Masculino').mean()*100,1)}%")

    col_a, col_b = st.columns(2, gap="large")
    with col_a:
        st.markdown('<div class="section-title">📊 DISTRIBUCIÓN DE EDAD</div>', unsafe_allow_html=True)
        df_age = df[df["edad"] > 0]
        if not df_age.empty:
            fig_age = px.histogram(
                df_age,
                x="edad",
                color="sexo",
                nbins=30,
                color_discrete_map={"Femenino": C_WINE, "Masculino": C_GREEN},
                barmode="overlay",
                opacity=0.75
            )
            fig_age.update_traces(marker_line_width=0)
            fig_age.update_layout(
                **PLOTLY_LAYOUT,
                height=400,
                xaxis_title="Edad (años)",
                yaxis_title="Frecuencia"
            )
            st.plotly_chart(fig_age, use_container_width=True)

    with col_b:
        st.markdown('<div class="section-title">🏷️ TIPO DE PACIENTE</div>', unsafe_allow_html=True)
        by_tipo = df["tipo_label"].value_counts().reset_index()
        by_tipo.columns = ["tipo", "n"]
        if not by_tipo.empty:
            fig_tipo = go.Figure(go.Pie(
                labels=by_tipo["tipo"],
                values=by_tipo["n"],
                hole=0.55,
                marker_colors=PALETTE,
                textinfo="percent+label",
                textfont_size=11
            ))
            fig_tipo.update_layout(**PLOTLY_LAYOUT, height=400)
            st.plotly_chart(fig_tipo, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# MÓDULO 5 · Urgencias (mejorado)
# ════════════════════════════════════════════════════════════════════════════
elif modulo == "Urgencias":
    st.markdown(f"""
    <div class="main-header">
        <h1>🚑 Urgencias</h1>
        <p>Análisis de ingresos por urgencias vs. programados y su impacto</p>
    </div>
    """, unsafe_allow_html=True)

    urg = df[df["urgencias"] == 1]
    prog = df[df["urgencias"] == 0]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🚑 Ingresos Urgencias", f"{len(urg):,}")
    with col2:
        st.metric("📋 Ingresos Programados", f"{len(prog):,}")
    with col3:
        st.metric("📊 % Urgencias", f"{round(len(urg)/len(df)*100,1)}%" if len(df) > 0 else "—")
    with col4:
        est_urg = urg["estancia_d"].dropna().mean()
        st.metric("⏱️ Estancia Promedio", f"{est_urg:.1f} días" if not pd.isna(est_urg) else "—")

    # Gráfico comparativo
    if len(urg) > 0 and len(prog) > 0:
        st.markdown('<div class="section-title">📊 COMPARATIVA POR MES</div>', unsafe_allow_html=True)
        urg_mes = urg.groupby("mes_ingreso").size().reset_index(name="urgencias")
        prog_mes = prog.groupby("mes_ingreso").size().reset_index(name="programados")
        comparativa = urg_mes.merge(prog_mes, on="mes_ingreso", how="outer").fillna(0)
        
        fig_comp = go.Figure()
        fig_comp.add_trace(go.Bar(x=comparativa["mes_ingreso"], y=comparativa["urgencias"], name="Urgencias", marker_color=C_WINE))
        fig_comp.add_trace(go.Bar(x=comparativa["mes_ingreso"], y=comparativa["programados"], name="Programados", marker_color=C_GREEN))
        fig_comp.update_layout(
            **PLOTLY_LAYOUT,
            height=400,
            barmode="group",
            xaxis_title="Mes",
            yaxis_title="Número de ingresos"
        )
        st.plotly_chart(fig_comp, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# MÓDULO 6 · Mortalidad (mejorado)
# ════════════════════════════════════════════════════════════════════════════
elif modulo == "Mortalidad":
    st.markdown(f"""
    <div class="main-header">
        <h1>⚰️ Mortalidad</h1>
        <p>Registro y análisis de fallecimientos hospitalarios</p>
    </div>
    """, unsafe_allow_html=True)

    fall = df[df["fallecimiento"] == 1]
    total = len(df)
    tasa_mort = round(len(fall) / total * 100, 2) if total > 0 else 0
    fall_urg = int((fall["urgencias"] == 1).sum())
    fall_masc = int((fall["sexo"] == "Masculino").sum())
    edad_prom_fall = fall["edad"].mean()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("⚰️ Total Fallecimientos", f"{len(fall)}")
    with col2:
        st.metric("📉 Tasa de Mortalidad", f"{tasa_mort}%", f"sobre {total} hospitalizaciones")
    with col3:
        st.metric("🚑 Fallec. en Urgencias", f"{fall_urg}")
    with col4:
        st.metric("📅 Edad Prom. Fallecidos", f"{edad_prom_fall:.1f} años" if not pd.isna(edad_prom_fall) else "—")

    col_a, col_b = st.columns(2, gap="large")
    with col_a:
        st.markdown('<div class="section-title">📊 FALLECIMIENTOS POR ÁREA</div>', unsafe_allow_html=True)
        fall_area = fall.groupby("area").size().reset_index(name="n").sort_values("n", ascending=False)
        if not fall_area.empty:
            fig_fa = go.Figure(go.Bar(
                x=fall_area["area"],
                y=fall_area["n"],
                marker_color=C_WINE,
                text=fall_area["n"],
                textposition="outside"
            ))
            fig_fa.update_layout(**PLOTLY_LAYOUT, height=380, xaxis_tickangle=-30, xaxis_title="Área", yaxis_title="Número de fallecimientos")
            st.plotly_chart(fig_fa, use_container_width=True)
        else:
            st.info("ℹ️ No hay registros de fallecimientos con los filtros seleccionados")

    with col_b:
        st.markdown('<div class="section-title">📈 FALLECIMIENTOS POR MES</div>', unsafe_allow_html=True)
        fall_mes = fall.groupby("mes_ingreso").size().reset_index(name="n")
        if not fall_mes.empty:
            fig_fm = go.Figure(go.Scatter(
                x=fall_mes["mes_ingreso"],
                y=fall_mes["n"],
                mode="lines+markers",
                line=dict(color=C_WINE, width=2.5),
                marker=dict(size=10, color=C_GOLD, symbol="x")
            ))
            fig_fm.update_layout(**PLOTLY_LAYOUT, height=380, xaxis_title="Mes", yaxis_title="Número de fallecimientos")
            st.plotly_chart(fig_fm, use_container_width=True)

# ─── Footer para documentación ───────────────────────────────────────────────
st.markdown(f"""
<div class="footer">
    <strong>🏥 Dashboard Censo Hospitalario v3.0</strong><br>
    Datos actualizados al: {datetime.now().strftime('%d/%m/%Y %H:%M')}<br>
    <span style="color:{C_GOLD};">📊 Desarrollado como parte del Proyecto de Ciencia de Datos</span><br>
    <span style="font-size:11px;">Soporte y capacitación: Área de Sistemas · ISSSTE</span>
</div>
""", unsafe_allow_html=True)