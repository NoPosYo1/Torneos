import streamlit as st

# Password simple para entrar
password = st.text_input("Ingresa clave de Moderador", type="password")
if password == st.secrets["ADMIN_PASSWORD"]:
    st.title("🛠️ PANEL DE CONTROL")
    # ... Aquí pones el código con botones Win/Lose/Edit ...
else:
    st.warning("Acceso restringido a moderadores.")