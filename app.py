import sqlite3
import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Control de Ventas y Ganancias", page_icon="📊", layout="wide")

# --- FUNCIONES DE BASE DE DATOS ---
def conectar_db():
    return sqlite3.connect("control_ventas.db")

def inicializar_db():
    conn = conectar_db()
    cursor = conn.cursor()
    
    # Tabla de Productos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            costo_unitario REAL NOT NULL,
            precio_venta REAL NOT NULL,
            stock INTEGER DEFAULT 0
        )
    ''')
    
    # Tabla de Clientes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            telefono TEXT
        )
    ''')
    
    # Insertar cliente por defecto
    cursor.execute("SELECT COUNT(*) FROM clientes WHERE id = 1")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO clientes (id, nombre, telefono) VALUES (1, 'Cliente Mostrador / General', 'S/N')")

    # Tabla de Ventas (incluye estado_pago)
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
    
    # Verificaciones de compatibilidad para tablas existentes
    cursor.execute("PRAGMA table_info(ventas)")
    columnas = [col[1] for col in cursor.fetchall()]
    if 'cliente_id' not in columnas:
        cursor.execute("ALTER TABLE ventas ADD COLUMN cliente_id INTEGER DEFAULT 1")
    if 'estado_pago' not in columnas:
        cursor.execute("ALTER TABLE ventas ADD COLUMN estado_pago TEXT DEFAULT 'Pagado'")

    conn.commit()
    conn.close()

# Inicializar DB al arrancar
inicializar_db()

# --- INTERFAZ DE USUARIO CON STREAMLIT ---
st.title("📊 Sistema de Control de Ventas y Ganancias")

menu = st.sidebar.selectbox("Navegación", ["🛒 Registrar Venta", "👥 Clientes", "📦 Productos e Inventario", "📈 Reportes y Métricas"])

# ---------------------------------------------------------
# OPCIÓN 1: REGISTRAR VENTA
# ---------------------------------------------------------
if menu == "🛒 Registrar Venta":
    st.header("Registrar Nueva Venta")
    
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

        # Selección de Condición de Pago
        tipo_pago = st.radio(
            "Condición de Pago", 
            ["💵 Pagado de Contado", "📝 Deuda / Crédito Pendiente (Fiado)"], 
            horizontal=True
        )
        estado_pago_val = "Pagado" if "Pagado" in tipo_pago else "Pendiente"

        if prod_data['stock'] <= 0:
            st.error("❌ Producto agotado. Actualiza el stock en el inventario.")
        else:
            if st.button("Confirmar Venta", type="primary"):
                conn = conectar_db()
                cursor = conn.cursor()
                
                fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Insertar Venta con estado de pago
                cursor.execute('''
                    INSERT INTO ventas (producto_id, cliente_id, cantidad, precio_unitario, costo_unitario, ganancia_total, estado_pago, fecha)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (prod_data['id'], cliente_data['id'], cantidad, prod_data['precio_venta'], prod_data['costo_unitario'], ganancia_estimada, estado_pago_val, fecha_actual))
                
                # Actualizar Stock
                cursor.execute("UPDATE productos SET stock = stock - ? WHERE id = ?", (cantidad, prod_data['id']))
                
                conn.commit()
                conn.close()
                st.balloons()
                st.success(f"🎉 ¡Venta registrada exitosamente para {cliente_data['nombre']} ({'Contado' if estado_pago_val=='Pagado' else 'Deuda'})!")
                st.rerun()

# ---------------------------------------------------------
# OPCIÓN 2: GESTIÓN DE CLIENTES Y DEUD
to"])

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
            with col1:
                costo = st.number_input("Costo Unitario ($)", min_value=0.0, format="%.2f")
            with col2:
                precio = st.number_input("Precio de Venta ($)", min_value=0.0, format="%.2f")
            with col3:
                stock = st.number_input("Stock Inicial", min_value=0, step=1)

            guardar = st.form_submit_button("Guardar Producto")

            if guardar:
                if nombre.strip() == "":
                    st.error("El nombre del producto no puede estar vacío.")
                else:
                    conn = conectar_db()
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO productos (nombre, costo_unitario, precio_venta, stock)
                        VALUES (?, ?, ?, ?)
                    ''', (nombre, costo, precio, stock))
                    conn.commit()
                    conn.close()
                    st.success(f"✅ Producto '{nombre}' agregado correctamente.")
                    st.rerun()

# ---------------------------------------------------------
# OPCIÓN 4: REPORTES Y MÉTRICAS
# ---------------------------------------------------------
elif menu == "📈 Reportes y Métricas":
    st.header("Métricas y Rendimiento Financiero")

    conn = conectar_db()
    df_ventas = pd.read_sql_query('''
        SELECT v.id AS 'ID Venta', 
               p.nombre AS 'Producto', 
               c.nombre AS 'Cliente',
               c.telefono AS 'Teléfono Cliente',
               v.cantidad AS 'Cantidad', 
               v.precio_unitario AS 'Precio Unit. ($)', 
               v.costo_unitario AS 'Costo Unit. ($)',
               (v.cantidad * v.precio_unitario) AS 'Ingreso Total ($)',
               v.ganancia_total AS 'Ganancia ($)', 
               v.estado_pago AS 'Estado de Pago',
               v.fecha AS 'Fecha'
        FROM ventas v
        JOIN productos p ON v.producto_id = p.id
        LEFT JOIN clientes c ON v.cliente_id = c.id
        ORDER BY v.id DESC
    ''', conn)
    conn.close()

    if df_ventas.empty:
        st.info("Aún no hay ventas registradas para generar reportes.")
    else:
        # Métricas Principales (KPIs)
        total_ingresos = df_ventas['Ingreso Total ($)'].sum()
        total_ganancias = df_ventas['Ganancia ($)'].sum()
        
        # Calcular total de deudas pendientes
        df_pendientes = df_ventas[df_ventas['Estado de Pago'] == 'Pendiente']
        total_deudas = df_pendientes['Ingreso Total ($)'].sum() if not df_pendientes.empty else 0.0

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Ingresos Totales", f"${total_ingresos:,.2f}")
        col2.metric("Ganancia Neta Total", f"${total_ganancias:,.2f}")
        col3.metric("Deudas Pendientes", f"${total_deudas:,.2f}", delta_color="inverse")
        col4.metric("Unidades Vendidas", f"{df_ventas['Cantidad'].sum()}")

        st.divider()

        st.subheader("Historial Detallado de Ventas")
        st.dataframe(df_ventas, use_container_width=True)
        
