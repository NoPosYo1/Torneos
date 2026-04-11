import streamlit as st
from supabase import create_client

# Conexión
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

def actualizar_estado(equipo_id, nuevo_estado):
    supabase.table("equipo").update({"estado_activo": nuevo_estado}).eq("id", equipo_id).execute()
    st.rerun()

st.title("🏆 Gestión de Torneo")

 
# Fíjate en el formato de los dos puntos
res = supabase.table("equipo").select("""
    id,
    estado_activo,
    jugador1:jugador_1(nick),
    jugador2:jugador_2(nick)
""").execute()

equipos_db = res.data

if equipos_db:
    col1, vs_col, col2 = st.columns([4, 1, 4])

    for eq in equipos_db:
        # Extraemos el dato. Si es un diccionario, sacamos el nick. 
        # Si es un número o None, ponemos 'Sin nombre'.
        j1_data = eq.get('jugador1')
        nick_1 = j1_data.get('nick') if isinstance(j1_data, dict) else "Sin nombre"
        
        j2_data = eq.get('jugador2')
        nick_2 = j2_data.get('nick') if isinstance(j2_data, dict) else "Sin nombre"

                
        with st.container(border=True):
            st.subheader(f"Equipo {eq['id']}")
            st.info(f"👤 {nick_1}  —  👤 {nick_2}")
            
            # Aquí van tus botones de Edit, Lose, Win...
            if eq["estado_activo"] == True: # Activo
                btn_col1, btn_col2, btn_col3 = st.columns(3)
                with btn_col1:
                    st.button("Pago reinscripción", key=f"pago_{eq['id']}")
                with btn_col2:
                    # Botón LOSE: Cambia el estado a eliminado
                    if st.button("Lose", key=f"lose_{eq['id']}", type="primary"):
                        actualizar_estado(eq["id"], "False")
                with btn_col3:
                    st.button("Win", key=f"win_{eq['id']}")
            
            elif eq["estado_activo"] == "False": # Eliminado
                st.error("Eliminado")
                # Botón REINSCRIPCIÓN: Vuelve a ponerlo activo
                if st.button("🔄 Reinscripción", key=f"pago_{eq['id']}", use_container_width=True):
                    actualizar_estado(eq["id"], "True")

    with vs_col:
        st.markdown("<h2 style='text-align: center;'>VS</h2>", unsafe_allow_html=True)

else:
    st.warning("No hay equipos registrados aún.")