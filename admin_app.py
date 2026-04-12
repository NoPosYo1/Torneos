import streamlit as st
from supabase import create_client
import re

supabd = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

st.set_page_config(page_title="Torneo 2v2 GGReport - Admin", layout="wide", initial_sidebar_state="collapsed")

st.session_state.logged_in = st.session_state.get('logged_in', False)

def cambiar_vista(nueva_vista):
    st.session_state.vista = nueva_vista
    st.rerun()

def sanitizar_input(texto):
    if not texto:
        return ""
    # 1. Eliminar caracteres de control Unicode (como los BiDi que vimos)
    # \u200b-\u200f y \u202a-\u202e son los más comunes que dan problemas
    texto_limpio = re.sub(r'[\u200e\u200f\u202a-\u202e\u2066-\u2069]', '', texto)
    
    # 2. Quitar espacios extra al inicio y final
    return texto_limpio.strip()

def registrar_equipo(jugador1, jugador2):
    # 1. Limpieza inicial
    j1_limpio = sanitizar_input(jugador1)
    j2_limpio = sanitizar_input(jugador2)

    if not j1_limpio:
        st.error("Error: El Jugador 1 es obligatorio.")
        return

    try:
        # 2. Registrar Jugador 1 y capturar su ID inmediatamente
        # El .data[0] accede directamente a la fila recién creada
        try:
            res_j1 = supabd.table("jugador").insert({"nick": j1_limpio}).execute()
            id_j1 = res_j1.data[0]["id"]
        except Exception as e:
            if "duplicate key" in str(e):
                st.error(f"⚠️ Error: El nick '{j1_limpio}' ya está registrado en el torneo.")
            else:                
                st.error(f"❌ Error al registrar Jugador 1: {e}")
            return

        id_j2 = None
        # 3. Registrar Jugador 2 solo si existe y es distinto al J1
        if j2_limpio and j2_limpio != "" and j2_limpio != j1_limpio:
            try:
                res_j2 = supabd.table("jugador").insert({"nick": j2_limpio}).execute()
                id_j2 = res_j2.data[0]["id"]
            except Exception as e:
                if "duplicate key" in str(e):
                    st.error(f"⚠️ Error: El nick '{j2_limpio}' ya está registrado en el torneo.")
                else:
                    st.error(f"❌ Error al registrar Jugador 2: {e}")
                return

        # 4. Crear el equipo usando los IDs obtenidos arriba
        try:
            res_equipo = supabd.table("equipo").insert({
                "jugador_1": id_j1, 
                "jugador_2": id_j2,
                "estado": "activo" # Siempre inicializar con un estado
            }).execute()
            id_equipo = res_equipo.data[0]["id"]
        except Exception as e:
            st.error(f"❌ Error al crear el equipo: {e}")
            return

        st.toast(f"✅ Equipo registrado: {id_equipo}", icon="🔥")
        st.rerun()

    except Exception as e:
        # Capturamos el error específico de Supabase (ej: Nick duplicado)
        error_msg = str(e)
        if "duplicate key" in error_msg:
            st.error(f"⚠️ Error: Uno de los nicks ya está registrado en el torneo.")
        else:
            st.error(f"❌ Error en la base de datos: {error_msg}")

if st.session_state.logged_in == False:
    st.title("🔒 PANEL DE CONTROL - ADMINISTRADOR")
    password = st.text_input("Ingresa clave de Moderador", type="password")
    if password == st.secrets["ADMIN_PASSWORD"]:
        st.session_state.logged_in = True
        st.success("¡Acceso concedido! Redirigiendo...")
        st.rerun()
    else:
        st.warning("Acceso restringido a moderadores.")
else:
    if 'vista' not in st.session_state:
        st.session_state.vista = 'principal'

    st.sidebar.title("Menú de Administración")
    if st.sidebar.button("🏠 IR A PANEL PRINCIPAL"):
        cambiar_vista('principal')
    if st.sidebar.button("⚔️ IR A GESTIÓN DE EQUIPOS"):
        cambiar_vista('reg_equipo')
    if st.sidebar.button("✏️ IR A EDICIÓN DE EQUIPOS"):
        cambiar_vista('editar_equipo')


    def panel_control_admin():
        st.title("🔧 PANEL DE CONTROL - ADMINISTRADOR")
        st.markdown("""
            Bienvenido al panel de control del torneo. Aquí puedes gestionar equipos, rondas y reportes.
            Usa el menú lateral para navegar entre las diferentes secciones de administración.
        """)
        st.markdown("""
            <style>
            /* Aquí puedes agregar estilos personalizados para el panel de administración */
            .stButton button {
                background-color: #007bff;
                color: white;
                border-radius: 5px;
                padding: 0.5em 1em;
                font-size: 1rem;
                border: none;
            }
            .stButton button:hover {
                background-color: #0056b3;
            }
            </style>
        """, unsafe_allow_html=True)

    def panel_registro_equipo():
        st.title("Gestión de Equipos")
        st.markdown("""
            Bienvenido al panel de control del torneo. Aquí puedes gestionar equipos, rondas y reportes.
            Usa el menú lateral para navegar entre las diferentes secciones de administración.
        """)
        st.markdown("""
            <style>
            /* Aquí puedes agregar estilos personalizados para el panel de administración */
            .stButton button {
                background-color: #007bff;
                color: white;
                border-radius: 5px;
                padding: 0.5em 1em;
                font-size: 1rem;
                border: none;
            }
            .stButton button:hover {
                background-color: #0056b3;
            }
            </style>
        """, unsafe_allow_html=True)
        # Formulario para registrar equipos
        jugador_1 =st.text_input("Ingrese Nick del Jugador 1")
        jugador_2 = st.text_input("Ingrese Nick del Jugador 2")
        st.button("Registrar Equipo", on_click=registrar_equipo, args=(jugador_1, jugador_2), use_container_width=True, type="primary")

    def panel_editar_equipo():

        st.title("Editar Equipos Registrados")
        st.markdown("""
            Aquí podrás editar los detalles de un equipo registrado. Selecciona el equipo que deseas modificar y actualiza la información.
        """)
        st.markdown("""
            <style>
            /* Aquí puedes agregar estilos personalizados para el panel de administración */
            .stButton button {
                background-color: #007bff;
                color: white;
                border-radius: 5px;
                padding: 0.5em 1em;
                font-size: 1rem;
                border: none;
            }
            .stButton button:hover {
                background-color: #0056b3;
            }
            </style>
        """, unsafe_allow_html=True)

        # 1. Traemos los datos de Supabase
        # Traemos el ID del equipo y los nicks de ambos jugadores
        res = supabd.table("equipo").select("""
            id,
            jugador_1 ( nick ),
            jugador_2 ( nick )
        """).execute()

        equipos = res.data# Esto es una lista de diccionarios
        if equipos:

            opciones = {
                f"{e['id']} - {e['jugador_1']['nick']} & {e['jugador_2']['nick'] if e['jugador_2'] else 'Sin Duo -----!!!'}": e['id'] 
                for e in equipos
            }

            seleccion = st.selectbox(
                "Seleccione un equipo para gestionar:",
                options=list(opciones.keys()),
                index=None,
                placeholder="Elija un equipo..."
            )

            if seleccion:
                id_seleccionado = opciones[seleccion]
                st.write(f"Has seleccionado el ID: {id_seleccionado}")
                # Aquí podrías cargar la función para editar ese equipo específico
                # editar_equipo(id_seleccionado)
                st.divider()
                st.info("Funcionalidad de edición aún en desarrollo. Pronto podrás modificar los detalles del equipo seleccionado.")

                st.info("Grupos incompletos:")

                res_equipos = supabd.table("equipo").select("id,jugador_1(nick)", "jugador_2(nick)").is_("jugador_2","null").order("id", desc=True).execute()
                
                res_jugadores = supabd.table("equipo").select("jugador_1,jugador_1(nick)", "jugador_2").is_("jugador_2","null").order("jugador_1", desc=True).execute()

                dict_jugadores = {j['jugador_1']['nick']: j['id'] for j in res_jugadores.data}

                st.subheader("Equipos sin Dúo Asignado")
                
                for eq in res_equipos.data:
                    st.markdown(f"""
                        <div style="
                            background-color: #091428; 
                            border: 1px solid #785a28; 
                            padding: 10px; 
                            border-radius: 5px;
                            color: #cdbe91;
                            font-weight: bold;
                            text-align: center;">
                            🛡️ {eq['jugador_1']['nick']} - Sin Duo
                        </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns([2, 3])

                    with col1:
                        st.markdown(f"""
                            <div style="
                                background-color: #091428; 
                                border: 1px solid #785a28; 
                                padding: 10px; 
                                border-radius: 5px;
                                color: #cdbe91;
                                font-weight: bold;
                                text-align: center;">
                                🛡️ {eq['jugador_1']['nick']}
                            </div>
                        """, unsafe_allow_html=True)

                    with col2:
                        nuevo_j2 = st.selectbox(
                            f"Asignar pareja a {eq['jugador_1']['nick']}",
                            options=[None] + list(dict_jugadores.keys()),
                            key=f"sel_{eq['id']}", # Key única obligatoria en bucles
                            label_visibility="collapsed" # Escondemos el texto para que quede alineado al div
                        )
                        
                        if nuevo_j2:
                            if st.button(f"Confirmar Dúo", key=f"btn_{eq['id']}"):
                                id_j2 = dict_jugadores[nuevo_j2]
                                supabd.table("equipo").update({"jugador_2": id_j2}).eq("id", eq['id']).execute()
                                st.success(f"¡Dúo formado!")
                                st.rerun()
                        
        else:
            st.warning("No hay equipos registrados aún.")

    # --- LÓGICA PRINCIPAL (EL SELECTOR) ---
    if st.session_state.vista == 'reg_equipo':
        panel_registro_equipo()
    elif st.session_state.vista == 'principal':
        panel_control_admin()
    elif st.session_state.vista == 'editar_equipo':
        panel_editar_equipo()
    