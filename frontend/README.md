# UniLab Frontend - Microservicio

Frontend moderno para UniLab Dashboard, separado como microservicio independiente containerizado con Nginx.

## Características

✅ **Diseño Responsivo** - Se adapta a dispositivos móviles y escritorio  
✅ **Interfaz Moderna** - CSS moderno con variables CSS personalizables  
✅ **Comunicación con API** - Conecta automáticamente con el backend  
✅ **Gráficos en Tiempo Real** - Visualización de telemetría con Chart.js  
✅ **Manejo de Errores** - Notificaciones claras y recuperación de fallos  
✅ **Auto-refresh** - Actualización automática de datos cada 3 segundos  

## Estructura

```
frontend/
├── index.html          # Template principal
├── styles.css          # Estilos modernos
├── app.js              # Lógica del cliente
├── package.json        # Dependencias (Node.js)
├── Dockerfile          # Imagen Docker
├── nginx.conf          # Configuración Nginx
├── .dockerignore       # Archivos a ignorar en Docker
└── README.md           # Este archivo
```

## Tecnologías

- **HTML5** - Estructura semántica
- **CSS3** - Grid, Flexbox, animaciones
- **JavaScript Vanilla** - Sin dependencias frontend
- **Nginx** - Servidor web de alto rendimiento
- **Docker** - Containerización
- **Chart.js** - Gráficos interactivos

## Configuración

### Variables de Entorno

En `app.js`:

```javascript
const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';
const REFRESH_INTERVAL = 3000; // ms
```

En Docker Compose, se configura como:

```yaml
environment:
  - API_BASE_URL=http://backend:8000
```

## Desarrollo Local

### Opción 1: Con Nginx local

```bash
# Instalar Nginx en tu sistema
# En Windows: descargar de https://nginx.org/en/download.html
# En macOS: brew install nginx
# En Linux: apt install nginx

# Copiar nginx.conf
cp nginx.conf /etc/nginx/nginx.conf

# Iniciar Nginx
nginx

# Acceder a http://localhost
```

### Opción 2: Con Node.js HTTP Server

```bash
npm install -g http-server
http-server . -p 8080
# Acceder a http://localhost:8080
```

### Opción 3: Con Python Simple Server

```bash
python -m http.server 8000
# Acceder a http://localhost:8000
```

## Deployment con Docker

### Build

```bash
# Desde la raíz del proyecto
docker build -f frontend/Dockerfile -t unilab-frontend:latest ./frontend
```

### Run Individual

```bash
docker run -d \
  --name unilab-frontend \
  -p 80:80 \
  -e API_BASE_URL=http://backend:8000 \
  unilab-frontend:latest
```

### Con Docker Compose (Recomendado)

```bash
# Desde la raíz del proyecto
docker-compose up -d

# Ver logs
docker-compose logs -f frontend

# Detener
docker-compose down
```

## Endpoints API Esperados

El frontend espera que el backend expose estos endpoints:

- `GET /api/status` - Estado del sistema
- `GET /api/latest-packet` - Último paquete de telemetría
- `GET /api/recent-packets?limit=10` - Historial de paquetes
- `GET /api/recent-events?limit=10` - Eventos del sistema
- `GET /api/variables` - Variables disponibles
- `GET /api/visible-variables` - Variables configuradas
- `POST /api/clear` - Limpiar almacenamiento
- `POST /api/visible-variables` - Guardar variables seleccionadas

## Mejoras Implementadas vs Original

| Aspecto | Original | Mejorado |
|--------|----------|----------|
| **Navbar** | Mixto | Sticky con estado de conexión |
| **Estilos** | Básico | Moderno con variables CSS |
| **Responsive** | Limitado | Completamente responsive |
| **Formularios** | Simple | Con validación y feedback |
| **Errores** | Silent | Notificaciones claras |
| **Gráficos** | Canvas vacío | Chart.js con datos reales |
| **Auto-refresh** | Manual | Automático cada 3s |
| **Accesibilidad** | Mínima | Mejorada con ARIA labels |
| **Performance** | Estándar | Optimizado con caching |

## CORS

Si necesitas acceder desde otro dominio, configura CORS en el backend:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:80"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Health Check

El frontend responde a:

```bash
curl http://localhost/health
# Respuesta: healthy
```

## Troubleshooting

### "Cannot connect to backend"

1. Verifica que el backend está corriendo: `curl http://backend:8000/api/status`
2. Revisa la configuración de `API_BASE_URL` en `app.js`
3. Verifica la conectividad de red en Docker Compose

### "Sin datos disponibles"

1. Asegúrate de que el backend está recibiendo datos
2. Revisa los logs: `docker-compose logs backend`
3. Limpia el almacenamiento y reinicia

### Gráfico vacío

1. Verificar que hay paquetes recibidos
2. Revisar que las variables están siendo enviadas correctamente
3. Abrir consola del navegador (F12) para ver errores

## Licencia

MIT

## Próximas Fases

- [ ] Migrar a React/Vue.js para mejor mantenibilidad
- [ ] Agregar WebSockets para tiempo real
- [ ] Sistema de alertas push
- [ ] Exportación de reportes (PDF/CSV)
- [ ] Temas oscuros/claros
- [ ] Autenticación y autorización
