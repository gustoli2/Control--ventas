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
            df_prods_disponibles = df_prods_disponibles[df_prods_disponibles['nombre'].str.contains(busqueda_prod_rv, case=False, na=False)]
        
        if df_prods_disponibles.empty:
            st.error("❌ No se encontraron productos con stock disponible.")
        else:
            opciones_productos = {f"{row['nombre']} (Stock: {int(limpiar_float(row['stock']))})": row for _, row in df_prods_disponibles.iterrows()}
            prod_seleccionado_str = st.selectbox("Selecciona un Producto", list(opciones_productos.keys()), key="sb_prod_rv")
            prod_data = opciones_productos[prod_seleccionado_str]

            c_unit = limpiar_float(prod_data.get('costo_unitario', 0.0))
            p_vent = limpiar_float(prod_data.get('precio_venta', 0.0))
            s_act = int(limpiar_float(prod_data.get('stock', 0)))

            cantidad_ya_en_carrito = sum(item['cantidad'] for item in st.session_state['carrito_ventas'] if item['producto_id'] == prod_data['id'])
            stock_restringido = s_act - cantidad_ya_en_carrito

            col_p1, col_p2, col_p3 = st.columns([2, 1, 1])
            with col_p1:
                st.info(f"**Precio:** ${p_vent:.2f} (~ Bs. {p_vent*tasa_oficial:,.2f}) | **Costo:** ${c_unit:.2f}")
            with col_p2:
                if stock_restringido > 0:
                    cant_a_agregar = st.number_input("Cantidad", min_value=1, max_value=stock_restringido, value=1, step=1)
                else:
                    st.warning("⚠️ Límite de stock alcanzado")
                    cant_a_agregar = 0
            with col_p3:
                st.write("")
                st.write("")
                if stock_restringido > 0:
                    if st.button("➕ Agregar al Carrito", type="secondary", use_container_width=True):
                        st.session_state['carrito_ventas'].append({
                            'producto_id': int(prod_data['id']),
                            'nombre': str(prod_data['nombre']),
                            'cantidad': int(cant_a_agregar),
                            'precio_unitario': float(p_vent),
                            'costo_unitario': float(c_unit),
                            'subtotal': float(p_vent) * int(cant_a_agregar),
                            'ganancia': (float(p_vent) - float(c_unit)) * int(cant_a_agregar)
                        })
                        st.rerun()

        st.markdown('<div class="sub-header-yellow">🛒 Resumen del Carrito de Ventas</div>', unsafe_allow_html=True)
        
        if len(st.session_state['carrito_ventas']) == 0:
            st.info("🛒 Tu carrito está vacío.")
        else:
            for idx, item in enumerate(st.session_state['carrito_ventas']):
                col_i1, col_i2, col_i3, col_i4, col_i5 = st.columns([3, 1, 2, 2, 1])
                col_i1.write(f"**{item['nombre']}**")
                col_i2.write(f"{item['cantidad']} uds.")
                col_i3.write(f"${item['precio_unitario']:.2f} c/u")
                col_i4.write(f"**Subtotal: ${item['subtotal']:.2f}**")
                if col_i5.button("🗑️", key=f"del_cart_{idx}"):
                    st.session_state['carrito_ventas'].pop(idx)
                    st.rerun()

            monto_total_pedido = sum(item['subtotal'] for item in st.session_state['carrito_ventas'])
            ganancia_total_pedido = sum(item['ganancia'] for item in st.session_state['carrito_ventas'])

            st.divider()

            col_tot1, col_tot2 = st.columns(2)
            col_tot1.metric("Total General Pedido", f"${monto_total_pedido:,.2f}", f"Bs. {monto_total_pedido * tasa_oficial:,.2f}")
            col_tot2.metric("Ganancia Estimada Pedido", f"${ganancia_total_pedido:,.2f}")

            tipo_pago = st.radio("Condición de Pago del Pedido", ["💵 Pagado de Contado", "📝 Crédito / Cuenta por Cobrar"], horizontal=True)
            estado_pago_val = "Pagado" if "Pagado" in tipo_pago else "Pendiente"

            if cliente_data is None:
                st.warning("⚠️ Selecciona un cliente registrado para finalizar la venta.")
            else:
                col_b_clear, col_b_confirm = st.columns([1, 2])
                with col_b_clear:
                    if st.button("❌ Vaciar Carrito", use_container_width=True):
                        st.session_state['carrito_ventas'] = []
                        st.rerun()

                with col_b_confirm:
                    if st.button("🎉 Confirmar y Registrar Venta Completa", type="primary", use_container_width=True):
                        try:
                            hora_actual_str = datetime.now().strftime(" %H:%M:%S")
                            fecha_final_str = fecha_venta_elegida.strftime("%Y-%m-%d") + hora_actual_str

                            for item in st.session_state['carrito_ventas']:
                                saldo_ini_item = 0.0 if estado_pago_val == "Pagado" else item['subtotal']
                                
                                supabase.table("ventas").insert({
                                    "producto_id": int(item['producto_id']),
                                    "cliente_id": int(cliente_data['id']),
                                    "cantidad": int(item['cantidad']),
                                    "precio_unitario": float(item['precio_unitario']),
                                    "costo_unitario": float(item['costo_unitario']),
                                    "ganancia_total": float(item['ganancia']),
                                    "estado_pago": str(estado_pago_val),
                                    "saldo_pendiente": float(saldo_ini_item),
                                    "fecha": str(fecha_final_str)
                                }).execute()
                                
                                p_id_curr = item['producto_id']
                                stock_actual = int(limpiar_float(df_prods[df_prods['id'] == p_id_curr]['stock'].values[0]))
                                nuevo_stock = max(0, stock_actual - int(item['cantidad']))
                                supabase.table("productos").update({"stock": int(nuevo_stock)}).eq("id", int(p_id_curr)).execute()

                            st.session_state['carrito_ventas'] = []
                            st.balloons()
                            st.success(f"🎉 ¡Venta registrada exitosamente para {cliente_data['nombre']} por un total de ${monto_total_pedido:,.2f}!")
                        except Exception as e:
                            st.error(f"❌ Error al registrar la venta: {e}")

# ---------------------------------------------------------
# TRANSACCIONES PAGADAS
# ---------------------------------------------------------
elif menu == "💰 Transacciones Pagadas":
    col_header, col_home = st.columns([3, 1])
    with col_header:
        st.markdown('<div class="section-header-yellow">💰 Transacciones Pagadas</div>', unsafe_allow_html=True)
    with col_home:
        st.button("🏠 Volver al Inicio", key="btn_home_tp", on_click=ir_a_seccion, args=("🏠 Inicio / Dashboard",), use_container_width=True)

    st.markdown('<div class="sub-header-yellow">📅 Filtrar Pagos por Fecha</div>', unsafe_allow_html=True)
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        fecha_ini = st.date_input("Fecha Inicial", value=date.today().replace(day=1))
    with col_f2:
        fecha_fin = st.date_input("Fecha Final", value=date.today())

    res_p = supabase.table("ventas").select("id, cliente_id, producto_id, cantidad, precio_unitario, ganancia_total, estado_pago, fecha, clientes(nombre, telefono), productos(nombre)").eq("estado_pago", "Pagado").order("fecha", desc=True).execute()
    df_pagadas = pd.DataFrame(res_p.data)

    if not df_pagadas.empty:
        df_pagadas['fecha_dt'] = pd.to_datetime(df_pagadas['fecha']).dt.date
        df_filt_pagadas = df_pagadas[(df_pagadas['fecha_dt'] >= fecha_ini) & (df_pagadas['fecha_dt'] <= fecha_fin)].copy()

        if df_filt_pagadas.empty:
            st.info(f"No hay transacciones pagadas entre el {fecha_ini.strftime('%d/%m/%Y')} y el {fecha_fin.strftime('%d/%m/%Y')}.")
        else:
            df_filt_pagadas['Cliente'] = df_filt_pagadas['clientes'].apply(lambda x: x['nombre'] if isinstance(x, dict) else 'Cliente')
            df_filt_pagadas['Producto'] = df_filt_pagadas['productos'].apply(lambda x: x['nombre'] if isinstance(x, dict) else 'Producto')
            df_filt_pagadas['Monto Total ($)'] = df_filt_pagadas['cantidad'] * df_filt_pagadas['precio_unitario']
            df_filt_pagadas['Monto Total (Bs.)'] = df_filt_pagadas['Monto Total ($)'] * tasa_oficial

            total_recaudado = float(df_filt_pagadas['Monto Total ($)'].sum())
            total_ganancia = float(df_filt_pagadas['ganancia_total'].sum())

            c_met1, c_met2 = st.columns(2)
            c_met1.metric("Total Recaudado Período", f"${total_recaudado:,.2f}", f"Bs. {total_recaudado * tasa_oficial:,.2f}")
            c_met2.metric("Ganancia Total Período", f"${total_ganancia:,.2f}")

            st.divider()

            df_display = df_filt_pagadas[['id', 'Cliente', 'Producto', 'cantidad', 'precio_unitario', 'Monto Total ($)', 'Monto Total (Bs.)', 'ganancia_total', 'fecha']].copy()
            df_display.rename(columns={
                'id': 'ID Venta',
                'cantidad': 'Cantidad',
                'precio_unitario': 'Precio Unit ($)',
                'ganancia_total': 'Ganancia ($)',
                'fecha': 'Fecha / Hora'
            }, inplace=True)

            st.dataframe(df_display, use_container_width=True)

            with st.expander("🗑️ Anular / Borrar una Transacción Pagada (En caso de error)"):
                dict_pagos_del = {
                    f"ID #{row['id']} - {row['Cliente']} | {row['Producto']} ({row['cantidad']} uds) - ${row['Monto Total ($)']:.2f} ({row['fecha']})": row 
                    for _, row in df_filt_pagadas.iterrows()
                }
                pago_sel_del_str = st.selectbox("Selecciona la transacción a anular", list(dict_pagos_del.keys()))
                p_del_info = dict_pagos_del[pago_sel_del_str]

                if st.button("🗑️ Anular Transacción y Restituir Inventario", type="primary", use_container_width=True):
                    try:
                        res_p_curr = supabase.table("productos").select("stock").eq("id", int(p_del_info['producto_id'])).execute()
                        if res_p_curr.data:
                            stock_act = int(limpiar_float(res_p_curr.data[0]['stock']))
                            supabase.table("productos").update({"stock": stock_act + int(p_del_info['cantidad'])}).eq("id", int(p_del_info['producto_id'])).execute()

                        supabase.table("ventas").delete().eq("id", int(p_del_info['id'])).execute()
                        st.warning(f"🗑️ Transacción #{p_del_info['id']} anulada correctamente.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error al anular la transacción: {e}")
    else:
        st.info("Aún no hay ventas o pagos registrados como completados.")

# ---------------------------------------------------------
# GESTIÓN DE CLIENTES Y CUENTAS POR COBRAR
# ---------------------------------------------------------
elif menu == "👥 Clientes y Cuentas por Cobrar":
    col_header, col_home = st.columns([3, 1])
    with col_header:
        st.markdown('<div class="section-header-yellow">👥 Gestión de Clientes</div>', unsafe_allow_html=True)
    with col_home:
        st.button("🏠 Volver al Inicio", key="btn_home_c", on_click=ir_a_seccion, args=("🏠 Inicio / Dashboard",), use_container_width=True)

    card_col1, card_col2 = st.columns(2)
    with card_col1:
        st.button("📋 Listado General", key="btn_sub_list", use_container_width=True, on_click=ir_a_subseccion_clientes, args=("📋 Listado General",))
        st.button("✏️ Editar / Eliminar", key="btn_sub_edit", use_container_width=True, on_click=ir_a_subseccion_clientes, args=("✏️ Editar / Eliminar",))
    with card_col2:
        st.button("➕ Agregar Cliente", key="btn_sub_add", use_container_width=True, on_click=ir_a_subseccion_clientes, args=("➕ Agregar Cliente",))
        st.button("📋 Cuentas por Cobrar", key="btn_sub_cxc", use_container_width=True, on_click=ir_a_subseccion_clientes, args=("📋 Cuentas por Cobrar",))

    st.divider()
    submenu = st.session_state['subseccion_clientes']

    if submenu == "📋 Listado General":
        st.markdown('<div class="sub-header-yellow">📋 Listado General de Clientes</div>', unsafe_allow_html=True)
        res_c = supabase.table("clientes").select("id, nombre, telefono").order("nombre").execute()
        df_cli = pd.DataFrame(res_c.data)
        
        if not df_cli.empty:
            busq_cli_gen = st.text_input("🔍 Buscar Cliente...", placeholder="Escribe para buscar...")
            if busq_cli_gen.strip() != "":
                df_cli = df_cli[df_cli['nombre'].str.contains(busq_cli_gen, case=False, na=False)]
            st.dataframe(df_cli, use_container_width=True)
        else:
            st.info("No hay clientes registrados.")

    elif submenu == "➕ Agregar Cliente":
        st.markdown('<div class="sub-header-yellow">➕ Agregar Nuevo Cliente</div>', unsafe_allow_html=True)
        with st.form("form_cliente"):
            nombre_cliente = st.text_input("Nombre Completo del Cliente")
            telefono_cliente = st.text_input("Número de Teléfono / WhatsApp")
            guardar_cliente = st.form_submit_button("Guardar Cliente")

            if guardar_cliente:
                if nombre_cliente.strip() != "":
                    try:
                        supabase.table("clientes").insert({
                            "nombre": str(nombre_cliente.strip()), 
                            "telefono": str(telefono_cliente.strip() if telefono_cliente.strip() else 'Sin teléfono')
                        }).execute()
                        st.success(f"✅ Cliente '{nombre_cliente}' agregado.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error al guardar cliente: {e}")
                else:
                    st.error("El nombre no puede estar vacío.")

    elif submenu == "✏️ Editar / Eliminar":
        st.markdown('<div class="sub-header-yellow">✏️ Editar o Eliminar Cliente</div>', unsafe_allow_html=True)
        res_c = supabase.table("clientes").select("*").order("nombre").execute()
        df_cli_edit = pd.DataFrame(res_c.data)

        if not df_cli_edit.empty:
            dict_cli = {f"{row['nombre']} (ID: {row['id']})": row for _, row in df_cli_edit.iterrows()}
            cli_edit_str = st.selectbox("Selecciona el cliente", list(dict_cli.keys()))
            cli_sel = dict_cli[cli_edit_str]

            with st.form("form_editar_cliente_reg"):
                n_nombre = st.text_input("Nombre", value=cli_sel['nombre'])
                n_telefono = st.text_input("Teléfono", value=cli_sel['telefono'])
                col_b1, col_b2 = st.columns(2)
                with col_b1: act_cli = st.form_submit_button("💾 Actualizar", type="primary")
                with col_b2: elim_cli = st.form_submit_button("🗑️ Eliminar")

                if act_cli:
                    try:
                        supabase.table("clientes").update({
                            "nombre": str(n_nombre.strip()), 
                            "telefono": str(n_telefono.strip())
                        }).eq("id", int(cli_sel['id'])).execute()
                        st.success("✅ Cliente actualizado.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error al actualizar: {e}")

                if elim_cli:
                    if cli_sel['id'] == 1:
                        st.error("❌ No se puede eliminar el cliente general por defecto.")
                    else:
                        try:
                            supabase.table("ventas").update({"cliente_id": 1}).eq("cliente_id", int(cli_sel['id'])).execute()
                            supabase.table("clientes").delete().eq("id", int(cli_sel['id'])).execute()
                            st.warning("🗑️ Cliente eliminado.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error al eliminar: {e}")

    elif submenu == "📋 Cuentas por Cobrar":
        res_v = supabase.table("ventas").select("id, cliente_id, producto_id, saldo_pendiente, cantidad, precio_unitario, fecha, clientes(id, nombre, telefono), productos(nombre)").eq("estado_pago", "Pendiente").gt("saldo_pendiente", 0).order("fecha", desc=True).execute()
        df_deudas = pd.DataFrame(res_v.data)

        if df_deudas.empty:
            st.success("🎉 ¡No hay cuentas por cobrar pendientes!")
        else:
            df_deudas['Cliente'] = df_deudas['clientes'].apply(lambda x: x['nombre'] if isinstance(x, dict) else 'Cliente')
            df_deudas['Teléfono'] = df_deudas['clientes'].apply(lambda x: x['telefono'] if isinstance(x, dict) else 'S/N')
            df_deudas['Producto'] = df_deudas['productos'].apply(lambda x: x['nombre'] if isinstance(x, dict) else 'Producto')
            
            df_deudas_resumen = df_deudas.groupby(['cliente_id', 'Cliente', 'Teléfono'])['saldo_pendiente'].sum().reset_index()
            df_deudas_resumen.rename(columns={'saldo_pendiente': 'Saldo Pendiente ($)'}, inplace=True)

            total_general = df_deudas_resumen['Saldo Pendiente ($)'].sum()
            col_m1, col_m2 = st.columns(2)
            col_m1.metric("Total USD por Cobrar", f"${total_general:,.2f}")
            col_m2.metric("Total Bs. por Cobrar", f"Bs. {total_general * tasa_oficial:,.2f}")
            
            st.markdown('<div class="sub-header-yellow">💵 Registrar Abono / Recordatorio</div>', unsafe_allow_html=True)
            
            opciones_deudores = {f"{row['Cliente']} (Monto: ${row['Saldo Pendiente ($)']:,.2f})": row for _, row in df_deudas_resumen.iterrows()}
            cliente_sel_str = st.selectbox("Selecciona el Cliente", list(opciones_deudores.keys()))
            cliente_info = opciones_deudores[cliente_sel_str]
            cliente_id_sel = int(cliente_info['cliente_id'])
            deuda_maxima = limpiar_float(cliente_info['Saldo Pendiente ($)'])
            deuda_maxima_bs = deuda_maxima * tasa_oficial

            tel_bruto = str(cliente_info['Teléfono']).replace(" ", "").replace("-", "").replace("+", "")
            num_wa = "58" + tel_bruto[1:] if tel_bruto.startswith("0") else tel_bruto

            m_nombre = cliente_info['Cliente']
            m_monto_usd = f"${deuda_maxima:,.2f}".replace(",", "@").replace(".", ",").replace("@", ".")
            m_monto_bs = f"Bs. {deuda_maxima_bs:,.2f}".replace(",", "@").replace(".", ",").replace("@", ".")

            texto_msj = (
                f"Hola {m_nombre},\n\n"
                f"Queremos recordarte que tienes pagos pendientes de {m_monto_usd} ({m_monto_bs}) con Olinuts. "
                f"Nada mejor que llevar tus cuentas al día, por eso no olvides realizar los pagos. "
                f"Que tengas un feliz día!"
            )

            link_wa = f"https://wa.me/{num_wa}?text={urllib.parse.quote(texto_msj)}"

            st.markdown(f'''
                <a href="{link_wa}" target="_blank" style="text-decoration: none;">
                    <div style="
                        background-color: #25D366; 
                        color: white; 
                        padding: 14px 20px; 
                        border-radius: 12px; 
                        text-align: center; 
                        font-weight: bold; 
                        font-size: 18px;
                        margin-top: 10px;
                        margin-bottom: 20px;
                        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);">
                        📲 Enviar Recordatorio por WhatsApp a {m_nombre}
                    </div>
                </a>
            ''', unsafe_allow_html=True)

            if deuda_maxima <= 0:
                st.success(f"🎉 ¡El cliente {m_nombre} ya no tiene deudas pendientes!")
            else:
                col_ab1, col_ab2 = st.columns(2)
                with col_ab1:
                    monto_abono = st.number_input("Monto a Abonar ($)", min_value=0.01, max_value=deuda_maxima, value=deuda_maxima, step=0.5)
                with col_ab2:
                    btn_abonar = st.button("💰 Registrar Abono", type="primary", use_container_width=True)

                if btn_abonar:
                    res_pend = supabase.table("ventas").select("id, saldo_pendiente").eq("cliente_id", cliente_id_sel).eq("estado_pago", "Pendiente").gt("saldo_pendiente", 0).order("fecha").execute()
                    abono_rest = float(monto_abono)

                    for v_item in res_pend.data:
                        if abono_rest <= 0: break
                        s_pend = float(limpiar_float(v_item['saldo_pendiente']))
                        if abono_rest >= s_pend:
                            abono_rest -= s_pend
                            supabase.table("ventas").update({"saldo_pendiente": 0.0, "estado_pago": "Pagado"}).eq("id", int(v_item['id'])).execute()
                        else:
                            nuevo_s = s_pend - abono_rest
                            supabase.table("ventas").update({"saldo_pendiente": float(nuevo_s)}).eq("id", int(v_item['id'])).execute()
                            abono_rest = 0.0

                    st.success(f"🎉 Abono de ${monto_abono:,.2f} registrado exitosamente.")
                    st.rerun()

            with st.expander("🗑️ Borrar un Registro de Deuda Específico (En caso de error)"):
                st.caption("Selecciona una venta a crédito para eliminarla y reponer el stock correspondiente.")
                dict_deudas_borrar = {
                    f"ID Venta #{row['id']} - {row['Cliente']} | {row['Producto']} ({row['cantidad']} uds) - Pendiente: ${row['saldo_pendiente']:.2f} ({row['fecha']})": row 
                    for _, row in df_deudas.iterrows()
                }
                
                venta_a_borrar_str = st.selectbox("Selecciona la deuda a borrar", list(dict_deudas_borrar.keys()))
                v_del_info = dict_deudas_borrar[venta_a_borrar_str]

                if st.button("🗑️ Eliminar Venta y Restablecer Inventario", type="primary", use_container_width=True):
                    try:
                        res_p_curr = supabase.table("productos").select("stock").eq("id", int(v_del_info['producto_id'])).execute()
                        if res_p_curr.data:
                            stock_actual = int(limpiar_float(res_p_curr.data[0]['stock']))
                            supabase.table("productos").update({"stock": stock_actual + int(v_del_info['cantidad'])}).eq("id", int(v_del_info['producto_id'])).execute()
                        
                        supabase.table("ventas").delete().eq("id", int(v_del_info['id'])).execute()
                        
                        st.warning(f"🗑️ Registro de deuda #{v_del_info['id']} eliminado y stock restituido.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error al borrar el registro: {e}")

            st.divider()
            st.markdown('<div class="sub-header-yellow">📋 Registro General de Clientes Deudores (Detalle por Compra)</div>', unsafe_allow_html=True)
            
            df_tabla_deudores = df_deudas[['Cliente', 'Teléfono', 'Producto', 'cantidad', 'precio_unitario', 'saldo_pendiente', 'fecha']].copy()
            df_tabla_deudores['Pendiente (Bs.)'] = df_tabla_deudores['saldo_pendiente'] * tasa_oficial
            
            df_tabla_deudores.rename(columns={
                'cantidad': 'Cantidad',
                'precio_unitario': 'Precio Unit. ($)',
                'saldo_pendiente': 'Saldo Pendiente ($)',
                'fecha': 'Fecha de Compra'
            }, inplace=True)

            st.dataframe(df_tabla_deudores[['Cliente', 'Teléfono', 'Producto', 'Cantidad', 'Precio Unit. ($)', 'Saldo Pendiente ($)', 'Pendiente (Bs.)', 'Fecha de Compra']], use_container_width=True)

# ---------------------------------------------------------
# PRODUCTOS E INVENTARIO
# ---------------------------------------------------------
elif menu == "📦 Productos e Inventario":
    col_header, col_home = st.columns([3, 1])
    with col_header:
        st.markdown('<div class="section-header-yellow">📦 Gestión de Inventario</div>', unsafe_allow_html=True)
    with col_home:
        st.button("🏠 Volver al Inicio", key="btn_home_p", on_click=ir_a_seccion, args=("🏠 Inicio / Dashboard",), use_container_width=True)

    inv_col1, inv_col2 = st.columns(2)
    with inv_col1:
        st.button("📋 Listado de Productos", key="btn_inv_list", use_container_width=True, on_click=ir_a_subseccion_inventario, args=("📋 Listado de Productos",))
        st.button("✏️ Editar / Eliminar", key="btn_inv_edit", use_container_width=True, on_click=ir_a_subseccion_inventario, args=("✏️ Editar / Eliminar",))
    with inv_col2:
        st.button("➕ Agregar Producto", key="btn_inv_add", use_container_width=True, on_click=ir_a_subseccion_inventario, args=("➕ Agregar Nuevo Producto",))

    st.divider()
    sub_inv = st.session_state['subseccion_inventario']

    if sub_inv == "📋 Listado de Productos":
        res_p = supabase.table("productos").select("*").order("nombre").execute()
        df_prods = pd.DataFrame(res_p.data)
        
        if not df_prods.empty:
            total_referencias = len(df_prods)
            df_prods['costo_unitario'] = df_prods['costo_unitario'].apply(limpiar_float)
            df_prods['precio_venta'] = df_prods['precio_venta'].apply(limpiar_float)
            df_prods['stock'] = df_prods['stock'].apply(limpiar_float)

            df_prods['val_costo_tot'] = df_prods['costo_unitario'] * df_prods['stock']
            costo_total_inv = float(df_prods['val_costo_tot'].sum())

            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.markdown(f"""
                    <div class="business-card" style="padding: 16px; text-align: center; margin-bottom: 15px;">
                        <span style="color: #666; font-size: 16px;">Total de referencias</span>
                        <div style="font-size: 32px; font-weight: bold; color: #111;">{total_referencias}</div>
                    </div>
                """, unsafe_allow_html=True)
            with col_m2:
                st.markdown(f"""
                    <div class="business-card" style="padding: 16px; text-align: center; margin-bottom: 15px;">
                        <span style="color: #666; font-size: 16px;">Costo total inventario</span>
                        <div style="font-size: 32px; font-weight: bold; color: #111;">${costo_total_inv:,.2f}</div>
                    </div>
                """, unsafe_allow_html=True)

            busq_prod = st.text_input("🔍 Buscar producto...", placeholder="Escribe para buscar...")
            
            f_col1, f_col2, f_col3 = st.columns(3)
            with f_col1:
                if st.button("🏷️ Todas", use_container_width=True):
                    st.session_state['filtro_inv'] = "Todas"
            with f_col2:
                if st.button("⚠️ Unidades bajas", use_container_width=True):
                    st.session_state['filtro_inv'] = "Unidades bajas"
            with f_col3:
                if st.button("✅ Disponibles", use_container_width=True):
                    st.session_state['filtro_inv'] = "Disponibles"

            df_filtered = df_prods.copy()
            if busq_prod.strip() != "":
                df_filtered = df_filtered[df_filtered['nombre'].str.contains(busq_prod, case=False, na=False)]

            if st.session_state['filtro_inv'] == "Unidades bajas":
                df_filtered = df_filtered[df_filtered['stock'] <= 3]
            elif st.session_state['filtro_inv'] == "Disponibles":
                df_filtered = df_filtered[df_filtered['stock'] > 0]

            st.caption(f"Mostrando productos: **{st.session_state['filtro_inv']}** ({len(df_filtered)} items)")

            if df_filtered.empty:
                st.info("No hay productos que coincidan con el filtro seleccionado.")
            else:
                for _, p_row in df_filtered.iterrows():
                    p_name = p_row['nombre']
                    p_stock = int(limpiar_float(p_row['stock']))
                    p_precio = limpiar_float(p_row['precio_venta'])
                    p_precio_bs = p_precio * tasa_oficial
                    p_img_url = p_row.get('imagen_url', '')

                    if p_stock == 0:
                        badge_html = '<span class="badge-no-stock">No disponible</span>'
                    elif p_stock <= 3:
                        badge_html = f'<span class="badge-low-stock">⚠️ Pocas unidades: {p_stock} uds</span>'
                    else:
                        badge_html = f'<span class="badge-in-stock">Disponible: {p_stock} uds</span>'

                    if p_img_url and not pd.isna(p_img_url) and str(p_img_url).strip() != "":
                        icon_html = f'<img src="{p_img_url}">'
                    else:
                        icon_html = '🥜'

                    st.markdown(f"""
                        <div class="product-card">
                            <div class="product-icon-box">{icon_html}</div>
                            <div class="product-info">
                                <div class="product-title">{p_name}</div>
                                {badge_html}<br>
                                <span class="product-price">${p_precio:,.2f}</span> 
                                <span class="product-price-bs">(~ Bs. {p_precio_bs:,.2f})</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

        else:
            st.info("No hay productos registrados en el inventario.")

    elif sub_inv == "➕ Agregar Nuevo Producto":
        st.markdown('<div class="sub-header-yellow">➕ Agregar Nuevo Producto</div>', unsafe_allow_html=True)
        
        uploaded_img = st.file_uploader("📷 Subir Fotografía del Producto (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"], key="up_img_new")
        imagen_url_txt = st.text_input("🔗 O pegar URL de la Imagen (Opcional)", placeholder="https://ejemplo.com/imagen.jpg", key="txt_img_new")

        with st.form("form_producto"):
            nombre = st.text_input("Nombre del Producto")
            col1, col2, col3 = st.columns(3)
            with col1: costo = st.number_input("Costo Unitario ($)", min_value=0.0, value=0.0, format="%.2f")
            with col2: precio = st.number_input("Precio de Venta ($)", min_value=0.0, value=0.0, format="%.2f")
            with col3: stock = st.number_input("Stock Inicial", min_value=0, value=0, step=1)

            if st.form_submit_button("Guardar Producto"):
                if nombre.strip() != "":
                    try:
                        final_img_str = ""
                        if uploaded_img is not None:
                            final_img_str = archivo_a_base64(uploaded_img)
                        elif imagen_url_txt.strip() != "":
                            final_img_str = str(imagen_url_txt.strip())

                        nuevo_producto = {
                            "nombre": str(nombre.strip()),
                            "costo_unitario": float(limpiar_float(costo)),
                            "precio_venta": float(limpiar_float(precio)),
                            "stock": int(limpiar_float(stock)),
                            "imagen_url": str(final_img_str)
                        }
                        supabase.table("productos").insert(nuevo_producto).execute()
                        st.success(f"✅ Producto '{nombre}' agregado exitosamente.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error al guardar en Supabase: {e}")
                else:
                    st.error("El nombre del producto no puede estar vacío.")

    elif sub_inv == "✏️ Editar / Eliminar":
        res_p = supabase.table("productos").select("*").order("nombre").execute()
        df_prods_edit = pd.DataFrame(res_p.data)

        if not df_prods_edit.empty:
            dict_prods = {f"{row['nombre']} (ID: {row['id']})": row for _, row in df_prods_edit.iterrows()}
            prod_edit_str = st.selectbox("Selecciona el producto", list(dict_prods.keys()))
            prod_sel = dict_prods[prod_edit_str]

            img_actual_val = prod_sel.get('imagen_url', '')
            img_actual = str(img_actual_val) if not pd.isna(img_actual_val) and img_actual_val is not None else ""

            if img_actual and img_actual.strip() != "":
                st.caption("📷 Vista previa de la foto actual:")
                st.markdown(f'<div style="width: 100px; height: 100px; border-radius: 12px; overflow: hidden;"><img src="{img_actual}" style="width: 100%; height: 100%; object-fit: cover;"></div>', unsafe_allow_html=True)

            uploaded_img_edit = st.file_uploader("📷 Subir/Cambiar Fotografía del Producto", type=["png", "jpg", "jpeg"], key="up_img_edit")
            n_imagen_url = st.text_input("🔗 O cambiar URL de la Imagen", value=img_actual if not img_actual.startswith("data:image") else "", key="txt_img_edit")

            val_costo = limpiar_float(prod_sel.get('costo_unitario', 0.0))
            val_precio = limpiar_float(prod_sel.get('precio_venta', 0.0))
            val_stock = int(limpiar_float(prod_sel.get('stock', 0)))

            with st.form("form_editar"):
                n_nombre = st.text_input("Nombre", value=str(prod_sel['nombre']))
                c1, c2, c3 = st.columns(3)
                with c1: n_costo = st.number_input("Costo ($)", min_value=0.0, value=val_costo, format="%.2f")
                with c2: n_precio = st.number_input("Precio ($)", min_value=0.0, value=val_precio, format="%.2f")
                with c3: n_stock = st.number_input("Stock", min_value=0, value=val_stock, step=1)

                col_b1, col_b2 = st.columns(2)
                with col_b1: act = st.form_submit_button("💾 Actualizar", type="primary")
                with col_b2: elim = st.form_submit_button("🗑️ Eliminar")

                if act:
                    try:
                        if uploaded_img_edit is not None:
                            final_img_str = archivo_a_base64(uploaded_img_edit)
                        elif n_imagen_url.strip() != "":
                            final_img_str = str(n_imagen_url.strip())
                        else:
                            final_img_str = img_actual

                        supabase.table("productos").update({
                            "nombre": str(n_nombre.strip()),
                            "costo_unitario": float(limpiar_float(n_costo)),
                            "precio_venta": float(limpiar_float(n_precio)),
                            "stock": int(limpiar_float(n_stock)),
                            "imagen_url": str(final_img_str)
                        }).eq("id", int(prod_sel['id'])).execute()
                        st.success("✅ Producto actualizado.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error al actualizar: {e}")

                if elim:
                    try:
                        supabase.table("productos").delete().eq("id", int(prod_sel['id'])).execute()
                        st.warning("🗑️ Producto eliminado.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error al eliminar: {e}")

# ---------------------------------------------------------
# GASTOS Y PROVEEDORES
# ---------------------------------------------------------
elif menu == "💸 Gastos y Proveedores":
    col_header, col_home = st.columns([3, 1])
    with col_header:
        st.markdown('<div class="section-header-yellow">💸 Gastos y Materia Prima</div>', unsafe_allow_html=True)
    with col_home:
        st.button("🏠 Volver al Inicio", key="btn_home_g", on_click=ir_a_seccion, args=("🏠 Inicio / Dashboard",), use_container_width=True)

    g_col1, g_col2 = st.columns(2)
    with g_col1:
        st.button("📋 Registrar / Ver Gastos", key="btn_gasto_list", use_container_width=True, on_click=ir_a_subseccion_gastos, args=("📋 Registrar / Ver Gastos",))
    with g_col2:
        st.button("🏭 Gestión de Proveedores", key="btn_prov_add", use_container_width=True, on_click=ir_a_subseccion_gastos, args=("🏭 Gestión de Proveedores",))

    st.divider()
    sub_gasto = st.session_state['subseccion_gastos']

    if sub_gasto == "📋 Registrar / Ver Gastos":
        st.markdown('<div class="sub-header-yellow">➕ Registrar Nuevo Gasto o Materia Prima</div>', unsafe_allow_html=True)
        
        try:
            res_prov = supabase.table("proveedores").select("*").order("nombre").execute()
            df_provs = pd.DataFrame(res_prov.data)
        except Exception:
            df_provs = pd.DataFrame()

        dict_provs = {"➕ Agregar Nuevo Proveedor": None}
        if not df_provs.empty:
            for _, r in df_provs.iterrows():
                dict_provs[f"{r['nombre']} ({r['telefono']})"] = r

        with st.form("form_nuevo_gasto"):
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                prov_sel_str = st.selectbox("Selecciona Proveedor", list(dict_provs.keys()))
                cat_gasto = st.selectbox("Categoría", ["🥜 Materia Prima (Maní, papas, etc.)", "📦 Empaques y Bolsas", "🧼 Insumos / Limpieza", "🚚 Transporte / Flete", "💡 Servicios / Varios"])
            with col_g2:
                fecha_gasto = st.date_input("Fecha del Gasto", value=date.today())
                monto_gasto = st.number_input("Monto en USD ($)", min_value=0.01, value=10.0, step=1.0, format="%.2f")

            desc_gasto = st.text_input("Descripción del Gasto / Compra", placeholder="Ej. Compra de 50 kg de maní en grano")
            guardar_gasto = st.form_submit_button("💾 Registrar Gasto", type="primary")

            if guardar_gasto:
                if desc_gasto.strip() == "":
                    st.error("Por favor coloca una pequeña descripción del gasto.")
                else:
                    prov_info = dict_provs[prov_sel_str]
                    p_id_final = int(prov_info['id']) if prov_info is not None else 1

                    fecha_g_final = fecha_gasto.strftime("%Y-%m-%d") + datetime.now().strftime(" %H:%M:%S")

                    try:
                        supabase.table("gastos").insert({
                            "proveedor_id": p_id_final,
                            "descripcion": str(desc_gasto.strip()),
                            "categoria": str(cat_gasto),
                            "monto_usd": float(monto_gasto),
                            "fecha": str(fecha_g_final)
                        }).execute()
                        st.success(f"✅ Gasto de ${monto_gasto:,.2f} registrado con éxito.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error al guardar el gasto: {e}")

        st.divider()
        st.markdown('<div class="sub-header-yellow">📋 Historial de Gastos Registrados</div>', unsafe_allow_html=True)
        
        try:
            res_gastos_all = supabase.table("gastos").select("id, descripcion, categoria, monto_usd, fecha, proveedores(nombre)").order("fecha", desc=True).execute()
            df_gastos_all = pd.DataFrame(res_gastos_all.data)
        except Exception:
            df_gastos_all = pd.DataFrame()

        if df_gastos_all.empty:
            st.info("Aún no has registrado gastos de materia prima o insumos.")
        else:
            df_gastos_all['Proveedor'] = df_gastos_all['proveedores'].apply(lambda x: x['nombre'] if isinstance(x, dict) else 'Proveedor General')
            df_gastos_all['Monto USD ($)'] = df_gastos_all['monto_usd'].apply(limpiar_float)
            df_gastos_all['Monto Bs.'] = df_gastos_all['Monto USD ($)'] * tasa_oficial

            total_gastos = df_gastos_all['Monto USD ($)'].sum()
            st.metric("Total Egresos Registrados", f"${total_gastos:,.2f}", f"Bs. {total_gastos * tasa_oficial:,.2f}")

            df_display_g = df_gastos_all[['id', 'descripcion', 'categoria', 'Proveedor', 'Monto USD ($)', 'Monto Bs.', 'fecha']].copy()
            df_display_g.rename(columns={
                'id': 'ID Gasto',
                'descripcion': 'Descripción',
                'categoria': 'Categoría',
                'fecha': 'Fecha / Hora'
            }, inplace=True)

            st.dataframe(df_display_g, use_container_width=True)

            with st.expander("🗑️ Eliminar un Registro de Gasto (En caso de error)"):
                dict_gastos_del = {
                    f"ID #{row['ID Gasto']} - {row['Descripción']} (${row['Monto USD ($)']:.2f})": row['ID Gasto']
                    for _, row in df_display_g.iterrows()
                }
                g_del_sel = st.selectbox("Selecciona el gasto a eliminar", list(dict_gastos_del.keys()))
                if st.button("🗑️ Eliminar Registro de Gasto", type="primary", use_container_width=True):
                    try:
                        id_g_del = dict_gastos_del[g_del_sel]
                        supabase.table("gastos").delete().eq("id", int(id_g_del)).execute()
                        st.warning(f"🗑️ Registro de gasto #{id_g_del} eliminado.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error al eliminar el gasto: {e}")

    elif sub_gasto == "🏭 Gestión de Proveedores":
        st.markdown('<div class="sub-header-yellow">🏭 Directorio de Proveedores</div>', unsafe_allow_html=True)

        try:
            res_p = supabase.table("proveedores").select("*").order("nombre").execute()
            df_provs_dir = pd.DataFrame(res_p.data)
        except Exception:
            df_provs_dir = pd.DataFrame()

        if not df_provs_dir.empty:
            st.dataframe(df_provs_dir[['id', 'nombre', 'contacto', 'telefono', 'notas']], use_container_width=True)

        st.divider()
        st.markdown('<div class="sub-header-yellow">➕ Registrar Nuevo Proveedor</div>', unsafe_allow_html=True)
        with st.form("form_nuevo_proveedor"):
            p_nombre = st.text_input("Nombre de la Empresa / Proveedor")
            c1, c2 = st.columns(2)
            with c1: p_contacto = st.text_input("Persona de Contacto")
            with c2: p_telefono = st.text_input("Teléfono / WhatsApp")
            p_notas = st.text_area("Notas / Productos que vende")

            if st.form_submit_button("💾 Guardar Proveedor"):
                if p_nombre.strip() != "":
                    try:
                        # Se excluye el campo 'id' para permitir que Supabase asigne el autonumérico correctamente
                        supabase.table("proveedores").insert({
                            "nombre": str(p_nombre.strip()),
                            "contacto": str(p_contacto.strip() if p_contacto else 'N/A'),
                            "telefono": str(p_telefono.strip() if p_telefono else 'S/N'),
                            "notas": str(p_notas.strip() if p_notas else '')
                        }).execute()
                        st.success(f"✅ Proveedor '{p_nombre}' guardado exitosamente.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error al guardar proveedor: {e}")
                else:
                    st.error("El nombre del proveedor no puede estar vacío.")

# ---------------------------------------------------------
# ALMANAQUE DE VENTAS
# ---------------------------------------------------------
elif menu == "📅 Almanaque de Ventas":
    col_header, col_home = st.columns([3, 1])
    with col_header:
        st.markdown('<div class="section-header-yellow">📅 Almanaque de Ventas</div>', unsafe_allow_html=True)
    with col_home:
        st.button("🏠 Volver al Inicio", key="btn_home_cal", on_click=ir_a_seccion, args=("🏠 Inicio / Dashboard",), use_container_width=True)

    col_anio, col_mes = st.columns(2)
    with col_anio:
        anio_sel = st.selectbox("Año", list(range(2024, 2031)), index=2)
    with col_mes:
        meses_nombres = {1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"}
        mes_sel_nombre = st.selectbox("Mes", list(meses_nombres.values()), index=datetime.now().month - 1)
        mes_sel = [k for k, v in meses_nombres.items() if v == mes_sel_nombre][0]

    mes_str = f"{anio_sel}-{mes_sel:02d}"
    
    try:
        res_v = supabase.table("ventas").select("id, fecha, cantidad, precio_unitario, ganancia_total, clientes(nombre), productos(nombre)").like("fecha", f"{mes_str}%").execute()
        df_ventas_mes = pd.DataFrame(res_v.data)
    except Exception:
        df_ventas_mes = pd.DataFrame()

    ventas_por_dia = {}
    if not df_ventas_mes.empty:
        df_ventas_mes['cantidad'] = df_ventas_mes['cantidad'].apply(limpiar_float)
        df_ventas_mes['precio_unitario'] = df_ventas_mes['precio_unitario'].apply(limpiar_float)
        df_ventas_mes['ganancia_total'] = df_ventas_mes['ganancia_total'].apply(limpiar_float)
        
        df_ventas_mes['ingreso'] = df_ventas_mes['cantidad'] * df_ventas_mes['precio_unitario']
        df_ventas_mes['dia'] = pd.to_datetime(df_ventas_mes['fecha']).dt.day
        ventas_por_dia = df_ventas_mes.groupby('dia')['ingreso'].sum().to_dict()

    st.markdown('<div class="sub-header-yellow">🗓️ Calendario de Ventas del Mes</div>', unsafe_allow_html=True)

    cal = calendar.monthcalendar(anio_sel, mes_sel)
    
    rows_html = []
    for semana in cal:
        tds = []
        for dia in semana:
            if dia == 0:
                tds.append('<td class="empty-day"></td>')
            else:
                monto_dia = ventas_por_dia.get(dia, 0.0)
                if monto_dia > 0:
                    tds.append(f'<td class="active-day"><span class="day-number">{dia}</span><span class="day-amount">${monto_dia:,.2f}</span></td>')
                else:
                    tds.append(f'<td><span class="day-number" style="color: #666;">{dia}</span></td>')
        rows_html.append(f'<tr>{"".join(tds)}</tr>')

    table_html = f'<div class="calendar-container"><table class="calendar-table"><thead><tr><th>Lun</th><th>Mar</th><th>Mié</th><th>Jue</th><th>Vie</th><th>Sáb</th><th>Dom</th></tr></thead><tbody>{"".join(rows_html)}</tbody></table></div>'

    st.markdown(table_html, unsafe_allow_html=True)

    st.divider()

    st.markdown('<div class="sub-header-yellow">🔍 Consultar Operaciones de un Día Específico</div>', unsafe_allow_html=True)
    
    num_dias_mes = calendar.monthrange(anio_sel, mes_sel)[1]
    opciones_dias = list(range(1, num_dias_mes + 1))
    
    dia_defecto = date.today().day if (date.today().month == mes_sel and date.today().year == anio_sel) else 1
    dia_elegido = st.selectbox("📅 Selecciona el día a consultar:", opciones_dias, index=dia_defecto - 1)

    fecha_consulta_str = f"{anio_sel}-{mes_sel:02d}-{dia_elegido:02d}"

    if not df_ventas_mes.empty:
        df_ventas_dia = df_ventas_mes[df_ventas_mes['fecha'].str.startswith(fecha_consulta_str)].copy()
    else:
        df_ventas_dia = pd.DataFrame()

    if df_ventas_dia.empty:
        st.info(f"ℹ️ No se registraron ventas el **{dia_elegido} de {mes_sel_nombre} de {anio_sel}**.")
    else:
        df_ventas_dia['Cliente'] = df_ventas_dia['clientes'].apply(lambda x: x['nombre'] if isinstance(x, dict) else 'Cliente')
        df_ventas_dia['Producto'] = df_ventas_dia['productos'].apply(lambda x: x['nombre'] if isinstance(x, dict) else 'Producto')
        df_ventas_dia['Monto Total ($)'] = df_ventas_dia['cantidad'] * df_ventas_dia['precio_unitario']

        monto_dia_tot = float(df_ventas_dia['Monto Total ($)'].sum())
        ganancia_dia_tot = float(df_ventas_dia['ganancia_total'].sum())

        c_met1, c_met2 = st.columns(2)
        c_met1.metric(f"Total Vendido ({dia_elegido} {mes_sel_nombre})", f"${monto_dia_tot:,.2f}", f"Bs. {monto_dia_tot * tasa_oficial:,.2f}")
        c_met2.metric("Ganancia Neta del Día", f"${ganancia_dia_tot:,.2f}")

        st.caption(f"📋 Detalle de ventas registradas el **{dia_elegido}/{mes_sel:02d}/{anio_sel}**:")
        
        df_display_dia = df_ventas_dia[['id', 'Cliente', 'Producto', 'cantidad', 'precio_unitario', 'Monto Total ($)', 'ganancia_total', 'fecha']].copy()
        df_display_dia.rename(columns={
            'id': 'ID Venta',
            'cantidad': 'Cantidad',
            'precio_unitario': 'Precio Unit ($)',
            'ganancia_total': 'Ganancia ($)',
            'fecha': 'Hora'
        }, inplace=True)

        st.dataframe(df_display_dia, use_container_width=True)

# ---------------------------------------------------------
# REPORTES Y MÉTRICAS
# ---------------------------------------------------------
elif menu == "📈 Reportes y Métricas":
    col_header, col_home = st.columns([3, 1])
    with col_header:
        st.markdown('<div class="section-header-yellow">📈 Reportes Financieros</div>', unsafe_allow_html=True)
    with col_home:
        st.button("🏠 Volver al Inicio", key="btn_home_r", on_click=ir_a_seccion, args=("🏠 Inicio / Dashboard",), use_container_width=True)

    st.markdown('<div class="sub-header-yellow">📅 Filtrar Reporte por Año y Mes</div>', unsafe_allow_html=True)
    
    col_rep_an, col_rep_me = st.columns(2)
    with col_rep_an:
        anio_rep_sel = st.selectbox("Selecciona el Año", list(range(2024, 2031)), index=2, key="rep_anio")
    with col_rep_me:
        meses_nombres_rep = {1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"}
        mes_rep_nombre_sel = st.selectbox("Selecciona el Mes", list(meses_nombres_rep.values()), index=datetime.now().month - 1, key="rep_mes")
        mes_rep_sel = [k for k, v in meses_nombres_rep.items() if v == mes_rep_nombre_sel][0]

    mes_filtro_str = f"{anio_rep_sel}-{mes_rep_sel:02d}"

    try:
        res_v = supabase.table("ventas").select("id, cantidad, precio_unitario, ganancia_total, estado_pago, fecha, productos(nombre), clientes(nombre)").order("id", desc=True).execute()
        df_ventas = pd.DataFrame(res_v.data)
    except Exception:
        df_ventas = pd.DataFrame()

    try:
        res_g = supabase.table("gastos").select("monto_usd, fecha").order("id", desc=True).execute()
        df_gastos_rep = pd.DataFrame(res_g.data)
    except Exception:
        df_gastos_rep = pd.DataFrame()

    if not df_ventas.empty:
        df_ventas['cantidad'] = df_ventas['cantidad'].apply(limpiar_float)
        df_ventas['precio_unitario'] = df_ventas['precio_unitario'].apply(limpiar_float)
        df_ventas['ganancia_total'] = df_ventas['ganancia_total'].apply(limpiar_float)
        
        df_ventas['Producto'] = df_ventas['productos'].apply(lambda x: x['nombre'] if isinstance(x, dict) else '')
        df_ventas['Cliente'] = df_ventas['clientes'].apply(lambda x: x['nombre'] if isinstance(x, dict) else '')
        df_ventas['Ingreso Total ($)'] = df_ventas['cantidad'] * df_ventas['precio_unitario']
        
        df_ventas_filtrado = df_ventas[df_ventas['fecha'].str.startswith(mes_filtro_str)].copy()
        df_gastos_filtrado = df_gastos_rep[df_gastos_rep['fecha'].str.startswith(mes_filtro_str)].copy() if not df_gastos_rep.empty else pd.DataFrame()

        total_ingresos = float(df_ventas_filtrado['Ingreso Total ($)'].sum()) if not df_ventas_filtrado.empty else 0.0
        total_ganancias_ventas = float(df_ventas_filtrado['ganancia_total'].sum()) if not df_ventas_filtrado.empty else 0.0
        total_gastos_mes = float(df_gastos_filtrado['monto_usd'].apply(limpiar_float).sum()) if not df_gastos_filtrado.empty else 0.0

        balance_neto_mes = total_ganancias_ventas - total_gastos_mes

        col1, col2, col3 = st.columns(3)
        col1.metric("Ingresos Ventas ($)", f"${total_ingresos:,.2f}", f"Bs. {total_ingresos * tasa_oficial:,.2f}")
        col2.metric("Egresos / Gastos ($)", f"${total_gastos_mes:,.2f}", f"Bs. {total_gastos_mes * tasa_oficial:,.2f}")
        col3.metric("Ganancia Neta Real ($)", f"${balance_neto_mes:,.2f}", f"Bs. {balance_neto_mes * tasa_oficial:,.2f}")
        
        st.divider()
        
        if not df_ventas_filtrado.empty:
            df_display_rep = df_ventas_filtrado[['id', 'Producto', 'Cliente', 'cantidad', 'precio_unitario', 'Ingreso Total ($)', 'ganancia_total', 'estado_pago', 'fecha']].copy()
            df_display_rep.rename(columns={
                'id': 'ID Venta',
                'cantidad': 'Cantidad',
                'precio_unitario': 'Precio Unit ($)',
                'ganancia_total': 'Ganancia ($)',
                'estado_pago': 'Estado',
                'fecha': 'Fecha / Hora'
            }, inplace=True)

            st.dataframe(df_display_rep, use_container_width=True)
    else:
        st.info("Aún no hay ventas registradas.")
