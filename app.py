import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

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

# ─── CSS Global ─────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

  html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
    background-color: {BG};
    color: #e8eaec;
  }}
  .stApp {{ background-color: {BG}; }}

  section[data-testid="stSidebar"] {{
    background-color: {C_BLACK} !important;
    border-right: 1px solid {BORDER};
  }}
  section[data-testid="stSidebar"] * {{ color: #d0d4d8 !important; }}

  [data-testid="stMetric"] {{
    background: {CARD_BG};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 16px;
  }}
  h1, h2, h3, h4, h5, h6 {{ color: #f0f2f4; }}
  .stSelectbox label, .stMultiSelect label, .stDateInput label {{ color: {C_GRAY} !important; font-size: 12px !important; }}
  div[data-baseweb="select"] > div {{ background: {CARD_BG} !important; border-color: {BORDER} !important; }}
  .stDataFrame {{ border-radius: 8px; overflow: hidden; }}
  .block-container {{ padding: 1.5rem 2rem; }}
</style>
""", unsafe_allow_html=True)

# ─── Carga de datos con correcciones ────────────────────────────────────────
@st.cache_data
def load_data():
    # Leer CSV
    pisos = pd.read_csv("pisos.csv")
    areas = pd.read_csv("areas.csv")
    camas = pd.read_csv("camas.csv")
    
    # CORRECCIÓN: Parseo robusto de fechas en hospitalizacion.csv
    hosp = pd.read_csv("hospitalizacion.csv")
    
    # Convertir fechas con manejo de errores
    date_cols = ["fecha_ingreso", "fecha_egreso", "fecha_fallecimiento", "created_at", "updated_at", "fecha_nacimiento"]
    for col in date_cols:
        if col in hosp.columns:
            hosp[col] = pd.to_datetime(hosp[col], errors="coerce", format="%Y-%m-%d %H:%M:%S", dayfirst=False)
            # Si falla, intentar con otro formato
            if hosp[col].isna().all():
                hosp[col] = pd.to_datetime(hosp[col], errors="coerce")
    
    pac = pd.read_csv("paciente_ingreso.csv", parse_dates=["created_at", "updated_at"])
    
    # CORRECCIÓN: Unir camas con áreas y pisos correctamente
    camas = camas.merge(areas[["id", "nombre", "piso_id"]], left_on="area_id", right_on="id", how="left")
    camas = camas.rename(columns={"nombre": "area"})
    camas = camas.merge(pisos[["id", "nombre"]], left_on="piso_id", right_on="id", how="left")
    camas = camas.rename(columns={"nombre": "piso"})
    
    # CORRECCIÓN: Unir hospitalizacion con camas
    # hosp ya tiene su propia columna "urgencias" → renombrar la de camas antes del merge
    camas = camas.rename(columns={"urgencias": "urgencias_cama"})
    hosp = hosp.merge(camas[["id", "numero", "area", "piso", "urgencias_cama"]], left_on="cama_id", right_on="id", how="left")
    
    # CORRECCIÓN: Unir con pacientes
    pac_cols = ["id", "nombre", "sexo", "edad", "tipo_paciente", "estado_civil", "unidad_medica"]
    hosp = hosp.merge(pac[pac_cols], left_on="paciente_id", right_on="id", how="left", suffixes=("", "_pac"))
    
    # CORRECCIÓN: Mapear tipo_paciente correctamente
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
    
    # CORRECCIÓN: Fechas de nacimiento - priorizar fecha_nacimiento de hospitalizacion
    if "fecha_nacimiento" in hosp.columns:
        hosp["fecha_nacimiento"] = pd.to_datetime(hosp["fecha_nacimiento"], errors="coerce")
        # Calcular edad si no viene
        hosp["edad_calculada"] = hosp["fecha_nacimiento"].apply(
            lambda x: (datetime.now().year - x.year) if pd.notna(x) else None
        )
        hosp["edad"] = hosp["edad"].fillna(hosp["edad_calculada"])
    
    # CORRECCIÓN: Variables derivadas
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
    margin=dict(l=10, r=10, t=36, b=10),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=BORDER),
    colorway=PALETTE,
    xaxis=dict(gridcolor=BORDER, zerolinecolor=BORDER),
    yaxis=dict(gridcolor=BORDER, zerolinecolor=BORDER),
)

def fig_update(fig):
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig

# ─── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center;padding:18px 0 24px 0;">
      <div style="font-size:28px;">🏥</div>
      <div style="font-size:15px;font-weight:700;color:#f0f2f4;margin-top:6px;">Censo Hospitalario</div>
      <div style="font-size:11px;color:{C_GRAY};margin-top:2px;">Dashboard · ISSSTE</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**Módulo**")
    modulo = st.selectbox("", ["Resumen General","Ocupación de Camas","Ingresos y Egresos","Pacientes","Urgencias","Mortalidad"], label_visibility="collapsed")

    st.markdown("---")
    st.markdown("**Filtros**")
    
    area_lista = ["Todos"] + sorted(areas["nombre"].unique())
    area_sel = st.selectbox("Área", area_lista)
    
    mes_opts = sorted(hosp["mes_ingreso"].dropna().unique())
    if len(mes_opts) > 6:
        mes_default = mes_opts[-3:]
    else:
        mes_default = mes_opts
    mes_sel = st.multiselect("Mes de ingreso", mes_opts, default=mes_default)
    
    sexo_sel = st.multiselect("Sexo", ["Femenino","Masculino"], default=["Femenino","Masculino"])
    urg_sel = st.checkbox("Solo urgencias", value=False)

    st.markdown("---")
    st.caption(f"Registros totales: **{len(hosp):,}**")
    st.caption(f"Camas registradas: **{len(camas):,}**")

# ─── Filtrado de datos ──────────────────────────────────────────────────────
df = hosp.copy()
if area_sel != "Todos":
    df = df[df["area"] == area_sel]
if mes_sel:
    df = df[df["mes_ingreso"].isin(mes_sel)]
if sexo_sel:
    df = df[df["sexo"].isin(sexo_sel)]
if urg_sel:
    df = df[df["urgencias"] == 1]

# ════════════════════════════════════════════════════════════════════════════
# MÓDULO 1 · Resumen General
# ════════════════════════════════════════════════════════════════════════════
if modulo == "Resumen General":
    st.markdown("""
    <div style="background: linear-gradient(135deg, #002f2a 0%, #161a1d 100%); border-bottom: 1px solid #2a3038; padding: 20px 28px; margin: -1rem -1rem 0 -1rem;">
      <h1 style="font-size: 22px; font-weight: 700; color: #f0f2f4; margin: 0;">Resumen General</h1>
      <div style="font-size: 12px; color: #98989a; margin-top: 3px;">Vista consolidada del censo hospitalario</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="font-size: 13px; font-weight: 600; letter-spacing: 1.4px; text-transform: uppercase; color: #98989a; margin: 28px 0 14px 0; padding-bottom: 8px; border-bottom: 1px solid #2a3038;">KPIs Clave</div>', unsafe_allow_html=True)

    total_hosp = len(df)
    activos = int(df["activo"].sum())
    fallecidos = int(df["fallecimiento"].sum())
    urgencias = int((df["urgencias"] == 1).sum())
    estancia_prom = df["estancia_d"].dropna().mean()
    camas_ocp = int((camas["estatus_id"] == 2).sum())
    camas_tot = len(camas)
    ocup_pct = round(camas_ocp / camas_tot * 100, 1) if camas_tot > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("🏥 Total Hospitalizaciones", f"{total_hosp:,}")
    with col2: st.metric("🟢 Pacientes Activos", f"{activos:,}")
    with col3: st.metric("🚑 Ingresos por Urgencias", f"{urgencias:,}")
    with col4: st.metric("⚰️ Fallecimientos", f"{fallecidos:,}")

    col5, col6, col7, col8 = st.columns(4)
    with col5: st.metric("📊 Estancia Promedio (días)", f"{estancia_prom:.1f}" if not pd.isna(estancia_prom) else "—")
    with col6: st.metric("🛏️ Camas Ocupadas", f"{camas_ocp}", f"de {camas_tot} total")
    with col7: st.metric("📈 Tasa Ocupación", f"{ocup_pct}%")
    with col8: st.metric("🏢 Áreas Activas", f"{areas['nombre'].nunique()}")

    st.markdown('<div style="font-size: 13px; font-weight: 600; letter-spacing: 1.4px; text-transform: uppercase; color: #98989a; margin: 28px 0 14px 0; padding-bottom: 8px; border-bottom: 1px solid #2a3038;">Ingresos por Mes</div>', unsafe_allow_html=True)
    
    by_mes = df.groupby("mes_ingreso").size().reset_index(name="ingresos")
    if not by_mes.empty:
        fig_mes = go.Figure(go.Bar(x=by_mes["mes_ingreso"], y=by_mes["ingresos"], marker_color=C_WINE, marker_line_width=0))
        fig_mes.update_layout(**PLOTLY_LAYOUT, height=280, title="Ingresos mensuales")
        st.plotly_chart(fig_mes, use_container_width=True)
    else:
        st.info("No hay datos para mostrar con los filtros seleccionados")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div style="font-size: 13px; font-weight: 600; letter-spacing: 1.4px; text-transform: uppercase; color: #98989a; margin: 28px 0 14px 0; padding-bottom: 8px; border-bottom: 1px solid #2a3038;">Distribución por Área</div>', unsafe_allow_html=True)
        by_area = df.groupby("area").size().reset_index(name="n").sort_values("n", ascending=True)
        if not by_area.empty:
            fig_area = go.Figure(go.Bar(x=by_area["n"], y=by_area["area"], orientation="h", marker_color=C_GREEN, marker_line_width=0))
            fig_area.update_layout(**PLOTLY_LAYOUT, height=320)
            st.plotly_chart(fig_area, use_container_width=True)
        else:
            st.info("No hay datos")

    with col_b:
        st.markdown('<div style="font-size: 13px; font-weight: 600; letter-spacing: 1.4px; text-transform: uppercase; color: #98989a; margin: 28px 0 14px 0; padding-bottom: 8px; border-bottom: 1px solid #2a3038;">Distribución por Sexo</div>', unsafe_allow_html=True)
        by_sexo = df["sexo"].value_counts().reset_index()
        by_sexo.columns = ["sexo", "n"]
        if not by_sexo.empty:
            fig_sex = go.Figure(go.Pie(labels=by_sexo["sexo"], values=by_sexo["n"], hole=0.55, marker_colors=[C_WINE, C_GREEN]))
            fig_sex.update_layout(**PLOTLY_LAYOUT, height=320)
            st.plotly_chart(fig_sex, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# MÓDULO 2 · Ocupación de Camas
# ════════════════════════════════════════════════════════════════════════════
elif modulo == "Ocupación de Camas":
    st.markdown("""
    <div style="background: linear-gradient(135deg, #002f2a 0%, #161a1d 100%); border-bottom: 1px solid #2a3038; padding: 20px 28px; margin: -1rem -1rem 0 -1rem;">
      <h1 style="font-size: 22px; font-weight: 700; color: #f0f2f4; margin: 0;">Ocupación de Camas</h1>
      <div style="font-size: 12px; color: #98989a; margin-top: 3px;">Estado actual y capacidad instalada por área</div>
    </div>
    """, unsafe_allow_html=True)

    camas_full = camas.copy()
    camas_full["estado"] = camas_full["estatus_id"].map({1: "Disponible", 2: "Ocupada", 3: "Fuera Servicio"}).fillna("Desconocido")

    col1, col2, col3 = st.columns(3)
    disp = int((camas_full["estado"] == "Disponible").sum())
    ocup = int((camas_full["estado"] == "Ocupada").sum())
    fuera = int((camas_full["estado"] == "Fuera Servicio").sum())
    tot = len(camas_full)
    
    with col1: st.metric("🛏️ Camas Totales", f"{tot}")
    with col2: st.metric("🟢 Camas Disponibles", f"{disp}", f"{round(disp/tot*100,1)}%")
    with col3: st.metric("🔴 Camas Ocupadas", f"{ocup}", f"{round(ocup/tot*100,1)}%")

    st.markdown('<div style="font-size: 13px; font-weight: 600; letter-spacing: 1.4px; text-transform: uppercase; color: #98989a; margin: 28px 0 14px 0; padding-bottom: 8px; border-bottom: 1px solid #2a3038;">Ocupación por Área</div>', unsafe_allow_html=True)
    
    ocp_area = camas_full.groupby(["area", "estado"]).size().reset_index(name="n")
    fig_ocp = px.bar(ocp_area, x="area", y="n", color="estado",
                     color_discrete_map={"Disponible": C_GREEN, "Ocupada": C_WINE, "Fuera Servicio": C_GRAY},
                     barmode="stack")
    fig_ocp.update_layout(**PLOTLY_LAYOUT, height=340, xaxis_tickangle=-30)
    st.plotly_chart(fig_ocp, use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div style="font-size: 13px; font-weight: 600; letter-spacing: 1.4px; text-transform: uppercase; color: #98989a; margin: 28px 0 14px 0; padding-bottom: 8px; border-bottom: 1px solid #2a3038;">% Ocupación por Área</div>', unsafe_allow_html=True)
        ocp_pct = camas_full.groupby("area").apply(lambda g: round((g["estado"] == "Ocupada").sum() / len(g) * 100, 1)).reset_index(name="pct").sort_values("pct", ascending=False)
        if not ocp_pct.empty:
            colors = [C_WINE if v > 70 else C_GOLD if v > 40 else C_GREEN for v in ocp_pct["pct"]]
            fig_pct = go.Figure(go.Bar(x=ocp_pct["area"], y=ocp_pct["pct"], marker_color=colors, text=ocp_pct["pct"].astype(str)+"%", textposition="outside"))
            fig_pct.update_layout(**PLOTLY_LAYOUT, height=320, yaxis_range=[0, 115], xaxis_tickangle=-30)
            st.plotly_chart(fig_pct, use_container_width=True)

    with col_b:
        st.markdown('<div style="font-size: 13px; font-weight: 600; letter-spacing: 1.4px; text-transform: uppercase; color: #98989a; margin: 28px 0 14px 0; padding-bottom: 8px; border-bottom: 1px solid #2a3038;">Camas por Piso</div>', unsafe_allow_html=True)
        by_piso = camas_full.groupby(["piso", "estado"]).size().reset_index(name="n")
        fig_piso = px.bar(by_piso, x="piso", y="n", color="estado",
                          color_discrete_map={"Disponible": C_GREEN, "Ocupada": C_WINE, "Fuera Servicio": C_GRAY},
                          barmode="group")
        fig_piso.update_layout(**PLOTLY_LAYOUT, height=320)
        st.plotly_chart(fig_piso, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# MÓDULO 3 · Ingresos y Egresos
# ════════════════════════════════════════════════════════════════════════════
elif modulo == "Ingresos y Egresos":
    st.markdown("""
    <div style="background: linear-gradient(135deg, #002f2a 0%, #161a1d 100%); border-bottom: 1px solid #2a3038; padding: 20px 28px; margin: -1rem -1rem 0 -1rem;">
      <h1 style="font-size: 22px; font-weight: 700; color: #f0f2f4; margin: 0;">Ingresos y Egresos</h1>
      <div style="font-size: 12px; color: #98989a; margin-top: 3px;">Flujo de pacientes y estancias hospitalarias</div>
    </div>
    """, unsafe_allow_html=True)

    egresados = df[df["fecha_egreso"].notna()]
    est_mean = egresados["estancia_d"].mean()
    est_med = egresados["estancia_d"].median()

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("📥 Total Ingresos", f"{len(df):,}")
    with col2: st.metric("📤 Egresados", f"{len(egresados):,}")
    with col3: st.metric("📊 Estancia Media (días)", f"{est_mean:.1f}" if not pd.isna(est_mean) else "—")
    with col4: st.metric("📈 Estancia Mediana (días)", f"{est_med:.1f}" if not pd.isna(est_med) else "—")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div style="font-size: 13px; font-weight: 600; letter-spacing: 1.4px; text-transform: uppercase; color: #98989a; margin: 28px 0 14px 0; padding-bottom: 8px; border-bottom: 1px solid #2a3038;">Tendencia de Ingresos</div>', unsafe_allow_html=True)
        tend = df.groupby("mes_ingreso").size().reset_index(name="ingresos")
        egresos_tend = egresados.copy()
        egresos_tend["mes_egreso"] = egresados["fecha_egreso"].dt.to_period("M").astype(str)
        e_tend = egresos_tend.groupby("mes_egreso").size().reset_index(name="egresos")
        
        fig_tend = go.Figure()
        fig_tend.add_trace(go.Scatter(x=tend["mes_ingreso"], y=tend["ingresos"], name="Ingresos", line=dict(color=C_WINE, width=2.5), mode="lines+markers"))
        fig_tend.add_trace(go.Scatter(x=e_tend["mes_egreso"], y=e_tend["egresos"], name="Egresos", line=dict(color=C_GREEN, width=2.5, dash="dash"), mode="lines+markers"))
        fig_tend.update_layout(**PLOTLY_LAYOUT, height=300)
        st.plotly_chart(fig_tend, use_container_width=True)

    with col_b:
        st.markdown('<div style="font-size: 13px; font-weight: 600; letter-spacing: 1.4px; text-transform: uppercase; color: #98989a; margin: 28px 0 14px 0; padding-bottom: 8px; border-bottom: 1px solid #2a3038;">Motivo de Ingreso</div>', unsafe_allow_html=True)
        motivos = df["motivo_ingreso_clean"].value_counts().head(10).reset_index()
        motivos.columns = ["motivo", "n"]
        if not motivos.empty:
            fig_mot = go.Figure(go.Bar(x=motivos["n"], y=motivos["motivo"], orientation="h", marker_color=C_GOLD))
            fig_mot.update_layout(**PLOTLY_LAYOUT, height=300)
            st.plotly_chart(fig_mot, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# MÓDULO 4 · Pacientes
# ════════════════════════════════════════════════════════════════════════════
elif modulo == "Pacientes":
    st.markdown("""
    <div style="background: linear-gradient(135deg, #002f2a 0%, #161a1d 100%); border-bottom: 1px solid #2a3038; padding: 20px 28px; margin: -1rem -1rem 0 -1rem;">
      <h1 style="font-size: 22px; font-weight: 700; color: #f0f2f4; margin: 0;">Pacientes</h1>
      <div style="font-size: 12px; color: #98989a; margin-top: 3px;">Perfil demográfico y tipo de derechohabiencia</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("👥 Pacientes Únicos", f"{df['paciente_id'].nunique():,}")
    with col2: st.metric("📅 Edad Promedio", f"{df['edad'].mean():.1f} años" if not pd.isna(df['edad'].mean()) else "—")
    with col3: st.metric("♀️ % Femenino", f"{round((df['sexo']=='Femenino').mean()*100,1)}%")
    with col4: st.metric("♂️ % Masculino", f"{round((df['sexo']=='Masculino').mean()*100,1)}%")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div style="font-size: 13px; font-weight: 600; letter-spacing: 1.4px; text-transform: uppercase; color: #98989a; margin: 28px 0 14px 0; padding-bottom: 8px; border-bottom: 1px solid #2a3038;">Distribución de Edad</div>', unsafe_allow_html=True)
        df_age = df[df["edad"] > 0]
        if not df_age.empty:
            fig_age = px.histogram(df_age, x="edad", color="sexo", nbins=30,
                                   color_discrete_map={"Femenino": C_WINE, "Masculino": C_GREEN},
                                   barmode="overlay", opacity=0.8)
            fig_age.update_traces(marker_line_width=0)
            fig_age.update_layout(**PLOTLY_LAYOUT, height=300)
            st.plotly_chart(fig_age, use_container_width=True)

    with col_b:
        st.markdown('<div style="font-size: 13px; font-weight: 600; letter-spacing: 1.4px; text-transform: uppercase; color: #98989a; margin: 28px 0 14px 0; padding-bottom: 8px; border-bottom: 1px solid #2a3038;">Tipo de Paciente</div>', unsafe_allow_html=True)
        by_tipo = df["tipo_label"].value_counts().reset_index()
        by_tipo.columns = ["tipo", "n"]
        if not by_tipo.empty:
            fig_tipo = go.Figure(go.Pie(labels=by_tipo["tipo"], values=by_tipo["n"], hole=0.5, marker_colors=PALETTE))
            fig_tipo.update_layout(**PLOTLY_LAYOUT, height=300)
            st.plotly_chart(fig_tipo, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# MÓDULO 5 · Urgencias
# ════════════════════════════════════════════════════════════════════════════
elif modulo == "Urgencias":
    st.markdown("""
    <div style="background: linear-gradient(135deg, #002f2a 0%, #161a1d 100%); border-bottom: 1px solid #2a3038; padding: 20px 28px; margin: -1rem -1rem 0 -1rem;">
      <h1 style="font-size: 22px; font-weight: 700; color: #f0f2f4; margin: 0;">Urgencias</h1>
      <div style="font-size: 12px; color: #98989a; margin-top: 3px;">Análisis de ingresos por urgencias vs. programados</div>
    </div>
    """, unsafe_allow_html=True)

    urg = df[df["urgencias"] == 1]
    prog = df[df["urgencias"] == 0]

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("🚑 Ingresos por Urgencias", f"{len(urg):,}")
    with col2: st.metric("📋 Ingresos Programados", f"{len(prog):,}")
    with col3: st.metric("📊 % Urgencias", f"{round(len(urg)/len(df)*100,1)}%" if len(df) > 0 else "—")
    with col4:
        est_urg = urg["estancia_d"].dropna().mean()
        st.metric("⏱️ Est. Prom. Urgencias (días)", f"{est_urg:.1f}" if not pd.isna(est_urg) else "—")

# ════════════════════════════════════════════════════════════════════════════
# MÓDULO 6 · Mortalidad
# ════════════════════════════════════════════════════════════════════════════
elif modulo == "Mortalidad":
    st.markdown("""
    <div style="background: linear-gradient(135deg, #002f2a 0%, #161a1d 100%); border-bottom: 1px solid #2a3038; padding: 20px 28px; margin: -1rem -1rem 0 -1rem;">
      <h1 style="font-size: 22px; font-weight: 700; color: #f0f2f4; margin: 0;">Mortalidad</h1>
      <div style="font-size: 12px; color: #98989a; margin-top: 3px;">Registro y análisis de fallecimientos hospitalarios</div>
    </div>
    """, unsafe_allow_html=True)

    fall = df[df["fallecimiento"] == 1]
    total = len(df)
    tasa_mort = round(len(fall) / total * 100, 2) if total > 0 else 0
    fall_urg = int((fall["urgencias"] == 1).sum())
    fall_masc = int((fall["sexo"] == "Masculino").sum())
    edad_prom_fall = fall["edad"].mean()

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("⚰️ Total Fallecimientos", f"{len(fall)}")
    with col2: st.metric("📉 Tasa de Mortalidad", f"{tasa_mort}%", f"sobre {total} hospitalizaciones")
    with col3: st.metric("🚑 Fallec. en Urgencias", f"{fall_urg}")
    with col4: st.metric("📅 Edad Prom. Fallecidos", f"{edad_prom_fall:.1f} años" if not pd.isna(edad_prom_fall) else "—")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div style="font-size: 13px; font-weight: 600; letter-spacing: 1.4px; text-transform: uppercase; color: #98989a; margin: 28px 0 14px 0; padding-bottom: 8px; border-bottom: 1px solid #2a3038;">Fallecimientos por Área</div>', unsafe_allow_html=True)
        fall_area = fall.groupby("area").size().reset_index(name="n").sort_values("n", ascending=False)
        if not fall_area.empty:
            fig_fa = go.Figure(go.Bar(x=fall_area["area"], y=fall_area["n"], marker_color=C_WINE, text=fall_area["n"], textposition="outside"))
            fig_fa.update_layout(**PLOTLY_LAYOUT, height=300, xaxis_tickangle=-30)
            st.plotly_chart(fig_fa, use_container_width=True)
        else:
            st.info("No hay registros de fallecimientos con los filtros seleccionados")

    with col_b:
        st.markdown('<div style="font-size: 13px; font-weight: 600; letter-spacing: 1.4px; text-transform: uppercase; color: #98989a; margin: 28px 0 14px 0; padding-bottom: 8px; border-bottom: 1px solid #2a3038;">Fallecimientos por Mes</div>', unsafe_allow_html=True)
        fall_mes = fall.groupby("mes_ingreso").size().reset_index(name="n")
        if not fall_mes.empty:
            fig_fm = go.Figure(go.Scatter(x=fall_mes["mes_ingreso"], y=fall_mes["n"], mode="lines+markers", line=dict(color=C_WINE, width=2.5), marker=dict(size=8, color=C_GOLD)))
            fig_fm.update_layout(**PLOTLY_LAYOUT, height=300)
            st.plotly_chart(fig_fm, use_container_width=True)