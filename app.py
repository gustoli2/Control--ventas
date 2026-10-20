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
    # Asegurar cliente mostrador id = 1
    try:
        res = supabase.table("clientes").select("id").eq("id", 1).execute()
        if not res.data:
            supabase.table("clientes").insert({"id": 1, "nombre": "Cliente Mostrador / General", "telefono": "S/N"}).execute()
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

def archivo_a_base64(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        base64_str = base64.b64encode(bytes_data).decode('utf-8')
        mime_type = uploaded_file.type
        return f"data:{mime_type};base64,{base64_str}"
    return ""

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
    
    res_v_hoy = supabase.table("ventas").select("cantidad, precio_unitario, costo_unitario, ganancia_total").like("fecha", f"{fecha_hoy_str}%").execute()
    df_ventas_hoy = pd.DataFrame(res_v_hoy.data)
    
    if not df_ventas_hoy.empty:
        df_ventas_hoy['ingreso'] = df_ventas_hoy['cantidad'] * df_ventas_hoy['precio_unitario']
        df_ventas_hoy['costo'] = df_ventas_hoy['cantidad'] * df_ventas_hoy['costo_unitario']
        ventas_hoy = float(df_ventas_hoy['ingreso'].sum())
        costos_hoy = float(df_ventas_hoy['costo'].sum())
    else:
        ventas_hoy = 0.0
        costos_hoy = 0.0
        
    balance_hoy = ventas_hoy - costos_hoy

    st.markdown(f"""
        <div class="business-card">
            <div class="card-title">Tu negocio hoy</div>
            <div class="card-amount">${ventas_hoy:,.2f}</div>
            <div style="font-size: 15px; color: #555; margin-bottom: 15px;">Bs. {ventas_hoy * tasa_oficial:,.2f}</div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 15px;">
                <div>
                    <span style="font-size: 14px; color: #666;">Balance</span><br>
                    <span class="amount-green">${balance_hoy:,.2f}</span><br>
                    <span style="font-size: 13px; color: #666;">Bs. {balance_hoy * tasa_oficial:,.2f}</span>
                </div>
                <div style="text-align: right;">
                    <span style="font-size: 14px; color: #666;">Costos hoy</span><br>
                    <span class="amount-red">${costos_hoy:,.2f}</span><br>
                    <span style="font-size: 13px; color: #666;">Bs. {costos_hoy * tasa_oficial:,.2f}</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.button("🛒  Nueva Venta", key="btn_nv", use_container_width=True, on_click=ir_a_seccion, args=("🛒 Registrar Venta",))

    c1, c2 = st.columns(2)
    with c1:
        st.button("📦  Inventario", key="btn_inv", use_container_width=True, on_click=ir_a_seccion, args=("📦 Productos e Inventario",))
    with c2:
        st.button("👥  Gestión de Clientes", key="btn_deu", use_container_width=True, on_click=ir_a_seccion, args=("👥 Clientes y Cuentas por Cobrar",))

    st.button("💰  Transacciones Pagadas", key="btn_trans_pag", use_container_width=True, on_click=ir_a_seccion, args=("💰 Transacciones Pagadas",))
    st.button("📅  Almanaque de Ventas", key="btn_cal_home", use_container_width=True, on_click=ir_a_seccion, args=("📅 Almanaque de Ventas",))

    st.divider()

    # Estadísticas Mes
    mes_actual_str = date.today().strftime("%Y-%m")
    res_mes = supabase.table("ventas").select("ganancia_total, cantidad, productos(nombre)").like("fecha", f"{mes_actual_str}%").execute()
    df_ventas_mes = pd.DataFrame(res_mes.data)
    
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
        st.caption("Ganancias del mes")
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
            opciones_productos = {f"{row['nombre']} (Stock: {row['stock']})": row for _, row in df_prods_disponibles.iterrows()}
            prod_seleccionado_str = st.selectbox("Selecciona un Producto", list(opciones_productos.keys()), key="sb_prod_rv")
            prod_data = opciones_productos[prod_seleccionado_str]

            cantidad_ya_en_carrito = sum(item['cantidad'] for item in st.session_state['carrito_ventas'] if item['producto_id'] == prod_data['id'])
            stock_restringido = int(prod_data['stock']) - cantidad_ya_en_carrito

            col_p1, col_p2, col_p3 = st.columns([2, 1, 1])
            with col_p1:
                st.info(f"**Precio:** ${prod_data['precio_venta']:.2f} (~ Bs. {prod_data['precio_venta']*tasa_oficial:,.2f}) | **Costo:** ${prod_data['costo_unitario']:.2f}")
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
                            'producto_id': prod_data['id'],
                            'nombre': prod_data['nombre'],
                            'cantidad': int(cant_a_agregar),
                            'precio_unitario': float(prod_data['precio_venta']),
                            'costo_unitario': float(prod_data['costo_unitario']),
                            'subtotal': float(prod_data['precio_venta']) * int(cant_a_agregar),
                            'ganancia': (float(prod_data['precio_venta']) - float(prod_data['costo_unitario'])) * int(cant_a_agregar)
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
                                
                                # Actualizar Stock
                                stock_actual = int(df_prods[df_prods['id'] == item['producto_id']]['stock'].values[0])
                                nuevo_stock = stock_actual - int(item['cantidad'])
                                supabase.table("productos").update({"stock": int(nuevo_stock)}).eq("id", int(item['producto_id'])).execute()

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
                            stock_act = int(res_p_curr.data[0]['stock'])
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
            deuda_maxima = float(cliente_info['Saldo Pendiente ($)'])
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
                    s_pend = float(v_item['saldo_pendiente'])
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
                            stock_actual = int(res_p_curr.data[0]['stock'])
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

            with st.expander("🔍 Ver detalle desplegable agrupado por cada cliente"):
                for _, row_cli in df_deudas_resumen.iterrows():
                    c_id = int(row_cli['cliente_id'])
                    c_nom = row_cli['Cliente']
                    c_tel = row_cli['Teléfono']
                    c_monto = row_cli['Saldo Pendiente ($)']
                    c_monto_bs = c_monto * tasa_oficial
                    
                    st.write(f"### 👤 {c_nom} (Pendiente: ${c_monto:,.2f} / Bs. {c_monto_bs:,.2f}) - Tel: {c_tel}")
                    
                    df_sub = df_deudas[df_deudas['cliente_id'] == c_id][['Producto', 'cantidad', 'precio_unitario', 'saldo_pendiente', 'fecha']].copy()
                    df_sub['Saldo Pendiente (Bs.)'] = df_sub['saldo_pendiente'] * tasa_oficial
                    df_sub.rename(columns={
                        'cantidad': 'Cantidad',
                        'precio_unitario': 'Precio Unit. ($)',
                        'saldo_pendiente': 'Saldo Pendiente ($)',
                        'fecha': 'Fecha de Compra'
                    }, inplace=True)
                    
                    st.dataframe(df_sub, use_container_width=True)

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
                    p_stock = int(p_row['stock'])
                    p_precio = float(p_row['precio_venta'])
                    p_precio_bs = p_precio * tasa_oficial
                    p_img_url = p_row.get('imagen_url', '')

                    if p_stock == 0:
                        badge_html = '<span class="badge-no-stock">No disponible</span>'
                    elif p_stock <= 3:
                        badge_html = f'<span class="badge-low-stock">⚠️ Pocas unidades: {p_stock} uds</span>'
                    else:
                        badge_html = f'<span class="badge-in-stock">Disponible: {p_stock} uds</span>'

                    if p_img_url and str(p_img_url).strip() != "":
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
            with col1: costo = st.number_input("Costo Unitario ($)", min_value=0.0, format="%.2f")
            with col2: precio = st.number_input("Precio de Venta ($)", min_value=0.0, format="%.2f")
            with col3: stock = st.number_input("Stock Inicial", min_value=0, step=1)

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
                            "costo_unitario": float(costo),
                            "precio_venta": float(precio),
                            "stock": int(stock),
                            "imagen_url": final_img_str
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

            img_actual = prod_sel.get('imagen_url', '')
            if img_actual and str(img_actual).strip() != "":
                st.caption("📷 Vista previa de la foto actual:")
                st.markdown(f'<div style="width: 100px; height: 100px; border-radius: 12px; overflow: hidden;"><img src="{img_actual}" style="width: 100%; height: 100%; object-fit: cover;"></div>', unsafe_allow_html=True)

            uploaded_img_edit = st.file_uploader("📷 Subir/Cambiar Fotografía del Producto", type=["png", "jpg", "jpeg"], key="up_img_edit")
            n_imagen_url = st.text_input("🔗 O cambiar URL de la Imagen", value=img_actual if not str(img_actual).startswith("data:image") else "", key="txt_img_edit")

            with st.form("form_editar"):
                n_nombre = st.text_input("Nombre", value=prod_sel['nombre'])
                c1, c2, c3 = st.columns(3)
                with c1: n_costo = st.number_input("Costo ($)", min_value=0.0, value=float(prod_sel['costo_unitario']), format="%.2f")
                with c2: n_precio = st.number_input("Precio ($)", min_value=0.0, value=float(prod_sel['precio_venta']), format="%.2f")
                with c3: n_stock = st.number_input("Stock", min_value=0, value=int(prod_sel['stock']), step=1)

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
                            "costo_unitario": float(n_costo),
                            "precio_venta": float(n_precio),
                            "stock": int(n_stock),
                            "imagen_url": final_img_str
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
# ALMANAQUE DE VENTAS (NATIVO STREAMLIT)
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
    
    res_v = supabase.table("ventas").select("id, fecha, cantidad, precio_unitario, ganancia_total, clientes(nombre), productos(nombre)").like("fecha", f"{mes_str}%").execute()
    df_ventas_mes = pd.DataFrame(res_v.data)

    ventas_por_dia = {}
    if not df_ventas_mes.empty:
        df_ventas_mes['ingreso'] = df_ventas_mes['cantidad'] * df_ventas_mes['precio_unitario']
        df_ventas_mes['dia'] = pd.to_datetime(df_ventas_mes['fecha']).dt.day
        ventas_por_dia = df_ventas_mes.groupby('dia')['ingreso'].sum().to_dict()

    st.markdown('<div class="sub-header-yellow">🗓️ Calendario de Ventas del Mes</div>', unsafe_allow_html=True)

    # Cabecera Días de la Semana
    dias_nom = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    cols_hdr = st.columns(7)
    for idx, d_n in enumerate(dias_nom):
        cols_hdr[idx].markdown(f"**{d_n}**")

    # Renderizado Nativo de la Matriz del Almanaque
    cal = calendar.monthcalendar(anio_sel, mes_sel)
    for semana in cal:
        cols_sem = st.columns(7)
        for idx_d, dia in enumerate(semana):
            with cols_sem[idx_d]:
                if dia == 0:
                    st.write("")
                else:
                    monto_dia = ventas_por_dia.get(dia, 0.0)
                    if monto_dia > 0:
                        st.markdown(f"**{dia}**")
                        st.caption(f"🟢 ${monto_dia:,.2f}")
                    else:
                        st.markdown(f"**{dia}**")
                        st.caption("$0")

    st.divider()

    # DESPLIEGUE Y CONSULTA DE OPERACIONES DE UN DÍA
    st.markdown('<div class="sub-header-yellow">🔍 Consultar Operaciones de un Día Especifico</div>', unsafe_allow_html=True)
    
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

    res_v = supabase.table("ventas").select("id, cantidad, precio_unitario, ganancia_total, estado_pago, fecha, productos(nombre), clientes(nombre)").order("id", desc=True).execute()
    df_ventas = pd.DataFrame(res_v.data)

    if not df_ventas.empty:
        df_ventas['Producto'] = df_ventas['productos'].apply(lambda x: x['nombre'] if isinstance(x, dict) else '')
        df_ventas['Cliente'] = df_ventas['clientes'].apply(lambda x: x['nombre'] if isinstance(x, dict) else '')
        df_ventas['Ingreso Total ($)'] = df_ventas['cantidad'] * df_ventas['precio_unitario']
        
        df_ventas_filtrado = df_ventas[df_ventas['fecha'].str.startswith(mes_filtro_str)].copy()

        if df_ventas_filtrado.empty:
            st.warning(f"⚠️ No hay registros de transacciones para {mes_rep_nombre_sel} {anio_rep_sel}.")
        else:
            total_ingresos = float(df_ventas_filtrado['Ingreso Total ($)'].sum())
            total_ganancias = float(df_ventas_filtrado['ganancia_total'].sum())
            
            col1, col2 = st.columns(2)
            col1.metric(f"Ingresos Totales ({mes_rep_nombre_sel} {anio_rep_sel})", f"${total_ingresos:,.2f}", f"Bs. {total_ingresos * tasa_oficial:,.2f}")
            col2.metric(f"Ganancia Neta Total ({mes_rep_nombre_sel} {anio_rep_sel})", f"${total_ganancias:,.2f}", f"Bs. {total_ganancias * tasa_oficial:,.2f}")
            st.divider()
            
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
