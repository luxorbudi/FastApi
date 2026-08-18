# --- Etapa 1: Compilación (Todo en Alpine) ---
FROM python:3.11-alpine3.19 AS compiler

WORKDIR /app

# Quitamos patchelf de apk add para evitar la versión buggeada 0.18.0
RUN apk add --no-cache \
    build-base \
    gcc \
    g++ \
    musl-dev \
    ccache \
    python3-dev

COPY requirements.txt .

# Instala dependencias, Nuitka y una versión limpia de patchelf vía pip
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir patchelf nuitka

COPY main.py .

# Compilación nativa para el ecosistema Alpine
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

# Copiamos la carpeta autocontenida que generó Nuitka
COPY --from=compiler /app/main.dist /app/main.dist

# Variables de entorno dinámicas
ENV APP_HOST=0.0.0.0
ENV APP_PORT=80

EXPOSE 80

# Ejecutamos el binario nativo directo sobre Alpine
CMD ["/app/main.dist/main.bin"]