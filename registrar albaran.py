def registrar_albaran(num, trabajador, partida_id, gasto, comentario, ruta_foto=None):
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    conn = sqlite3.connect('seguimiento_obra.db')
    cursor = conn.cursor()
    
    try:
        # 1. Insertar el albarán
        cursor.execute('''
            INSERT INTO albaranes (num_albaran, fecha, trabajador, partida_id, gasto, comentarios, foto_patron)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (num, fecha_actual, trabajador, partida_id, gasto, comentario, ruta_foto))
        
        # 2. Actualizar el gasto en la partida presupuestaria
        cursor.execute('''
            UPDATE presupuestos 
            SET monto_gastado = monto_gastado + ? 
            WHERE id = ?
        ''', (gasto, partida_id))
        
        conn.commit()
        print("¡Albarán registrado y presupuesto actualizado!")
        
    except Exception as e:
        print(f"Error al registrar: {e}")
        conn.rollback()
    finally:
        conn.close()
