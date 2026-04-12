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
    if not j2_limpio:
        st.error("Error: El Jugador 2 es obligatorio.")
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
        try:
            supabd.table("jugador").update({"EnDuo": True}).eq("id", id_j1).execute()
            supabd.table("jugador").update({"EnDuo": True}).eq("id", id_j2).execute()
        except Exception as e:
            st.error(f"❌ Error al crear el equipo: {e}")
            return
        st.toast(f"✅ Equipo registrado: {id_equipo}", icon="🔥")

    except Exception as e:
        # Capturamos el error específico de Supabase (ej: Nick duplicado)
        error_msg = str(e)
        if "duplicate key" in error_msg:
            st.error(f"⚠️ Error: Uno de los nicks ya está registrado en el torneo.")
        else:
            st.error(f"❌ Error en la base de datos: {error_msg}")

def registrar_player_solitario(jugador1):
    
    j1_limpio = sanitizar_input(jugador1)

    if not j1_limpio:
        st.error("Error: El Jugador 1 es obligatorio.")
        return

    try:

        try:
            supabd.table("jugador").insert({"nick": j1_limpio}).execute()
        except Exception as e:
            if "duplicate key" in str(e):
                st.toast(f"⚠️ Error: El nick '{j1_limpio}' ya está registrado en el torneo.")
            else:                
                st.error(f"❌ Error al registrar Jugador 1: {e}")
            return
    except Exception as e:
        # Capturamos el error específico de Supabase (ej: Nick duplicado)
        error_msg = str(e)
        if "duplicate key" in error_msg:
            st.error(f"⚠️ Error: El nick '{j1_limpio}' ya está registrado en el torneo.")
        else:
            st.error(f"❌ Error en la base de datos: {error_msg}")
        return
    st.toast(f"✅ Jugador registrado: {j1_limpio}", icon="🔥")
    
def llamada_db_duos():
    res_equipos_sin_duo = supabd.table("equipo").select("id, jugador_1(nick)").is_("jugador_2", None).execute()
    res_ocupados = supabd.table("equipo").select("jugador_1, jugador_2").execute()


if st.session_state.logged_in == False:
    st.title("🔒 PANEL DE CONTROL - ADMINISTRADOR")
    password = st.text_input("Ingresa clave de Moderador", type="password")
    if password == supabd.table("passw").select("password").execute().data[0]["password"]:
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
    if st.sidebar.button("📊 IR A RONDAS Y RESULTADOS"):
        cambiar_vista('rondas_resultados')

# --- FUNCIONES DE CADA PANEL ---
#---------------------------------------------------------------------------------------------+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
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
#---------------------------------------------------------------------------------------------+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def panel_registro_equipo():
        st.title("Gestión de Equipos")
        st.markdown("""
            Bienvenido al panel de control del torneo. -- Aquí puedes añadir Jugadores en solitario y a equipos de 2 jugadores.
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
        
        st.subheader("Registrar Equipo")
        st.text("Aquí puedes registrar un nuevo equipo (2 jugadores no registrados anteriormente) para el torneo. Ingresa los nicks de ambos jugadores.")
        st.info("Si deseas unir a 2 jugadores solitarios en un equipo, ve a la sección de Edición de Equipos y asigna un dúo a cada uno.")
        jugador_1 =st.text_input("Ingrese Nick del Jugador 1")
        jugador_2 = st.text_input("Ingrese Nick del Jugador 2")
        st.button("Registrar Equipo", on_click=registrar_equipo, args=(jugador_1, jugador_2), use_container_width=True, type="primary")

        st.divider()

        st.subheader("Agregar Player en Solitario")
        st.text("Si un jugador no tiene dúo, puedes registrarlo aquí como solitario. Luego podrás asignarle un dúo desde el panel de edición.")
        jugador_1 = st.text_input("Ingrese Nick del Jugador Solitario")
        st.button("Registrar Jugador Solitario", on_click=registrar_player_solitario, args=(jugador_1,), use_container_width=True, type="primary")

        st.info("Si quieres unir a 2 players solitarios en un equipo, vaya a la seccion de Edicion de Equipos y asignale un dúo a cada uno.")
#---------------------------------------------------------------------------------------------+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
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
        
        st.subheader("🛠️ Asignación de Dúos")
        
        res_ocupados = supabd.table("jugador").select("id, nick, EnDuo").is_("EnDuo", True).execute()
        players_ocupados = set()

        for reg in res_ocupados.data:
            if reg['EnDuo'] == True:
                players_ocupados.add(reg['id'])
        res_todos = supabd.table("jugador").select("id, nick").execute()
        jugadores_libres = [j for j in res_todos.data if j['id'] not in players_ocupados]
        dict_jugadores = {j['nick']: j['id'] for j in jugadores_libres}

        if not jugadores_libres:
            st.info("No hay jugadores solitarios disponibles para asignar como dúo.")
            return

        for player in jugadores_libres:
            col1, col2 = st.columns([2, 3])
            with col1:
                st.markdown(f"""
                    <div style="background-color: #091428; border: 1px solid #785a28; 
                    padding: 10px; border-radius: 5px; color: #cdbe91; text-align: center;">
                        🛡️ {player['nick']}
                    </div>
                """, unsafe_allow_html=True)
            with col2:
                nuevo_j2_nick = st.selectbox(
                    f"Duo para {player['nick']}",
                    options=[None] + list(dict_jugadores.keys()),
                    key=f"sel_{player['id']}",
                    label_visibility="collapsed"
                )
                if nuevo_j2_nick == player['nick']:
                    st.toast("No puedes seleccionar el mismo jugador como dúo.")
                    continue
                else:

                    if nuevo_j2_nick:
                        id_j2 = dict_jugadores[nuevo_j2_nick]
                        if st.button("Confirmar", key=f"btn_{player['id']}"):
                            # UPDATE en la tabla equipo
                            supabd.table("equipo").insert({id_j2: "jugador_2", player['id']: "jugador_1", "estado": "activo"}).execute()
                            supabd.table("jugador").update({"EnDuo": True}).eq("id", player['id']).execute()
                            supabd.table("jugador").update({"EnDuo": True}).eq("id", id_j2).execute()
                            st.toast(f"¡Dúo {player['nick']} & {nuevo_j2_nick} creado!", icon="⚔️")
                            st.rerun()











    # --- LÓGICA PRINCIPAL (EL SELECTOR) ---
    if st.session_state.vista == 'reg_equipo':
        panel_registro_equipo()
    elif st.session_state.vista == 'principal':
        panel_control_admin()
    elif st.session_state.vista == 'editar_equipo':
        panel_editar_equipo()
    