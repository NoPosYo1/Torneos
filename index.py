import streamlit as st
from supabase import create_client
import re

# 1. Configuración y Estilo LoL (Hextech)
st.set_page_config(page_title="Torneo 2v2 GGReport", layout="wide")

st.markdown("""
    <style>
    /* Fondo oscuro de la Grieta */
    .stApp {
        background-color: #010a13;
        color: #f0e6d2;
    }

    /* NUEVA REGLA: Título centrado y con aire */
    h1 {
        text-align: center !important;
        padding-top: 60px !important;
        padding-bottom: 40px !important;
        color: #c8aa6e !important;
        text-transform: uppercase;
        letter-spacing: 4px;
    }
    

    /* Tarjeta de Equipo Estilo Hextech */
    .team-card {
        background: linear-gradient(180deg, #091428 0%, #0a1428 100%);
        border: 2px solid #785a28;
        border-radius: 4px;
        padding: 20px;
        margin-bottom: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.6);
    }
    
    .team-card:hover {
        border-color: #c8aa6e;
    }

    /* Texto de los Nicks */
    .nick-display {
        color: #cdbe91;
        font-size: 1.2rem;
        font-weight: bold;
        text-align: center;
        margin: 10px 0;
        text-shadow: 1px 1px 2px black;
    }

    /* Estado del equipo arriba */
    .status-badge {
        text-transform: uppercase;
        font-size: 0.7rem;
        font-weight: bold;
        letter-spacing: 1px;
        color: #c89b3c;
        text-align: center;
    }

    /* Botones personalizados */
    div.stButton > button {
        background-color: #1e2328;
        color: #cdbe91;
        border: 1px solid #785a28;
        border-radius: 0px;
        text-transform: uppercase;
        font-weight: bold;
        width: 100%;
    }

    div.stButton > button:hover {
        background-color: #32281e;
        color: #f0e6d2;
        border-color: #c8aa6e;
    }

    /* Botón LOSE (Rojo) */
    div.stButton > button[kind="primary"] {
        background-color: #4c1616;
        border-color: #8c2626;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Conexión
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

st.title("🏆 Gestión de Torneo 2v2 GGReport", anchor="center")

# 3. Consulta de datos
res = supabase.table("equipo").select("""
    id,
    estado,
    jugador1:jugador_1 (nick, estado),
    jugador2:jugador_2 (nick, estado)
""").order("id").execute()

equipos_db = res.data

# 4. Renderizado de la Interfaz
if len(equipos_db) > 0:
    # Mostramos de 2 en 2 para simular enfrentamientos (VS)
    for i in range(0, len(equipos_db), 2):
        col1, vs_text, col2 = st.columns([4, 1, 4])
        
        for idx, col_actual in enumerate([col1, col2]):
            pos = i + idx
            if pos < len(equipos_db):
                equipo = equipos_db[pos]
                
                # Extracción segura
                j1 = equipo.get('jugador1')
                j2 = equipo.get('jugador2')
                estado_eq = equipo.get('estado', 'activo')

                nick1 = j1.get('nick', 'Sin nombre') if isinstance(j1, dict) else "Sin nombre"
                nick2 = j2.get('nick', 'Sin Duo') if isinstance(j2, dict) else "Sin Duo"
                est1 = j1.get('estado', 'N/A') if isinstance(j1, dict) else "N/A"
                est2 = j2.get('estado', 'N/A') if isinstance(j2, dict) else "N/A"

                with col_actual:
                    # Contenedor visual (El "Rectángulo" de tu dibujo)
                    st.markdown(f"""
                        <div class="team-card">
                            <div class="status-badge">Equipo {equipo['id']} • {estado_eq}</div>
                            <div class="nick-display">👤 {nick1} <span style="color:#45475a;">  -- </span> 👤 {nick2}</div>
                            <div style="text-align: center; font-size: 0.7rem; color: #a09b8c;">
                                {est1} | {est2 if nick2 != 'Sin Duo' else 'ESPERANDO...'}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                    # Lógica de Botones según tu dibujo
                    if estado_eq == 'activo':
                        b1, b2, b3 = st.columns(3)
                        with b1:
                            st.button("Edit", key=f"e_{equipo['id']}")
                        with b2:
                            if st.button("Lose", key=f"l_{equipo['id']}", type="primary"):
                                supabase.table("equipo").update({"estado": "eliminado"}).eq("id", equipo['id']).execute()
                                st.rerun()
                        with b3:
                            st.button("Win", key=f"w_{equipo['id']}")
                    else:
                        # Botón de Reinscripción
                        if st.button("🔄 Reinscripción", key=f"r_{equipo['id']}", use_container_width=True):
                            supabase.table("equipo").update({"estado": "activo"}).eq("id", equipo['id']).execute()
                            st.rerun()

        with vs_text:
            st.markdown("<br><h1 style='text-align: center; color: #785a28;'>VS</h1>", unsafe_allow_html=True)
        st.divider()
else:
    st.info("No hay equipos en la base de datos.")

st.button("Actualizar Lista", on_click=st.rerun)