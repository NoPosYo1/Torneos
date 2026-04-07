import streamlit as st
from supabase import create_client

# Configuración de conexión (Usa tus credenciales de Supabase)
url = "https://zokmyozaqhpmtwbtljsi.supabase.co"
key = "o5Yz!u*u$CQqqT"
supabase = create_client(url, key)

st.title("🎮 Panel de Gestión de Torneo")

## --- FUNCIÓN PARA CLASIFICAR ---
def clasificar_equipo(equipo_id, ronda_actual):
    nueva_ronda = ronda_actual + 1
    # Insertamos al equipo en la siguiente ronda
    supabase.table("estructura_torneo").insert({
        "equipo_id": equipo_id,
        "ronda": nueva_ronda,
        "grupo": "A-B-C-D" # Según tu Excel, en Ronda 2 se unen los grupos
    }).execute()
    st.success(f"Equipo clasificado a Ronda {nueva_ronda}")

## --- VISTA DE GRUPOS (RONDA 1) ---
st.header("Ronda 1 - Grupo A")

# Traemos los equipos de la Ronda 1, Grupo A
query = supabase.table("estructura_torneo") \
    .select("equipo_id, equipos(nombre_jugador_1, nombre_jugador_2)") \
    .eq("ronda", 1) \
    .eq("grupo", "A") \
    .execute()

equipos_r1 = query.data

if equipos_r1:
    for item in equipos_r1:
        equipo = item['equipos']
        e_id = item['equipo_id']
        
        # Creamos una fila visual estilo tu Excel
        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 3, 1])
            col1.write(f"**Nick:** {equipo['nombre_jugador_1']}")
            col2.write(f"**Dúo:** {equipo['nombre_jugador_2']}")
            
            if col3.button("✅", key=e_id):
                clasificar_equipo(e_id, 1)
else:
    st.info("No hay equipos registrados en el Grupo A.")



    