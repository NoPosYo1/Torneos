import streamlit as st
from supabase import create_client

# Conexión
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

def actualizar_estado(equipo_id, nuevo_estado):
    supabase.table("equipo").update({"estado_activo": nuevo_estado}).eq("id", equipo_id).execute()
    st.rerun()

st.title("🏆 Gestión de Torneo")

 
equipos_db = supabase.table("equipo").select("*").execute().data

if equipos_db:
    col1, vs_col, col2 = st.columns([4, 1, 4])

    for i, col in enumerate([col1, col2]):
        eq = equipos_db[i]
        with col:
            st.subheader(f"Equipo {eq['id']}")
            # El rectángulo del equipo (diseño de tu dibujo)
            st.info(f"👤 {eq['jugador_1']} - 👤 {eq['jugador_2']}")
                
                # Lógica de botones según estado
            if eq["estado_activo"] == True: # Activo
                btn_col1, btn_col2, btn_col3 = st.columns(3)
                with btn_col1:
                    st.button("Edit", key=f"edit_{eq['id']}")
                with btn_col2:
                    # Botón LOSE: Cambia el estado a eliminado
                    if st.button("Lose", key=f"lose_{eq['id']}", type="primary"):
                        actualizar_estado(eq["id"], "False")
                with btn_col3:
                    st.button("Win", key=f"win_{eq['id']}")
            
            elif eq["estado_activo"] == "False": # Eliminado
                st.error("Eliminado")
                # Botón REINSCRIPCIÓN: Vuelve a ponerlo activo
                if st.button("🔄 Reinscripción", key=f"re_{eq['id']}", use_container_width=True):
                    actualizar_estado(eq["id"], "True")

    with vs_col:
        st.markdown("<h2 style='text-align: center;'>VS</h2>", unsafe_allow_html=True)