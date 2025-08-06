import os
import requests
import time

# 🔐 TOKEN del bot (configurado como variable de entorno en Railway)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# 🏘️ Lista de comunidades con su chat_id y nombre
comunidades = {
    "-1002585455176": "brisas",
    "-1002594518135": "mosca",
    "-1002886664361": "mosca2",
    "-1002773966470": "miraflores",
    "-1002780392932": "sos",
    "-1002735693923": "avion"
}

# 🌐 URL base de tu WebApp
BASE_URL = "https://alarma-production.up.railway.app"

# 📤 Enviar botón adecuado según el tipo de chat
def enviar_boton(chat_id, nombre, chat_type):
    url_webapp = f"{BASE_URL}/?comunidad={nombre}"

    if chat_type == "private":
        # ✅ WebApp button (solo en privado)
        reply_markup = {
            "keyboard": [[{
                "text": "🚨 ABRIR ALARMA VECINAL",
                "web_app": {
                    "url": url_webapp
                }
            }]],
            "resize_keyboard": True,
            "one_time_keyboard": False
        }
    else:
        # ✅ Botón tipo inline URL (válido en grupos)
        reply_markup = {
            "inline_keyboard": [[{
                "text": "🚨 ABRIR ALARMA VECINAL",
                "url": url_webapp
            }]]
        }

    payload = {
        "chat_id": chat_id,
        "text": f"🚨 Abre la alarma de la comunidad: {nombre.upper()}",
        "reply_markup": reply_markup
    }

    response = requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
        json=payload
    )

    if response.ok:
        print(f"✅ Botón enviado para {nombre} en {chat_type}")
    else:
        print(f"❌ Error al enviar botón para {nombre}: {response.text}")

# 🔄 Obtener actualizaciones del bot
def obtener_actualizaciones(offset=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    params = {"timeout": 30}
    if offset:
        params["offset"] = offset
    response = requests.get(url, params=params)
    return response.json()

# 🚀 Loop principal
def main():
    last_update_id = None
    while True:
        data = obtener_actualizaciones(last_update_id)
        for update in data.get("result", []):
            last_update_id = update["update_id"] + 1
            message = update.get("message") or update.get("edited_message")
            if not message:
                continue

            text = message.get("text", "").lower()
            chat = message.get("chat", {})
            chat_id = str(chat.get("id"))
            chat_type = chat.get("type")

            if text == "sos" and chat_id in comunidades:
                nombre = comunidades[chat_id]
                enviar_boton(chat_id, nombre, chat_type)

        time.sleep(2)

if __name__ == "__main__":
    main()
