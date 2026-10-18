"""
main.py
Requiere una variable de entorno GEMINI_API_KEY (en un archivo .env).
"""

from google import genai
from dotenv import load_dotenv #Este paquete permite leer variables de entorno desde un archivo .env

from agent import Agent, MORADO, RESET

load_dotenv()

MODEL = "gemini-3.7-flash"

print("Agentita")
print("Escribe 'salir' para terminar.\n")

client = genai.Client()
agent = Agent()

while True:
    max_iter = 3
    iter = 0
                                       
    user_input = input(f"{MORADO}Tú:{RESET} ").strip()

    if not user_input:
        continue
    if user_input.lower() in ("salir", "exit", "bye", "sayonara", "adiós", "hasta luego","chao","nos vemos","hasta la próxima"):
        print("Que la suerte siempre esté de tu lado!")
        break

    agent.add_user_message(user_input)

    while True and iter < max_iter:                             
        interaction = client.interactions.create(
            model=MODEL,
            store=False,                      # la memoria se maneja desde el agente
            system_instruction=Agent.SYSTEM_PROMPT,
            input=agent.history,
            tools=agent.tools,
        )
        if not agent.process_interaction(interaction):
            break                             # no pidió herramientas, termino.
        iter += 1

    else: 
        print("Llegamos al límite de iteraciones para este mensaje," \
        "¿quieres seguir? :)")