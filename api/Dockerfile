# Usa una versión estable de Python
FROM python:3.9

WORKDIR /app

# Copia los archivos de tu aplicación
COPY . /app

# Actualiza pip antes de instalar dependencias
RUN pip install --upgrade pip

# Instala las dependencias
RUN pip install \
    fastapi \
    requests \
    pandas \
    openai \
    geopy \
    langchain \
    langchain_community \ 
    uvicorn \
    pydantic

# Expone el puerto en el que corre FastAPI
EXPOSE 7900

# Comando para ejecutar la aplicación (ajústalo según tu código)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7900"]
