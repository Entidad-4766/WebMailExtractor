# Extractor de Correos Electrónicos WebMailExtractor
# WebMailExtractor
WebMailExtractor es una herramienta de Python diseñada para extraer direcciones de correo electrónico de páginas web. Actualmente, el proyecto está en desarrollo y se espera agregar más funcionalidades en el futuro.

## Estado Actual del Codigo
El proyecto actualmente es capaz de realizar las siguientes tareas:
- **Extracción de Direcciones de Correo Electrónico**: Utiliza expresiones regulares y BeautifulSoup para extraer direcciones de correo electrónico de páginas web. Esto incluye correos encontrados directamente en el texto HTML, así como aquellos presentes en atributos de etiquetas (como enlaces `mailto:`) y dentro de comentarios y scripts.

- **Selección Aleatoria de Headers HTTP**: Para simular diferentes navegadores y evitar posibles bloqueos por parte de los servidores web, el script selecciona aleatoriamente User-Agents y otros headers HTTP de una lista predefinida.

- **Manejo de Sesiones HTTP con Reintentos**: Implementa una sesión de `requests` con una política de reintentos y backoff exponencial para manejar respuestas de error temporales y limitaciones de tasa impuestas por servidores web.

- **Validación de URLs**: Antes de intentar extraer correos electrónicos, el script verifica si las URLs proporcionadas son accesibles y devuelven un código de estado HTTP válido.

- **Registro de Actividades y Errores**: Utiliza el módulo de logging de Python para registrar eventos importantes y errores durante la ejecución del script, facilitando la depuración y el seguimiento de la actividad.

- **Interfaz de Línea de Comandos**: Permite al usuario especificar URLs directamente a través de la línea de comandos o cargarlas desde un archivo, además de elegir el nivel de extracción de correos electrónicos (básico, intermedio, avanzado).

Este script representa una base sólida para una herramienta de extracción de correos electrónicos, con funcionalidades clave ya implementadas y funcionando. El enfoque en la aleatorización de headers y el manejo cuidadoso de las sesiones HTTP muestra una consideración por la eficiencia y la discreción en la recopilación de datos.

## Funcionalidades Futuras del Codigo
- Mejorar el manejo de excepciones y la validación de entradas.
- Implementar la extracción de correos electrónicos de dominios específicos.
- Optimización del rendimiento y la eficiencia del código.
- Extraer correos de manera recursiva
- Almacenamiento y exportacion de datos
- Throttling y Gestión de la Velocidad de Solicitud
- Opciones de Personalización para el Usuario
