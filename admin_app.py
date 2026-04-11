import streamlit as st

st.set_page_config(page_title="Torneo 2v2 GGReport - Admin", layout="wide", initial_sidebar_state="collapsed")
st.session_state.logged_in = st.session_state.get('logged_in', False)

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
    st.impute("Aquí puedes agregar funcionalidades de administración como editar equipos, gestionar rondas, revisar reportes, etc.")
    st.markdown("**Nota:** Asegúrate de tener cuidado al modificar datos, ya que esto puede afectar el desarrollo del torneo.")

