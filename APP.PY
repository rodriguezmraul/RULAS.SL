import streamlit as st
import pandas as pd
from datetime import date
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

# --- CONFIGURACIÓN E IDENTIDAD VISUAL ---
st.set_page_config(page_title="ElectroInstalaciones - Gestión de Obra", layout="wide")

def cargar_identidad():
    col_logo, col_titulo = st.columns([1, 4])
    with col_logo:
        if os.path.exists("logo.png"):
            st.image("logo.png", width=150)
        else:
            st.warning("Subir 'logo.png' al repo")
    with col_titulo:
        st.title("Sistema de Gestión: Electricidad y Obra")
        st.caption("Control de partes de trabajo y ejecución presupuestaria")

# --- LÓGICA DE CORREO ELECTRÓNICO (SEGURIDAD) ---
def enviar_reporte_email(archivo, destinatario):
    try:
        # Los secretos se configuran en el panel de Streamlit Cloud
        remitente = st.secrets["email_usuario"]
        password = st.secrets["email_password"]
        
        msg = MIMEMultipart()
        msg['From'] = remitente
        msg['To'] = destinatario
        msg['Subject'] = f"REPORTE TÉCNICO - {date.today()}"
        
        cuerpo = "Se adjunta el archivo Excel con los últimos partes de obra y albaranes de presupuesto."
        msg.attach(MIMEText(cuerpo, 'plain'))
        
        with open(archivo, "rb") as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f"attachment; filename= {archivo}")
            msg.attach(part)
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(remitente, password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Error en el envío: {e}")
        return False

# --- PERSISTENCIA TEMPORAL (Session State) ---
if 'obra_data' not in st.session_state:
    st.session_state.obra_data = pd.DataFrame(columns=["Fecha", "Oficial/Técnico", "Tarea Eléctrica", "Estado Avance", "Observaciones"])
if 'presu_data' not in st.session_state:
    st.session_state.presu_data = pd.DataFrame(columns=["Nº Albarán", "Fecha", "Técnico", "Partida Material", "Coste (€)", "Notas"])

# --- INTERFAZ PRINCIPAL ---
cargar_identidad()
st.divider()

menu = st.sidebar.radio("Módulos de Gestión", ["📊 Seguimiento de Obra", "🧾 Control de Albaranes"])

# ---------------------------------------------------------
# MÓDULO 1: SEGUIMIENTO DE OBRA (ELECTRICIDAD)
# ---------------------------------------------------------
if menu == "📊 Seguimiento de Obra":
    st.subheader("🛠️ Parte de Trabajo Diario")
    
    with st.form("form_obra"):
        c1, c2 = st.columns(2)
        with c1:
            fecha = st.date_input("Fecha del informe", date.today())
            operario = st.text_input("Nombre del Oficial/Técnico")
        with c2:
            tarea = st.selectbox("Tarea ejecutada:", [
                "Trazado y marcado de cajas, tubos y cuadros",
                "Ejecución rozas en paredes y techos",
                "Montaje de soportes",
                "Colocación tubos y conductos",
                "Tendido de cables",
                "Identificación y etiquetado",
                "Conexionado de cables en bornes o regletas",
                "Instalación y conexionado de mecanismos",
                "Fijación de carril DIN y mecanismos en cuadro",
                "Cableado interno del cuadro eléctrico",
                "Configuración de equipos domóticos/automáticos",
                "Conexionado de sensores/actuadores",
                "Pruebas de continuidad",
                "Pruebas de aislamiento",
                "Verificación de tierras",
                "Programación del automatismo",
                "Pruebas de funcionamiento"
            ])
            estado = st.selectbox("Estado de avance:", [
                "Avance de la tarea en torno al 25% aprox.",
                "Avance de la tarea en torno al 50% aprox.",
                "Avance de la tarea en torno al 75% aprox.",
                "OK, finalizado sin errores",
                "Finalizado, pero con errores pendientes de corregir",
                "Finalizado y corregidos los errores"
            ])
        
        comentarios = st.text_area("Notas técnicas / Incidencias en obra")
        if st.form_submit_button("Registrar Parte"):
            nuevo = {"Fecha": fecha, "Oficial/Técnico": operario, "Tarea Eléctrica": tarea, "Estado Avance": estado, "Observaciones": comentarios}
            st.session_state.obra_data = pd.concat([st.session_state.obra_data, pd.DataFrame([nuevo])], ignore_index=True)
            st.success("Parte añadido correctamente.")

    st.dataframe(st.session_state.obra_data, use_container_width=True)

# ---------------------------------------------------------
# MÓDULO 2: SEGUIMIENTO DE PRESUPUESTO
# ---------------------------------------------------------
else:
    st.subheader("💰 Control de Gastos y Materiales")
    
    with st.form("form_presu"):
        c1, c2 = st.columns(2)
        with c1:
            n_albaran = st.text_input("Nº de Albarán / Factura")
            f_presu = st.date_input("Fecha recepción", date.today())
            tecnico_p = st.text_input("Persona que recibe")
        with c2:
            partida_elec = st.selectbox("Partida asociada:", [
                "Material Eléctrico (Mecanismos/Cables)",
                "Cuadros y Protecciones",
                "Iluminación y Luminarias",
                "Domótica y Control",
                "Canalización y Soportería",
                "Pequeño Material / Consumibles",
                "Mano de Obra Subcontratada"
            ])
            monto = st.number_input("Importe del albarán (€)", min_value=0.0, format="%.2f")
            foto = st.file_uploader("Captura del Albarán (Foto)", type=["jpg", "png", "pdf"])
            
        coment_p = st.text_area("Detalles del pedido")
        if st.form_submit_button("Cargar Gasto"):
            nuevo_g = {"Nº Albarán": n_albaran, "Fecha": f_presu, "Técnico": tecnico_p, "Partida Material": partida_elec, "Coste (€)": monto, "Notas": coment_p}
            st.session_state.presu_data = pd.concat([st.session_state.presu_data, pd.DataFrame([nuevo_g])], ignore_index=True)
            st.success("Gasto imputado a la partida.")

    st.dataframe(st.session_state.presu_data, use_container_width=True)
    st.metric("Gasto Acumulado Total", f"{st.session_state.presu_data['Coste (€)'].sum()} €")

# ---------------------------------------------------------
# EXPORTACIÓN Y ENVÍO (Requisito Obligatorio)
# ---------------------------------------------------------
st.sidebar.divider()
st.sidebar.subheader("📤 Finalizar Jornada")

if st.sidebar.button("📦 Generar Excel"):
    file_name = "Control_Obra_Electrica.xlsx"
    with pd.ExcelWriter(file_name) as writer:
        st.session_state.obra_data.to_excel(writer, sheet_name='Partes de Obra', index=False)
        st.session_state.presu_data.to_excel(writer, sheet_name='Gastos Presupuesto', index=False)
    
    with open(file_name, "rb") as f:
        st.sidebar.download_button("⬇️ Descargar Excel", f, file_name=file_name)
    st.sidebar.success("Excel listo para descarga")

target_mail = st.sidebar.text_input("Email Destino (Profesor/Empresa)", "profesora@colegio.com")
if st.sidebar.button("📧 Enviar Reporte por Email"):
    # Guardamos temporalmente para enviar
    temp_file = "Reporte_Final.xlsx"
    with pd.ExcelWriter(temp_file) as writer:
        st.session_state.obra_data.to_excel(writer, sheet_name='Obra', index=False)
        st.session_state.presu_data.to_excel(writer, sheet_name='Presupuesto', index=False)
    
    if enviar_reporte_email(temp_file, target_mail):
        st.sidebar.success("¡Email enviado con éxito!")
    else:
        st.sidebar.error("Error en el envío. Verifica los Secrets.")
