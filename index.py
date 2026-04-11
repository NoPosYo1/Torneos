import streamlit as st
from supabase import create_client

# Conexión
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

st.title("🏆 Gestión de Torneo")
st.subheader("Lista de Equipos")

st.button("Actualizar Lista", on_click=st.rerun)  # Botón para actualizar la lista de equipos

# Fíjate bien en los paréntesis y los nombres
res = supabase.table("equipo").select("""
    id,
    estado,
    jugador1:jugador_1 (
        nick,
        estado
    ),
    jugador2:jugador_2 (
        nick,
        estado
    )
""").execute()

equipos_db = res.data

if len(equipos_db) > 0:
    for equipo in equipos_db:
        # Extraemos los datos de forma segura
        j1 = equipo.get('jugador1')
        j2 = equipo.get('jugador2')
        estado_eq = equipo.get('estado', 'N/A')

        # Procesamos Jugador 1
        nick1 = j1.get('nick', 'Sin nombre') if isinstance(j1, dict) else "Sin nombre"
        est1 = j1.get('estado', 'N/A') if isinstance(j1, dict) else "N/A"

        # Procesamos Jugador 2 (Dúo)
        if isinstance(j2, dict):
            nick2 = j2.get('nick', 'Sin Duo')
            est2 = j2.get('estado', 'N/A')
        else:
            nick2 = "Sin Duo"
            est2 = "N/A"

        # --- DISEÑO DE LA INTERFAZ ---
        st.subheader(f"Equipo {equipo['id']} - Estado: {estado_eq}")
        
        # Fila de Nicks
        st.info(f"👤 {nick1} -- 👤 {nick2}")
        
        # Fila de Estados de los jugadores
        # Solo mostramos el segundo estado si hay un segundo jugador
        if nick2 != "Sin Duo":
            st.caption(f"Estado J1: {est1} | Estado J2: {est2}")
        else:
            st.caption(f"Estado J1: {est1} | Esperando integrante...")
        
        st.divider() # Línea para separar equipos