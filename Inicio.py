import streamlit as st
import paho.mqtt.client as mqtt
import json
import time

# ================= CONFIGURACIÓN =================
st.set_page_config(
    page_title="Lector de Sensor MQTT",
    page_icon="📡",
    layout="centered"
)

# ================= SESSION STATE =================
if 'sensor_data' not in st.session_state:
    st.session_state.sensor_data = None

# ================= FUNCIÓN MQTT =================
def get_mqtt_message(broker, port, topic, client_id):
    """Función para obtener un mensaje MQTT"""
    message_received = {"received": False, "payload": None}
    
    def on_message(client, userdata, message):
        try:
            payload = json.loads(message.payload.decode())
            message_received["payload"] = payload
            message_received["received"] = True
        except:
            # Si no es JSON, guardar como texto
            message_received["payload"] = message.payload.decode()
            message_received["received"] = True
    
    try:
        client = mqtt.Client(client_id=client_id)
        client.on_message = on_message
        client.connect(broker, port, 60)
        client.subscribe(topic)
        client.loop_start()
        
        # Esperar máximo 5 segundos
        timeout = time.time() + 5
        while not message_received["received"] and time.time() < timeout:
            time.sleep(0.1)
        
        client.loop_stop()
        client.disconnect()
        
        return message_received["payload"]
    
    except Exception as e:
        return {"error": str(e)}

# ================= SIDEBAR =================
with st.sidebar:
    st.title('⚙️ Configuración')

    st.markdown("### 📡 Conexión MQTT")

    broker = st.text_input(
        'Broker MQTT',
        value='broker.mqttdashboard.com',
        help='Dirección del broker MQTT'
    )

    port = st.number_input(
        'Puerto',
        value=1883,
        min_value=1,
        max_value=65535,
        help='Puerto del broker MQTT'
    )

    topic = st.text_input(
        'Tópico',
        value='Sensor/THP2',
        help='Canal MQTT al que deseas suscribirte'
    )

    client_id = st.text_input(
        'ID del Cliente',
        value='streamlit_client',
        help='Identificador único del cliente'
    )

    st.markdown("---")

    st.markdown("### 🧪 Brokers Públicos")
    st.code(
        """broker.mqttdashboard.com
test.mosquitto.org
broker.hivemq.com"""
    )

# ================= HEADER =================
st.title('📡 Lector de Sensor MQTT')

st.image(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Internet2.jpg/960px-Internet2.jpg",
    caption="Comunicación IoT mediante MQTT",
    width=600
)

st.subheader("Monitoreo de datos enviados desde sensores IoT")

# ================= INFORMACIÓN =================
with st.expander('ℹ️ Cómo usar esta aplicación', expanded=False):
    st.markdown("""
    ### Instrucciones

    1. Configura el broker MQTT en el panel lateral
    2. Ingresa el tópico al que deseas suscribirte
    3. Presiona el botón **Obtener Datos del Sensor**
    4. Espera la recepción del mensaje MQTT

    ### Esta aplicación permite:
    - Conectarse a brokers MQTT públicos
    - Leer mensajes enviados por sensores
    - Mostrar datos JSON automáticamente
    - Visualizar métricas en tiempo real
    """)

st.divider()

# ================= BOTÓN =================
col1, col2 = st.columns([3,1])

with col1:
    get_data = st.button(
        '🔄 Obtener Datos del Sensor',
        use_container_width=True
    )

with col2:
    clear_data = st.button(
        '🧹 Limpiar',
        use_container_width=True
    )

if clear_data:
    st.session_state.sensor_data = None
    st.rerun()

# ================= OBTENER DATOS =================
if get_data:
    with st.spinner('📡 Conectando al broker MQTT...'):
        sensor_data = get_mqtt_message(
            broker,
            int(port),
            topic,
            client_id
        )

        st.session_state.sensor_data = sensor_data

# ================= RESULTADOS =================
if st.session_state.sensor_data:

    st.divider()
    st.subheader('📊 Datos Recibidos')

    data = st.session_state.sensor_data

    # ================= ERROR =================
    if isinstance(data, dict) and 'error' in data:

        st.error(f"❌ Error de conexión: {data['error']}")

    # ================= DATOS CORRECTOS =================
    else:

        st.success('✅ Datos recibidos correctamente')

        # Si llegan datos JSON
        if isinstance(data, dict):

            # Métricas visuales
            cols = st.columns(len(data))

            for i, (key, value) in enumerate(data.items()):
                with cols[i]:
                    st.metric(
                        label=key,
                        value=value
                    )

            st.markdown("### 🧾 Datos completos")

            with st.expander('Ver JSON completo'):
                st.json(data)

        # Si llegan datos tipo texto
        else:

            st.markdown("### 📝 Mensaje recibido")

            st.code(data)

# ================= FOOTER =================
st.divider()

st.caption("Aplicación MQTT desarrollada con Streamlit e IoT")
