# Scrappy Instagram
Este proyecto trata sobre **Web Scraping** desarrollado para extraer y analizar datos de perfiles públicos de Instagram. El sistema utiliza una arquitectura robusta para superar las barreras de renderizado dinámico y seguridad de la plataforma.

## Características Técnicas
- **Extracción de Metadatos**: Captura las últimas 10 publicaciones, incluyendo enlaces directos e imágenes.
- **Análisis de Contenido**: Procesamiento de descripciones para identificar los 5 Hashtags más usados y los 6 Emojis más frecuentes.
- **Dashboard en Tiempo Real**: Interfaz web dinámica que muestra el conteo de seguidores y estadísticas del perfil.
- **Funcionalidad de Descarga**: Acceso directo a las fuentes de imagen para almacenamiento local.

## Lógica y Estrategia de Scraping

### 1. Análisis de Solicitudes Web
A diferencia de los sitios estáticos, Instagram utiliza **Client-Side Rendering (CSR)**. El análisis de tráfico de red determinó que la información no está presente en el código fuente inicial. Por ello, se implementó **Playwright** para emular un motor de navegación que ejecute el JavaScript necesario para renderizar los elementos.

### 2. Estrategia Anti-Bloqueo
Para evitar la detección automática, se diseñó la siguiente estrategia:
* **Gestión de Sesiones**: Uso de un archivo `cookies.json` para inyectar sesiones auténticas, evitando peticiones anónimas que disparan sistemas de seguridad (Rate Limiting).
* **Human Emulation**: Implementación de `slow_mo` y desplazamientos de ratón (`mouse.wheel`) para simular la navegación de un usuario real.
* **User-Agent Spoofing**: Configuración de encabezados de navegador moderno para evitar la identificación como un agente de automatización básico.

### 3. Manejo de Lazy Loading
Se implementó un **bucle de scroll dinámico** que monitorea la cantidad de nodos `<a>` presentes en el DOM. El script continúa el desplazamiento hasta asegurar la carga de al menos 10 elementos válidos, garantizando la integridad de los datos en conexiones de red variables.

## Instalación

Siga estos pasos para desplegar el proyecto en un entorno local:

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/Johnale22/ScrappyInstagram.git
   cd nombre-del-repo