import requests
import logging
from PIL import Image
from io import BytesIO
import time
import torch

# Configurar el registro
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración del bot de Telegram
TOKEN = '7289735023:AAHQU3xMDBE4GgvbbmqvqCui8CsclmUvmbw'
API_URL = "https://api-inference.huggingface.co/models/ZB-Tech/Text-to-Image"
API_TOKEN = "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"
headers = {"Authorization": f"Bearer {API_TOKEN}"}

# Ruta al modelo local
MODEL_PATH = "C:/Users/Sanny/remove-clothes.safetensors"

def generate_image_from_text(text, target_width, target_height):
    """
    Genera una imagen a partir de texto utilizando la API de Hugging Face y la ajusta a las dimensiones especificadas.
    """
    try:
        response = requests.post(API_URL, headers=headers, json={"inputs": text, "parameters": {"output_resolution": [target_height, target_width]}})
        response.raise_for_status()
        image_bytes = response.content
        image = Image.open(BytesIO(image_bytes))
        return image
    except Exception as e:
        logger.error(f"Error al generar la imagen desde el texto: {e}")
        return None

def send_photo(chat_id, photo):
    """
    Envía una foto al chat de Telegram.
    """
    try:
        # Convertir la imagen a bytes
        img_byte_arr = BytesIO()
        photo.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        files = {'photo': ('image.jpg', img_byte_arr, 'image/jpeg')}
        requests.post(f'https://api.telegram.org/bot{TOKEN}/sendPhoto', data={'chat_id': chat_id}, files=files)
    except Exception as e:
        logger.error(f"Error al enviar la foto: {e}")

def send_message(chat_id, message):
    """
    Envía un mensaje al chat de Telegram.
    """
    try:
        requests.post(f'https://api.telegram.org/bot{TOKEN}/sendMessage', data={'chat_id': chat_id, 'text': message})
    except Exception as e:
        logger.error(f"Error al enviar el mensaje: {e}")

def process_message(update):
    """
    Procesa el mensaje recibido y envía la imagen generada como respuesta.
    """
    # Obtener el mensaje del usuario
    user_message = update['message'].get('text')
    user_photo = update['message'].get('photo')

    # Dimensiones objetivo
    target_width = 512
    target_height = 1024

    # Si el mensaje es texto
    if user_message:
        # Enviar mensaje de espera
        send_message(update['message']['chat']['id'], "Me llevare tu alma😈 Mientras Esperas...")

        # Generar la imagen correspondiente al mensaje
        generated_image = generate_image_from_text(user_message, target_width, target_height)

        if generated_image:
            # Enviar la imagen al usuario
            send_photo(update['message']['chat']['id'], generated_image)
        else:
            # Enviar un mensaje de error
            send_message(update['message']['chat']['id'], "Lo siento, no se pudo generar la imagen.")

    # Si se envió una foto
    elif user_photo:
        # Descargar la foto
        photo_id = user_photo[-1]['file_id']
        file = requests.get(f'https://api.telegram.org/bot{TOKEN}/getFile', params={'file_id': photo_id}).json()
        file_path = file['result']['file_path']
        photo_url = f'https://api.telegram.org/file/bot{TOKEN}/{file_path}'
        photo_response = requests.get(photo_url)

        if photo_response.status_code == 200:
            # Procesar la imagen
            modified_image = process_photo(photo_response.content)
            
            if modified_image:
                # Enviar la imagen modificada al usuario
                send_photo(update['message']['chat']['id'], modified_image)
            else:
                send_message(update['message']['chat']['id'], "Error al procesar la imagen.")
        else:
            send_message(update['message']['chat']['id'], "Error al descargar la imagen.")

def process_photo(photo_bytes):
    """
    Procesa la imagen recibida utilizando un modelo local para modificarla.
    """
    try:
        # Cargar el modelo local
        model = torch.load(MODEL_PATH)

        # Preprocesar la imagen
        image = Image.open(BytesIO(photo_bytes))

        # Aplicar el modelo para modificar la imagen
        # Aquí deberías agregar tu lógica para aplicar el modelo a la imagen

        # Por ahora, simplemente devolvemos la imagen original
        return image
    except Exception as e:
        logger.error(f"Error al procesar la imagen: {e}")
        return None

def get_updates(offset=None):
    """
    Obtiene las actualizaciones del bot de Telegram.
    """
    try:
        response = requests.get(f'https://api.telegram.org/bot{TOKEN}/getUpdates', params={'offset': offset})
        response.raise_for_status()
        return response.json()['result']
    except Exception as e:
        logger.error(f"Error al obtener las actualizaciones: {e}")
        return []

def main():
    """
    Función principal para manejar las actualizaciones de Telegram.
    """
    offset = None
    while True:
        # Obtener y procesar las actualizaciones
        updates = get_updates(offset)
        for update in updates:
            process_message(update)
            offset = update['update_id'] + 1

if __name__ == '__main__':
    main()
