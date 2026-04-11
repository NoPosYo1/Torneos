import streamlit as st

st.set_page_config(page_title="Torneo 2v2 GGReport - Admin", layout="wide", initial_sidebar_state="collapsed")
st.session_state.logged_in = st.session_state.get('logged_in', False)

def registrar_equipo(jugador1, jugador2):
    # Aquí iría la lógica para registrar el equipo en la base de datos
    if jugador2 == "":
        jugador2 = "Sin Duo"
    st.success(f"Equipo registrado: {jugador1} y {jugador2}",settings={"duration": 10})

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
    jugador_1 =st.text_input("Ingrese Nick del Jugador 1")
    jugador_2 = st.text_input("Ingrese Nick del Jugador 2")
    st.button("Registrar Equipo", on_click=registrar_equipo(jugador_1, jugador_2), use_container_width=True, type="primary")



