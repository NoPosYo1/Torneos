import time
from streamlit_autorefresh import st_autorefresh
import streamlit as st
import random
from supabase import create_client
import re

supabd = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

st.set_page_config(page_title="Torneo 2v2 GGReport - Admin", layout="wide", initial_sidebar_state="collapsed")

st.session_state.logged_in = st.session_state.get('logged_in', False)
st.markdown(f"""
    <style>
    [data-testid="stSidebar"] {{
        background-image: url("https://images6.alphacoders.com/909/909375.jpg");
        background-size: cover !important;
        background-position: center !important;
        background-repeat: no-repeat !important;
    }}
    /* Esto hace que los widgets encima del fondo sean legibles */
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] .stButton {{
        background-color: rgba(0, 0, 0, 0.4) !important; /* Fondo semi-transparente para botones */
        border-radius: 10px !important;
        border-bottom: 2px solid #785a28 !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.5) !important;
    }}
    </style>
""", unsafe_allow_html=True
)




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
                "jugador_2": id_j2
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

def avanzar_equipo_completo(supabd, id_equipo_ganador, ronda_actual, id_duelo_actual):
    # 1. VALIDACIÓN CRÍTICA: ¿Ya se registró un ganador para este duelo?
    duelo_check = supabd.table("encuentros").select("ganador_id").eq("id", id_duelo_actual).execute()
    
    if duelo_check.data and duelo_check.data[0]['ganador_id'] is not None:
        st.warning("Este duelo ya tiene un ganador registrado.")
        return

    # 2. Registrar el ganador en el duelo actual para "bloquearlo"
    supabd.table("encuentros").update({"ganador_id": id_equipo_ganador}).eq("id", id_duelo_actual).execute()

    # --- El resto de la lógica de avance sigue igual ---
    orden_rondas = ["Ronda 1", "Ronda 2", "Ronda 3", "Ronda 4", "Ronda 5", "Semifinal", "Final"]
    try:
        idx = orden_rondas.index(ronda_actual)
        proxima = orden_rondas[idx + 1]
    except (ValueError, IndexError):
        return

    # 3. Buscar hueco en la próxima ronda
    partido_pendiente = supabd.table("encuentros")\
        .select("id")\
        .eq("ronda", proxima)\
        .is_("equipo_2", "null")\
        .execute()

    if partido_pendiente.data:
        id_partido_next = partido_pendiente.data[0]['id']
        supabd.table("encuentros").update({"equipo_2": id_equipo_ganador}).eq("id", id_partido_next).execute()
    else:
        supabd.table("encuentros").insert({
            "ronda": proxima,
            "equipo_1": id_equipo_ganador,
            "equipo_2": None
        }).execute()
    
    st.toast("Progreso guardado correctamente")

def generar_ronda_1_automatica(supabd):
    # 1. Traer todos los equipos activos
    res = supabd.table("equipo").select("id").execute()
    for equipo in res.data:
        supabd.table("equipo").update({"estado": "En Espera"}).eq("id", equipo['id']).execute()
    equipos = [e['id'] for e in res.data]
    supabd.table("encuentros").delete().neq("id", 0).execute()  # Limpiar rondas anteriores antes de generar la nueva
    st.toast("Generando Ronda 1... Esto puede tardar unos segundos.", icon="⚔️")
    time.sleep(5)  # Pequeña pausa para asegurar que los estados se actualicen antes de generar la ronda

    if not equipos:
        st.error("No hay equipos activos para emparejar.")
        return

    # 2. Mezclar aleatoriamente (Sorteo)
    random.shuffle(equipos)

    # 3. Emparejar de a dos
    duelos_a_insertar = []
    for i in range(0, len(equipos), 2):
        equipo_1 = equipos[i]
        # Si el número es impar, el último equipo queda solo (jugador_2 = None)
        equipo_2 = equipos[i+1] if (i + 1) < len(equipos) else None

        duelos_a_insertar.append({
            "ronda": "Ronda 1",
            "equipo_1": equipo_1,
            "equipo_2": equipo_2,
            "formato": "eliminacion_directa"
        })

    # 4. Insertar en la BD
    try:
        supabd.table("encuentros").insert(duelos_a_insertar).execute()
        st.success(f"✅ Ronda 1 generada con {len(duelos_a_insertar)} enfrentamientos.")
    except Exception as e:
        st.error(f"Error al generar ronda: {e}")

def resetear_torneo_completo(supabd):
    try:
        # 1. Eliminar todos los enfrentamientos (Brackets)
        # Usamos un filtro que siempre sea cierto para borrar todo
        supabd.table("encuentros").delete().neq("id", 0).execute()
        
        # 2. Resetear estados en la tabla Equipo
        # Ponemos ganador_id en NULL y el estado en 'activo'
        supabd.table("equipo").update({
            "estado": "activo" 
        }).neq("id", 0).execute()

        # 3. Opcional: Si quieres disolver los dúos también
        # supabd.table("jugador").update({"EnDuo": False}).neq("id", 0).execute()
        # supabd.table("equipo").delete().neq("id", 0).execute()

        st.success("✅ Torneo reseteado. Brackets eliminados y equipos reactivados.")
    except Exception as e:
        st.error(f"Error al resetear: {e}")

def cambiar_estado_equipo(id_equipo, nuevo_estado):
    try:
        supabd.table("equipo").update({"estado": nuevo_estado}).eq("id", id_equipo).execute()
        st.toast(f"Estado del equipo actualizado a '{nuevo_estado}'", icon="🔄")
    except Exception as e:
        st.error(f"Error al actualizar estado: {e}")

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


    st.sidebar.title("Reglas del Torneo")
    
    st.sidebar.title("Menú de Administración")
    if st.sidebar.button("🏠 IR A PANEL PRINCIPAL", key="btn_principal"):
        cambiar_vista('principal')
    if st.sidebar.button("⚔️ IR A GESTIÓN DE EQUIPOS", key="btn_gestion_equipos"):
        cambiar_vista('reg_equipo')
    if st.sidebar.button("✏️ IR A EDICIÓN DE EQUIPOS", key="btn_edicion_equipos"):
        cambiar_vista('editar_equipo')
    if st.sidebar.button("📊 IR A RONDAS Y RESULTADOS", key="btn_rondas_resultados"):
        cambiar_vista('rondas_resultados')

    st.sidebar.markdown(
        f'<img src="https://media1.tenor.com/m/PYORpU4s_zAAAAAd/zoe-laugh.gif">',
        unsafe_allow_html=True,
    )

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
            .stApp {
                background-color: #010a13;
                color: #f0e6d2;
            }
            
            </style>
        """, unsafe_allow_html=True)
#---------------------------------------------------------------------------------------------+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def panel_registro_equipo():
        st.title("Gestión de Equipos")
        st.markdown("""
            Bienvenido al panel de control del torneo. -- Aquí puedes añadir Jugadores en solitario y a equipos de 2 jugadores.
        """)
        


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
           .stApp {
               background-color: #010a13;
               color: #f0e6d2;
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
            st.write(f"Actualmente hay {len(jugadores_libres)} jugadores solitarios disponibles para asignar como dúo.")

            return
        
        st.write(f"Actualmente hay {len(jugadores_libres)} jugadores solitarios disponibles para asignar como dúo.")

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
                            # FORMA CORRECTA
                            supabd.table("equipo").insert({"jugador_1": player['id'],"jugador_2": id_j2}).execute()
                            supabd.table("jugador").update({"EnDuo": True}).eq("id", player['id']).execute()
                            supabd.table("jugador").update({"EnDuo": True}).eq("id", id_j2).execute()
                            st.toast(f"¡Dúo {player['nick']} & {nuevo_j2_nick} creado!", icon="⚔️")
                            st.rerun()

    def panel_rondas():
        st.title("🏆 Panel de Control de Brackets")
        if st.sidebar.button("🚀 Generar Sorteo Ronda 1"):
            generar_ronda_1_automatica(supabd)
        # 1. Espacio para el temporizador en la parte superior
        if st.session_state.vista == 'rondas_resultados':
            st_autorefresh(interval=600000, key="refresh_rondas")
                
        timer_placeholder = st.empty()

        if "last_refresh" not in st.session_state:
            st.session_state.last_refresh = time.time()

        tiempo_transcurrido = time.time() - st.session_state.last_refresh

        # Si ya pasamos el tiempo, forzamos el refresh ANTES de intentar dibujar nada
        if tiempo_transcurrido >= 20:
            st.session_state.last_refresh = time.time()
            st.rerun()

        # Solo si no hemos llegado a 20, dibujamos
        tiempo_restante = max(0, 20 - int(tiempo_transcurrido))
        with timer_placeholder.container():
            if tiempo_restante == 10 or tiempo_restante == 20:
                st.toast(f"Quedan {tiempo_restante} para reiniciar la pagina")
        

        if st.button("🔄 Actualizar Ahora"):
            st.rerun()
        
        ronda_actual = st.select_slider(
            "Visualizar Fase:",
            options=["Ronda 1", "Ronda 2", "Ronda 3", "Ronda 4", "Ronda 5","Ronda 6","Ronda 7", "Semifinal", "Final"]
        )

        with st.sidebar.expander("⚠️ ZONA DE PELIGRO - GESTIÓN CRÍTICA"):
            st.warning("Al resetear se borrarán todos los avances de las rondas. Los equipos y jugadores permanecerán registrados.")
            
            confirmacion = st.checkbox("Confirmo que deseo borrar todos los resultados.")
            
            if st.button("🚨 RESETEAR RONDAS Y VOLVER A R1", disabled=not confirmacion, type="primary"):
                resetear_torneo_completo(supabd)
                st.rerun()
        # 2. Consulta con Doble Join para traer nicks de los 4 posibles jugadores
        res = supabd.table("encuentros").select("""
            id,
            ronda,
            ganador_id,
            equipo_1 (
                id,
                j1:jugador_1(nick),
                j2:jugador_2(nick),
                estado
            ),
            equipo_2 (
                id,
                j1:jugador_1(nick),
                j2:jugador_2(nick),
                estado
            )
        """).eq("ronda", ronda_actual).execute()

        if not res.data:
            st.info(f"No hay encuentros generados para {ronda_actual}")
            return

        st.divider()

        # 3. Listado de Duelos
        # 3. Listado de Duelos
        for enc in res.data:
            ya_tiene_ganador = enc.get('ganador_id') is not None
            
            with st.container(border=True):
                # Usamos columnas con anchos proporcionales
                col_e1, col_vs, col_e2 = st.columns([10, 2, 10]) 
                e1 = enc.get('equipo_1')
                e2 = enc.get('equipo_2')
                # --- COLUMNA 1: EQUIPO 1 ---
                with col_e1:
                    
                    estado_e1 = supabd.table("equipo").select("estado").eq("id", e1['id']).execute().data[0]['estado'] if e1 else "desconocido"
                    if e1:
                        nick_j1 = e1.get('j1', {}).get('nick', '???')
                        nick_j2 = e1.get('j2', {}).get('nick', 'Solo')
                        st.code(f"{nick_j1}", language="None")
                        st.code(f"{nick_j2}", language="None")
                        if estado_e1 == "Eliminado" or (enc['ganador_id'] != e1['id'] and ya_tiene_ganador):
                            st.markdown(f"<div style='color: red; font-weight: bold;'>ELIMINADO</div>", unsafe_allow_html=True)
                            st.button("Reinscribir Equipo", key=f"reinscribir_e1_{enc['id']}", use_container_width=True)
                        else:        
                            c1, c2, c3 = st.columns(3)
                            with c1:
                                if st.button(f"Ganador E1", key=f"win_e1_{enc['id']}", disabled=ya_tiene_ganador, use_container_width=True):
                                    avanzar_equipo_completo(supabd, e1['id'], ronda_actual, enc['id'])
                                    st.rerun()
                            with c2:                                                        
                                if st.button("Equipo Ausente", key=f"ausente_e1_{enc['id']}", disabled=ya_tiene_ganador, use_container_width=True):
                                    cambiar_estado_equipo(e1['id'], "Ausente")
                                    st.rerun()
                            with c3:
                                if st.button("Eliminado", key=f"eliminado_e1_{enc['id']}", disabled=ya_tiene_ganador, use_container_width=True):
                                    cambiar_estado_equipo(e1['id'],"Eliminado")
                                    st.rerun()
                                if ya_tiene_ganador:
                                    st.markdown(f"<div style='color: green; font-weight: bold;'>GANADOR</div>", unsafe_allow_html=True)
                            

                # --- COLUMNA 2: VS (SIEMPRE VISIBLE) ---
                with col_vs:
                    st.markdown("""""", unsafe_allow_html=True)  # Espaciador para centrar el VS
                    st.markdown("""
                        <style>
                        /* Estilo para botones primarios (Dorado Hextech) */
                        .stButton > button[kind="primary"] {
                            background-color: #cdbe91 !important;
                            color: #010a13 !important;
                            border: 1px solid #785a28 !important;
                            font-weight: bold !important;
                        }
                        
                        /* Efecto hover (al pasar el mouse) */
                        .stButton > button[kind="primary"]:hover {
                            background-color: #f0e6d2 !important;
                            border-color: #c8aa6e !important;
                            box-shadow: 0px 0px 15px rgba(205, 190, 145, 0.5) !important;
                        }
                        </style>
                    """, unsafe_allow_html=True)
                    #color letra VS
                    st.markdown("""
                        <p style='
                            text-align: center; 
                            color: #cdbe91; 
                            font-weight: bold; 
                            font-size: 24px; 
                            padding-top: 10px;
                            text-shadow: 0px 0px 10px rgba(205, 190, 145, 0.5);
                        '>
                            VS
                        </p>
                    """, unsafe_allow_html=True)
# --- LÓGICA DENTRO DEL BUCLE DE ENCUENTROS ---
                    if e2:
                        # 1. Determinar el estado actual (asumiendo que e1 y e2 traen el campo 'estado')
                        # Si ambos están "En Partida", el botón debe resaltar
                        estando_en_partida = (e1.get('estado') == "En Partida" and e2.get('estado') == "En Partida")
                        
                        # 2. Elegir el tipo de botón (primary es el color de marca, suele ser azul o naranja)
                        tipo_boton = "primary" if estando_en_partida else "secondary"

                        # 3. El botón cambia de color visualmente si ya están en partida
                        if st.button("En Partida", key=f"btn_p_{enc['id']}", disabled=ya_tiene_ganador, use_container_width=True, type=tipo_boton):
                            st.toast("¡Equipos en combate!", icon="⚔️")
                            cambiar_estado_equipo(e1['id'], "En Partida")
                            cambiar_estado_equipo(e2['id'], "En Partida")
                            st.rerun()

                # --- COLUMNA 3: EQUIPO 2 ---
                with col_e2:
                    estado_e2 = supabd.table("equipo").select("estado").eq("id", e2['id']).execute().data[0]['estado'] if e2 else "desconocido"
                    if e2:
                        nick2_j1 = e2.get('j1', {}).get('nick', '???')
                        nick2_j2 = e2.get('j2', {}).get('nick', 'Solo')
                        st.code(f"{nick2_j1}", language="None")
                        st.code(f"{nick2_j2}", language="None")                        

                        if estado_e2 == "eliminado" or (enc['ganador_id'] != e2['id'] and ya_tiene_ganador):
                            st.markdown("<div style='color: red; font-weight: bold; '>ELIMINADO </div>",unsafe_allow_html=True)
                            st.button("Reinscribir Equipo", key=f"reinscribir_e2_{enc['id']}", use_container_width=True)
                        else:
                            
                            c1, c2, c3 = st.columns(3)
                            with c1:
                                if st.button(f"Ganador E2", key=f"win_e2_{enc['id']}", disabled=ya_tiene_ganador, use_container_width=True):
                                    avanzar_equipo_completo(supabd, e2['id'], ronda_actual, enc['id'])
                                    st.rerun()
                            with c2:                                                        
                                if st.button("Equipo Ausente", key=f"ausente_e2_{enc['id']}", disabled=ya_tiene_ganador, use_container_width=True):
                                    cambiar_estado_equipo(e2['id'], "Ausente")
                                    st.rerun()
                            with c3:
                                if st.button("Eliminado", key=f"eliminado_e2_{enc['id']}", disabled=ya_tiene_ganador, use_container_width=True):
                                    cambiar_estado_equipo(e2['id'], "Eliminado")
                                    st.rerun()
                            if ya_tiene_ganador:
                                st.markdown(f"<div style='color: green; font-weight: bold;'>GANADOR</div>", unsafe_allow_html=True)
                    else:
                        # Placeholder para que la columna no se colapse
                        st.markdown("<p style='color:gray; font-style:italic; padding-top:10px;'>Esperando rival...</p>", unsafe_allow_html=True)
                        st.markdown("<p style='color:gray; font-style:italic; padding-top:10px;'>Se mostraran equipos que no consiguieron rivales de la ronda actual y anteriores </p>", unsafe_allow_html=True)
                        
                        c1,c2 = st.columns(2)
                        with c1:
                            res_enc = supabd.table("encuentros").select("id, equipo_1(id,estado), equipo_2(id,estado),ronda,ganador_id").execute()
                            grupos_ocupados = set()
                            grupos_ocupados.add(e1['id'])
                            for reg in res_enc.data:
                                if reg['equipo_2']:
                                    grupos_ocupados.add(reg['equipo_2']['id'])
                                    grupos_ocupados.add(reg['equipo_1']['id'])
                            
                            res_todos_equipos = supabd.table("equipo").select("id, jugador_1(nick), jugador_2(nick)").execute()
                            equipos_libres = [e for e in res_todos_equipos.data if e['id'] not in grupos_ocupados]
                            opciones_e2 = {f"Equipo {e['id']} - {e['jugador_1']['nick']} & {e['jugador_2']['nick'] if e['jugador_2'] else 'Solo'}": e['id'] for e in equipos_libres}
                            seleccion_e2 = st.selectbox("Seleccionar Equipo 2 para este duelo", options=[None] + list(opciones_e2.keys()), key=f"select_e2_{enc['id']}")
                            if seleccion_e2:
                                id_equipo_2 = opciones_e2[seleccion_e2]
                                supabd.table("encuentros").update({"equipo_2": id_equipo_2}).eq("id", enc['id']).execute()
                                st.toast(f"Equipo 2 asignado: {seleccion_e2}", icon="✅")
                                st.rerun()
                        with c2:
                            # 1. Obtener todos los encuentros para analizar estados
                            res_enc = supabd.table("encuentros").select("""
                                id, 
                                ganador_id,
                                equipo_1(id, jugador_1(nick), jugador_2(nick), estado), 
                                equipo_2(id, jugador_1(nick), jugador_2(nick), estado),
                                ronda
                            """).execute()
                            huerfanos = {}
                            
                            for reg in res_enc.data:
                                # Si el duelo ya se cerró (tiene ganador), no nos interesa para reubicar
                                if reg['ronda'] == "Ronda 1":
                                    if reg.get('ganador_id'):
                                        continue
                                    eq1 = reg.get('equipo_1')
                                    eq2 = reg.get('equipo_2')
                                    # Caso 1: Equipo 1 está vivo pero el 2 no existe o está eliminado
                                    if (eq1 and eq1['estado'] != "Eliminado") and eq1['id'] != e1['id']:
                                        if not eq2 or eq2['estado'] == "Eliminado":
                                            n1 = eq1['jugador_1']['nick'] if eq1['jugador_1'] else "???"
                                            n2 = eq1['jugador_2']['nick'] if eq1['jugador_2'] else "Solo"
                                            label = f"{n1} & {n2}"
                                            huerfanos[label] = eq1['id']

                                    # Caso 2: Equipo 2 está vivo pero el 1 está eliminado
                                    if (eq2 and eq2['estado'] != "Eliminado") and eq2['id'] != e1['id']:
                                        if eq1 and eq1['estado'] == "Eliminado" :
                                            n1 = eq2['jugador_1']['nick'] if eq2['jugador_1'] else "???"
                                            n2 = eq2['jugador_2']['nick'] if eq2['jugador_2'] else "Solo"
                                            label = f"{n1} & {n2}"
                                            huerfanos[label] = eq2['id']

                            # 2. Mostrar el Selectbox
                            seleccion_huerfano = st.selectbox(
                                "Asignar equipo huérfano como rival",
                                options=[None] + list(huerfanos.keys()),
                                key=f"reubicar_{enc['id']}" # 'enc' es el duelo vacío donde lo quieres meter
                            )

                            if seleccion_huerfano:
                                id_reubicado = huerfanos[seleccion_huerfano]
                                # Actualizamos el duelo vacío con este equipo
                                supabd.table("encuentros").update({"equipo_2": id_reubicado}).eq("id", enc['id']).execute()
                                st.toast("Equipo reubicado correctamente", icon="🔄")
                                st.rerun()
        

    # --- LÓGICA PRINCIPAL (EL SELECTOR) ---
    if st.session_state.vista == 'reg_equipo':
        panel_registro_equipo()
    elif st.session_state.vista == 'principal':
        panel_control_admin()
    elif st.session_state.vista == 'editar_equipo':
        panel_editar_equipo()
    elif st.session_state.vista == 'rondas_resultados':
        panel_rondas()
    