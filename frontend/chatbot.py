import streamlit as st
import requests
import json
import os
import uuid
import time

API_URL = "http://api:7900/chat" 

# Obtener todas las conversaciones guardadas
def get_conversations():
    response = requests.get("http://api:7900/conversations")
    return response.json()["conversations"]




# Cargar una conversación desde un archivo JSON
def load_conversation(conv_id):
    response = requests.get("http://api:7900/conversation_history", params={"conv_id": conv_id})
    return response.json()


def create_conversation(conv_id):
    data = {
        "conv_id": conv_id,
        
    }

    # Realizamos la petición POST
    response =requests.post("http://api:7900/create_conversation", json=data)
    print("status code")
    print(response.status_code)


# Guardar una conversación en un archivo JSON
def save_conversation2(conv_id, user_input, conversation_text):
    # Datos a enviar en el cuerpo de la petición
    data = {
        "conv_id": conv_id,
        "user_input": user_input,
        "conversation_text": conversation_text
    }

    # Realizamos la petición POST
    response =requests.post("http://api:7900/save_conversation", json=data)
    print("status code")
    print(response.status_code)
    
        
        
# Formatear el historial del chat para mostrarlo en la interfaz
def format_chat_history(historial):
    if historial["messages"] and st.session_state["conv_id"] != "Nueva Conversación":
        return "\n\n".join(
            [f"👤 Usuario: {msg['text']}" if msg["role"] == "user" else f"🤖 Bot: {msg['text']}" for msg in historial["messages"]]
        )
    else:
        if st.session_state["conv_id"] != "Nueva Conversación":
            return "Archivo con formato inválido"




st.title("Chatbot con Memoria")
st.sidebar.header("Conversaciones Guardadas")

# Obtener conversaciones
conversations = get_conversations()

# Inicializar valores en session_state
if "conv_id" not in st.session_state:
    st.session_state["conv_id"] = "Nueva Conversación"
if "bot_response" not in st.session_state:
    st.session_state["bot_response"] = ""
if "last_conv_id" not in st.session_state:
    st.session_state["last_conv_id"] = ""

# Sidebar para seleccionar la conversación
selected_conv = st.sidebar.radio(
    "Selecciona una conversación:",
    ["Nueva Conversación"] + conversations,
    index=0 if st.session_state["conv_id"] == "Nueva Conversación" else conversations.index(st.session_state["conv_id"]) + 1
)

# Si se inicia una nueva conversación
if selected_conv != st.session_state["conv_id"]:
    st.session_state["conv_id"] = selected_conv
    st.session_state["bot_response"] = ""  # Limpiar la respuesta del bot
    st.rerun()  # Refrescar la interfaz

if selected_conv == "Nueva Conversación":
    if st.sidebar.button("Iniciar nueva conversación"):
        new_conv_id = str(uuid.uuid4())  # Generar nuevo UUID
        create_conversation(new_conv_id)  # Guardar conversación vacía
        st.session_state["conv_id"] = new_conv_id  # Actualizar la conversación activa
        st.session_state["bot_response"] = ""  # Limpiar la respuesta del bot
        st.rerun()  # Refrescar la interfaz

# Cargar historial de la conversación activa
conv_id = st.session_state["conv_id"]
historial = load_conversation(conv_id)

# Mostrar historial en un cuadro de texto fijo
st.text_area(f"Historial de Conversación ({conv_id})", format_chat_history(historial), height=200, disabled=True)

# Entrada de usuario (usando text_area en vez de text_input)
user_input = st.text_input("Escribe tu mensaje:", value="", key="user_input")

# Espacio para la respuesta del bot
chat_area = st.empty()

# Enviar mensaje y actualizar historial
if st.button("Enviar") and user_input and st.session_state["conv_id"] != "Nueva Conversación":
    # Añadir mensaje del usuario al historial
    
    placeholder = st.empty()
    chat_area = st.empty()
    conversation_text = ""

    # Enviar la consulta a la API
    with requests.get(API_URL, params={"query": user_input, "session_id": conv_id}) as response:

        if response.status_code == 200:
            for line in response.iter_lines(decode_unicode=True):
                    
                
                    conversation_text_part = line +"\n"
                    time.sleep(0.1)
                    chat_area.text(conversation_text + conversation_text_part)
                    conversation_text += conversation_text_part
            

            # Guardar conversación y actualizar respuesta en session_state
            save_conversation2(conv_id, user_input, conversation_text)
            st.session_state["bot_response"] = conversation_text  # Guardar la respuesta para mostrarla

            chat_area.text(conversation_text)


    
