import os
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
    .day-box {
        background-color: #FFFFFF; border: 1px solid #E0E0E0; border-radius: 10px; padding: 10px; text-align: center; min-height: 95px; margin-bottom: 10px;
    }
    .day-box-active {
        background-color: #FFFDE7; border: 2px solid #FBC02D; border-radius: 10px; padding: 10px; text-align: center; min-height: 95px; margin-bottom: 10px;
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
    "👥 Clientes y Cuentas por Cobrar", 
    "📦 Productos e Inventario", 
    "📅 Calendario Anual de Ventas",
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

    st.button("📅  Calendario Anual de Ventas", key="btn_cal_home", use_container_width=True, on_click=ir_a_seccion, args=("📅 Calendario Anual de Ventas",))

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
        res_v = supabase.table("ventas").select("id, cliente_id, saldo_pendiente, clientes(id, nombre, telefono)").eq("estado_pago", "Pendiente").gt("saldo_pendiente", 0).execute()
        df_deudas = pd.DataFrame(res_v.data)

        if df_deudas.empty:
            st.success("🎉 ¡No hay cuentas por cobrar pendientes!")
        else:
            df_deudas['Cliente'] = df_deudas['clientes'].apply(lambda x: x['nombre'] if isinstance(x, dict) else 'Cliente')
            df_deudas['Teléfono'] = df_deudas['clientes'].apply(lambda x: x['telefono'] if isinstance(x, dict) else 'S/N')
            
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
        res_p = supabase.table("productos").select("id, nombre, costo_unitario, precio_venta, stock").order("nombre").execute()
        df_prods = pd.DataFrame(res_p.data)
        if not df_prods.empty:
            df_prods['Precio (Bs.)'] = df_prods['precio_venta'] * tasa_oficial
            st.dataframe(df_prods, use_container_width=True)
        else:
            st.info("No hay productos registrados.")

    elif sub_inv == "➕ Agregar Nuevo Producto":
        st.markdown('<div class="sub-header-yellow">➕ Agregar Nuevo Producto</div>', unsafe_allow_html=True)
        with st.form("form_producto"):
            nombre = st.text_input("Nombre del Producto")
            col1, col2, col3 = st.columns(3)
            with col1: costo = st.number_input("Costo Unitario ($)", min_value=0.0, format="%.2f")
            with col2: precio = st.number_input("Precio de Venta ($)", min_value=0.0, format="%.2f")
            with col3: stock = st.number_input("Stock Inicial", min_value=0, step=1)

            if st.form_submit_button("Guardar Producto"):
                if nombre.strip() != "":
                    try:
                        nuevo_producto = {
                            "nombre": str(nombre.strip()),
                            "costo_unitario": float(costo),
                            "precio_venta": float(precio),
                            "stock": int(stock)
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
                        supabase.table("productos").update({
                            "nombre": str(n_nombre.strip()),
                            "costo_unitario": float(n_costo),
                            "precio_venta": float(n_precio),
                            "stock": int(n_stock)
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
# CALENDARIO ANUAL DE VENTAS
# ---------------------------------------------------------
elif menu == "📅 Calendario Anual de Ventas":
    col_header, col_home = st.columns([3, 1])
    with col_header:
        st.markdown('<div class="section-header-yellow">📅 Calendario Anual de Ventas</div>', unsafe_allow_html=True)
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
    res_v = supabase.table("ventas").select("fecha, cantidad, precio_unitario").like("fecha", f"{mes_str}%").execute()
    df_ventas_mes = pd.DataFrame(res_v.data)

    ventas_por_dia = {}
    if not df_ventas_mes.empty:
        df_ventas_mes['ingreso'] = df_ventas_mes['cantidad'] * df_ventas_mes['precio_unitario']
        df_ventas_mes['dia'] = pd.to_datetime(df_ventas_mes['fecha']).dt.day
        ventas_por_dia = df_ventas_mes.groupby('dia')['ingreso'].sum().to_dict()

    cal = calendar.monthcalendar(anio_sel, mes_sel)
    cols_dias = st.columns(7)
    for i, d_nombre in enumerate(["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]):
        cols_dias[i].markdown(f"<div style='text-align: center; font-weight: bold;'>{d_nombre}</div>", unsafe_allow_html=True)

    for semana in cal:
        cols_semana = st.columns(7)
        for i, dia in enumerate(semana):
            with cols_semana[i]:
                if dia == 0:
                    st.markdown("<div style='color: #CCC; text-align: center;'>-</div>", unsafe_allow_html=True)
                else:
                    monto_dia = ventas_por_dia.get(dia, 0.0)
                    if monto_dia > 0:
                        st.markdown(f'<div class="day-box-active"><b>{dia}</b><br><span style="color: #00A86B;">${monto_dia:,.2f}</span></div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="day-box"><b>{dia}</b><br><span style="color: #999;">$0.00</span></div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# REPORTES Y MÉTRICAS
# ---------------------------------------------------------
elif menu == "📈 Reportes y Métricas":
    col_header, col_home = st.columns([3, 1])
    with col_header:
        st.markdown('<div class="section-header-yellow">📈 Reportes Financieros</div>', unsafe_allow_html=True)
    with col_home:
        st.button("🏠 Volver al Inicio", key="btn_home_r", on_click=ir_a_seccion, args=("🏠 Inicio / Dashboard",), use_container_width=True)

    res_v = supabase.table("ventas").select("id, cantidad, precio_unitario, ganancia_total, estado_pago, fecha, productos(nombre), clientes(nombre)").order("id", desc=True).execute()
    df_ventas = pd.DataFrame(res_v.data)

    if not df_ventas.empty:
        df_ventas['Producto'] = df_ventas['productos'].apply(lambda x: x['nombre'] if isinstance(x, dict) else '')
        df_ventas['Cliente'] = df_ventas['clientes'].apply(lambda x: x['nombre'] if isinstance(x, dict) else '')
        df_ventas['Ingreso Total ($)'] = df_ventas['cantidad'] * df_ventas['precio_unitario']
        
        total_ingresos = float(df_ventas['Ingreso Total ($)'].sum())
        total_ganancias = float(df_ventas['ganancia_total'].sum())
        
        col1, col2 = st.columns(2)
        col1.metric("Ingresos Totales", f"${total_ingresos:,.2f}", f"Bs. {total_ingresos * tasa_oficial:,.2f}")
        col2.metric("Ganancia Neta Total", f"${total_ganancias:,.2f}", f"Bs. {total_ganancias * tasa_oficial:,.2f}")
        st.divider()
        st.dataframe(df_ventas[['id', 'Producto', 'Cliente', 'cantidad', 'precio_unitario', 'Ingreso Total ($)', 'ganancia_total', 'estado_pago', 'fecha']], use_container_width=True)
    else:
        st.info("Aún no hay ventas registradas.")
