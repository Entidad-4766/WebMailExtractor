from concurrent.futures import ThreadPoolExecutor
import random
import requests
from bs4 import BeautifulSoup, Comment
import re
import argparse
import logging
from queue import Queue
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Lista de 50 User-Agents
user_agents = [
"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/37.0.2062.94 Chrome/37.0.2062.94 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/600.8.9 (KHTML, like Gecko) Version/8.0.8 Safari/600.8.9",
    "Mozilla/5.0 (iPad; CPU OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H321 Safari/600.1.4",
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.10240",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/600.7.12 (KHTML, like Gecko) Version/8.0.7 Safari/600.7.12",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/600.8.9 (KHTML, like Gecko) Version/7.1.8 Safari/537.85.17",
    "Mozilla/5.0 (iPad; CPU OS 8_4 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H143 Safari/600.1.4",
    "Mozilla/5.0 (iPad; CPU OS 8_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12F69 Safari/600.1.4",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:39.0) Gecko/20100101 Firefox/39.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11) AppleWebKit/601.1.56 (KHTML, like Gecko) Version/9.0 Safari/601.1.56",
    "Mozilla/5.0 (Linux; U; Android 4.4.3; en-us; KFSOWI Build/KTU84M) AppleWebKit/537.36 (KHTML, like Gecko) Silk/3.68 like Chrome/39.0.2171.93 Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 5_1_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9B206 Safari/7534.48.3",
    "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 8_1_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12B435 Safari/600.1.4",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.10240",
    "Mozilla/5.0 (Windows NT 6.3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; Touch; LCJB; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; MDDRJS; rv:11.0) like Gecko",
    "Mozilla/5.0 (Linux; U; Android 4.4.3; en-us; KFAPWI Build/KTU84M) AppleWebKit/537.36 (KHTML, like Gecko) Silk/3.68 like Chrome/39.0.2171.93 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; Trident/7.0; Touch; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; LCJB; rv:11.0) like Gecko",
    "Mozilla/5.0 (Linux; U; Android 4.0.3; en-us; KFOT Build/IML74K) AppleWebKit/537.36 (KHTML, like Gecko) Silk/3.68 like Chrome/39.0.2171.93 Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 6_1_3 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10B329 Safari/8536.25",
    "Mozilla/5.0 (Linux; U; Android 4.4.3; en-us; KFARWI Build/KTU84M) AppleWebKit/537.36 (KHTML, like Gecko) Silk/3.68 like Chrome/39.0.2171.93 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; ASU2JS; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 7_0_2 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) Version/7.0 Mobile/11A501 Safari/9537.53",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; Touch; MAARJS; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 7_0 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) Version/7.0 Mobile/11A465 Safari/9537.53",
    "Mozilla/5.0 (Windows NT 10.0; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (iPad; CPU OS 8_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) GSA/7.0.55539 Mobile/12F69 Safari/600.1.4",
    "Mozillailla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.78.2 (KHTML, like Gecko) Version/7.0.6 Safari/537.78.2",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:36.0) Gecko/20100101 Firefox/36.0",
]

# Lista de valores para el header 'Accept'
accepts = [
    "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "application/json, text/javascript, */*; q=0.01",
    "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "application/json, text/javascript, */*; q=0.01",
    "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5",
    "text/html,application/xhtml+xml,application/xml;q=0.9;q=0.8",
    "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "application/signed-exchange;v=b3,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5",
    "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "application/json,text/javascript,application/xml;q=0.9,application/xhtml+xml,text/html;q=0.8",
    "image/webp,image/apng,image/*,*/*;q=0.8",
    "application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5",
    "application/json,application/xml;q=0.9,text/html;q=0.8,text/plain;q=0.7,*/*;q=0.6",
    "application/json,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5",
    "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8,image/png,image/jpeg,image/gif",
    "application/json,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "application/json,application/xml;q=0.9,text/html;q=0.8,text/plain;q=0.7,application/xhtml+xml,*/*;q=0.5",
    "text/plain,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "application/json,application/xml;q=0.9,text/html;q=0.8,application/xhtml+xml,*/*;q=0.7",
]

# Lista de valores para el header 'Accept-Language'
accept_languages = [
    "en-US,en;q=0.9",
    "es-ES,es;q=0.9,en;q=0.8",
    "fr-FR,fr;q=0.9,en;q=0.8",
    "de-DE,de;q=0.9,en;q=0.8",
    "zh-CN,zh;q=0.9,en;q=0.8",
    "en-GB,en;q=0.9",
    "pt-BR,pt;q=0.9,en;q=0.8",
    "it-IT,it;q=0.9,en;q=0.8",
    "ru-RU,ru;q=0.9,en;q=0.8",
    "ja-JP,ja;q=0.9,en;q=0.8",
    "ko-KR,ko;q=0.9,en;q=0.8",
    "ar-SA,ar;q=0.9,en;q=0.8",
    "nl-NL,nl;q=0.9,en;q=0.8",
    "sv-SE,sv;q=0.9,en;q=0.8",
    "en-AU,en;q=0.9",
    "no-NO,no;q=0.9,en;q=0.8",
    "tr-TR,tr;q=0.9,en;q=0.8",
    "pl-PL,pl;q=0.9,en;q=0.8",
    "fi-FI,fi;q=0.9,en;q=0.8",
    "da-DK,da;q=0.9,en;q=0.8",
]

# Lista de valores para el header 'Accept-Encoding'
accept_encodings = [
    "gzip, deflate, br",
    "gzip, deflate",
    "br",
    "gzip",
    "identity",
]

# Configuración del registro de errores
logging.basicConfig(filename='WebMailExtractor.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Inicializa una sesión de requests con reintentos y backoff exponencial
session = requests.Session()
retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
session.mount('http://', HTTPAdapter(max_retries=retries))
session.mount('https://', HTTPAdapter(max_retries=retries))

def seleccionar_headers_aleatorios():
    return {
        "User-Agent": random.choice(user_agents),
        "Accept": random.choice(accepts),
        "Accept-Language": random.choice(accept_languages),
        "Accept-Encoding": random.choice(accept_encodings)
    }

def es_url_valida(url):
    headers = seleccionar_headers_aleatorios()
    try:
        resultado = session.get(url, headers=headers, timeout=10)  # Timeout de 10 segundos
        return resultado.status_code in [200, 301, 302]
    except requests.RequestException as e:
        logging.exception(f"Error al validar la URL: {e}")
        return False

def descargar_y_guardar_html(url, filename="pagina_descargada.html"):
    if not es_url_valida(url):
        logging.error(f"URL no válida o inaccesible: {url}")
        return False

    headers = seleccionar_headers_aleatorios()
    try:
        respuesta = session.get(url, headers=headers, timeout=10)  # Timeout de 10 segundos
        # Aquí puedes agregar validaciones adicionales sobre la respuesta si es necesario
        with open(filename, "w", encoding="utf-8") as file:
            file.write(respuesta.text)
        return True
    except requests.RequestException as e:
        logging.exception(f"Error en la solicitud HTTP: {e}")
        return False
    except Exception as e:
        logging.exception(f"Error inesperado: {e}")
        return False

def extraer_correos_de_html(filename):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            html = file.read()
            correos = re.findall(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}', html)
            return correos
    except Exception as e:
        logging.exception(f"Error al leer o procesar el archivo HTML: {e}")
        return []

def extraer_correos_de_atributos_html(soup):
    correos = set()
    for tag in soup.find_all(href=True):
        if "mailto:" in tag['href']:
            correo = tag['href'].split(':')[1]
            correos.add(correo)
    return list(correos)

def extraer_correos_nivel_intermedio(filename):
    correos = []
    try:
        with open(filename, "r", encoding="utf-8") as file:
            html = file.read()
            soup = BeautifulSoup(html, 'html.parser')
            correos.extend(re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', html))
            correos.extend(extraer_correos_de_atributos_html(soup))
    except Exception as e:
        logging.exception(f"Error durante la extracción nivel intermedio: {e}")
    return correos

def extraer_correos_de_comentarios(soup):
    correos = set()
    comentarios = soup.find_all(string=lambda text: isinstance(text, Comment))
    for comentario in comentarios:
        correos.update(re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', comentario))
    return list(correos)

def extraer_correos_de_scripts(soup):
    correos = set()
    scripts = soup.find_all('script')
    for script in scripts:
        correos.update(re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', script.text))
    return list(correos)

def extraer_correos_nivel_avanzado(filename):
    correos = []
    try:
        with open(filename, "r", encoding="utf-8") as file:
            html = file.read()
            soup = BeautifulSoup(html, 'html.parser')
            correos.extend(extraer_correos_de_html(filename))
            correos.extend(extraer_correos_de_comentarios(soup))
            correos.extend(extraer_correos_de_scripts(soup))
    except Exception as e:
        logging.exception(f"Error durante la extracción nivel avanzado: {e}")
    return correos

def procesar_url(url, nivel, queue):
    try:
        if descargar_y_guardar_html(url):
            correos = []
            if nivel == 1:
                correos = extraer_correos_de_html("pagina_descargada.html")
            elif nivel == 2:
                correos = extraer_correos_nivel_intermedio("pagina_descargada.html")
            elif nivel == 3:
                correos = extraer_correos_nivel_avanzado("pagina_descargada.html")

            for correo in set(correos):
                queue.put(correo)
    except Exception as e:
        logging.exception(f"Error procesando URL {url}: {e}")

def leer_urls_de_archivo(nombre_archivo):
    """Lee URLs de un archivo y devuelve una lista."""
    with open(nombre_archivo, 'r') as archivo:
        return [url.strip() for url in archivo.readlines()]

def main():
    try:
        parser = argparse.ArgumentParser(description='WebMailExtractor: Herramienta para extraer correos electrónicos de páginas web.')
        parser.add_argument('-u', '--urls', nargs='*', help='URLs de las páginas web para extraer correos electrónicos.')
        parser.add_argument('-f', '--archivo', help='Archivo que contiene URLs para procesar.')
        parser.add_argument('-n', '--nivel', type=int, choices=[1, 2, 3], default=1, help='Nivel de extracción: 1-Básico, 2-Intermedio, 3-Avanzado')
        args = parser.parse_args()

        urls = args.urls if args.urls else leer_urls_de_archivo(args.archivo) if args.archivo else []
        queue = Queue()

        with ThreadPoolExecutor(max_workers=5) as executor:
            for url in urls:
                executor.submit(procesar_url, url, args.nivel, queue)

        while not queue.empty():
            print(queue.get())
    except Exception as e:
        logging.exception(f"Error inesperado en la ejecución del programa: {e}")

if __name__ == "__main__":
    main()
