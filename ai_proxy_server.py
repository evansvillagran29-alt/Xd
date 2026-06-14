from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

# Configuración de las API Keys (¡REEMPLAZA CON TUS CLAVES REALES!)
# ADVERTENCIA: NUNCA expongas estas claves directamente en un entorno de producción sin una gestión de secretos adecuada.
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "TU_API_KEY_DE_GEMINI_AQUI")
GROK_API_KEY = os.environ.get("GROK_API_KEY", "TU_API_KEY_DE_GROK_AQUI")
CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY", "TU_API_KEY_DE_CLAUDE_AQUI")
DALL_E_API_KEY = os.environ.get("DALL_E_API_KEY", "TU_API_KEY_DE_DALL_E_AQUI")

# URLs de las APIs (ejemplos, pueden variar)
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=" + GEMINI_API_KEY
# GROK_API_URL = "https://api.grok.com/v1/chat/completions" # URL hipotética
# CLAUDE_API_URL = "https://api.anthropic.com/v1/messages" # URL hipotética
DALL_E_API_URL = "https://api.openai.com/v1/images/generations"

# Función de moderación de contenido (ejemplo básico)
def moderate_content(text):
    # Esta es una implementación MUY BÁSICA. En un entorno real, usarías un servicio de moderación de contenido robusto.
    # Por ejemplo, la API de moderación de OpenAI, o un servicio similar.
    blocked_keywords = ["violencia", "odio", "ilegal", "sexo", "desnudo", "armas", "drogas"]
    for keyword in blocked_keywords:
        if keyword in text.lower():
            return True, f"Contenido detectado que viola las políticas: '{keyword}'"
    return False, None

# Función para obtener respuesta de Gemini
def get_gemini_response(prompt):
    if GEMINI_API_KEY == "TU_API_KEY_DE_GEMINI_AQUI":
        return "Error: La API Key de Gemini no está configurada en el proxy."
    
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
    try:
        response = requests.post(GEMINI_API_URL, headers=headers, json=data)
        response.raise_for_status() # Lanza una excepción para códigos de estado HTTP erróneos
        decoded_response = response.json()
        if decoded_response and decoded_response.get("candidates") and decoded_response["candidates"][0].get("content") and decoded_response["candidates"][0]["content"].get("parts") and decoded_response["candidates"][0]["content"]["parts"][0].get("text"):
            return decoded_response["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return f"Respuesta inesperada de Gemini: {decoded_response}"
    except requests.exceptions.RequestException as e:
        return f"Error al conectar con Gemini: {e}"
    except Exception as e:
        return f"Error al procesar respuesta de Gemini: {e}"

# Función para obtener respuesta de Grok (simulada)
def get_grok_response(prompt):
    # Grok no tiene una API pública y fácil de integrar como Gemini o Claude.
    # Esto es una simulación. En un caso real, necesitarías acceso a la API de Grok.
    return f"Grok (simulado): Entiendo que preguntaste sobre '{prompt}'. Actualmente, Grok no tiene una API pública para integración directa. "

# Función para obtener respuesta de Claude (simulada)
def get_claude_response(prompt):
    # Claude requiere una API Key y su integración es similar a Gemini/OpenAI.
    # Esto es una simulación. En un caso real, necesitarías acceso a la API de Claude.
    return f"Claude (simulado): Tu consulta '{prompt}' ha sido recibida. Para una respuesta real de Claude, se requiere una integración de API."

# Función para generar imagen con DALL-E
def get_dalle_image(prompt):
    if DALL_E_API_KEY == "TU_API_KEY_DE_DALL_E_AQUI":
        return "Error: La API Key de DALL-E no está configurada en el proxy."
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DALL_E_API_KEY}"
    }
    data = {
        "prompt": prompt,
        "n": 1,
        "size": "512x512"
    }
    try:
        response = requests.post(DALL_E_API_URL, headers=headers, json=data)
        response.raise_for_status()
        decoded_response = response.json()
        if decoded_response and decoded_response.get("data") and decoded_response["data"][0].get("url"):
            return decoded_response["data"][0]["url"]
        else:
            return f"Respuesta inesperada de DALL-E: {decoded_response}"
    except requests.exceptions.RequestException as e:
        return f"Error al conectar con DALL-E: {e}"
    except Exception as e:
        return f"Error al procesar respuesta de DALL-E: {e}"

@app.route('/ai-chat', methods=['POST'])
def ai_chat():
    data = request.json
    user_prompt = data.get('user_prompt', '')
    player_name = data.get('player_name', 'JugadorDesconocido')
    is_premium = data.get('is_premium', False)

    # Moderación de contenido antes de enviar a la IA
    is_blocked, reason = moderate_content(user_prompt)
    if is_blocked:
        return jsonify({"ai_response": f"Lo siento, tu mensaje contiene contenido inapropiado: {reason}. Por favor, reformula tu pregunta."})

    ai_response = ""
    # Lógica para seleccionar y orquestar modelos de IA
    # Esta es una lógica de ejemplo. Puedes hacerla tan compleja como quieras.
    if "imagen de" in user_prompt.lower() or "dalle" in user_prompt.lower():
        image_prompt = user_prompt.replace("imagen de", "").replace("dalle", "").strip()
        ai_response = get_dalle_image(image_prompt)
        if "Error" in ai_response: # Si DALL-E falla, intentar con Gemini
            ai_response = get_gemini_response(user_prompt)
    elseif "grok" in user_prompt.lower():
        ai_response = get_grok_response(user_prompt)
    elseif "claude" in user_prompt.lower():
        ai_response = get_claude_response(user_prompt)
    else:
        # Por defecto, usar Gemini para preguntas generales
        ai_response = get_gemini_response(user_prompt)

    return jsonify({"ai_response": ai_response})

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "message": "AI Proxy is running"})

if __name__ == '__main__':
    # Para desarrollo local, usa un puerto como 5000
    # En producción, usa un servidor WSGI como Gunicorn o uWSGI y un proxy inverso como Nginx.
    app.run(host='0.0.0.0', port=5000)
