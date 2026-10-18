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
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto_id INTEGER,
            cantidad INTEGER NOT NULL,
            precio_unitario REAL NOT NULL,
            costo_unitario REAL NOT NULL,
            ganancia_total REAL NOT NULL,
            fecha TEXT NOT NULL,
            FOREIGN KEY (producto_id) REFERENCES productos(id)
        )
    ''')
    conn.commit()
    conn.close()

# Inicializar DB al arrancar
inicializar_db()

# --- INTERFAZ DE USUARIO CON STREAMLIT ---
st.title("📊 Sistema de Control de Ventas y Ganancias")

menu = st.sidebar.selectbox("Navegación", ["🛒 Registrar Venta", "📦 Productos e Inventario", "📈 Reportes y Métricas"])

# ---------------------------------------------------------
# OPCIÓN 1: REGISTRAR VENTA
# ---------------------------------------------------------
if menu == "🛒 Registrar Venta":
    st.header("Registrar Nueva Venta")
    
    conn = conectar_db()
    df_prods = pd.read_sql_query("SELECT id, nombre, costo_unitario, precio_venta, stock FROM productos", conn)
    conn.close()

    if df_prods.empty:
        st.warning("⚠️ Primero debes agregar productos en la sección 'Productos e Inventario'.")
    else:
        # Formulario de Selección
        opciones_productos = {f"{row['nombre']} (Stock: {row['stock']})": row for _, row in df_prods.iterrows()}
        prod_seleccionado_str = st.selectbox("Selecciona un Producto", list(opciones_productos.keys()))
        prod_data = opciones_productos[prod_seleccionado_str]

        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Precio de Venta:** ${prod_data['precio_venta']:.2f}")
            st.info(f"**Costo Unitario:** ${prod_data['costo_unitario']:.2f}")
        
        with col2:
            cantidad = st.number_input("Cantidad a vender", min_value=1, max_value=int(prod_data['stock']) if prod_data['stock'] > 0 else 1, step=1)
            ganancia_estimada = (prod_data['precio_venta'] - prod_data['costo_unitario']) * cantidad
            st.success(f"**Ganancia de esta venta:** ${ganancia_estimada:.2f}")

        if prod_data['stock'] <= 0:
            st.error("❌ Producto agotado. Actualiza el stock en el inventario.")
        else:
            if st.button("Confirmar Venta", type="primary"):
                conn = conectar_db()
                cursor = conn.cursor()
                
                fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Insertar Venta
                cursor.execute('''
                    INSERT INTO ventas (producto_id, cantidad, precio_unitario, costo_unitario, ganancia_total, fecha)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (prod_data['id'], cantidad, prod_data['precio_venta'], prod_data['costo_unitario'], ganancia_estimada, fecha_actual))
                
                # Actualizar Stock
                cursor.execute("UPDATE productos SET stock = stock - ? WHERE id = ?", (cantidad, prod_data['id']))
                
                conn.commit()
                conn.close()
                st.balloons()
                st.success("🎉 ¡Venta registrada exitosamente!")
                st.rerun()

# ---------------------------------------------------------
# OPCIÓN 2: PRODUCTOS E INVENTARIO
# ---------------------------------------------------------
elif menu == "📦 Productos e Inventario":
    st.header("Gestión de Inventario")

    tab1, tab2 = st.tabs(["📋 Listado de Productos", "➕ Agregar Nuevo Producto"])

    with tab1:
        conn = conectar_db()
        df_prods = pd.read_sql_query("SELECT id, nombre AS Producto, costo_unitario AS 'Costo ($)', precio_venta AS 'Precio ($)', stock AS Stock FROM productos", conn)
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
# OPCIÓN 3: REPORTES Y MÉTRICAS
# ---------------------------------------------------------
elif menu == "📈 Reportes y Métricas":
    st.header("Métricas y Rendimiento Financiero")

    conn = conectar_db()
    df_ventas = pd.read_sql_query('''
        SELECT v.id, p.nombre AS Producto, v.cantidad AS Cantidad, 
               v.precio_unitario AS 'Precio Unit. ($)', v.costo_unitario AS 'Costo Unit. ($)',
               (v.cantidad * v.precio_unitario) AS 'Ingreso Total ($)',
               v.ganancia_total AS 'Ganancia ($)', v.fecha AS Fecha
        FROM ventas v
        JOIN productos p ON v.producto_id = p.id
        ORDER BY v.id DESC
    ''', conn)
    conn.close()

    if df_ventas.empty:
        st.info("Aún no hay ventas registradas para generar reportes.")
    else:
        # Métricas Principales (KPIs)
        total_ingresos = df_ventas['Ingreso Total ($)'].sum()
        total_ganancias = df_ventas['Ganancia ($)'].sum()
        total_unidades = df_ventas['Cantidad'].sum()
        margen_promedio = (total_ganancias / total_ingresos * 100) if total_ingresos > 0 else 0

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Ingresos Totales", f"${total_ingresos:,.2f}")
        col2.metric("Ganancia Neta Total", f"${total_ganancias:,.2f}")
        col3.metric("Unidades Vendidas", f"{total_unidades}")
        col4.metric("Margen Global", f"{margen_promedio:.1f}%")

        st.divider()

        st.subheader("Historial Detallado de Ventas")
        st.dataframe(df_ventas, use_container_width=True)
