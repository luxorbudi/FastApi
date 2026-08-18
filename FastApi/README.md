# 🚀 FastAPI + Nuitka + Alpine Linux (Kubernetes Enterprise Cluster)

Este proyecto contiene la arquitectura extrema para compilar una API de FastAPI en Python como un binario nativo en C, ejecutado dentro de un entorno Alpine Linux ultra ligero de **90.15 MB** y orquestado en alta disponibilidad con **Kubernetes (Minikube)**.

## 📄 Código de la Aplicación (`main.py`)

```python
import os
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class UsuarioModelo(BaseModel):
    nombre: str
    edad: int
    es_activo: bool

@app.post("/usuarios/")
def crear_usuario(usuario: UsuarioModelo):
    return {
        "mensaje": "Usuario creado con éxito",
        "datos_recibidos": usuario
    }

@app.post("/usuarios3/")
def crear_usuario2(usuario: UsuarioModelo):
    return {
        "mensaje": "Usuario creado con éxito3",
        "datos_recibidos": usuario
    }

if __name__ == "__main__":
    host_env = os.getenv("APP_HOST", "0.0.0.0")
    port_env = int(os.getenv("APP_PORT", "80"))
    
    # Pasamos el objeto 'app' directo para compatibilidad con Nuitka
    uvicorn.run(app, host=host_env, port=port_env)
```

---

## 🐳 Configuración del Contenedor (`Dockerfile`)

```dockerfile
# --- Etapa 1: Compilación (Todo en Alpine) ---
FROM python:3.11-alpine3.19 AS compiler
WORKDIR /app

# Herramientas de desarrollo nativas de Alpine
RUN apk add --no-cache \
    build-base \
    gcc \
    g++ \
    musl-dev \
    ccache \
    python3-dev

COPY requirements.txt .

# Se instala patchelf vía pip para evitar la versión buggeada 0.18.0 de Alpine
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir patchelf nuitka

COPY main.py .

# Compilación nativa empaquetada
RUN python -m nuitka \
    --standalone \
    --prefer-source-code \
    --include-package=fastapi \
    --include-package=uvicorn \
    --include-package=pydantic \
    --include-package=pydantic_core \
    main.py

# --- Etapa 2: El Runner (Mismo Alpine 3.19) ---
FROM alpine:3.19 AS runner
WORKDIR /app

# Copiamos ÚNICAMENTE la carpeta del binario compilado
COPY --from=compiler /app/main.dist /app/main.dist

# Variables de entorno dinámicas
ENV APP_HOST=0.0.0.0
ENV APP_PORT=80

EXPOSE 80

# Ejecución directa del binario nativo
CMD ["/app/main.dist/main.bin"]
```

---

## ☸️ Orquestación Elástica (`fast-api.yaml`)

Este archivo de Kubernetes define un **Deployment** con 3 réplicas que se auto-reparan y están protegidas con límites estrictos de hardware, además de un **Service** que actúa como balanceador de carga automático.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fast-api-deployment
  labels:
    app: api-fast
spec:
  replicas: 3  # Mantiene 3 copias idénticas en paralelo para alta disponibilidad
  selector:
    matchLabels:
      app: api-fast
  template:
    metadata:
      labels:
        app: api-fast
    spec:
      containers:
      - name: fast-api
        image: api-fastapi-lite:latest
        imagePullPolicy: Never  # Obliga a buscar la imagen en la máquina local (no internet)
        env:
        - name: APP_PORT
          value: "8085"
        ports:
        - containerPort: 8085
        
        # 🛡️ Control de hardware quirúrgico (QoS Class: Burstable)
        resources:
          requests:
            memory: "40Mi"      # RAM mínima reservada al nacer
            cpu: "100m"         # 10% de un núcleo de CPU mínimo reservado
          limits:
            memory: "100Mi"     # Techo máximo de RAM (Evita fugas de memoria globales)
            cpu: "500m"         # Techo máximo de CPU (Bloquea el uso a máximo medio núcleo)
---
apiVersion: v1
kind: Service
metadata:
  name: api-fast-public-service
spec:
  type: LoadBalancer  # Abre la puerta para recibir tráfico desde tu Windows
  selector:
    app: api-fast
  ports:
  - protocol: TCP
    port: 8085        # Puerto externo en tu computadora
    targetPort: 8085  # Puerto interno de destino en los Pods
```

---

## 🛠️ Comandos de Operación en PowerShell

### 1. Construir la imagen de Docker
```powershell
docker build -t api-fastapi-lite .
```

### 2. Iniciar el clúster local de Kubernetes
```powershell
minikube start --driver=docker
```

### 3. Cargar la imagen local dentro del entorno de Minikube
```powershell
minikube image load api-fastapi-lite:latest
```

### 4. Desplegar / Actualizar en caliente la infraestructura
```powershell
kubectl apply -f fast-api.yaml
```

### 5. Verificar el estado de los Pods y el blindaje
```powershell
kubectl get pods
kubectl describe pod NOMBRE_DE_UN_POD
```

### 6. Ejecutar prueba de esfuerzo masiva (Autocannon cruzando el puente virtual)
```powershell
docker run --rm -it autocannon -c 100 -d 10 -m POST -H "Content-Type: application/json" -b '{"nombre": "Carlos El Optimizador", "edad": 25, "es_activo": true}' http://host.docker.internal:8085/usuarios/
```

---

## 📊 Reporte Final de Benchmarking y Hardware

### Especificaciones del Host de Pruebas
* **Procesador**: AMD Ryzen 7 5800H (8 núcleos / 16 procesadores lógicos) @ ~3.67 GHz.
* **Orquestador**: Minikube con arquitectura elástica de Nodo Único.

### Resultados bajo estrés real (17,000 peticiones en 10 segundos)
* **Peticiones por Segundo (Avg)**: **1,641.2 req/seg** (100% de respuestas exitosas HTTP 200).
* **Latencia Promedio**: **60.32 ms** (Repartido simétricamente entre los 16 hilos del CPU por `kube-proxy`).
* **Consumo de Memoria por Pod**: **33.46 MiB** en reposo y solo **36.63 MiB** bajo estrés máximo. Un incremento controlado de apenas el 9.4% gracias a la eficiencia del código nativo compilado en C.
* **Auto-reparación (Self-healing)**: Validada con éxito. Al eliminar de forma agresiva un Pod en ejecución (`kubectl delete pod`), el Deployment tardó **menos de 1 segundo** en aprovisionar un clon completamente operativo sin interrumpir la conectividad de los usuarios.
