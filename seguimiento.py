import streamlit as st
import pandas as pd
from datetime import date
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import io

# Configuración de la página e imagen de logo [cite: 10]
st.set_page_config(page_title="Seguimiento de Obra", page_icon="🏗️")
st.title("🏗️ App Seguimiento de Obra")
st.subheader("Fundación Masaveu - Salesianos Oviedo")

# 1. Selección de Tareas [cite: 11, 12-23, 29-33]
tareas = [
    "Trazado y marcado de cajas, tubos y cuadros",
    "Ejecución rozas en paredes y techos",
    "Montaje de soportes",
    "Colocación tubos y conductos",
    "Tendido de cables",
    "Identificación y etiquetado",
    "Conexionado de cables en bornes o regletas",
    "Instalación y conexionado de mecanismos",
    "Fijación de carril DIN y mecanismos en cuadro eléctrico",
    "Cableado interno del cuadro eléctrico",
    "Configuración de equipos domóticos y/o automáticos",
    "Conexionado de sensores/actuadores de equipos domóticos/automáticos",
    "Pruebas de continuidad",
    "Pruebas de aislamiento",
    "Verificación de tierras",
    "Programación del automatismo",
    "Pruebas de funcionamiento"
]

# 2. Selección de Estado [cite: 34-40]
estados = [
    "Avance de la tarea en torno al 25% aprox.",
    "Avance de la tarea en torno al 50% aprox.",
    "Avance de la tarea en torno al 75% aprox.",
    "OK, finalizado sin errores",
    "Finalizado, pero con errores pendientes de corregir",
    "Finalizado y corregidos los errores"
]

# Formulario de entrada de datos
with st.form("registro_obra"):
    nombre_trabajador = st.text_input("Nombre del trabajador [cite: 41]")
    fecha_envio = st.date_input("Fecha de envío [cite: 42]", date.today())
    tarea_seleccionada = st.selectbox("Seleccione la tarea [cite: 11]", tareas)
    estado_seleccionado = st.selectbox("Estado de la tarea [cite: 34]", estados)
    
    boton_registro = st.form_submit_button("Registrar Tarea")

# Inicializar historial en la sesión (temporal, dura 2 horas en Streamlit Cloud) 
if 'historial' not in st.session_state:
    st.session_state.historial = pd.DataFrame(columns=["Fecha", "Trabajador", "Tarea", "Estado"])

if boton_registro:
    nuevo_registro = {
        "Fecha": fecha_envio,
        "Trabajador": nombre_trabajador,
        "Tarea": tarea_seleccionada,
        "Estado": estado_seleccionado
    }
    st.session_state.historial = pd.concat([st.session_state.historial, pd.DataFrame([nuevo_registro])], ignore_index=True)
    st.success("Registro añadido localmente.")

# Mostrar tabla de registros
st.write("### Registros actuales")
st.dataframe(st.session_state.historial)

# 3. Generación de Excel (.xlsx) [cite: 43]
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
    st.session_state.historial.to_excel(writer, index=False, sheet_name='Seguimiento')

# Botón para descargar el Excel al móvil/PC [cite: 43]
st.download_button(
    label="Descargar Excel (.xlsx)",
    data=buffer.getvalue(),
    file_name=f"seguimiento_obra_{date.today()}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# 4. Envío por Correo Electrónico [cite: 44, 45]
st.divider()
st.subheader("Envío por Email")
st.info("Nota: Para el envío, configura los 'Secrets' en Streamlit con tu contraseña de aplicación.")

email_destino = st.text_input("Email Destino (Profesora)", value="profesora@ejemplo.com")

if st.button("Enviar Excel por Correo"):
    try:
        # Recuperar credenciales de Streamlit Secrets 
        user_email = st.secrets["EMAIL_USER"]
        password = st.secrets["EMAIL_PASSWORD"] # Contraseña específica de app 

        msg = MIMEMultipart()
        msg['From'] = user_email
        msg['To'] = email_destino
        msg['Subject'] = f"Seguimiento Obra - {nombre_trabajador}"

        # Adjuntar archivo
        part = MIMEBase('application', "octet-stream")
        part.set_payload(buffer.getvalue())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="reporte.xlsx"')
        msg.attach(part)

        # Configuración servidor SMTP (ejemplo Gmail)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(user_email, password)
        server.send_message(msg)
        server.quit()
        st.success("Correo enviado con éxito.")
    except Exception as e:
        st.error(f"Error al enviar: {e}")
