# RestaurantsAgent


Este proyecto utiliza Docker para su despliegue y requiere configurar algunas dependencias antes de ejecutarlo.

## 📥 Clonar el repositorio

```sh
git clone https://github.com/SparkEnjoyer/AgenticRestaurantAdvisor
cd AgenticRestaurantAdvisor
```

## 📂 Añadir los archivos necesarios

1. Pega el archivo `restaurant_processed.csv` dentro de `./api` en el repositorio:


2. Configura la clave de API de OpenAI en el archivo `.env`, modificando la variable OPENAI_API_KEY.



```sh
OPENAI_API_KEY=tu_clave_aqui
```

## 🚀 Ejecutar el proyecto

Construye y ejecuta los contenedores con Docker Compose:

```sh
docker-compose up --build
```

Esto levantará todos los servicios necesarios para la API.

## 📌 Notas
- Asegúrate de tener **Docker** y **Docker Compose** instalados.
- Verifica que la clave de API de OpenAI es válida.
- Si necesitas detener la ejecución, usa `Ctrl + C` o el comando:

```sh
docker-compose down
```

