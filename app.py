import os
import base64
import streamlit as st
import pandas as pd
import requests
import urllib.parse
from datetime import datetime, date
import calendar
from supabase import create_client, Client

# Configuración de la página
st.set_page_config(
    page_title="OLINUTS - Control de Ventas",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inicializar claves de estado de navegación y carrito
if 'menu_radio' not in st.session_state:
    st.session_state['menu_radio'] = "🏠 Inicio / Dashboard"

if 'subseccion_clientes' not in st.session_state:
    st.session_state['subseccion_clientes'] = "📋 Listado General"

if 'subseccion_inventario' not in st.session_state:
    st.session_state['subseccion_inventario'] = "📋 Listado de Productos"

if 'subseccion_gastos' not in st.session_state:
    st.session_state['subseccion_gastos'] = "📋 Registrar / Ver Gastos"

if 'filtro_inv' not in st.session_state:
    st.session_state['filtro_inv'] = "Todas"

if 'carrito_ventas' not in st.session_state:
    st.session_state['carrito_ventas'] = []

# --- CONEXIÓN A SUPABASE VÍA API REST HTTP ---
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets.get("SUPABASE_URL", "")
    key = st.secrets.get("SUPABASE_KEY", "")
    if not url or not key:
        st.error("⚠️ Faltan SUPABASE_URL y SUPABASE_KEY en los Secrets de Streamlit.")
        st.stop()
    return create_client(url, key)

supabase = init_supabase()

def inicializar_db():
    try:
        res_c = supabase.table("clientes").select("id").eq("id", 1).execute()
        if not res_c.data:
            supabase.table("clientes").insert({"id": 1, "nombre": "Cliente Mostrador / General", "telefono": "S/N"}).execute()
    except Exception:
        pass

    try:
        res_p = supabase.table("proveedores").select("id").eq("id", 1).execute()
        if not res_p.data:
            supabase.table("proveedores").insert({"id": 1, "nombre": "Proveedor General / Varios", "telefono": "S/N"}).execute()
    except Exception:
        pass

inicializar_db()

# --- TASA BCV EN TIEMPO REAL ---
@st.cache_data(ttl=3600)
def obtener_tasa_bcv():
    try:
        url = "https://ve.dolarapi.com/v1/dolares/oficial"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return float(data.get("promedio", 0.0))
    except Exception:
        pass

    try:
        url_alt = "https://pydolarvenezuela-api.vercel.app/api/v1/dollar?page=bcv"
        response_alt = requests.get(url_alt, timeout=5)
        if response_alt.status_code == 200:
            data = response_alt.json()
            return float(data['monedas']['usd']['promedio'])
    except Exception:
        pass

    return 880.12

# --- FUNCIONES DE NAVEGACIÓN ---
def ir_a_seccion(nombre_seccion):
    st.session_state['menu_radio'] = nombre_seccion

def ir_a_subseccion_clientes(nombre_subseccion):
    st.session_state['subseccion_clientes'] = nombre_subseccion

def ir_a_subseccion_inventario(nombre_subseccion):
    st.session_state['subseccion_inventario'] = nombre_subseccion

def ir_a_subseccion_gastos(nombre_subseccion):
    st.session_state['subseccion_gastos'] = nombre_subseccion

def archivo_a_base64(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        base64_str = base64.b64encode(bytes_data).decode('utf-8')
        mime_type = uploaded_file.type
        return f"data:{mime_type};base64,{base64_str}"
    return ""

def limpiar_float(valor, por_defecto=0.0):
    try:
        if pd.isna(valor) or valor is None:
            return float(por_defecto)
        return float(valor)
    except (ValueError, TypeError):
        return float(por_defecto)

# --- ESTILOS CSS ---
st.markdown("""
<style>
    html, body, [class*="css"], .stMarkdown, p, div, label {
        font-size: 18px !important;
    }
    .stApp {
        background-color: #F5F2EB;
    }
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input {
        font-size: 18px !important;
    }
    .stButton button {
        font-size: 18px !important;
        font-weight: bold !important;
        padding: 10px 16px !important;
    }
    .header-container {
        background-color: #FFDE59;
        padding: 22px 20px 12px 20px;
        border-bottom-left-radius: 20px;
        border-bottom-right-radius: 20px;
        margin-top: -60px;
        margin-bottom: 20px;
    }
    .header-title {
        font-size: 28px !important;
        font-weight: bold;
        color: #111111;
        margin: 0;
    }
    .header-subtitle {
        font-size: 16px !important;
        color: #555555;
        margin-bottom: 10px;
    }
    .section-header-yellow {
        background-color: #FFDE59;
        padding: 14px 18px;
        border-radius: 12px;
        color: #111111;
        font-size: 22px !important;
        font-weight: bold;
        text-align: center;
        margin-bottom: 12px;
        box-shadow: 0px 2px 6px rgba(0, 0, 0, 0.05);
    }
    .sub-header-yellow {
        background-color: #FFEE99;
        border: 1px solid #FBC02D;
        padding: 12px 16px;
        border-radius: 10px;
        color: #222222;
        font-size: 18px !important;
        font-weight: bold;
        margin-top: 18px;
        margin-bottom: 18px;
    }
    .tasa-card {
        background-color: #FFF9C4;
        border: 1px solid #FBC02D;
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 15px;
        text-align: center;
        font-weight: bold;
        color: #333333;
        font-size: 19px !important;
    }
    .business-card {
        background-color: #FFFFFF;
        border-radius: 16px;
        padding: 22px;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }
    .card-title { font-size: 20px !important; font-weight: 600; color: #333; }
    .card-amount { font-size: 36px !important; font-weight: bold; color: #111; }
    .amount-green { color: #00A86B; font-weight: bold; font-size: 22px !important; }
    .amount-red { color: #E53935; font-weight: bold; font-size: 22px !important; }
    .stat-card {
        background-color: #FFFFFF;
        border-radius: 14px;
        padding: 16px;
        border: 1px solid #EEEEEE;
    }

    /* ESTILOS TABLA ALMANAQUE */
    .calendar-container {
        width: 100%;
        overflow-x: auto;
    }
    .calendar-table {
        width: 100%;
        border-collapse: collapse;
        background-color: #FFFFFF;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0px 3px 8px rgba(0, 0, 0, 0.04);
        margin-bottom: 20px;
        table-layout: fixed;
    }
    .calendar-table th {
        background-color: #FFDE59;
        color: #111111;
        text-align: center;
        padding: 8px 2px;
        font-size: 14px !important;
        font-weight: bold;
        border: 1px solid #E0E0E0;
    }
    .calendar-table td {
        width: 14.28%;
        height: 65px;
        vertical-align: top;
        padding: 4px;
        border: 1px solid #E0E0E0;
        background-color: #FFFFFF;
        text-align: center;
    }
    .calendar-table td.empty-day {
        background-color: #FAFAFA;
    }
    .calendar-table td.active-day {
        background-color: #FFFDE7;
        border: 1.5px solid #FBC02D;
    }
    .day-number {
        font-weight: bold;
        font-size: 14px !important;
        color: #222;
        display: block;
        margin-bottom: 2px;
    }
    .day-amount {
        font-size: 11px !important;
        font-weight: bold;
        color: #00A86B;
        background-color: #E8F5E9;
        padding: 2px 3px;
        border-radius: 4px;
        display: block;
        word-break: break-all;
    }

    /* ESTILOS CATÁLOGO DE PRODUCTOS */
    .product-card {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 18px;
        padding: 16px;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        gap: 16px;
        box-shadow: 0px 3px 8px rgba(0, 0, 0, 0.03);
    }
    .product-icon-box {
        background-color: #F3E5F5;
        border-radius: 14px;
        width: 75px;
        height: 75px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 38px;
        flex-shrink: 0;
        overflow: hidden;
    }
    .product-icon-box img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    .product-info {
        flex-grow: 1;
    }
    .product-title {
        font-size: 20px !important;
        font-weight: bold;
        color: #222222;
        margin-bottom: 4px;
    }
    .badge-no-stock {
        background-color: #FFEBEE;
        color: #C62828;
        font-size: 14px !important;
        font-weight: bold;
        padding: 4px 10px;
        border-radius: 12px;
        display: inline-block;
        margin-bottom: 6px;
    }
    .badge-low-stock {
        background-color: #FFF3E0;
        color: #E65100;
        font-size: 14px !important;
        font-weight: bold;
        padding: 4px 10px;
        border-radius: 12px;
        display: inline-block;
        margin-bottom: 6px;
    }
    .badge-in-stock {
        background-color: #E8F5E9;
        color: #2E7D32;
        font-size: 14px !important;
        font-weight: bold;
        padding: 4px 10px;
        border-radius: 12px;
        display: inline-block;
        margin-bottom: 6px;
    }
    .product-price {
        font-size: 22px !important;
        font-weight: bold;
        color: #111111;
    }
    .product-price-bs {
        font-size: 14px !important;
        color: #666666;
    }
</style>
""", unsafe_allow_html=True)

tasa_bcv_auto = obtener_tasa_bcv()

# --- MENÚ LATERAL ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2515/2515183.png", width=90)
st.sidebar.title("OLINUTS")

tasa_oficial = st.sidebar.number_input("💵 Tasa BCV Hoy (Bs/$)", min_value=1.0, value=tasa_bcv_auto, format="%.2f")

opciones_menu = [
    "🏠 Inicio / Dashboard", 
    "🛒 Registrar Venta", 
    "💰 Transacciones Pagadas",
    "👥 Clientes y Cuentas por Cobrar", 
    "📦 Productos e Inventario", 
    "💸 Gastos y Proveedores",
    "📅 Almanaque de Ventas",
    "📈 Reportes y Métricas"
]

menu = st.sidebar.radio("Ir a:", opciones_menu, key='menu_radio')

# ---------------------------------------------------------
# INICIO / DASHBOARD
# ---------------------------------------------------------
if menu == "🏠 Inicio / Dashboard":
    st.markdown("""
        <div class="header-container">
            <div class="header-title">👑 OLINUTS</div>
            <div class="header-subtitle">Gustavo Oliveira / Propietario</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f'<div class="tasa-card">💵 Tasa Oficial BCV: <b>{tasa_oficial:,.2f} Bs/$</b></div>', unsafe_allow_html=True)
    
    fecha_hoy_str = date.today().strftime("%Y-%m-%d")
    
    try:
        res_v_hoy = supabase.table("ventas").select("cantidad, precio_unitario, costo_unitario, ganancia_total").like("fecha", f"{fecha_hoy_str}%").execute()
        df_ventas_hoy = pd.DataFrame(res_v_hoy.data)
    except Exception:
        df_ventas_hoy = pd.DataFrame()

    try:
        res_g_hoy = supabase.table("gastos").select("monto_usd").like("fecha", f"{fecha_hoy_str}%").execute()
        df_gastos_hoy = pd.DataFrame(res_g_hoy.data)
    except Exception:
        df_gastos_hoy = pd.DataFrame()
    
    if not df_ventas_hoy.empty:
        df_ventas_hoy['ingreso'] = df_ventas_hoy['cantidad'] * df_ventas_hoy['precio_unitario']
        df_ventas_hoy['costo'] = df_ventas_hoy['cantidad'] * df_ventas_hoy['costo_unitario']
        ventas_hoy = float(df_ventas_hoy['ingreso'].sum())
        costos_prod_hoy = float(df_ventas_hoy['costo'].sum())
    else:
        ventas_hoy = 0.0
        costos_prod_hoy = 0.0

    gastos_directos_hoy = float(df_gastos_hoy['monto_usd'].apply(limpiar_float).sum()) if not df_gastos_hoy.empty else 0.0
    costos_totales_hoy = costos_prod_hoy + gastos_directos_hoy
    balance_hoy = ventas_hoy - costos_totales_hoy

    st.markdown(f"""
        <div class="business-card">
            <div class="card-title">Tu negocio hoy</div>
            <div class="card-amount">${ventas_hoy:,.2f}</div>
            <div style="font-size: 15px; color: #555; margin-bottom: 15px;">Bs. {ventas_hoy * tasa_oficial:,.2f}</div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 15px;">
                <div>
                    <span style="font-size: 14px; color: #666;">Balance Real</span><br>
                    <span class="amount-green">${balance_hoy:,.2f}</span><br>
                    <span style="font-size: 13px; color: #666;">Bs. {balance_hoy * tasa_oficial:,.2f}</span>
                </div>
                <div style="text-align: right;">
                    <span style="font-size: 14px; color: #666;">Egresos/Costos hoy</span><br>
                    <span class="amount-red">${costos_totales_hoy:,.2f}</span><br>
                    <span style="font-size: 13px; color: #666;">Bs. {costos_totales_hoy * tasa_oficial:,.2f}</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.button("🛒  Nueva Venta", key="btn_nv", use_container_width=True, on_click=ir_a_seccion, args=("🛒 Registrar Venta",))

    c1, c2 = st.columns(2)
    with c1:
        st.button("📦  Inventario", key="btn_inv", use_container_width=True, on_click=ir_a_seccion, args=("📦 Productos e Inventario",))
    with c2:
        st.button("💸  Gastos y Materia Prima", key="btn_gas", use_container_width=True, on_click=ir_a_seccion, args=("💸 Gastos y Proveedores",))

    st.button("👥  Gestión de Clientes", key="btn_deu", use_container_width=True, on_click=ir_a_seccion, args=("👥 Clientes y Cuentas por Cobrar",))
    st.button("💰  Transacciones Pagadas", key="btn_trans_pag", use_container_width=True, on_click=ir_a_seccion, args=("💰 Transacciones Pagadas",))
    st.button("📅  Almanaque de Ventas", key="btn_cal_home", use_container_width=True, on_click=ir_a_seccion, args=("📅 Almanaque de Ventas",))

    st.divider()

    mes_actual_str = date.today().strftime("%Y-%m")
    try:
        res_mes = supabase.table("ventas").select("ganancia_total, cantidad, productos(nombre)").like("fecha", f"{mes_actual_str}%").execute()
        df_ventas_mes = pd.DataFrame(res_mes.data)
    except Exception:
        df_ventas_mes = pd.DataFrame()
    
    col_stat1, col_stat2 = st.columns(2)
    with col_stat1:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.caption("Producto estrella del mes")
        if not df_ventas_mes.empty:
            df_ventas_mes['prod_nom'] = df_ventas_mes['productos'].apply(lambda x: x['nombre'] if isinstance(x, dict) else 'Producto')
            grouped = df_ventas_mes.groupby('prod_nom')['cantidad'].sum()
            prod_estrella = grouped.idxmax()
            cant_estrella = grouped.max()
            st.subheader(f"⭐ {prod_estrella}")
            st.write(f"Vendidos: **{cant_estrella} uds.**")
        else:
            st.write("Sin ventas este mes")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_stat2:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.caption("Ganancias estimadas ventas mes")
        ganancias_mes = float(df_ventas_mes['ganancia_total'].sum()) if not df_ventas_mes.empty else 0.0
        st.subheader(f"💵 ${ganancias_mes:,.2f}")
        st.caption(f"Bs. {ganancias_mes * tasa_oficial:,.2f}")
        st.success("📈 Conectado a Supabase Nube")
        st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# REGISTRAR VENTA
# ---------------------------------------------------------
elif menu == "🛒 Registrar Venta":
    col_header, col_home = st.columns([3, 1])
    with col_header:
        st.markdown('<div class="section-header-yellow">🛒 Registrar Venta</div>', unsafe_allow_html=True)
    with col_home:
        st.button("🏠 Volver al Inicio", key="btn_home_v", on_click=ir_a_seccion, args=("🏠 Inicio / Dashboard",), use_container_width=True)
    
    res_p = supabase.table("productos").select("*").order("nombre").execute()
    res_c = supabase.table("clientes").select("*").order("nombre").execute()
    
    df_prods = pd.DataFrame(res_p.data)
    df_clientes = pd.DataFrame(res_c.data)

    if df_prods.empty:
        st.warning("⚠️ Primero debes agregar productos en la sección 'Productos e Inventario'.")
    else:
        col_f, col_c = st.columns(2)
        with col_f:
            st.markdown('<div class="sub-header-yellow">📅 Fecha de la Venta</div>', unsafe_allow_html=True)
            fecha_venta_elegida = st.date_input("Selecciona la fecha de la venta", value=date.today())

        with col_c:
            st.markdown('<div class="sub-header-yellow">👤 Cliente</div>', unsafe_allow_html=True)
            busqueda_cliente_rv = st.text_input("🔍 Buscar Cliente...", placeholder="Escribe el nombre del cliente", key="busq_cli_rv")
            
            if not df_clientes.empty and busqueda_cliente_rv.strip() != "":
                df_clientes_filt = df_clientes[df_clientes['nombre'].str.contains(busqueda_cliente_rv, case=False, na=False)]
            else:
                df_clientes_filt = df_clientes

            opciones_clientes = {"➕ ¡Agregar Nuevo Cliente!": None}
            if not df_clientes_filt.empty:
                for _, row in df_clientes_filt.iterrows():
                    opciones_clientes[f"{row['nombre']} ({row['telefono']})"] = row
                
            cliente_seleccionado_str = st.selectbox("Selecciona un Cliente", list(opciones_clientes.keys()), key="sb_cli_rv")
            
            if cliente_seleccionado_str == "➕ ¡Agregar Nuevo Cliente!":
                with st.expander("👤 Registrar Nuevo Cliente Rápido", expanded=True):
                    nuevo_nombre = st.text_input("Nombre Completo del Cliente", key="nv_cli_nom")
                    nuevo_tel = st.text_input("Teléfono / WhatsApp", key="nv_cli_tel")
                    if st.button("💾 Guardar Cliente", use_container_width=True, type="primary"):
                        if nuevo_nombre.strip() != "":
                            try:
                                supabase.table("clientes").insert({
                                    "nombre": str(nuevo_nombre.strip()), 
                                    "telefono": str(nuevo_tel.strip() if nuevo_tel.strip() else 'Sin teléfono')
                                }).execute()
                                st.success(f"✅ Cliente '{nuevo_nombre}' guardado. Por favor selecciónalo en la lista.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error al guardar cliente: {e}")
                        else:
                            st.error("El nombre del cliente no puede estar vacío.")
                cliente_data = None
            else:
                cliente_data = opciones_clientes[cliente_seleccionado_str]

        st.divider()

        st.markdown('<div class="sub-header-yellow">📦 Agregar Productos al Pedido</div>', unsafe_allow_html=True)
        
        busqueda_prod_rv = st.text_input("🔍 Buscar Producto...", placeholder="Escribe para buscar un producto...", key="busq_prod_rv")
        
        df_prods_disponibles = df_prods[df_prods['stock'] > 0] if not df_prods.empty else pd.DataFrame()
        if not df_prods_disponibles.empty and busqueda_prod_rv.strip() != "":
            df_prods_disponibles = df_prods_disponibles[df_prods_disponibles['nombre'].str.contains(busqueda_prod_rv, case=False, na=
