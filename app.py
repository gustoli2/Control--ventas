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
    
    mes_actual_str = date.today().strftime("%
    
