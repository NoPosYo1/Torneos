import streamlit as st
from supabase import create_client

# Conexión
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

def actualizar_estado(equipo_id, nuevo_estado):
    supabase.table("equipo").update({"estado_activo": nuevo_estado}).eq("id", equipo_id).execute()
    st.rerun()

st.title("🏆 Gestión de Torneo")
st.subheader("Lista de Equipos")

 
# Fíjate en el formato de los dos puntos
res = supabase.table("equipo").select("""
    id,
    estado_activo,
    jugador1:jugador_1(nick),
    jugador2:jugador_2(nick)
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
            if eq["estado_activo"] == True: # Activo
                st.success("Activo")
            
            elif eq["estado_activo"] == "False": # Eliminado
                st.error("Eliminado")

if equipos_db:
    for equipo in equipos_db:
        estado_jugador1 = "Activo" if equipo.get('jugador1', {}).get('estado', 'Sin estado') is True else "Inactivo"
        estado_jugador2 = "Activo" if equipo.get('jugador2', {}).get('estado', 'Sin estado') is True else "Inactivo"
        st.write(f"""Equipo ID: {equipo['id']}. Estado: {equipo['estado_activo']}. 
                 Jugador 1: {equipo.get('jugador1', {}).get('nick', 'Sin nombre')} estado: {estado_jugador1}. 
                 Jugador 2: {equipo.get('jugador2', {}).get('nick', 'Sin Duo')} estado: {estado_jugador2}""")
        
