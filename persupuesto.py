import sqlite3
from datetime import datetime

# Configuración inicial de la base de datos
def inicializar_db():
    conn = sqlite3.connect('seguimiento_obra.db')
    cursor = conn.cursor()
    
    # Tabla de Partidas Presupuestarias
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS presupuestos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_partida TEXT NOT NULL,
            monto_total REAL NOT NULL,
            monto_gastado REAL DEFAULT 0
        )
    ''')
    
    # Tabla de Albaranes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS albaranes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            num_albaran TEXT NOT NULL,
            fecha TEXT NOT NULL,
            trabajador TEXT NOT NULL,
            partida_id INTEGER,
            gasto REAL NOT NULL,
            comentarios TEXT,
            foto_patron TEXT, -- Aquí guardaremos la ruta del archivo de imagen
            FOREIGN KEY (partida_id) REFERENCES presupuestos(id)
        )
    ''')
    conn.commit()
    conn.close()
