import sqlite3
import streamlit as st
import pandas as pd
import requests
import urllib.parse
from datetime import datetime, date
import calendar

# Configuración de la página
st.set_page_config(
    page_title="OLINUTS - Control de Ventas",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inicializar claves de estado de navegación y carrito si no existen
if 'menu_radio' not in st.session_state:
    st.session_state['menu_radio'] = "🏠 Inicio / Dashboard"

if 'subseccion_clientes' not in st.session_state:
    st.session_state['subseccion_clientes'] = "📋 Listado General"

if 'subseccion_inventario' not in st.session_state:
    st.session_state['subseccion_inventario'] = "📋 Listado de Productos"

if 'carrito_ventas' not in st.session_state:
    st.session_state['carrito_ventas'] = []

# --- FUNCIÓN PARA OBTENER LA TASA BCV EN TIEMPO REAL ---
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

# --- ESTILOS CSS PERSONALIZADOS ---
st.markdown("""
<style>
    .stApp {
        background-color: #F5F2EB;
    }
    .header-container {
        background-color: #FFDE59;
        padding: 20px 20px 10px 20px;
        border-bottom-left-radius: 20px;
        border-bottom-right-radius: 20px;
        margin-top: -60px;
        margin-bottom: 20px;
    }
    .section-header-yellow {
        background-color: #FFDE59;
        padding: 12px 15px;
        border-radius: 12px;
        color: #111111;
        font-size: 20px;
        font-weight: bold;
        text-align: center;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-bottom: 10px;
        box-shadow: 0px 2px 6px rgba(0, 0, 0, 0.05);
    }
    .sub-header-yellow {
        background-color: #FFEE99;
        border: 1px solid #FBC02D;
        padding: 10px 14px;
        border-radius: 10px;
        color: #222222;
        font-size: 16px;
        font-weight: bold;
        margin-top: 15px;
        margin-bottom: 15px;
        box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.04);
    }
    .tasa-card {
        background-color: #FFF9C4;
        border: 1px solid #FBC02D;
        border-radius: 12px;
        padding: 10px 15px;
        margin-bottom: 15px;
        text-align: center;
        font-weight: bold;
        color: #333333;
    }
    .header-title {
        font-size: 24px;
        font-weight: bold;
        color: #111111;
        margin: 0;
    }
    .header-subtitle {
        font-size: 14px;
        color: #555555;
        margin-bottom: 10px;
    }
    .business-card {
        background-color: #FFFFFF;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }
    .card-title {
        font-size: 18px;
        font-weight: 600;
        color: #333333;
    }
    .card-amount {
        font-size: 32px;
        font-weight: bold;
        color: #111111;
    }
    .amount-green {
        color: #00A86B;
        font-weight: bold;
        font-size: 20px;
    }
    .amount-red {
        color: #E53935;
        font-weight: bold;
        font-size: 20px;
    }
    .quick-access-title {
        font-size: 16px;
        font-weight: bold;
        color: #222222;
        margin-top: 15px;
        margin-bottom: 10px;
    }
    .stat-card {
        background-color: #FFFFFF;
        border-radius: 14px;
        padding: 15px;
        border: 1px solid #EEEEEE;
        box-shadow: 0px 2px 8px rgba(0, 0, 0, 0.03);
    }
    .day-box {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 10px;
        padding: 10px;
        text-align: center;
        min-height: 90px;
        margin-bottom: 10px;
        box-shadow: 0px 1px 3px rgba(0, 0, 0, 0.02);
    }
    .day-box-active {
        background-color: #FFFDE7;
        border: 2px solid #FBC02D;
        border-radius: 10px;
        padding: 10px;
        text-align: center;
        min-height: 90px;
        margin-bottom: 10px;
        box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.05);
    }
</style>
""", unsafe_allow_html=True)

# --- FUNCIONES DE BASE DE DATOS ---
def conectar_db():
    return sqlite3.connect("control_ventas.db")

def inicializar_db():
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            costo_unitario REAL NOT NULL,
            precio_venta REAL NOT NULL,
            stock INTEGER DEFAULT 0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            telefono TEXT
        )
    ''')
    
    cursor.execute("SELECT COUNT(*) FROM clientes WHERE id = 1")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO clientes (id, nombre, telefono) VALUES (1, 'Cliente Mostrador / General', 'S/N')")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto_id INTEGER,
            cliente_id INTEGER DEFAULT 1,
            cantidad INTEGER NOT NULL,
            precio_unitario REAL NOT NULL,
            costo_unitario REAL NOT NULL,
            ganancia_total REAL NOT NULL,
            estado_pago TEXT DEFAULT 'Pagado',
            saldo_pendiente REAL DEFAULT 0.0,
            fecha TEXT NOT NULL,
            FOREIGN KEY (producto_id) REFERENCES productos(id),
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        )
    ''')
    
    cursor.execute("PRAGMA table_info(ventas)")
    columnas = [col[1] for col in cursor.fetchall()]
    if 'cliente_id' not in columnas:
        cursor.execute("ALTER TABLE ventas ADD COLUMN cliente_id INTEGER DEFAULT 1")
    if 'estado_pago' not in columnas:
        cursor.execute("ALTER TABLE ventas ADD COLUMN estado_pago TEXT DEFAULT 'Pagado'")
    if 'saldo_pendiente' not in columnas:
        cursor.execute("ALTER TABLE ventas ADD COLUMN saldo_pendiente REAL DEFAULT 0.0")
        cursor.execute("UPDATE ventas SET saldo_pendiente = (cantidad * precio_unitario) WHERE estado_pago = 'Pendiente'")

    conn.commit()
    conn.close()

inicializar_db()

# Cargar Tasa BCV
tasa_bcv_auto = obtener_tasa_bcv()

# --- NAVEGACIÓN EN EL MENÚ LATERAL ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=60)
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

menu = st.sidebar.radio(
    "Ir a:", 
    opciones_menu, 
    key='menu_radio'
)

# ---------------------------------------------------------
# OPCIÓN: INICIO / DASHBOARD
# ---------------------------------------------------------
if menu == "🏠 Inicio / Dashboard":
    st.markdown("""
        <div class="header-container">
            <div class="header-title">👑 OLINUTS</div>
            <div class="header-subtitle">Gustavo Oliveira / Propietario</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f'''
        <div class="tasa-card">
            💵 Tasa Oficial BCV: <b>{tasa_oficial:,.2f} Bs/$</b>
        </div>
    ''', unsafe_allow_html=True)
    
    fecha_hoy_str = date.today().strftime("%Y-%m-%d")
    
    conn = conectar_db()
    df_ventas_hoy = pd.read_sql_query(f'''
        SELECT (cantidad * precio_unitario) AS ingreso, 
               (cantidad * costo_unitario) AS costo,
               ganancia_total
        FROM ventas 
        WHERE fecha LIKE '{fecha_hoy_str}%'
    ''', conn)
    
    mes_actual_str = date.today().strftime("%Y-%m")
    df_ventas_mes = pd.read_sql_query(f'''
        SELECT v.ganancia_total, p.nombre AS producto, v.cantidad
        FROM ventas v
        JOIN productos p ON v.producto_id = p.id
        WHERE v.fecha LIKE '{mes_actual_str}%'
    ''', conn)
    conn.close()
    
    ventas_hoy = df_ventas_hoy['ingreso'].sum() if not df_ventas_hoy.empty else 0.0
    costos_hoy = df_ventas_hoy['costo'].sum() if not df_ventas_hoy.empty else 0.0
    balance_hoy = ventas_hoy - costos_hoy

    ventas_hoy_bs = ventas_hoy * tasa_oficial
    balance_hoy_bs = balance_hoy * tasa_oficial
    costos_hoy_bs = costos_hoy * tasa_oficial

    st.markdown(f"""
        <div class="business-card">
            <div class="card-title">Tu negocio hoy</div>
            <div class="card-amount">${ventas_hoy:,.2f}</div>
            <div style="font-size: 13px; color: #555; margin-bottom: 15px;">Bs. {ventas_hoy_bs:,.2f}</div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 15px;">
                <div>
                    <span style="font-size: 12px; color: #666;">Balance</span><br>
                    <span class="amount-green">${balance_hoy:,.2f}</span><br>
                    <span style="font-size: 11px; color: #666;">Bs. {balance_hoy_bs:,.2f}</span>
                </div>
                <div style="text-align: right;">
                    <span style="font-size: 12px; color: #666;">Costos hoy</span><br>
                    <span class="amount-red">${costos_hoy:,.2f}</span><br>
                    <span style="font-size: 11px; color: #666;">Bs. {costos_hoy_bs:,.2f}</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="quick-access-title">Descubre todo lo que puedes hacer</div>', unsafe_allow_html=True)
    
    st.button("🛒  Nueva Venta", key="btn_nv", use_container_width=True, on_click=ir_a_seccion, args=("🛒 Registrar Venta",))

    c1, c2 = st.columns(2)
    with c1:
        st.button("📦  Inventario", key="btn_inv", use_container_width=True, on_click=ir_a_seccion, args=("📦 Productos e Inventario",))
    with c2:
        st.button("👥  Gestión de Clientes", key="btn_deu", use_container_width=True, on_click=ir_a_seccion, args=("👥 Clientes y Cuentas por Cobrar",))

    st.button("📅  Calendario Anual de Ventas", key="btn_cal_home", use_container_width=True, on_click=ir_a_seccion, args=("📅 Calendario Anual de Ventas",))

    st.divider()

    st.markdown('<div class="quick-access-title">📊 Estadísticas del Mes</div>', unsafe_allow_html=True)
    
    col_stat1, col_stat2 = st.columns(2)
    
    with col_stat1:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.caption("Producto estrella del mes")
        if not df_ventas_mes.empty:
            prod_estrella = df_ventas_mes.groupby('producto')['cantidad'].sum().idxmax()
            cant_estrella = df_ventas_mes.groupby('producto')['cantidad'].sum().max()
            st.subheader(f"⭐ {prod_estrella}")
            st.write(f"Vendidos: **{cant_estrella} uds.**")
        else:
            st.write("Sin ventas este mes")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_stat2:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.caption("Ganancias del mes")
        ganancias_mes = df_ventas_mes['ganancia_total'].sum() if not df_ventas_mes.empty else 0.0
        ganancias_mes_bs = ganancias_mes * tasa_oficial
        st.subheader(f"💵 ${ganancias_mes:,.2f}")
        st.caption(f"Bs. {ganancias_mes_bs:,.2f}")
        st.success("📈 Registro activo")
        st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# OPCIÓN 1: REGISTRAR VENTA (CON CARRITO MULTIPRODUCTO)
# ---------------------------------------------------------
elif menu == "🛒 Registrar Venta":
    col_header, col_home = st.columns([3, 1])
    with col_header:
        st.markdown('<div class="section-header-yellow">🛒 Registrar Venta</div>', unsafe_allow_html=True)
    with col_home:
        st.button("🏠 Volver al Inicio", key="btn_home_v", on_click=ir_a_seccion, args=("🏠 Inicio / Dashboard",), use_container_width=True)
    
    conn = conectar_db()
    df_prods = pd.read_sql_query("SELECT id, nombre, costo_unitario, precio_venta, stock FROM productos", conn)
    df_clientes = pd.read_sql_query("SELECT id, nombre, telefono FROM clientes", conn)
    conn.close()

    if df_prods.empty:
        st.warning("⚠️ Primero debes agregar productos en la sección 'Productos e Inventario'.")
    else:
        # --- SECCIÓN 1: DATOS GENERALES (FECHA Y CLIENTE) ---
        col_f, col_c = st.columns(2)
        with col_f:
            st.markdown('<div class="sub-header-yellow">📅 Fecha de la Venta</div>', unsafe_allow_html=True)
            fecha_venta_elegida = st.date_input("Selecciona la fecha de la venta", value=date.today())

        with col_c:
            st.markdown('<div class="sub-header-yellow">👤 Cliente</div>', unsafe_allow_html=True)
            opciones_clientes = {"➕ ¡Agregar Nuevo Cliente!": None}
            for _, row in df_clientes.iterrows():
                opciones_clientes[f"{row['nombre']} ({row['telefono']})"] = row
                
            cliente_seleccionado_str = st.selectbox("Selecciona un Cliente", list(opciones_clientes.keys()))
            
            if cliente_seleccionado_str == "➕ ¡Agregar Nuevo Cliente!":
                with st.expander("👤 Registrar Nuevo Cliente Rápido", expanded=True):
                    nuevo_nombre = st.text_input("Nombre Completo del Cliente", key="nv_cli_nom")
                    nuevo_tel = st.text_input("Teléfono / WhatsApp", key="nv_cli_tel")
                    if st.button("💾 Guardar Cliente", use_container_width=True, type="primary"):
                        if nuevo_nombre.strip() != "":
                            conn = conectar_db()
                            cursor = conn.cursor()
                            cursor.execute("INSERT INTO clientes (nombre, telefono) VALUES (?, ?)", (nuevo_nombre, nuevo_tel if nuevo_tel.strip() else 'Sin teléfono'))
                            conn.commit()
                            conn.close()
                            st.success(f"✅ Cliente '{nuevo_nombre}' guardado. Por favor selecciónalo en la lista.")
                            st.rerun()
                        else:
                            st.error("El nombre del cliente no puede estar vacío.")
                cliente_data = None
            else:
                cliente_data = opciones_clientes[cliente_seleccionado_str]

        st.divider()

        # --- SECCIÓN 2: SELECCIÓN Y AGREGADO DE PRODUCTOS AL CARRITO ---
        st.markdown('<div class="sub-header-yellow">📦 Agregar Productos al Pedido</div>', unsafe_allow_html=True)
        
        # Filtrar productos con stock > 0
        df_prods_disponibles = df_prods[df_prods['stock'] > 0]
        
        if df_prods_disponibles.empty:
            st.error("❌ No hay productos con stock disponible para vender.")
        else:
            opciones_productos = {f"{row['nombre']} (Stock: {row['stock']})": row for _, row in df_prods_disponibles.iterrows()}
            prod_seleccionado_str = st.selectbox("Selecciona un Producto", list(opciones_productos.keys()))
            prod_data = opciones_productos[prod_seleccionado_str]

            # Calcular el stock disponible ajustado restando lo que ya está en el carrito
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
                            'cantidad': cant_a_agregar,
                            'precio_unitario': prod_data['precio_venta'],
                            'costo_unitario': prod_data['costo_unitario'],
                            'subtotal': prod_data['precio_venta'] * cant_a_agregar,
                            'ganancia': (prod_data['precio_venta'] - prod_data['costo_unitario']) * cant_a_agregar
                        })
                        st.rerun()

        # --- SECCIÓN 3: VER Y GESTIONAR CARRITO ---
        st.markdown('<div class="sub-header-yellow">🛒 Resumen del Carrito de Ventas</div>', unsafe_allow_html=True)
        
        if len(st.session_state['carrito_ventas']) == 0:
            st.info("🛒 Tu carrito está vacío. Selecciona un producto arriba y presiona 'Agregar al Carrito'.")
        else:
            # Renderizar tabla responsiva del carrito
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
            monto_total_pedido_bs = monto_total_pedido * tasa_oficial

            st.divider()

            col_tot1, col_tot2 = st.columns(2)
            col_tot1.metric("Total General Pedido", f"${monto_total_pedido:,.2f}", f"Bs. {monto_total_pedido_bs:,.2f}")
            col_tot2.metric("Ganancia Estimada Pedido", f"${ganancia_total_pedido:,.2f}")

            # Condición de pago
            tipo_pago = st.radio(
                "Condición de Pago del Pedido", 
                ["💵 Pagado de Contado", "📝 Crédito / Cuenta por Cobrar"], 
                horizontal=True
            )
            estado_pago_val = "Pagado" if "Pagado" in tipo_pago else "Pendiente"

            if cliente_data is None:
                st.warning("⚠️ Selecciona un cliente registrado en la parte superior para finalizar la venta.")
            else:
                col_b_clear, col_b_confirm = st.columns([1, 2])
                with col_b_clear:
                    if st.button("❌ Vaciar Carrito", use_container_width=True):
                        st.session_state['carrito_ventas'] = []
                        st.rerun()

                with col_b_confirm:
                    if st.button("🎉 Confirmar y Registrar Venta Completa", type="primary", use_container_width=True):
                        conn = conectar_db()
                        cursor = conn.cursor()
                        
                        hora_actual_str = datetime.now().strftime(" %H:%M:%S")
                        fecha_final_str = fecha_venta_elegida.strftime("%Y-%m-%d") + hora_actual_str

                        for item in st.session_state['carrito_ventas']:
                            saldo_ini_item = 0.0 if estado_pago_val == "Pagado" else item['subtotal']
                            
                            cursor.execute('''
                                INSERT INTO ventas (producto_id, cliente_id, cantidad, precio_unitario, costo_unitario, ganancia_total, estado_pago, saldo_pendiente, fecha)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (item['producto_id'], cliente_data['id'], item['cantidad'], item['precio_unitario'], item['costo_unitario'], item['ganancia'], estado_pago_val, saldo_ini_item, fecha_final_str))
                            
                            cursor.execute("UPDATE productos SET stock = stock - ? WHERE id = ?", (item['cantidad'], item['producto_id']))

                        conn.commit()
                        conn.close()

                        st.session_state['carrito_ventas'] = []
                        st.balloons()
                        st.success(f"🎉 ¡Venta multiproducto registrada exitosamente para {cliente_data['nombre']} por un total de ${monto_total_pedido:,.2f}!")

# ---------------------------------------------------------
# OPCIÓN 2: GESTIÓN DE CLIENTES Y CUENTAS POR COBRAR
# ---------------------------------------------------------
elif menu == "👥 Clientes y Cuentas por Cobrar":
    col_header, col_home = st.columns([3, 1])
    with col_header:
        st.markdown('<div class="section-header-yellow">👥 Gestión de Clientes</div>', unsafe_allow_html=True)
    with col_home:
        st.button("🏠 Volver al Inicio", key="btn_home_c", on_click=ir_a_seccion, args=("🏠 Inicio / Dashboard",), use_container_width=True)

    st.markdown('<div class="quick-access-title">Opciones de Gestión</div>', unsafe_allow_html=True)
    
    card_col1, card_col2 = st.columns(2)
    with card_col1:
        st.button(
            "📋 Listado General", 
            key="btn_sub_list", 
            use_container_width=True, 
            type="primary" if st.session_state['subseccion_clientes'] == "📋 Listado General" else "secondary",
            on_click=ir_a_subseccion_clientes, 
            args=("📋 Listado General",)
        )
        st.button(
            "✏️ Editar / Eliminar", 
            key="btn_sub_edit", 
            use_container_width=True, 
            type="primary" if st.session_state['subseccion_clientes'] == "✏️ Editar / Eliminar" else "secondary",
            on_click=ir_a_subseccion_clientes, 
            args=("✏️ Editar / Eliminar",)
        )

    with card_col2:
        st.button(
            "➕ Agregar Cliente", 
            key="btn_sub_add", 
            use_container_width=True, 
            type="primary" if st.session_state['subseccion_clientes'] == "➕ Agregar Cliente" else "secondary",
            on_click=ir_a_subseccion_clientes, 
            args=("➕ Agregar Cliente",)
        )
        st.button(
            "📋 Cuentas por Cobrar", 
            key="btn_sub_cxc", 
            use_container_width=True, 
            type="primary" if st.session_state['subseccion_clientes'] == "📋 Cuentas por Cobrar" else "secondary",
            on_click=ir_a_subseccion_clientes, 
            args=("📋 Cuentas por Cobrar",)
        )

    st.divider()

    submenu = st.session_state['subseccion_clientes']

    if submenu == "📋 Listado General":
        st.markdown('<div class="sub-header-yellow">📋 Listado General de Clientes</div>', unsafe_allow_html=True)
        conn = conectar_db()
        df_cli = pd.read_sql_query("SELECT id AS 'ID', nombre AS 'Nombre', telefono AS 'Teléfono' FROM clientes", conn)
        conn.close()
        
        if not df_cli.empty:
            st.dataframe(df_cli, use_container_width=True)
        else:
            st.info("No hay clientes registrados aún.")

    elif submenu == "➕ Agregar Cliente":
        st.markdown('<div class="sub-header-yellow">➕ Agregar Nuevo Cliente</div>', unsafe_allow_html=True)
        with st.form("form_cliente"):
            nombre_cliente = st.text_input("Nombre Completo del Cliente")
            telefono_cliente = st.text_input("Número de Teléfono / WhatsApp")
            guardar_cliente = st.form_submit_button("Guardar Cliente")

            if guardar_cliente:
                if nombre_cliente.strip() != "":
                    conn = conectar_db()
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO clientes (nombre, telefono) VALUES (?, ?)", (nombre_cliente, telefono_cliente if telefono_cliente.strip() else 'Sin teléfono'))
                    conn.commit()
                    conn.close()
                    st.success(f"✅ Cliente '{nombre_cliente}' agregado correctamente.")
                    st.rerun()

    elif submenu == "✏️ Editar / Eliminar":
        st.markdown('<div class="sub-header-yellow">✏️ Editar o Eliminar Cliente Existente</div>', unsafe_allow_html=True)
        conn = conectar_db()
        df_cli_edit = pd.read_sql_query("SELECT * FROM clientes", conn)
        conn.close()

        if not df_cli_edit.empty:
            dict_cli = {f"{row['nombre']} (ID: {row['id']})": row for _, row in df_cli_edit.iterrows()}
            cli_edit_str = st.selectbox("Selecciona el cliente a modificar", list(dict_cli.keys()))
            cli_sel = dict_cli[cli_edit_str]

            with st.form("form_editar_cliente_reg"):
                n_nombre = st.text_input("Nombre del Cliente", value=cli_sel['nombre'])
                n_telefono = st.text_input("Teléfono / WhatsApp", value=cli_sel['telefono'])

                col_b1, col_b2 = st.columns(2)
                with col_b1: act_cli = st.form_submit_button("💾 Actualizar Cambios", type="primary")
                with col_b2: elim_cli = st.form_submit_button("🗑️ Eliminar Cliente")

                if act_cli:
                    if n_nombre.strip() == "":
                        st.error("El nombre no puede estar vacío.")
                    else:
                        conn = conectar_db()
                        cursor = conn.cursor()
                        cursor.execute("UPDATE clientes SET nombre=?, telefono=? WHERE id=?", 
                                       (n_nombre, n_telefono if n_telefono.strip() else 'Sin teléfono', cli_sel['id']))
                        conn.commit()
                        conn.close()
                        st.success("✅ Cliente actualizado exitosamente.")
                        st.rerun()

                if elim_cli:
                    if cli_sel['id'] == 1:
                        st.error("❌ No se puede eliminar el cliente general/mostrador por defecto.")
                    else:
                        conn = conectar_db()
                        cursor = conn.cursor()
                        cursor.execute("UPDATE ventas SET cliente_id = 1 WHERE cliente_id = ?", (cli_sel['id'],))
                        cursor.execute("DELETE FROM clientes WHERE id=?", (cli_sel['id'],))
                        conn.commit()
                        conn.close()
                        st.warning("🗑️ Cliente eliminado correctamente.")
                        st.rerun()
        else:
            st.info("No hay clientes disponibles para editar.")

    elif submenu == "📋 Cuentas por Cobrar":
        conn = conectar_db()
        df_deudas_resumen = pd.read_sql_query('''
            SELECT c.id AS cliente_id,
                   c.nombre AS 'Cliente',
                   c.telefono AS 'Teléfono',
                   SUM(v.saldo_pendiente) AS 'Saldo Pendiente ($)',
                   COUNT(v.id) AS 'Cant. Compras'
            FROM ventas v
            JOIN clientes c ON v.cliente_id = c.id
            WHERE v.estado_pago = 'Pendiente' AND v.saldo_pendiente > 0
            GROUP BY c.id, c.nombre, c.telefono
        ''', conn)
        conn.close()

        if df_deudas_resumen.empty:
            st.success("🎉 ¡No hay cuentas por cobrar pendientes en este momento!")
        else:
            total_general = df_deudas_resumen['Saldo Pendiente ($)'].sum()
            total_general_bs = total_general * tasa_oficial
            col_m1, col_m2 = st.columns(2)
            col_m1.metric("Total USD por Cobrar", f"${total_general:,.2f}")
            col_m2.metric("Total Bs. por Cobrar", f"Bs. {total_general_bs:,.2f}")
            
            # --- SECCIÓN: REGISTRAR ABONO / NOTIFICAR WHATSAPP ---
            st.markdown('<div class="sub-header-yellow">💵 Registrar Abono o Pago / Notificar por WhatsApp</div>', unsafe_allow_html=True)
            
            opciones_clientes_deuda = {f"{row['Cliente']} (Monto Pendiente: ${row['Saldo Pendiente ($)']:,.2f})": row for _, row in df_deudas_resumen.iterrows()}
            cliente_a_liquidar_str = st.selectbox("Selecciona el Cliente", list(opciones_clientes_deuda.keys()))
            cliente_info = opciones_clientes_deuda[cliente_a_liquidar_str]
            cliente_id_sel = cliente_info['cliente_id']
            deuda_maxima = float(cliente_info['Saldo Pendiente ($)'])
            deuda_maxima_bs = deuda_maxima * tasa_oficial

            # --- BOTÓN DE ENVIAR WHATSAPP ---
            tel_bruto = str(cliente_info['Teléfono']).replace(" ", "").replace("-", "").replace("+", "")
            if tel_bruto.startswith("0"):
                num_wa = "58" + tel_bruto[1:]
            elif tel_bruto.startswith("4"):
                num_wa = "58" + tel_bruto
            else:
                num_wa = tel_bruto

            m_nombre = cliente_info['Cliente']
            m_monto_usd = f"${deuda_maxima:,.2f}".replace(",", "@").replace(".", ",").replace("@", ".")
            m_monto_bs = f"Bs. {deuda_maxima_bs:,.2f}".replace(",", "@").replace(".", ",").replace("@", ".")

            texto_msj = (
                f"Hola {m_nombre},\n\n"
                f"Queremos recordarte que tienes pagos pendientes de {m_monto_usd} ({m_monto_bs}) con Olinuts. "
                f"Nada mejor que llevar tus cuentas al día, por eso no olvides realizar los pagos. "
                f"¡Qué tengas un feliz día!"
            )
            
            texto_encoded = urllib.parse.quote(texto_msj)
            link_wa = f"https://wa.me/{num_wa}?text={texto_encoded}"

            st.markdown(f'''
                <a href="{link_wa}" target="_blank" style="text-decoration: none;">
                    <div style="
                        background-color: #25D366; 
                        color: white; 
                        padding: 14px 20px; 
                        border-radius: 12px; 
                        text-align: center; 
                        font-weight: bold; 
                        font-size: 16px;
                        margin-top: 10px;
                        margin-bottom: 20px;
                        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);">
                        📲 Enviar Recordatorio por WhatsApp a {m_nombre}
                    </div>
                </a>
            ''', unsafe_allow_html=True)

            col_ab1, col_ab2 = st.columns(2)
            with col_ab1:
                monto_abono = st.number_input("Monto a Abonar ($)", min_value=0.01, max_value=deuda_maxima, value=deuda_maxima, step=0.5, format="%.2f")
                st.caption(f"Equivalente a: **Bs. {monto_abono * tasa_oficial:,.2f}**")
            
            with col_ab2:
                st.write("")
                st.write("")
                btn_abonar = st.button("💰 Registrar Abono / Pago", type="primary", use_container_width=True)

            if btn_abonar:
                conn = conectar_db()
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, saldo_pendiente 
                    FROM ventas 
                    WHERE cliente_id = ? AND estado_pago = 'Pendiente' AND saldo_pendiente > 0
                    ORDER BY fecha ASC
                ''', (cliente_id_sel,))
                
                ventas_pendientes = cursor.fetchall()
                abono_restante = monto_abono

                for v_id, s_pendiente in ventas_pendientes:
                    if abono_restante <= 0:
                        break
                    
                    if abono_restante >= s_pendiente:
                        abono_restante -= s_pendiente
                        cursor.execute("UPDATE ventas SET saldo_pendiente = 0.0, estado_pago = 'Pagado' WHERE id = ?", (v_id,))
                    else:
                        nuevo_saldo = s_pendiente - abono_restante
                        cursor.execute("UPDATE ventas SET saldo_pendiente = ? WHERE id = ?", (nuevo_saldo, v_id))
                        abono_restante = 0.0

                conn.commit()
                conn.close()
                st.balloons()
                st.success(f"🎉 ¡Abono de ${monto_abono:,.2f} registrado exitosamente para {cliente_info['Cliente']}!")
                st.rerun()

            # --- OPCIÓN: ELIMINAR VENTA CON ERROR ---
            with st.expander("⚠️ ¿Registraste una deuda por error? Eliminar un registro de deuda"):
                conn = conectar_db()
                df_ventas_del = pd.read_sql_query('''
                    SELECT v.id, p.nombre AS producto, v.cantidad, v.saldo_pendiente, v.fecha, p.id AS producto_id
                    FROM ventas v
                    JOIN productos p ON v.producto_id = p.id
                    WHERE v.cliente_id = ? AND v.estado_pago = 'Pendiente' AND v.saldo_pendiente > 0
                ''', conn, params=(cliente_id_sel,))
                conn.close()

                if not df_ventas_del.empty:
                    dict_del = {f"ID Venta #{row['id']} - {row['producto']} ({row['cantidad']} uds) - Pendiente: ${row['saldo_pendiente']:.2f} ({row['fecha']})": row for _, row in df_ventas_del.iterrows()}
                    venta_del_sel_str = st.selectbox("Selecciona la venta pendiente a borrar", list(dict_del.keys()))
                    venta_del_info = dict_del[venta_del_sel_str]

                    if st.button("🗑️ Eliminar Registro de Deuda", type="primary", use_container_width=True):
                        conn = conectar_db()
                        cursor = conn.cursor()
                        # Devolver stock del producto
                        cursor.execute("UPDATE productos SET stock = stock + ? WHERE id = ?", (venta_del_info['cantidad'], venta_del_info['producto_id']))
                        # Borrar la venta
                        cursor.execute("DELETE FROM ventas WHERE id = ?", (venta_del_info['id'],))
                        conn.commit()
                        conn.close()
                        st.warning(f"🗑️ Registro de venta #{venta_del_info['id']} eliminado y stock restituido.")
                        st.rerun()

            st.divider()

            # --- TABLA UBICADA AL FINAL DE LA PÁGINA ---
            st.markdown('<div class="sub-header-yellow">📋 Listado de Cuentas por Cobrar por Cliente</div>', unsafe_allow_html=True)
            df_mostrar = df_deudas_resumen[['Cliente', 'Teléfono', 'Cant. Compras', 'Saldo Pendiente ($)']]
            st.dataframe(df_mostrar, use_container_width=True)

# ---------------------------------------------------------
# OPCIÓN 3: PRODUCTOS E INVENTARIO
# ---------------------------------------------------------
elif menu == "📦 Productos e Inventario":
    col_header, col_home = st.columns([3, 1])
    with col_header:
        st.markdown('<div class="section-header-yellow">📦 Gestión de Inventario</div>', unsafe_allow_html=True)
    with col_home:
        st.button("🏠 Volver al Inicio", key="btn_home_p", on_click=ir_a_seccion, args=("🏠 Inicio / Dashboard",), use_container_width=True)

    st.markdown('<div class="quick-access-title">Opciones de Inventario</div>', unsafe_allow_html=True)
    
    inv_col1, inv_col2 = st.columns(2)
    with inv_col1:
        st.button(
            "📋 Listado de Productos", 
            key="btn_inv_list", 
            use_container_width=True, 
            type="primary" if st.session_state['subseccion_inventario'] == "📋 Listado de Productos" else "secondary",
            on_click=ir_a_subseccion_inventario, 
            args=("📋 Listado de Productos",)
        )
        st.button(
            "✏️ Editar / Eliminar", 
            key="btn_inv_edit", 
            use_container_width=True, 
            type="primary" if st.session_state['subseccion_inventario'] == "✏️ Editar / Eliminar" else "secondary",
            on_click=ir_a_subseccion_inventario, 
            args=("✏️ Editar / Eliminar",)
        )

    with inv_col2:
        st.button(
            "➕ Agregar Producto", 
            key="btn_inv_add", 
            use_container_width=True, 
            type="primary" if st.session_state['subseccion_inventario'] == "➕ Agregar Nuevo Producto" else "secondary",
            on_click=ir_a_subseccion_inventario, 
            args=("➕ Agregar Nuevo Producto",)
        )

    st.divider()

    sub_inv = st.session_state['subseccion_inventario']

    if sub_inv == "📋 Listado de Productos":
        st.markdown('<div class="sub-header-yellow">📋 Listado de Productos</div>', unsafe_allow_html=True)
        conn = conectar_db()
        df_prods = pd.read_sql_query("SELECT id AS ID, nombre AS Producto, costo_unitario AS 'Costo ($)', precio_venta AS 'Precio ($)', stock AS Stock FROM productos", conn)
        conn.close()
        
        if not df_prods.empty:
            df_prods['Precio (Bs.)'] = df_prods['Precio ($)'] * tasa_oficial
            st.dataframe(df_prods, use_container_width=True)
        else:
            st.info("No hay productos registrados aún.")

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
                    conn = conectar_db()
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO productos (nombre, costo_unitario, precio_venta, stock) VALUES (?, ?, ?, ?)", (nombre, costo, precio, stock))
                    conn.commit()
                    conn.close()
                    st.success(f"✅ Producto '{nombre}' agregado.")
                    st.rerun()

    elif sub_inv == "✏️ Editar / Eliminar":
        st.markdown('<div class="sub-header-yellow">✏️ Editar o Eliminar Producto Existente</div>', unsafe_allow_html=True)
        conn = conectar_db()
        df_prods_edit = pd.read_sql_query("SELECT * FROM productos", conn)
        conn.close()

        if not df_prods_edit.empty:
            dict_prods = {f"{row['nombre']} (ID: {row['id']})": row for _, row in df_prods_edit.iterrows()}
            prod_edit_str = st.selectbox("Selecciona el producto a modificar", list(dict_prods.keys()))
            prod_sel = dict_prods[prod_edit_str]

            with st.form("form_editar"):
                n_nombre = st.text_input("Nombre", value=prod_sel['nombre'])
                c1, c2, c3 = st.columns(3)
                with c1: n_costo = st.number_input("Costo ($)", min_value=0.0, value=float(prod_sel['costo_unitario']), format="%.2f")
                with c2: n_precio = st.number_input("Precio ($)", min_value=0.0, value=float(prod_sel['precio_venta']), format="%.2f")
                with c3: n_stock = st.number_input("Stock", min_value=0, value=int(prod_sel['stock']), step=1)

                col_b1, col_b2 = st.columns(2)
                with col_b1: act = st.form_submit_button("💾 Actualizar Cambios", type="primary")
                with col_b2: elim = st.form_submit_button("🗑️ Eliminar Producto")

                if act:
                    conn = conectar_db()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE productos SET nombre=?, costo_unitario=?, precio_venta=?, stock=? WHERE id=?", (n_nombre, n_costo, n_precio, n_stock, prod_sel['id']))
                    conn.commit()
                    conn.close()
                    st.success("✅ Producto actualizado.")
                    st.rerun()

                if elim:
                    conn = conectar_db()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM productos WHERE id=?", (prod_sel['id'],))
                    conn.commit()
                    conn.close()
                    st.warning("🗑️ Producto eliminado.")
                    st.rerun()
        else:
            st.info("No hay productos disponibles para editar.")

# ---------------------------------------------------------
# OPCIÓN 4: CALENDARIO ANUAL DE VENTAS
# ---------------------------------------------------------
elif menu == "📅 Calendario Anual de Ventas":
    col_header, col_home = st.columns([3, 1])
    with col_header:
        st.markdown('<div class="section-header-yellow">📅 Calendario Anual de Ventas</div>', unsafe_allow_html=True)
    with col_home:
        st.button("🏠 Volver al Inicio", key="btn_home_cal", on_click=ir_a_seccion, args=("🏠 Inicio / Dashboard",), use_container_width=True)

    col_anio, col_mes = st.columns(2)
    with col_anio:
        anio_sel = st.selectbox("Selecciona el Año", list(range(2024, 2031)), index=2)
    with col_mes:
        meses_nombres = {
            1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 
            5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto", 
            9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
        }
        mes_sel_nombre = st.selectbox("Selecciona el Mes", list(meses_nombres.values()), index=datetime.now().month - 1)
        mes_sel = [k for k, v in meses_nombres.items() if v == mes_sel_nombre][0]

    st.markdown(f'<div class="sub-header-yellow">📊 Resumen diario de {mes_sel_nombre} {anio_sel}</div>', unsafe_allow_html=True)

    mes_str = f"{anio_sel}-{mes_sel:02d}"
    conn = conectar_db()
    df_ventas_mes = pd.read_sql_query(f'''
        SELECT v.fecha, (v.cantidad * v.precio_unitario) AS ingreso, v.cantidad, p.nombre AS producto, c.nombre AS cliente
        FROM ventas v
        JOIN productos p ON v.producto_id = p.id
        LEFT JOIN clientes c ON v.cliente_id = c.id
        WHERE v.fecha LIKE '{mes_str}%'
    ''', conn)
    conn.close()

    ventas_por_dia = {}
    if not df_ventas_mes.empty:
        df_ventas_mes['dia'] = pd.to_datetime(df_ventas_mes['fecha']).dt.day
        ventas_por_dia = df_ventas_mes.groupby('dia')['ingreso'].sum().to_dict()

    cal = calendar.monthcalendar(anio_sel, mes_sel)
    dias_semana = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]

    cols_dias = st.columns(7)
    for i, d_nombre in enumerate(dias_semana):
        cols_dias[i].markdown(f"<div style='text-align: center; font-weight: bold; color: #444;'>{d_nombre}</div>", unsafe_allow_html=True)

    for semana in cal:
        cols_semana = st.columns(7)
        for i, dia in enumerate(semana):
            with cols_semana[i]:
                if dia == 0:
                    st.markdown("<div style='color: #CCC; text-align: center; padding: 15px;'>-</div>", unsafe_allow_html=True)
                else:
                    monto_dia = ventas_por_dia.get(dia, 0.0)
                    monto_dia_bs = monto_dia * tasa_oficial
                    
                    if monto_dia > 0:
                        st.markdown(f'''
                            <div class="day-box-active">
                                <b style="font-size: 16px; color: #333;">{dia}</b><br>
                                <span style="color: #00A86B; font-weight: bold; font-size: 13px;">${monto_dia:,.2f}</span><br>
                                <span style="color: #666; font-size: 10px;">Bs. {monto_dia_bs:,.0f}</span>
                            </div>
                        ''', unsafe_allow_html=True)
                    else:
                        st.markdown(f'''
                            <div class="day-box">
                                <b style="font-size: 16px; color: #777;">{dia}</b><br>
                                <span style="color: #999; font-size: 12px;">$0.00</span>
                            </div>
                        ''', unsafe_allow_html=True)

    st.divider()
    st.markdown('<div class="sub-header-yellow">🔍 Consultar Detalle de un Día Específico</div>', unsafe_allow_html=True)
    
    dias_del_mes = list(range(1, calendar.monthrange(anio_sel, mes_sel)[1] + 1))
    dia_elegido = st.selectbox("Selecciona el día para ver las ventas detalladas", dias_del_mes, index=datetime.now().day - 1 if datetime.now().month == mes_sel and datetime.now().year == anio_sel else 0)

    fecha_busqueda = f"{anio_sel}-{mes_sel:02d}-{dia_elegido:02d}"
    
    conn = conectar_db()
    df_detalle_dia = pd.read_sql_query(f'''
        SELECT v.id AS 'ID', p.nombre AS 'Producto', c.nombre AS 'Cliente',
               v.cantidad AS 'Cant', v.precio_unitario AS 'Precio ($)', 
               (v.cantidad * v.precio_unitario) AS 'Total ($)',
               v.fecha AS 'Fecha y Hora'
        FROM ventas v
        JOIN productos p ON v.producto_id = p.id
        LEFT JOIN clientes c ON v.cliente_id = c.id
        WHERE v.fecha LIKE '{fecha_busqueda}%'
        ORDER BY v.fecha DESC
    ''', conn)
    conn.close()

    if not df_detalle_dia.empty:
        total_dia_usd = df_detalle_dia['Total ($)'].sum()
        total_dia_bs = total_dia_usd * tasa_oficial
        
        col_t1, col_t2 = st.columns(2)
        col_t1.metric(f"Total Ventas Día {dia_elegido} / {mes_sel_nombre}", f"${total_dia_usd:,.2f}")
        col_t2.metric("Total en Bolívares", f"Bs. {total_dia_bs:,.2f}")
        
        df_detalle_dia['Total (Bs.)'] = df_detalle_dia['Total ($)'] * tasa_oficial
        st.dataframe(df_detalle_dia, use_container_width=True)
    else:
        st.info(f"No se registraron ventas para el día {dia_elegido} de {mes_sel_nombre} de {anio_sel}.")

# ---------------------------------------------------------
# OPCIÓN 5: REPORTES Y MÉTRICAS
# ---------------------------------------------------------
elif menu == "📈 Reportes y Métricas":
    col_header, col_home = st.columns([3, 1])
    with col_header:
        st.markdown('<div class="section-header-yellow">📈 Reportes Financieros</div>', unsafe_allow_html=True)
    with col_home:
        st.button("🏠 Volver al Inicio", key="btn_home_r", on_click=ir_a_seccion, args=("🏠 Inicio / Dashboard",), use_container_width=True)

    conn = conectar_db()
    df_ventas = pd.read_sql_query('''
        SELECT v.id AS 'ID Venta', p.nombre AS 'Producto', c.nombre AS 'Cliente',
               v.cantidad AS 'Cantidad', v.precio_unitario AS 'Precio Unit. ($)', 
               (v.cantidad * v.precio_unitario) AS 'Ingreso Total ($)',
               v.saldo_pendiente AS 'Saldo Pendiente ($)',
               v.ganancia_total AS 'Ganancia ($)', v.estado_pago AS 'Estado de Pago', v.fecha AS 'Fecha'
        FROM ventas v
        JOIN productos p ON v.producto_id = p.id
        LEFT JOIN clientes c ON v.cliente_id = c.id
        ORDER BY v.id DESC
    ''', conn)
    conn.close()

    if not df_ventas.empty:
        total_ingresos = df_ventas['Ingreso Total ($)'].sum()
        total_ganancias = df_ventas['Ganancia ($)'].sum()
        
        col1, col2 = st.columns(2)
        col1.metric("Ingresos Totales", f"${total_ingresos:,.2f}", delta=f"Bs. {total_ingresos * tasa_oficial:,.2f}")
        col2.metric("Ganancia Neta Total", f"${total_ganancias:,.2f}", delta=f"Bs. {total_ganancias * tasa_oficial:,.2f}")
        st.divider()
        st.dataframe(df_ventas, use_container_width=True)
    else:
        st.info("Aún no hay ventas registradas para generar reportes.")
