import paho.mqtt.client as paho
import time
import streamlit as st
import json
import platform
import os
from PIL import Image
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from bokeh.models.widgets import Button

# Configuración de página
st.title("🎬 Control de Cine en Casa IoT")
st.subheader("Dicta comandos para ajustar el ambiente 🍿")

broker = "157.230.214.127"
port = 1883

def on_publish(client, userdata, result):
    print("El dato ha sido publicado \n")
    pass

def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received = str(message.payload.decode("utf-8"))
    st.write(message_received)

client1 = paho.Client("yos_voice_cinema")
client1.on_message = on_message

st.write("🎤 **Prueba diciendo:** *'modo cine'*, *'abrir persiana'*, *'ON'* o *'OFF'*")

stt_button = Button(label="🎙️ Toca para hablar", width=200)
stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if (value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
"""))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

if result:
    if "GET_TEXT" in result:
        texto_escuchado = result.get("GET_TEXT").strip().lower()
        st.info(f"🗣️ Comando detectado: **'{texto_escuchado}'**")
        
        client1.on_publish = on_publish
        client1.connect(broker, port)
        
        # Publicar el texto dictado al broker MQTT
        message = json.dumps({"Act1": texto_escuchado})
        ret = client1.publish("voice_ctrl", message)
        st.success("¡Comando enviado con éxito! 🍿")
