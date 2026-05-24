# Arquitectura de Microservicios - UniLab-SW

## Visión general

Este documento describe la primera etapa de transición de UniLab-SW hacia una arquitectura basada en microservicios. En esta fase se separó la capa de presentación del backend existente, manteniendo el backend como núcleo de aplicación y agregando servicios auxiliares para facilitar despliegue, pruebas e integración.

La arquitectura actual permite ejecutar UniLab mediante Docker Compose, levantando de forma coordinada:

- Un microservicio de frontend servido con Nginx.
- Un backend Python/FastAPI que conserva la lógica principal de UniLab.
- Un servicio de almacenamiento basado en Redis, preparado para futuras extensiones.

Además, el backend recibe telemetría externa mediante UDP, por ejemplo desde un ESP32, y expone dicha información al dashboard mediante endpoints HTTP.

---

## Fase 1: Frontend separado

**Estado:** completada.

### Objetivo

Independizar la capa de presentación del backend para permitir:

- Separar el ciclo de vida del frontend y del backend.
- Facilitar el desarrollo colaborativo entre integrantes del equipo.
- Probar cambios de interfaz sin modificar la lógica central del backend.
- Preparar el sistema para futuras migraciones hacia servicios más especializados.
- Ejecutar la aplicación completa mediante contenedores Docker.

---

## Arquitectura actual

```text
┌─────────────────────────────────────────────────────────────┐
│                    Cliente / Navegador                      │
│                    http://localhost                         │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTP
                             ▼
┌─────────────────────────────────────────────────────────────┐
│          Frontend Microservice - Nginx, puerto 80            │
├─────────────────────────────────────────────────────────────┤
│  • Sirve archivos estáticos: HTML, CSS y JavaScript          │
│  • Expone el dashboard web                                  │
│  • Redirige solicitudes /api/* hacia el backend              │
│  • Incluye health check en /health                           │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTP interno en red Docker
                             ▼
┌─────────────────────────────────────────────────────────────┐
│             Backend - FastAPI/Uvicorn, puerto 8000           │
├─────────────────────────────────────────────────────────────┤
│  • API HTTP para el dashboard                                │
│  • Recepción de telemetría por UDP en el puerto 5005         │
│  • Gestión de paquetes, variables, eventos y límites         │
│  • Integración con módulos existentes de UniLab              │
└──────────────┬──────────────────────────────┬───────────────┘
               │                              │
               │ UDP externo                  │ TCP interno
               ▼                              ▼
┌─────────────────────────────┐     ┌─────────────────────────┐
│ ESP32 / Simulador UDP        │     │ Redis - Storage          │
├─────────────────────────────┤     ├─────────────────────────┤
│ • Envía JSON por UDP         │     │ • Caché                  │
│ • Usa Wi-Fi 2.4 GHz          │     │ • Futuras colas/eventos  │
│ • Destino: IP_PC:5005        │     │ • Persistencia auxiliar  │
└─────────────────────────────┘     └─────────────────────────┘
```

---

## Componentes

### 1. Frontend

El frontend fue separado en una carpeta propia y se ejecuta como un microservicio independiente usando Nginx.

Funciones principales:

- Servir el dashboard web.
- Cargar `index.html`, `styles.css` y `app.js`.
- Consumir la API del backend mediante rutas `/api/...`.
- Mostrar el estado del sistema, últimos paquetes recibidos, variables y eventos.

URL local:

```text
http://localhost
```

Health check:

```text
http://localhost/health
```

### 2. Backend

El backend mantiene la lógica principal de UniLab y se ejecuta mediante FastAPI/Uvicorn.

Funciones principales:

- Levantar la API HTTP en el puerto `8000`.
- Recibir telemetría UDP en el puerto `5005`.
- Procesar paquetes recibidos desde dispositivos como ESP32.
- Entregar datos al dashboard mediante endpoints HTTP.

URL local:

```text
http://localhost:8000
```

Endpoint de estado:

```text
http://localhost:8000/api/status
```

### 3. Storage

Se agregó un contenedor Redis como servicio de almacenamiento auxiliar. En esta fase puede funcionar como placeholder, pero deja preparada la arquitectura para:

- Caché.
- Sesiones.
- Cola de eventos.
- Persistencia temporal.
- Separación futura de responsabilidades.

---

## Estructura de archivos

```text
Unilab-SW/
├── docker-compose.yml           # Orquestación de servicios
├── Dockerfile.backend           # Imagen Docker del backend
├── frontend/                    # Microservicio de frontend
│   ├── Dockerfile               # Imagen del frontend
│   ├── nginx.conf               # Configuración de Nginx
│   ├── index.html               # Vista principal del dashboard
│   ├── styles.css               # Estilos del dashboard
│   ├── app.js                   # Lógica del frontend
│   ├── package.json             # Metadatos/dependencias del frontend
│   ├── .dockerignore            # Exclusiones Docker
│   └── README.md                # Documentación específica del frontend
│
├── unilab/                      # Backend y módulos principales
│   ├── config/
│   ├── contracts/
│   ├── core/
│   └── modules/
│
├── tests/                       # Pruebas del proyecto
├── pyproject.toml               # Configuración del proyecto Python
├── requirements.txt             # Dependencias Python
└── README.md
```

---

## Docker Compose

La ejecución completa se realiza mediante `docker-compose.yml`.

Fragmento importante del servicio backend:

```yaml
backend:
  build:
    context: .
    dockerfile: Dockerfile.backend
  container_name: unilab-backend
  ports:
    - "8000:8000"
    - "5005:5005/udp"
```

La línea:

```yaml
- "5005:5005/udp"
```

es importante para que un ESP32 o un simulador externo pueda enviar datos UDP hacia el backend dentro del contenedor.

---

## Cómo ejecutar

### Ejecución recomendada con Docker Compose

Desde la raíz del proyecto:

```bash
docker compose up --build
```

En versiones antiguas de Docker Compose:

```bash
docker-compose up --build
```

Luego abrir:

```text
http://localhost
```

Backend:

```text
http://localhost:8000/api/status
```

Para detener los servicios:

```bash
docker compose down
```

Para reconstruir sin caché:

```bash
docker compose build --no-cache
docker compose up
```

---

## Verificación de servicios

### Ver contenedores activos

```bash
docker compose ps
```

Se espera ver servicios similares a:

```text
unilab-frontend   running
unilab-backend    running
unilab-storage    running
```

### Ver logs

Todos los servicios:

```bash
docker compose logs -f
```

Solo backend:

```bash
docker compose logs -f backend
```

Solo frontend:

```bash
docker compose logs -f frontend
```

Solo Redis:

```bash
docker compose logs -f storage
```

### Health checks

Frontend:

```bash
curl http://localhost/health
```

Backend:

```bash
curl http://localhost:8000/api/status
```

También se puede probar desde el navegador:

```text
http://localhost/api/status
http://localhost/api/latest-packet
http://localhost/api/recent-packets
```

---

## Comunicación entre frontend y backend

El frontend debe consumir la API usando rutas relativas:

```javascript
const API_BASE_URL = "";
```

De esa forma, las solicitudes como:

```javascript
fetch(`${API_BASE_URL}/api/status`)
```

se resuelven como:

```text
http://localhost/api/status
```

Luego Nginx redirige internamente la solicitud hacia el backend dentro de la red Docker.

Ejemplo conceptual de proxy en Nginx:

```nginx
location /api/ {
    proxy_pass http://backend:8000;
}
```

Esto evita depender de `http://localhost:8000` directamente desde el JavaScript del navegador y hace que el frontend sea más portable.

---

## Prueba con ESP32

El ESP32 envía paquetes JSON por UDP al backend.

### Consideración importante de red

El ESP32 clásico, por ejemplo el ESP32-WROOM-32, usa Wi-Fi de **2.4 GHz**. Si la red disponible está solo en 5 GHz, el ESP32 no podrá conectarse correctamente.

Recomendación:

- Usar una red Wi-Fi de 2.4 GHz.
- Separar los SSID del router, por ejemplo:
  - `MiWifi_2G`
  - `MiWifi_5G`
- Conectar el ESP32 siempre al SSID de 2.4 GHz.

### Destino UDP

Si el ESP32 está en la misma red local que la PC, debe enviar los paquetes a:

```text
IP_DE_LA_PC:5005
```

Ejemplo:

```text
192.168.1.35:5005
```

Para obtener la IP local en Windows:

```bash
ipconfig
```

Buscar la dirección IPv4 del adaptador Wi-Fi.

---

## Formato esperado de telemetría

Un paquete típico enviado por ESP32 o por un simulador UDP puede tener la siguiente forma:

```json
{
  "device_id": "esp32_lab_01",
  "temperature": 25.5,
  "humidity": 60.0,
  "ph": 6.7,
  "ec": 1.45
}
```

En los logs del backend se debe observar algo similar a:

```text
[Backend] Paquete recibido desde: esp32_lab_01
  - temperature: 25.5 C
  - humidity: 60.0 %
  - ph: 6.7 pH
  - ec: 1.45 mS/cm
```

Si esto aparece en los logs, significa que la recepción UDP está funcionando.

---

## Prueba con simulador UDP

Si no se dispone de un ESP32, se puede probar con un script Python que envíe datos al puerto UDP `5005`.

Ejemplo:

```python
import socket
import json
import time
import random

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    data = {
        "device_id": "esp32_test",
        "temperature": round(25 + random.uniform(-2, 2), 2),
        "humidity": round(60 + random.uniform(-5, 5), 2),
        "ph": round(6.5 + random.uniform(-0.5, 0.5), 2),
        "ec": round(1.2 + random.uniform(-0.2, 0.2), 2)
    }

    message = json.dumps(data).encode("utf-8")
    sock.sendto(message, (UDP_IP, UDP_PORT))

    print("Enviado:", data)
    time.sleep(1)
```

---

## Problemas encontrados durante la integración

Durante las pruebas se identificaron los siguientes puntos:

### 1. El backend recibía datos, pero el dashboard no actualizaba

Síntoma:

- En los logs del backend aparecían paquetes recibidos.
- El dashboard se quedaba en “Conectando...”.

Causa probable:

- Caché del navegador usando una versión antigua de `app.js`.
- Caché agresivo de archivos estáticos desde Nginx.

Solución aplicada:

- Abrir en modo incógnito para confirmar.
- Limpiar caché del navegador.
- Usar `Ctrl + Shift + R`.
- En DevTools, activar `Disable cache` en la pestaña Network.

Recomendación para desarrollo:

```nginx
location ~* \.(js|css)$ {
    expires -1;
    add_header Cache-Control "no-store, no-cache, must-revalidate, proxy-revalidate";
}

location ~* \.(png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
    expires 1h;
    add_header Cache-Control "public";
}
```

### 2. ESP32 conectado a red incompatible

Síntoma:

- El backend no recibía datos de forma consistente.
- El ESP32 no lograba conectarse correctamente a la red.

Causa:

- La red Wi-Fi usada estaba en 5 GHz.
- El ESP32 utilizado solo soporta 2.4 GHz.

Solución:

- Cambiar a una red Wi-Fi de 2.4 GHz.
- Separar los SSID de 2.4 GHz y 5 GHz si el router lo permite.

### 3. Puerto UDP no expuesto en Docker

Síntoma:

- El backend funcionaba dentro del contenedor.
- Pero datos externos enviados al puerto `5005` no llegaban al contenedor.

Solución:

Agregar al servicio `backend`:

```yaml
ports:
  - "8000:8000"
  - "5005:5005/udp"
```

---

## Troubleshooting

### El frontend no abre

Verificar que el contenedor esté activo:

```bash
docker compose ps
```

Ver logs:

```bash
docker compose logs -f frontend
```

Si el puerto 80 está ocupado, cambiar:

```yaml
ports:
  - "80:80"
```

por:

```yaml
ports:
  - "8080:80"
```

Luego abrir:

```text
http://localhost:8080
```

### El backend no responde

Probar:

```bash
curl http://localhost:8000/api/status
```

Ver logs:

```bash
docker compose logs -f backend
```

### El backend recibe datos, pero el dashboard no muestra nada

Probar endpoints desde navegador:

```text
http://localhost/api/status
http://localhost/api/latest-packet
http://localhost/api/recent-packets
```

Si los endpoints muestran datos, pero el dashboard no:

- Limpiar caché.
- Abrir en incógnito.
- Revisar la consola del navegador con `F12`.
- Verificar errores en `app.js`.
- Reconstruir frontend sin caché:

```bash
docker compose build --no-cache frontend
docker compose up
```

### El ESP32 no envía datos

Verificar:

- Que esté conectado a Wi-Fi 2.4 GHz.
- Que la IP destino sea la IP local de la PC.
- Que el puerto destino sea `5005`.
- Que Docker exponga `5005/udp`.
- Que PC y ESP32 estén en la misma red local.

### No usar `run_esp32_demo.py` junto con Docker Compose

Si se ejecuta la arquitectura con Docker Compose, no es necesario correr `run_esp32_demo.py`, porque el backend ya está activo dentro del contenedor.

Usar `run_esp32_demo.py` solo para pruebas locales sin Docker.

---

## Ventajas de la separación

### Independencia de ciclo de vida

```text
Frontend:
- Cambios visuales independientes
- Iteración rápida de UI
- Posible migración futura a React, Vue, Svelte o Angular

Backend:
- Mantiene lógica de adquisición y procesamiento
- Expone API estable para el dashboard
- Puede evolucionar hacia servicios especializados
```

### Escalabilidad selectiva

```bash
docker compose up --scale frontend=3
```

En fases futuras, el backend también puede dividirse por dominio:

- Servicio de telemetría.
- Servicio de eventos.
- Servicio de almacenamiento.
- Servicio de autenticación.
- Servicio de notificaciones.

### Desarrollo colaborativo

La separación permite que un integrante trabaje en el frontend sin interferir directamente con el desarrollo del backend, siempre que se respete la interfaz de API.

---

## Próximas fases de migración

### Fase 2: API Gateway

```text
Frontend → API Gateway → Backend / Servicios
```

Funciones esperadas:

- Enrutamiento centralizado.
- Autenticación.
- Rate limiting.
- Manejo de versiones de API.
- Registro de solicitudes.

### Fase 3: Separación por dominio

```text
Frontend → API Gateway
           ├── TelemetryService
           ├── EventService
           ├── StorageService
           ├── SafetyService
           └── AuthService
```

### Fase 4: Arquitectura orientada a eventos

```text
ESP32 → UDP → TelemetryService → Event Bus
                                   ├── Storage
                                   ├── Safety Manager
                                   ├── Dashboard
                                   └── Notification Service
```

Tecnologías posibles:

- RabbitMQ.
- Kafka.
- Redis Streams.
- MQTT para integración IoT.

---

## Monitoreo y métricas

Ver consumo de recursos:

```bash
docker stats
```

Valores esperados aproximados:

```text
CONTAINER         CPU %   MEM USAGE
unilab-frontend   <1%     ~50 MB
unilab-backend    5-15%   ~200-400 MB
unilab-storage    <1%     ~100 MB
```

---

## Conclusión

La Fase 1 permitió separar el frontend como un microservicio independiente y ejecutar UniLab-SW mediante Docker Compose.

Resultados principales:

- Frontend containerizado con Nginx.
- Backend containerizado con FastAPI/Uvicorn.
- Redis agregado como servicio auxiliar.
- Comunicación frontend-backend mediante proxy `/api`.
- Recepción de telemetría UDP desde ESP32 o simulador.
- Identificación y solución de problemas reales de integración:
  - Caché del navegador.
  - Puerto UDP no expuesto.
  - Compatibilidad Wi-Fi 2.4 GHz del ESP32.

La arquitectura queda preparada para evolucionar hacia una solución más modular, donde los servicios de telemetría, eventos, almacenamiento, seguridad y autenticación puedan separarse progresivamente.

---

**Tecnologías utilizadas:** Docker, Docker Compose, Nginx, FastAPI, Python, Redis, UDP, ESP32  
**Estado:** Fase 1 completada y validada experimentalmente
