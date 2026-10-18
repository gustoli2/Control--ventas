import sqlite3
import streamlit as st
import pandas as pd
from datetime import datetime, date

# Configuración de la página
st.set_page_config(
    page_title="Control de Ventas",
    page_icon="🟡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ESTILOS CSS PERSONALIZADOS ---
st.markdown("""
<style>
    .stApp {
        background-color: #FAFAFA;
    }
    .header-container {
        background-color: #FFDE59;
        padding: 20px 20px 10px 20px;
        border-bottom-left-radius: 20px;
        border-bottom-right-radius: 20px;
        margin-top: -60px;
        margin-bottom: 20px;
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
    .quick-card {
        background-color: #FFF9D6;
        border-radius: 14px;
        padding: 15px;
        text-align: center;
        border: 1px solid #FFE885;
        font-weight: 600;
        color: #333;
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

    conn.commit()
    conn.close()

inicializar_db()

# --- NAVEGACIÓN EN EL MENÚ LATERAL ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=60)
st.sidebar.title("Navegación")
menu = st.sidebar.radio("Ir a:", ["🏠 Inicio / Dashboard", "🛒 Registrar Venta", "👥 Clientes y Deudas", "📦 Productos e Inventario", "📈 Reportes y Métricas"])

# ---------------------------------------------------------
# OPCIÓN: INICIO / DASHBOARD
# ---------------------------------------------------------
if menu == "🏠 Inicio / Dashboard":
    st.markdown("""
        <div class="header-container">
            <div class="header-title">👑 Mi Negocio</div>
            <div class="header-subtitle">Propietario / Panel Principal</div>
        </div>
    """, unsafe_allow_html=True)
    
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

    st.markdown(f"""
        <div class="business-card">
            <div class="card-title">Tu negocio hoy</div>
            <div class="card-amount">${ventas_hoy:,.2f}</div>
            <div style="font-size: 13px; color: #777; margin-bottom: 15px;">Ventas hoy</div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 15px;">
                <div>
                    <span style="font-size: 12px; color: #666;">Balance</span><br>
                    <span class="amount-green">${balance_hoy:,.2f}</span>
                </div>
                <div style="text-align: right;">
                    <span style="font-size: 12px; color: #666;">Costos hoy</span><br>
                    <span class="amount-red">${costos_hoy:,.2f}</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="quick-access-title">Descubre todo lo que puedes hacer</div>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="quick-card">🛒<br>Nueva Venta</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="quick-card">📦<br>Inventario</div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="quick-card">⚠️<br>Deudas</div>', unsafe_allow_html=True)

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
        st.subheader(f"💵 ${ganancias_mes:,.2f}")
        st.success("📈 Registro activo")
        st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# OPCIÓN 1: REGISTRAR VENTA
# ---------------------------------------------------------
elif menu == "🛒 Registrar Venta":
    st.header("🛒 Registrar Nueva Venta")
    
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
            opciones_clientes = {f"{row['nombre']} ({row['telefono']})": row for _, row in df_clientes.iterrows()}
            cliente_seleccionado_str = st.selectbox("Selecciona un Cliente", list(opciones_clientes.keys()))
            cliente_data = opciones_clientes[cliente_seleccionado_str]

        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Precio de Venta:** ${prod_data['precio_venta']:.2f}")
            st.info(f"**Costo Unitario:** ${prod_data['costo_unitario']:.2f}")
        
        with col2:
            cantidad = st.number_input("Cantidad a vender", min_value=1, max_value=int(prod_data['stock']) if prod_data['stock'] > 0 else 1, step=1)
            ganancia_estimada = (prod_data['precio_venta'] - prod_data['costo_unitario']) * cantidad
            st.success(f"**Ganancia de esta venta:** ${ganancia_estimada:.2f}")

        tipo_pago = st.radio(
            "Condición de Pago", 
            ["💵 Pagado de Contado", "📝 Deuda / Crédito Pendiente (Fiado)"], 
            horizontal=True
        )
        estado_pago_val = "Pagado" if "Pagado" in tipo_pago else "Pendiente"

        if prod_data['stock'] <= 0:
            st.error("❌ Producto agotado. Actualiza el stock en el inventario.")
        else:
            if st.button("Confirmar Venta", type="primary", use_container_width=True):
                conn = conectar_db()
                cursor = conn.cursor()
                fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                cursor.execute('''
                    INSERT INTO ventas (producto_id, cliente_id, cantidad, precio_unitario, costo_unitario, ganancia_total, estado_pago, fecha)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (prod_data['id'], cliente_data['id'], cantidad, prod_data['precio_venta'], prod_data['costo_unitario'], ganancia_estimada, estado_pago_val, fecha_actual))
                
                cursor.execute("UPDATE productos SET stock = stock - ? WHERE id = ?", (cantidad, prod_data['id']))
                conn.commit()
                conn.close()
                st.balloons()
                st.success(f"🎉 ¡Venta registrada exitosamente para {cliente_data['nombre']}!")

# ---------------------------------------------------------
# OPCIÓN 2: GESTIÓN DE CLIENTES Y DEUDAS
# ---------------------------------------------------------
elif menu == "👥 Clientes y Deudas":
    st.header("👥 Gestión de Clientes y Deudas")

    tab1, tab2, tab3 = st.tabs(["📋 Listado General", "➕ Agregar Nuevo Cliente", "⚠️ Clientes Deudores"])

    with tab1:
        conn = conectar_db()
        df_cli = pd.read_sql_query("SELECT id AS 'ID', nombre AS 'Nombre', telefono AS 'Teléfono' FROM clientes", conn)
        conn.close()
        
        if not df_cli.empty:
            st.dataframe(df_cli, use_container_width=True)
        else:
            st.info("No hay clientes registrados aún.")

    with tab2:
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

    with tab3:
        st.subheader("Listado de Deudas Pendientes")
        conn = conectar_db()
        df_deudas = pd.read_sql_query('''
            SELECT v.id AS 'ID Venta', c.nombre AS 'Cliente', c.telefono AS 'Teléfono',
                   p.nombre AS 'Producto', v.cantidad AS 'Cantidad',
                   (v.cantidad * v.precio_unitario) AS 'Total Deuda ($)', v.fecha AS 'Fecha'
            FROM ventas v
            JOIN clientes c ON v.cliente_id = c.id
            JOIN productos p ON v.producto_id = p.id
            WHERE v.estado_pago = 'Pendiente'
            ORDER BY v.fecha DESC
        ''', conn)
        conn.close()

        if df_deudas.empty:
            st.success("🎉 ¡No hay deudas pendientes en este momento!")
        else:
            st.metric("Total General en Deudas", f"${df_deudas['Total Deuda ($)'].sum():,.2f}")
            st.dataframe(df_deudas, use_container_width=True)
            
            venta_a_pagar = st.selectbox("Selecciona ID de Venta a Liquidar", df_deudas['ID Venta'].tolist())
            if st.button("✅ Marcar Venta como Pagada", type="primary"):
                conn = conectar_db()
                cursor = conn.cursor()
                cursor.execute("UPDATE ventas SET estado_pago = 'Pagado' WHERE id = ?", (venta_a_pagar,))
                conn.commit()
                conn.close()
                st.success("🎉 ¡Venta marcada como pagada!")
                st.rerun()

# ---------------------------------------------------------
# OPCIÓN 3: PRODUCTOS E INVENTARIO
# ---------------------------------------------------------
elif menu == "📦 Productos e Inventario":
    st.header("📦 Gestión de Inventario")

    tab1, tab2, tab3 = st.tabs(["📋 Listado de Productos", "➕ Agregar Nuevo Producto", "✏️ Editar / Eliminar Producto"])

    with tab1:
        conn = conectar_db()
        df_prods = pd.read_sql_query("SELECT id AS ID, nombre AS Producto, costo_unitario AS 'Costo ($)', precio_venta AS 'Precio ($)', stock AS Stock FROM productos", conn)
        conn.close()
        
        if not df_prods.empty:
            st.dataframe(df_prods, use_container_width=True)
        else:
            st.info("No hay productos registrados aún.")

    with tab2:
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

    with tab3:
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
    st.header("📈 Reportes Financieros")

    conn = conectar_db()
    df_ventas = pd.read_sql_query('''
        SELECT v.id AS 'ID Venta', p.nombre AS 'Producto', c.nombre AS 'Cliente',
               v.cantidad AS 'Cantidad', v.precio_unitario AS 'Precio Unit. ($)', 
               (v.cantidad * v.precio_unitario) AS 'Ingreso Total ($)',
               v.ganancia_total AS 'Ganancia ($)', v.estado_pago AS 'Estado de Pago', v.fecha AS 'Fecha'
        FROM ventas v
        JOIN productos p ON v.producto_id = p.id
        LEFT JOIN clientes c ON v.cliente_id = c.id
        ORDER BY v.id DESC
    ''', conn)
    conn.close()

    if not df_ventas.empty:
        col1, col2, col3 = st.columns(3)
        col1.metric("Ingresos Totales", f"${df_ventas['Ingreso Total ($)'].sum():,.2f}")
        col2.metric("Ganancia Neta Total", f"${df_ventas['Ganancia ($)'].sum():,.2f}")
        col3.metric("Unidades Vendidas", f"{df_ventas['Cantidad'].sum()}")
        st.divider()
        st.dataframe(df_ventas, use_container_width=True)
    else:
        st.info("Aún no hay ventas registradas para generar reportes.")
    
