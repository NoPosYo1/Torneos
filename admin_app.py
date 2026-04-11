import streamlit as st
from supabase import create_client
import re

supabd = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

st.set_page_config(page_title="Torneo 2v2 GGReport - Admin", layout="wide", initial_sidebar_state="collapsed")
st.session_state.logged_in = st.session_state.get('logged_in', False)


def sanitizar_input(texto):
    if not texto:
        return ""
    # 1. Eliminar caracteres de control Unicode (como los BiDi que vimos)
    # \u200b-\u200f y \u202a-\u202e son los más comunes que dan problemas
    texto_limpio = re.sub(r'[\u200e\u200f\u202a-\u202e\u2066-\u2069]', '', texto)
    
    # 2. Quitar espacios extra al inicio y final
    return texto_limpio.strip()

def registrar_equipo(jugador1, jugador2):
    # Aquí iría la lógica para registrar el equipo en la base de datos
    
    jugador_1 = sanitizar_input(jugador1)
    if jugador2 == "":
        jugador_2 = "Sin Duo"
    else:
        jugador_2 = sanitizar_input(jugador2)
    
    try:
        supabd.table("jugador").insert({"nick": jugador_1}).execute()
    except:
        st.error(f"Error al registrar jugador 1: {jugador_1}")
    
    if jugador_2 != "Sin Duo":
        try:
            supabd.table("jugador").insert({"nick": jugador_2}).execute()
        except:
            st.error(f"Error al registrar jugador 2: {jugador_2}")

    try:
        id_jugador_1 = supabd.table("jugador").select("id").eq("nick", jugador_1).execute().data[0]["id"]    
    except:
        st.error(f"Error al obtener ID del jugador 1: {jugador_1}")
    id_jugador_2 = None
    if jugador_2 != "Sin Duo":
        try:
            id_jugador_2 = supabd.table("jugador").select("id").eq("nick", jugador_2).execute().data[0]["id"]
        except:
            st.error(f"Error al obtener ID del jugador 2: {jugador_2}")

    try:
        supabd.table("equipo").insert({"jugador_1": id_jugador_1, "jugador_2": id_jugador_2}).execute()
    except:
        st.error(f"Error al registrar equipo: {jugador_1} y {jugador_2}")

    st.toast(f"Equipo registrado: {jugador_1} y {jugador_2}", icon="✅")


if st.session_state.logged_in == False:
    st.title("🔒 PANEL DE CONTROL - ADMINISTRADOR")
    password = st.text_input("Ingresa clave de Moderador", type="password")
    if password == st.secrets["ADMIN_PASSWORD"]:
        st.session_state.logged_in = True
        st.success("¡Acceso concedido! Redirigiendo...")
        st.rerun()
    else:
        st.warning("Acceso restringido a moderadores.")
else:
    st.title("🔧 PANEL DE CONTROL - ADMINISTRADOR")
    st.markdown("""
        Bienvenido al panel de control del torneo. Aquí puedes gestionar equipos, rondas y reportes.
        Usa el menú lateral para navegar entre las diferentes secciones de administración.
    """)
    st.markdown("""
        <style>
        /* Aquí puedes agregar estilos personalizados para el panel de administración */
         .stButton button {
            background-color: #007bff;
            color: white;
            border-radius: 5px;
            padding: 0.5em 1em;
            font-size: 1rem;
            border: none;
        }
        .stButton button:hover {
            background-color: #0056b3;
        }
        </style>
    """, unsafe_allow_html=True)

    # Formulario para registrar equipos
    jugador_1 =st.text_input("Ingrese Nick del Jugador 1")
    jugador_2 = st.text_input("Ingrese Nick del Jugador 2")
    st.button("Registrar Equipo", on_click=registrar_equipo, args=(jugador_1, jugador_2), use_container_width=True, type="primary")



