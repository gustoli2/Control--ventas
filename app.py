import sqlite3
import streamlit as st
import pandas as pd
import requests
import urllib.parse
from datetime import datetime, date
import os
from PIL import Image, ImageDraw, ImageFont

# Configuración de la página
st.set_page_config(
    page_title="OLINUTS - Control de Ventas",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inicializar claves de estado de navegación si no existen
if 'menu_radio' not in st.session_state:
    st.session_state['menu_radio'] = "🏠 Inicio / Dashboard"

if 'subseccion_clientes' not in st.session_state:
    st.session_state['subseccion_clientes'] = "📋 Listado General"

if 'subseccion_inventario' not in st.session_state:
    st.session_state['subseccion_inventario'] = "📋 Listado de Productos"

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

# --- FUNCIÓN PARA GENERAR LA TARJETA DE COBRO EN ALTA RESOLUCIÓN ---
def generar_imagen_cobro(nombre_cliente, pendiente, neto, abonado, cant_pagos, fecha_antigua):
    # Lienzo grande de alta resolución (1000x1100 px) para máxima nitidez en móviles
    img = Image.new("RGB", (1000, 1100), color="#F5F7F8")
    draw = ImageDraw.Draw(img)
    
    # Cargar fuentes seguras de gran tamaño
    try:
        font_logo = ImageFont.truetype("arial.ttf", 44)
        font_titulo = ImageFont.truetype("arial.ttf", 38)
        font_sub = ImageFont.truetype("arial.ttf", 32)
        font_texto = ImageFont.truetype("arial.ttf", 40)
        font_monto = ImageFont.truetype("arial.ttf", 46)
    except:
        font_logo = ImageFont.load_default()
        font_titulo = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_texto = ImageFont.load_default()
        font_monto = ImageFont.load_default()

    # Recuadro principal estilo tarjeta blanca elegante
    draw.rectangle([(60, 60), (940, 1040)], fill="#FFFFFF", outline="#E0E0E0", width=3)

    # Cabecera superior con el color corporativo de Olinuts
    draw.rectangle([(60, 60), (940, 260)], fill="#3F5963")
    
    # Logo simulado / Inicial o título centrado
    draw.text((500, 120), "☕ Olinuts", fill="#FFDE59", font=font_logo, anchor="mm")
    draw.text((500, 195), f"Cliente: {nombre_cliente}", fill="#FFFFFF", font=font_titulo, anchor="mm")

    # Formatear fecha legible (Ej: 06 oct 2026)
    try:
        dt = datetime.strptime(fecha_antigua.split()[0], "%Y-%m-%d")
        meses = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
        fecha_formateada = f"{dt.day:02d} {meses[dt.month-1]} {dt.year}"
    except:
        fecha_formateada = fecha_antigua

    # Líneas financieras con excelente separación y tamaños claros
    y_pos = 360
    
    draw.text((150, y_pos), "Pendiente:", fill="#333333", font=font_texto)
    draw.text((850, y_pos), f"${pendiente:,.2f}", fill="#E53935", font=font_monto, anchor="rt")
    y_pos += 100

    draw.text((150, y_pos), "Deuda neta:", fill="#333333", font=font_texto)
    draw.text((850, y_pos), f"${neto:,.2f}", fill="#E53935", font=font_monto, anchor="rt")
    y_pos += 100

    draw.text((150, y_pos), "Abonado:", fill="#333333", font=font_texto)
    draw.text((850, y_pos), f"${abonado:,.2f}", fill="#00A86B", font=font_monto, anchor="rt")
    y_pos += 120

    # Línea divisoria decorativa
    draw.line([(150, y_pos), (850, y_pos)], fill="#E0E0E0", width=4)
    y_pos += 90

    # Texto inferior de detalle de pagos
    draw.text((500, y_pos), f"Tienes {cant_pagos} pago(s) pendiente(s)", fill="#222222", font=font_sub, anchor="mm")
    y_pos += 70
    draw.text((500, y_pos), f"desde el día {fecha_formateada}", fill="#666666", font=font_sub, anchor="mm")

    # Guardar imagen en alta calidad
    ruta_imagen = "recibo_cobro_hd.png"
    img.save(ruta_imagen, quality=95)
    return ruta_imagen

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

opciones_menu = ["🏠 Inicio / Dashboard", "🛒 Registrar Venta", "👥 Clientes y Cuentas por Cobrar", "📦 Productos e Inventario", "📈 Reportes y Métricas"]

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
# OPCIÓN 1: REGISTRAR VENTA
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
        col_prod, col_cli = st.columns(2)
        
        with col_prod:
            opciones_productos = {f"{row['nombre']} (Stock: {row['stock']})": row for _, row in df_prods.iterrows()}
            prod_seleccionado_str = st.selectbox("Selecciona un Producto", list(opciones_productos.keys()))
            prod_data = opciones_productos[prod_seleccionado_str]

        with col_cli:
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

        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Precio de Venta:** ${prod_data['precio_venta']:.2f} (~ Bs. {prod_data['precio_venta']*tasa_oficial:,.2f})")
            st.info(f"**Costo Unitario:** ${prod_data['costo_unitario']:.2f}")
        
        with col2:
            cantidad = st.number_input("Cantidad a vender", min_value=1, max_value=int(prod_data['stock']) if prod_data['stock'] > 0 else 1, step=1)
            ganancia_estimada = (prod_data['precio_venta'] - prod_data['costo_unitario']) * cantidad
            st.success(f"**Ganancia de esta venta:** ${ganancia_estimada:.2f}")

        tipo_pago = st.radio(
            "Condición de Pago", 
            ["💵 Pagado de Contado", "📝 Crédito / Cuenta por Cobrar"], 
            horizontal=True
        )
        estado_pago_val = "Pagado" if "Pagado" in tipo_pago else "Pendiente"
        
        monto_total_venta = prod_data['precio_venta'] * cantidad
        saldo_inicial = 0.0 if estado_pago_val == "Pagado" else monto_total_venta

        if prod_data['stock'] <= 0:
            st.error("❌ Producto agotado. Actualiza el stock en el inventario.")
        elif cliente_data is None:
            st.warning("⚠️ Primero guarda o selecciona un cliente de la lista para continuar con la venta.")
        else:
            if st.button("Confirmar Venta", type="primary", use_container_width=True):
                conn = conectar_db()
                cursor = conn.cursor()
                fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                cursor.execute('''
                    INSERT INTO ventas (producto_id, cliente_id, cantidad, precio_unitario, costo_unitario, ganancia_total, estado_pago, saldo_pendiente, fecha)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (prod_data['id'], cliente_data['id'], cantidad, prod_data['precio_venta'], prod_data['costo_unitario'], ganancia_estimada, estado_pago_val, saldo_inicial, fecha_actual))
                
                cursor.execute("UPDATE productos SET stock = stock - ? WHERE id = ?", (cantidad, prod_data['id']))
                conn.commit()
                conn.close()
                st.balloons()
                st.success(f"🎉 ¡Venta registrada exitosamente para {cliente_data['nombre']}!")

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
        st.subheader("📋 Listado General de Clientes")
        conn = conectar_db()
        df_cli = pd.read_sql_query("SELECT id AS 'ID', nombre AS 'Nombre', telefono AS 'Teléfono' FROM clientes", conn)
        conn.close()
        
        if not df_cli.empty:
            st.dataframe(df_cli, use_container_width=True)
        else:
            st.info("No hay clientes registrados aún.")

    elif submenu == "➕ Agregar Cliente":
        st.subheader("➕ Agregar Nuevo Cliente")
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
        st.subheader("✏️ Editar o Eliminar Cliente Existente")
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
        st.subheader("📋 Listado de Cuentas por Cobrar por Cliente")
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
            
            df_mostrar = df_deudas_resumen[['Cliente', 'Teléfono', 'Cant. Compras', 'Saldo Pendiente ($)']]
            st.dataframe(df_mostrar, use_container_width=True)
            
            st.subheader("💵 Registrar Abono o Pago / Notificar por WhatsApp")
            
            opciones_clientes_deuda = {f"{row['Cliente']} (Monto Pendiente: ${row['Saldo Pendiente ($)']:,.2f})": row for _, row in df_deudas_resumen.iterrows()}
            cliente_a_liquidar_str = st.selectbox("Selecciona el Cliente", list(opciones_clientes_deuda.keys()))
            cliente_info = opciones_clientes_deuda[cliente_a_liquidar_str]
            cliente_id_sel = cliente_info['cliente_id']
            deuda_maxima = float(cliente_info['Saldo Pendiente ($)'])
            deuda_maxima_bs = deuda_maxima * tasa_oficial

            # --- CONSULTAR DETALLES ADICIONALES DEL CLIENTE ---
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT MIN(fecha), COUNT(id) FROM ventas 
                WHERE cliente_id = ? AND estado_pago = 'Pendiente' AND saldo_pendiente > 0
            ''', (cliente_id_sel,))
            res_fechas = cursor.fetchone()
            conn.close()

            fecha_mas_antigua = res_fechas[0] if res_fechas and res_fechas[0] else str(date.today())
            cant_pagos_pendientes = res_fechas[1] if res_fechas else 1

            # Generar imagen de alta resolución y nitidez
            ruta_img_generada = generar_imagen_cobro(
                nombre_cliente=cliente_info['Cliente'],
                pendiente=deuda_maxima,
                neto=deuda_maxima,
                abonado=0.0,
                cant_pagos=cant_pagos_pendientes,
                fecha_antigua=fecha_mas_antigua
            )

            # Mostrar la imagen en tamaño grande y nítido
            st.image(ruta_img_generada, caption="📱 Tarjeta HD de Cobro Generada", use_container_width=True)

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
            
            st.success("💡 **Instrucciones:** La tarjeta de cobro se ha optimizado en alta definición y se muestra arriba. Al presionar el botón verde de WhatsApp, se abrirá el chat con el mensaje listo. Simplemente mantén presionada la tarjeta de arriba para guardarla en tu galería y adjúntala en el chat junto con el mensaje.")

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
        st.subheader("📋 Listado de Productos")
        conn = conectar_db()
        df_prods = pd.read_sql_query("SELECT id AS ID, nombre AS Producto, costo_unitario AS 'Costo ($)', precio_venta AS 'Precio ($)', stock AS Stock FROM productos", conn)
        conn.close()
        
        if not df_prods.empty:
            df_prods['Precio (Bs.)'] = df_prods['Precio ($)'] * tasa_oficial
            st.dataframe(df_prods, use_container_width=True)
        else:
            st.info("No hay productos registrados aún.")

    elif sub_inv == "➕ Agregar Nuevo Producto":
        st.subheader("➕ Agregar Nuevo Producto")
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
        st.subheader("✏️ Editar o Eliminar Producto Existente")
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
# OPCIÓN 4: REPORTES Y MÉTRICAS
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
