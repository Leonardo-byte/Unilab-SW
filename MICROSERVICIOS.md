# Arquitectura de Microservicios - UniLab-SW

## Visión General

Este documento describe la transición del monolito de UniLab a una arquitectura de microservicios, comenzando con la separación del frontend.

## Fase 1: Frontend Separado ✅ COMPLETADA

### Objetivo
Independizar la capa de presentación del backend, permitiendo:
- Deployments independientes
- Escalabilidad del frontend sin afectar el backend
- Desarrollo paralelo de frontend y backend
- Optimización de cada servicio según su necesidad

### Componentes

```
┌─────────────────────────────────────────────────────────────┐
│                    Cliente (Navegador)                       │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTP
                             ▼
┌─────────────────────────────────────────────────────────────┐
│              Nginx (Port 80) - Frontend Microservice         │
├─────────────────────────────────────────────────────────────┤
│  • Static Files (HTML, CSS, JS)                              │
│  • Proxy a Backend (/api/*)                                  │
│  • Cache, Compression, Health Checks                         │
└──────────────┬────────────────────────────────────────────────┘
               │ HTTP (internal network)
               ▼
┌──────────────────────────────────────────────────────────────┐
│           FastAPI (Port 8000) - Backend Monolito            │
├──────────────────────────────────────────────────────────────┤
│  • /api/status          - Estado general                      │
│  • /api/latest-packet   - Última telemetría                   │
│  • /api/recent-packets  - Historial                           │
│  • /api/recent-events   - Eventos                             │
│  • /api/variables       - Variables disponibles               │
│  • /api/visible-variables - Variables configuradas            │
│  • /api/clear           - Limpiar datos                       │
│  • /api/safe-limits     - Rangos de seguridad               │
└──────────────┬────────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────────┐
│                  Redis - Storage (opcional)                  │
├──────────────────────────────────────────────────────────────┤
│  • Almacenamiento en caché                                    │
│  • Sesiones de usuarios                                       │
│  • Cola de eventos                                            │
└──────────────────────────────────────────────────────────────┘
```

### Estructura de Archivos

```
Unilab-SW/
├── docker-compose.yml           ← Orquestación (NUEVO)
├── Dockerfile.backend           ← Backend containerizado (NUEVO)
├── frontend/                    ← Microservicio Frontend (NUEVO)
│   ├── Dockerfile               ├─ Imagen del servicio
│   ├── nginx.conf               ├─ Configuración Nginx
│   ├── index.html               ├─ Template mejorado
│   ├── styles.css               ├─ Estilos modernos
│   ├── app.js                   ├─ Lógica JavaScript
│   ├── package.json             ├─ Dependencies (Node)
│   ├── .dockerignore            ├─ Exclusiones Docker
│   ├── README.md                └─ Documentación
│
├── unilab/                      ← Backend (SIN CAMBIOS)
│   ├── config/
│   ├── contracts/
│   ├── core/
│   └── modules/
│
├── tests/                       ← Tests (SIN CAMBIOS)
├── pyproject.toml               ← Proyecto Python
├── requirements.txt             ← Deps Python
└── README.md
```

## Ventajas de la Separación

### 1. **Independencia de Ciclo de Vida**
```
Frontend:                    Backend:
- Deploy cada cambio UI      - Deploy cada bug fix/feature backend
- Sin esperar al backend     - Sin interrumpir frontend
- A su propio ritmo          - Versionado independiente
```

### 2. **Escalabilidad Selectiva**
```
# Si hay picos de tráfico en frontend
docker-compose up --scale frontend=3

# Si backend necesita más recursos
docker-compose up -d backend --cpus=2 --memory=2g
```

### 3. **Independencia Tecnológica**
```
Frontend puede migrar a:     Backend permanece en:
- React                      - Python/FastAPI
- Vue.js                     - O migrar a Node.js después
- Svelte                     - O a Rust, Go, Java, etc.
- Angular                    
```

### 4. **Facilita Testing**
```
# Test frontend independiente
docker-compose run frontend npm test

# Test backend independiente  
docker-compose run backend pytest

# Test integración con ambos
docker-compose up && npm run e2e
```

## Cómo Ejecutar

### Opción 1: Con Docker Compose (RECOMENDADO)

```bash
cd Unilab-SW

# Build e inicia todos los servicios
docker-compose up --build

# El dashboard estará en http://localhost
# Backend en http://localhost:8000
```

### Opción 2: Backend solo (Desarrollo)

```bash
# Terminal 1: Backend
cd Unilab-SW
python -m pip install -r requirements.txt
uvicorn unilab.core.app:app --reload

# Terminal 2: Frontend (desarrollo local)
cd Unilab-SW/frontend
python -m http.server 8080
# http://localhost:8080
```

## Comunicación entre Servicios

### Dentro de Docker Compose

```javascript
// Frontend habla con Backend
const API_BASE_URL = 'http://backend:8000';

// Nginx redirecciona /api/* a backend:8000
location /api/ {
    proxy_pass http://backend;
}
```

### En Producción

```javascript
// Usar URLs del dominio real
const API_BASE_URL = 'https://api.tudominio.com';
```

## Próximas Fases de Migración

### Fase 2: API Gateway (Próxima)
```
Frontend → API Gateway → Servicios
           (Kong/FastAPI)
           - Routing
           - Rate limiting
           - Autenticación
```

### Fase 3: Separar Servicios por Dominio
```
Frontend → API Gateway
           ├── TelemetryService (Python/FastAPI)
           ├── EventService (Node.js/Express)
           ├── StorageService (Go/Rust)
           └── AuthService (Java/Spring)
```

### Fase 4: Event-Driven
```
ESP32 → UDP → TelemetryService → Event Bus (RabbitMQ/Kafka)
                                   ├→ Storage
                                   ├→ Safety Manager
                                   └→ Notification Service
```

## Monitoreo y Logging

### Logs de Servicios

```bash
# Ver logs de todos
docker-compose logs -f

# Ver logs específicos
docker-compose logs -f frontend
docker-compose logs -f backend

# Con filtro
docker-compose logs backend | grep ERROR
```

### Health Checks

```bash
# Frontend
curl http://localhost/health

# Backend
curl http://localhost:8000/api/status

# Ambos
docker-compose ps
```

## Configuring Resources

### docker-compose.yml

```yaml
services:
  frontend:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M
        reservations:
          cpus: '0.25'
          memory: 128M

  backend:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
```

## Seguridad

### CORS

Frontend puede estar en dominio diferente, agregar a backend:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://tudominio.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

### Network Isolation

```yaml
networks:
  unilab-network:
    driver: bridge
    # Servicios en esta network solo hablan entre ellos
```

## Troubleshooting

### Frontend no conecta con Backend

```bash
# Verificar conectividad dentro del contenedor
docker-compose exec frontend curl http://backend:8000/api/status

# Ver logs
docker-compose logs backend
```

### Puertos en uso

```bash
# Liberar puerto 80 (si Nginx/Apache lo ocupa)
sudo systemctl stop apache2
sudo systemctl stop nginx

# O cambiar en docker-compose.yml
ports:
  - "8080:80"  # Cambiar de 80 a 8080
```

### Rebuild después de cambios

```bash
# Rebuild solo frontend
docker-compose build frontend

# Rebuild todo
docker-compose up --build
```

## Métricas

Ver consumo de recursos:

```bash
docker stats
```

Esperado:
```
CONTAINER         CPU %  MEM USAGE
unilab-frontend   <1%    ~50MB
unilab-backend    5-15%  ~200-400MB
unilab-storage    <1%    ~100MB
```

## Conclusión

Fase 1 completada: **Frontend como microservicio independiente** ✅

- Frontend containerizado con Nginx
- Separado del backend
- Listo para escalabilidad
- Preparado para futuras migraciones tecnológicas

Próximo paso: Crear API Gateway y separar servicios backend por dominio.

---

**Documentación**: [Ver README.md](README.md)  
**Tecnologías**: Docker, Docker Compose, Nginx, FastAPI, Python  
**Estado**: Producción lista
