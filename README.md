# UniLab SW

Repositorio base del software de **UniLab**, una plataforma modular para coordinar experimentos, adquisición de datos, simulación, almacenamiento, reportes, web backend e integración futura con SiLA.

Esta primera versión contiene la base desarrollada por la **Persona 1: Arquitectura, Contratos y Core**.

---

## Objetivo del repositorio

Este repositorio busca establecer una arquitectura común para que cada integrante del equipo pueda trabajar en su propio módulo sin romper la integración general del sistema.

La idea principal es que todos los módulos usen contratos compartidos, interfaces claras y una estructura ordenada.

---

## Estructura actual del proyecto

```txt
unilab/
├── __init__.py
├── contracts/
│   ├── __init__.py
│   ├── models.py
│   ├── protocols.py
│   └── events.py
│
├── core/
│   ├── __init__.py
│   ├── app.py
│   ├── registry.py
│   ├── module_loader.py
│   └── experiment_service.py
│
├── config/
│   ├── __init__.py
│   └── settings.py
│
tests/
├── test_contracts.py
└── test_core.py
```


---

## Módulos principales

### `unilab/contracts/`

Contiene los contratos comunes del sistema:

- Modelos de datos compartidos.
- Eventos del sistema.
- Protocolos o interfaces base.

Estos archivos deben ser usados por los demás módulos para mantener compatibilidad entre instrumentos, adquisición, simulación, scheduler, storage, web y SiLA.

### `unilab/core/`

Contiene el núcleo de la aplicación:

- Registro de módulos.
- Carga dinámica de componentes.
- Servicio principal de experimentos.
- Aplicación central `UniLabApp`.

El core funciona como punto de coordinación del sistema.

### `unilab/config/`

Contiene la configuración global del proyecto.

### `tests/`

Contiene pruebas unitarias usando `pytest`.

---

## Requisitos

Se recomienda usar:

```txt
Python 3.11 o superior
```

El proyecto fue probado inicialmente con:

```txt
Python 3.14
pytest 9.0.3
```

---

## Cómo clonar el repositorio

```bash
git clone URL_DEL_REPOSITORIO
cd "Proyecto SW"
```

Ejemplo:

```bash
git clone https://github.com/tu_usuario/unilab-sw.git
cd unilab-sw
```

---

## Crear entorno virtual

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### Windows CMD

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Cuando el entorno esté activado, debería aparecer algo similar a:

```txt
(.venv)
```

---

## Instalar dependencias

Con el entorno virtual activado:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

---

## Ejecutar pruebas

Desde la raíz del proyecto:

```bash
python -m pytest
```

Si todo está correcto, deberían ejecutarse las pruebas de:

```txt
tests/test_contracts.py
tests/test_core.py
```

---

## Verificar que el paquete se puede importar

Desde la raíz del proyecto:

```bash
python -c "import unilab; print(unilab)"
```

Debería mostrarse una ruta similar a:

```txt
<module 'unilab' from '.../unilab/__init__.py'>
```

---

## Flujo de trabajo recomendado

Antes de empezar a trabajar, actualizar la rama principal:

```bash
git checkout main
git pull origin main
```

Crear una rama nueva según el módulo asignado:

```bash
git checkout -b persona-2-instrumentos
```

Ejemplos de nombres de ramas:

```txt
persona-2-instrumentos
persona-3-scheduler
persona-4-storage-web
fix-tests
docs-readme
```

Después de hacer cambios:

```bash
python -m pytest
git status
git add .
git commit -m "Descripción breve del cambio"
git push -u origin nombre-de-la-rama
```

Luego crear un **Pull Request** en GitHub hacia la rama `main`.

---

## Reglas básicas para contribuir

1. No subir el entorno virtual `.venv/`.
2. No subir archivos temporales de Python como `__pycache__/`.
3. Antes de subir cambios, ejecutar:

```bash
python -m pytest
```

4. Si se agrega una librería nueva, actualizar `requirements.txt`:

```bash
python -m pip freeze > requirements.txt
```

5. Mantener los módulos separados según la responsabilidad de cada persona.
6. No modificar contratos comunes sin avisar al equipo, porque otros módulos dependen de ellos.

---

## Distribución inicial del trabajo

### Persona 1: Arquitectura, contratos y core

Carpetas principales:

```txt
unilab/contracts/
unilab/core/
unilab/config/
tests/
```

Responsabilidades:

- Definir modelos de datos.
- Definir eventos.
- Definir protocolos base.
- Implementar el registro de módulos.
- Implementar el core principal.
- Implementar pruebas unitarias del core y contratos.

---

### Persona 2: Instrumentos y adquisición

Carpetas sugeridas:

```txt
unilab/modules/instruments/
unilab/modules/acquisition/
tests/
```

Archivos sugeridos:

```txt
modules/instruments/base.py
modules/instruments/mock.py
modules/instruments/serial_json.py

modules/acquisition/base.py
modules/acquisition/udp_receiver.py
modules/acquisition/tcp_receiver.py
modules/acquisition/file_receiver.py

tests/test_instruments.py
tests/test_acquisition.py
```

---

### Persona 3: Perfiles, simulación y scheduler

Carpetas sugeridas:

```txt
unilab/modules/profiles/
unilab/modules/simulation/
unilab/modules/scheduler/
tests/
```

Archivos sugeridos:

```txt
modules/profiles/base.py
modules/profiles/waveforms.py
modules/profiles/validators.py

modules/simulation/base.py
modules/simulation/simple_model.py

modules/scheduler/experiment_plan.py
modules/scheduler/executor.py
modules/scheduler/scheduler.py

tests/test_profiles.py
tests/test_simulation.py
tests/test_scheduler.py
```

---

### Persona 4: Safety, storage, reports, web y SiLA

Carpetas sugeridas:

```txt
unilab/modules/safety/
unilab/modules/storage/
unilab/modules/reports/
unilab/modules/web/
unilab/modules/sila/
tests/
```

Archivos sugeridos:

```txt
modules/safety/manager.py
modules/safety/rules.py
modules/safety/faults.py
modules/safety/watchdog.py

modules/storage/database.py
modules/storage/repositories.py

modules/reports/csv_report.py
modules/reports/html_report.py
modules/reports/templates/basic_report.html

modules/web/api.py
modules/web/schemas.py
modules/web/routes/status.py
modules/web/routes/experiments.py
modules/web/routes/telemetry.py
modules/web/routes/reports.py
modules/web/routes/safety.py

modules/sila/features/
modules/sila/adapters.py
modules/sila/server.py

tests/test_safety.py
tests/test_storage.py
tests/test_reports.py
tests/test_web.py
```

---

## Convención de imports

Se recomienda importar desde el paquete `unilab`.

Ejemplo:

```python
from unilab.contracts.models import Measurement, Command
from unilab.core.app import UniLabApp
```

Evitar imports relativos complicados entre módulos.

---

## Estado actual

Actualmente el proyecto incluye:

- Contratos base.
- Core inicial.
- Configuración inicial.
- Pruebas unitarias para contratos y core.

El siguiente paso es que cada integrante cree su propia rama y avance con el módulo asignado.

---

## Comando rápido para nuevos integrantes

```bash
git clone URL_DEL_REPOSITORIO
cd unilab-sw
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pytest
```

En Linux/macOS reemplazar la activación del entorno por:

```bash
source .venv/bin/activate
```

---

## `.gitignore` recomendado

El archivo `.gitignore` debería incluir como mínimo:

```gitignore
.venv/
__pycache__/
*.pyc
.pytest_cache/
.env
.DS_Store
.vscode/
.idea/
```


### Texto para validar que Jenkins funciona
## Hola mundo

### Texto para validar que jenkins funciona otra vez 

### Texto para validar que jenkins funciona una vez más

### Texto para validar que jenkins funciona una vez +++++

### hola