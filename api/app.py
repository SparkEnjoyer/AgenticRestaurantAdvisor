import requests
import json
import os
import uuid
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from langchain_community.chat_models import ChatOpenAI
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from fastapi.responses import StreamingResponse

from fastapi import Request
from pydantic import BaseModel

from dummy_conversation import dummy_texts

df = pd.read_csv(r"restaurant_processed.csv", encoding="utf-8")


app = FastAPI()


CONVERSATIONS_DIR = "conversaciones"

# Crear el directorio si no existe
os.makedirs(CONVERSATIONS_DIR, exist_ok=True)


def load_conversation(conv_id):
    filepath = os.path.join(CONVERSATIONS_DIR, f"{conv_id}.json")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"messages": []}


@app.get("/conversations") 
def get_conversations(): 
    return {
        "conversations": [
            f.replace(".json", "")
            for f in os.listdir(CONVERSATIONS_DIR)
            if f.endswith(".json")
        ]
    }


def load_memory_history(memory, messages):
    # Cargar mensajes en la memoria
    for mensaje in messages["messages"]:
        if mensaje["role"] == "user":
            memory.chat_memory.add_user_message(mensaje["text"])
        elif mensaje["role"] == "bot":
            memory.chat_memory.add_ai_message(mensaje["text"])
    return memory


async def pregunta(query, agent):
    tt = agent.stream(query)
    for chunk in tt:
        pass

    yield (
        chunk["output"].encode("utf-8").decode("utf-8")
    )  # Enviar fragmento al cliente en tiempo real



llm = ChatOpenAI(
    model_name="gpt-4", streaming=True, openai_api_key=os.getenv("OPENAI_API_KEY")
)

location_prompt = PromptTemplate(
    input_variables=["query"],
    template="Extrae el nombre del barrio o ubicación de la siguiente consulta del usuario: {query}. Devuelve solo el nombre del barrio sin explicaciones adicionales.",
)

location_chain = LLMChain(llm=llm, prompt=location_prompt)


def geolocate_address(address, geolocator):
    location = geolocator.geocode(address)
    return (location.latitude, location.longitude) if location else None


def process_geolocate(frase):
    ll = frase.split(",")
    return (ll[0], ll[1])


def find_nearest_restaurants(user_input, df):
    neighborhood = location_chain.run(user_input).strip()
    geolocator = Nominatim(user_agent="restaurant_finder")
    neighborhood_coords = geolocate_address(neighborhood, geolocator)
    if not neighborhood_coords:
        return "No se pudo encontrar el barrio que has indicado."

    df["Distance"] = df["Coordinates"].map(
        lambda coord: geodesic(neighborhood_coords, process_geolocate(coord)).km
    )
    nearest = df.nsmallest(5, "Distance")

    return nearest[["name", "completed_address"]].to_dict(orient="records")


search_tool = Tool(
    name="Restaurant Search",
    func=lambda query: find_nearest_restaurants(query, df),
    description="""Busca los 5 restaurantes más cercanos a la dirección proporcionada por el usuario. Cuando tengas los restaurantes. Debes devolver los nombres y direcciones originales, conservando las tildes.  Debes seguir el siguiente formato para responder al usuario:
    Los restaurantes más cercanos a la #ubicación  son:

1. #nombre_1 - #dirección_1
2. #nombre_2 - #dirección_2
3. #nombre_3 - #dirección_3
4. #nombre_4 - #dirección_4
5. #nombre_5 - #dirección_5

¡Espero que disfrutes tu comida! 🍽️
    """,
)


# Endpoint para responder en streaming
@app.get("/chat")
async def chat(query: str, session_id: str):
    
    messages = load_conversation(session_id)
    

    memory = ConversationBufferMemory(memory_key="chat_history")

    memory = load_memory_history(memory, messages)
    

    agent = initialize_agent(
        tools=[search_tool],
        llm=llm,
        agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
        memory=memory,
        verbose=True,
    )

    return StreamingResponse(
        pregunta(query, agent), media_type="text/plain; charset=utf-8"
    )


@app.get("/conversation_history")  
def conversation_history(conv_id: str): 
    return load_conversation(conv_id)


def save_conversation2(conv_id, user_input, conversation_text):
    messages = load_conversation(conv_id)["messages"]
    messages.append({"role": "user", "text": user_input})
    messages.append({"role": "bot", "text": conversation_text})
    filepath = os.path.join(CONVERSATIONS_DIR, f"{conv_id}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump({"messages": messages}, f, indent=4, ensure_ascii=False)


# Define a Pydantic model for the request body
class ConversationRequest(BaseModel):
    conv_id: str
    user_input: str
    conversation_text: str


@app.post("/save_conversation")
def save_conversation(request: ConversationRequest):
    # Extract data from the request object
    save_conversation2(request.conv_id, request.user_input, request.conversation_text)


# Define a Pydantic model for the request body
class CreateConversation(BaseModel):
    conv_id: str


@app.post("/create_conversation")
def create_conversation(request: CreateConversation):
    filepath = os.path.join(CONVERSATIONS_DIR, f"{request.conv_id}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump({"messages": dummy_texts}, f, indent=4, ensure_ascii=False)
