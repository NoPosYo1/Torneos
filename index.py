import streamlit as st
from supabase import create_client

# 1. Conexión con Secretos
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="Admin Torneo", layout="wide")

st.title("🏆 Gestión de Torneo: Fase de Grupos")

# --- LÓGICA DE BASE DE DATOS ---
def obtener_equipos_ronda(ronda, grupo):
    # Trae equipos y sus datos unidos (Join)
    res = supabase.table("estructura_torneo") \
        .select("id, equipo_id, ronda, grupo, equipos(nombre_jugador_1, nombre_jugador_2, estado)") \
        .eq("ronda", ronda) \
        .eq("grupo", grupo) \
        .execute()
    return res.data

def actualizar_estado(equipo_id, nuevo_estado):
    supabase.table("equipos").update({"estado": nuevo_estado}).eq("id", equipo_id).execute()
    st.rerun()

def clasificar(equipo_id, ronda_actual, grupo_destino):
    # Insertar en la siguiente ronda
    supabase.table("estructura_torneo").insert({
        "equipo_id": equipo_id,
        "ronda": ronda_actual + 1,
        "grupo": grupo_destino
    }).execute()
    st.success("¡Clasificado!")

# --- INTERFAZ ---
col_izq, col_der = st.columns([1, 3])

with col_izq:
    st.subheader("Filtros de Vista")
    ronda_sel = st.selectbox("Ronda", [1, 2, 3, 4], index=0)
    grupo_sel = st.selectbox("Grupo", ["A", "B", "C", "D", "E", "F"], index=0)

with col_der:
    st.subheader(f"Participantes - Ronda {ronda_sel} | Grupo {grupo_sel}")
    
    equipos = obtener_equipos_ronda(ronda_sel, grupo_sel)
    
    if not equipos:
        st.info("No hay participantes en esta sección aún.")
    else:
        for item in equipos:
            e = item['equipos']
            e_id = item['equipo_id']
            
            # Estilo basado en el estado (como tu Excel)
            color = "#2ecc71" if e['estado'] == 'activo' else "#e74c3c"
            
            with st.container(border=True):
                c1, c2, c3, c4 = st.columns([3, 3, 2, 2])
                
                c1.markdown(f"**Nick:** {e['nombre_jugador_1']}")
                c2.markdown(f"**Dúo:** {e['nombre_jugador_2']}")
                
                # Botón de Asistencia / Estado
                if e['estado'] == 'activo':
                    if c3.button("Marcar Ausente ❌", key=f"btn_aus_{item['id']}"):
                        actualizar_estado(e_id, 'eliminado')
                else:
                    if c3.button("Marcar Activo ✅", key=f"btn_act_{item['id']}"):
                        actualizar_estado(e_id, 'activo')
                
                # Botón para Clasificar a la siguiente ronda
                if c4.button("Clasificar ➡️", key=f"btn_cla_{item['id']}"):
                    # Ejemplo: De Ronda 1 Grupo A pasan a Ronda 2 Grupo "A-B"
                    clasificar(e_id, ronda_sel, "A-B")