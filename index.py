import streamlit as st
from supabase import create_client

# Conexión
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

def actualizar_estado(equipo_id, nuevo_estado):
    supabase.table("equipos").update({"estado": nuevo_estado}).eq("id", equipo_id).execute()
    st.rerun()

st.title("🏆 Gestión de Torneo")

# Simulamos que traemos los dos equipos del VS actual
# En un caso real, filtrarías por el ID del partido
equipos_db = supabase.table("equipos").select("*").limit(2).execute().data

if len(equipos_db) < 2:
    st.warning("Faltan equipos en la base de datos.")
else:
    col1, vs_col, col2 = st.columns([4, 1, 4])

    for i, col in enumerate([col1, col2]):
        eq = equipos_db[i]
        with col:
            st.subheader(eq["nombre_equipo"])
            # El rectángulo del equipo (diseño de tu dibujo)
            st.info(f"👤 {eq['jugador_1']} - 👤 {eq['jugador_2']}")
            
            # Lógica de botones según estado
            if eq["estado"] == "activo":
                btn_col1, btn_col2, btn_col3 = st.columns(3)
                with btn_col1:
                    st.button("Edit", key=f"edit_{eq['id']}")
                with btn_col2:
                    # Botón LOSE: Cambia el estado a eliminado
                    if st.button("Lose", key=f"lose_{eq['id']}", type="primary"):
                        actualizar_estado(eq["id"], "eliminado")
                with btn_col3:
                    st.button("Win", key=f"win_{eq['id']}")
            
            elif eq["estado"] == "eliminado":
                # Botón REINSCRIPCIÓN: Vuelve a ponerlo activo
                if st.button("🔄 Reinscripción", key=f"re_{eq['id']}", use_container_width=True):
                    actualizar_estado(eq["id"], "activo")

    with vs_col:
        st.markdown("<h2 style='text-align: center;'>VS</h2>", unsafe_allow_html=True)