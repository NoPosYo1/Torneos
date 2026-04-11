import streamlit as st
from supabase import create_client

# Conexión
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

def actualizar_estado(equipo_id, nuevo_estado):
    supabase.table("equipo").update({"estado_activo": nuevo_estado}).eq("id", equipo_id).execute()
    st.rerun()

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

#Lista de equipos
if len(equipos_db) < 1:
    st.warning("Faltan equipos en la base de datos.")
else:

    for eq in equipos_db:
        # Extraemos el dato. Si es un diccionario, sacamos el nick. 
        # Si es un número o None, ponemos 'Sin nombre'.
        j1_data = eq.get('jugador1')
        nick_1 = j1_data.get('nick') if isinstance(j1_data, dict) else "Sin nombre"
        
        j2_data = eq.get('jugador2')
        nick_2 = j2_data.get('nick') if isinstance(j2_data, dict) else "Sin Duo"

                
        with st.container(border=True):
            st.subheader(f"Equipo {eq['id']}")
            st.info(f"👤 {nick_1}  —  👤 {nick_2}")
            
            # Aquí van tus botones de Edit, Lose, Win...
            if eq["estado"] == True: # Activo
                st.success("Activo")
            
            elif eq["estado"] == False: # Eliminado
                st.error("Eliminado")

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