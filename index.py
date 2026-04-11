import streamlit as st
from supabase import create_client

# --- CONFIGURACIÓN Y ESTILOS (Igual que antes) ---
st.set_page_config(layout="wide")

# Inicializamos el estado de la página si no existe
if 'vista' not in st.session_state:
    st.session_state.vista = 'equipos'

# Función para cambiar de vista
def cambiar_vista(nueva_vista):
    st.session_state.vista = nueva_vista
    st.rerun()

# --- CSS HEXTECH (El que ya tenemos) ---
st.markdown("""
    <style>
    /* Tu CSS de LoL aquí... */
    </style>
""", unsafe_allow_html=True)

# --- VISTA 1: LISTA DE EQUIPOS ---
def mostrar_equipos():
    st.title("🏆 GESTIÓN DE TORNEO 2V2")
    
    # Botón para ir a rondas
    if st.button("⚔️ IR A RONDAS"):
        cambiar_vista('rondas')
    
    # Aquí va toda tu lógica de equipos_db y el bucle FOR que ya tenemos...
    st.write("Mostrando equipos...")

# --- VISTA 2: RONDAS ---
def mostrar_rondas():
    st.title("🛡️ RONDAS DEL TORNEO")
    
    # Botón para volver
    if st.button("⬅️ VOLVER A EQUIPOS"):
        cambiar_vista('equipos')
    
    # Aquí va el código que tienes en rondas.py
    st.write("Mostrando enfrentamientos de rondas...")

# --- LÓGICA PRINCIPAL (EL SELECTOR) ---
if st.session_state.vista == 'equipos':
    mostrar_equipos()
elif st.session_state.vista == 'rondas':
    mostrar_rondas()