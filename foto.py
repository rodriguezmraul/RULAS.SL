import shutil
import os

def guardar_foto(archivo_origen, num_albaran):
    folder = "fotos_albaranes"
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    extension = os.path.splitext(archivo_origen)[1]
    nombre_archivo = f"foto_{num_albaran}{extension}"
    ruta_destino = os.path.join(folder, nombre_archivo)
    
    shutil.copy(archivo_origen, ruta_destino)
    return ruta_destino
