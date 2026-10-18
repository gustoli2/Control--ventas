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

# Inicializar la clave 'menu_radio' si no existe
if 'menu_radio' not in st.session_state:
    st.session_state['menu_radio'] = "🏠 Inicio / Dashboard"

# --- FUNCIONES DE NAVEGACIÓN ---
def ir_a_seccion(nombre_seccion):
    st.session_state['menu_radio'] = nombre_seccion

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

# --- NAVEGACIÓN EN EL MENÚ LATERAL ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=60)
st.sidebar.title("Navegación")

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
    
    # Botones directos con callback
    st.button("🛒  Nueva Venta", key="btn_nv", use_container_width=True, on_click=ir_a_seccion, args=("🛒 Registrar Venta",))

    c1, c2 = st.columns(2)
    with c1:
        st.button("📦  Inventario", key="btn_inv", use_container_width=True, on_click=ir_a_seccion, args=("📦 Productos e Inventario",))
    with c2:
        st.button("📋  Cuentas por Cobrar", key="btn_deu", use_container_width=True, on_click=ir_a_seccion, args=("👥 Clientes y Cuentas por Cobrar",))

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
    col_header, col_home = st.columns([3, 1])
    with col_header:
        st.header("🛒 Registrar Nueva Venta")
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
            ["💵 Pagado de Contado", "📝 Crédito / Cuenta por Cobrar"], 
            horizontal=True
        )
        estado_pago_val = "Pagado" if "Pagado" in tipo_pago else "Pendiente"
        
        monto_total_venta = prod_data['precio_venta'] * cantidad
        saldo_inicial = 0.0 if estado_pago_val == "Pagado" else monto_total_venta

        if prod_data['stock'] <= 0:
            st.error("❌ Producto agotado. Actualiza el stock en el inventario.")
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
        st.header("👥 Gestión de Clientes y Cuentas por Cobrar")
    with col_home:
        st.button("🏠 Volver al Inicio", key="btn_home_c", on_click=ir_a_seccion, args=("🏠 Inicio / Dashboard",), use_container_width=True)

    tab1, tab2, tab3, tab4 = st.tabs(["📋 Listado General", "➕ Agregar Nuevo Cliente", "✏️ Editar / Eliminar Cliente", "📋 Cuentas por Cobrar"])

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
        st.subheader("Editar o Eliminar Cliente Existente")
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

    with tab4:
        st.subheader("Listado de Cuentas por Cobrar por Cliente")
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
            st.metric("Total General por Cobrar", f"${total_general:,.2f}")
            
            df_mostrar = df_deudas_resumen[['Cliente', 'Teléfono', 'Cant. Compras', 'Saldo Pendiente ($)']]
            st.dataframe(df_mostrar, use_container_width=True)
            
            st.subheader("💵 Registrar Abono o Pago")
            
            opciones_clientes_deuda = {f"{row['Cliente']} (Monto Pendiente: ${row['Saldo Pendiente ($)']:,.2f})": row for _, row in df_deudas_resumen.iterrows()}
            cliente_a_liquidar_str = st.selectbox("Selecciona el Cliente", list(opciones_clientes_deuda.keys()))
            cliente_info = opciones_clientes_deuda[cliente_a_liquidar_str]
            cliente_id_sel = cliente_info['cliente_id']
            deuda_maxima = float(cliente_info['Saldo Pendiente ($)'])

            col_ab1, col_ab2 = st.columns(2)
            with col_ab1:
                monto_abono = st.number_input("Monto a Abonar ($)", min_value=0.01, max_value=deuda_maxima, value=deuda_maxima, step=0.5, format="%.2f")
            
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
        st.header("📦 Gestión de Inventario")
    with col_home:
        st.button("🏠 Volver al Inicio", key="btn_home_p", on_click=ir_a_seccion, args=("🏠 Inicio / Dashboard",), use_container_width=True)

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
    col_header, col_home = st.columns([3, 1])
    with col_header:
        st.header("📈 Reportes Financieros")
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
        col1, col2, col3 = st.columns(3)
        col1.metric("Ingresos Totales", f"${df_ventas['Ingreso Total ($)'].sum():,.2f}")
        col2.metric("Ganancia Neta Total", f"${df_ventas['Ganancia ($)'].sum():,.2f}")
        col3.metric("Unidades Vendidas", f"{df_ventas['Cantidad'].sum()}")
        st.divider()
        st.dataframe(df_ventas, use_container_width=True)
    else:
        st.info("Aún no hay ventas registradas para generar reportes.")
