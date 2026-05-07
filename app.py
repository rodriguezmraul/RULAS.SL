import streamlit as st
import pandas as pd
from datetime import datetime
import io

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Gestión de Obra - Fundación Masaveu", layout="centered")

# --- LOGO DE LA EMPRESA ---
# Nota: Reemplaza 'logo.png' con la ruta de tu imagen o una URL
try:
    st.image("https://www.fundacionmasaveu.com/wp-content/uploads/2021/03/logo-fundacion-masaveu.png", width=200)
except:
    st.warning("Logo no encontrado. Asegúrate de incluir 'logo.png' en tu repo.")

st.title("Sistema de Gestión de Obra")
st.markdown("---")

# --- MENÚ PRINCIPAL ---
opcion_principal = st.selectbox(
    "Seleccione el módulo:",
    ["Seguimiento de Obra", "Presupuesto / Albaranes"]
)

# --- INICIALIZACIÓN DE SESIÓN (Base de datos temporal) ---
if 'db_seguimiento' not in st.session_state:
    st.session_state.db_seguimiento = []
if 'db_presupuesto' not in st.session_state:
    st.session_state.db_presupuesto = []

# --- MÓDULO 1: SEGUIMIENTO DE OBRA ---
if opcion_principal == "Seguimiento de Obra":
    st.header("📝 Registro de Seguimiento")
    
    with st.form("form_obra"):
        col1, col2 = st.columns(2)
        with col1:
            trabajador = st.text_input("Nombre del Trabajador")
            fecha = st.date_input("Fecha de envío", datetime.now())
        
        tarea = st.selectbox("Tarea de la obra:", [
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
        ])
        
        estado = st.selectbox("Estado de la tarea:", [
            "Avance de la tarea en torno al 25% aprox.",
            "Avance de la tarea en torno al 50% aprox.",
            "Avance de la tarea en torno al 75% aprox.",
            "OK, finalizado sin errores",
            "Finalizado, pero con errores pendientes de corregir",
            "Finalizado y corregidos los errores"
        ])
        
        submitted = st.form_submit_button("Registrar Tarea")
        if submitted:
            nuevo_registro = {
                "Fecha": fecha, "Trabajador": trabajador, 
                "Tarea": tarea, "Estado": estado
            }
            st.session_state.db_seguimiento.append(nuevo_registro)
            st.success("Registro añadido temporalmente.")

# --- MÓDULO 2: PRESUPUESTO ---
else:
    st.header("💰 Gestión de Presupuesto y Albaranes")
    
    with st.form("form_presupuesto"):
        n_albaran = st.text_input("Número de albarán")
        fecha_alb = st.date_input("Fecha", datetime.now())
        trabajador_alb = st.text_input("Trabajador")
        partida = st.text_input("Partida del presupuesto asociada")
        gastos = st.number_input("Gastos de esa partida (€)", min_value=0.0, step=0.01)
        comentarios = st.text_area("Comentarios")
        
        # Nota Extra: Subida de fotos
        foto = st.file_uploader("Subir foto del albarán", type=['png', 'jpg', 'jpeg'])
        
        submitted_p = st.form_submit_button("Registrar Albarán")
        if submitted_p:
            st.session_state.db_presupuesto.append({
                "Albarán": n_albaran, "Fecha": fecha_alb, "Trabajador": trabajador_alb,
                "Partida": partida, "Gastos": gastos, "Comentarios": comentarios
            })
            st.success("Albarán registrado.")

# --- SECCIÓN DE EXPORTACIÓN Y ENVÍO ---
st.markdown("---")
st.subheader("📊 Exportar Datos")

# Mostrar tablas actuales
if st.session_state.db_seguimiento or st.session_state.db_presupuesto:
    df_seg = pd.DataFrame(st.session_state.db_seguimiento)
    df_pre = pd.DataFrame(st.session_state.db_presupuesto)
    
    # Crear Excel en memoria
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        if not df_seg.empty:
            df_seg.to_excel(writer, sheet_name='Seguimiento', index=False)
        if not df_pre.empty:
            df_pre.to_excel(writer, sheet_name='Presupuesto', index=False)
    
    excel_data = output.getvalue()

    col_down, col_mail = st.columns(2)
    
    with col_down:
        st.download_button(
            label="📥 Descargar Excel",
            data=excel_data,
            file_name=f"reporte_obra_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    with col_mail:
        if st.button("📧 Enviar por Correo a Empresa"):
            try:
                # 1. Configuración de credenciales (se sacan de 'Secrets')
                email_usuario = st.secrets["email_user"]
                email_password = st.secrets["email_password"]
                email_destino = "ana@fundacionmasaveu.com"

                # 2. Crear el mensaje
                import smtplib
                from email.mime.multipart import MIMEMultipart
                from email.mime.text import MIMEText
                from email.mime.base import MIMEBase
                from email import encoders

                msg = MIMEMultipart()
                msg['From'] = email_usuario
                msg['To'] = email_destino
                msg['Subject'] = f"Reporte de Obra - {datetime.now().strftime('%d/%m/%Y')}"
                msg.attach(MIMEText("Se adjunta el reporte de seguimiento y presupuesto.", 'plain'))

                # 3. Adjuntar el Excel que ya generaste
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(excel_data)
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f"attachment; filename=reporte.xlsx")
                msg.attach(part)

                # 4. Envío real (Usando el servidor de Gmail)
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(email_usuario, email_password)
                server.sendmail(email_usuario, email_destino, msg.as_string())
                server.quit()

                st.success("✅ ¡Correo enviado con éxito!")
            except Exception as e:
                st.error(f"Error técnico: {e}")
