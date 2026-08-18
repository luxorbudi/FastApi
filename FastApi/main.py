import os
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Modelo de entrada (define los datos que el usuario debe enviar)
class UsuarioModelo(BaseModel):
    nombre: str
    edad: int
    es_activo: bool

# Ruta POST que recibe el modelo como parámetro
@app.post("/usuarios/")
def crear_usuario(usuario: UsuarioModelo):
    # Aquí procesas los datos del usuario
    return {
        "mensaje": "Usuario creado con éxito",
        "datos_recibidos": usuario
    }

@app.post("/usuarios3/")
def crear_usuario2(usuario: UsuarioModelo):
    # Aquí procesas los datos del usuario
    return {
        "mensaje": "Usuario creado con éxito3",
        "datos_recibidos": usuario
    }

if __name__ == "__main__":
    # Lee las variables del entorno, si no existen usa los valores por defecto
    # Convertimos el puerto a entero (int) porque uvicorn lo necesita así
    host_env = os.getenv("APP_HOST", "0.0.0.0")
    port_env = int(os.getenv("APP_PORT", "80"))
    
    uvicorn.run(app, host=host_env, port=port_env)