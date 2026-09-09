"""
agent.py

Tres módulos principales:
  1. Memoria      -> self.history
  2. Herramientas -> self.tools (lo que el modelo ve) + los métodos que las ejecutan
  3. Decisión     -> process_interaction() revisa si el modelo pidió una herramienta

"""

import os
import json
import datetime


DATE_FORMAT = "%d-%m-%Y %H:%M"


class Agent:

    SYSTEM_PROMPT = (
        "Eres una asistente muy amable e inteligente que habla español y es concisa."
        "Si un pendiente ya venció, pregunta a la usuaria si lo completó en cuyo caso"
        "debes borrar el pendiente y si no, ofrecele ayuda con ese pendiente."
    )

    def __init__(self, to_do_file="reminders.json"):
        self.setup_tools()
        self.history = []          # memoria de la conversación
        self.to_do_file = to_do_file
        self.tasks = self.load_jsons()

    # ------------------------------------------------------------------
    # 1. Descripción de las herramientas que el modelo puede usar
    # ------------------------------------------------------------------
    def setup_tools(self):
        self.tools = [
            {
                "type": "function",
                "name": "list_files_in_dir",
                "description": (
                    "Lista los archivos que existen en un directorio dado "
                    "(por defecto es el directorio actual)"
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "directory": {
                            "type": "string",
                            "description": (
                                "Directorio para listar (opcional). "
                                "Por defecto es el directorio actual"
                            ),
                        }
                    },
                    "required": [],
                },
            },
            {
                "type": "function",
                "name": "read_file",
                "description": "Lee el contenido de un archivo en una ruta especificada",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "La ruta del archivo a leer",
                        }
                    },
                    "required": ["path"],
                },
            },
            {
                "type": "function",
                "name": "edit_file",
                "description": (
                    "Edita el contenido de un archivo reemplazando prev_text por "
                    "new_text. Crea el archivo si no existe."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "La ruta del archivo a editar",
                        },
                        "prev_text": {
                            "type": "string",
                            "description": (
                                "El texto que se va a buscar para reemplazar "
                                "(puede ser vacío para archivos nuevos)"
                            ),
                        },
                        "new_text": {
                            "type": "string",
                            "description": (
                                "El texto que reemplazará a prev_text "
                                "(o el texto para un archivo nuevo)"
                            ),
                        },
                    },
                    "required": ["path", "new_text"],
                },
            },
            {
                "type": "function",
                "name": "to_day",
                "description": "Consulta el día y hora actuales.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
            {
                "type": "function",
                "name": "to_do_tasks",
                "description": (
                    "Crea y elimina recordatorios en memoria local."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "fecha": {
                            "type": "string",
                            "description": (
                                "Fecha y hora del pendiente, formato "
                                "'DD-MM-YYYY HH:MM'"
                            ),
                        },
                        "reminder": {
                            "type": "string",
                            "description": "El texto que se va a recordar",
                        },
                    },
                    "required": ["fecha", "reminder"],
                },
            },
            {
                "type": "function",
                "name": "verify_task",
                "description": (
                    "Revisa la lista de pendientes y verifica"
                    "si siguen vigentes contrastando con el tiempo."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "actual": {
                            "type": "string",
                            "description": (
                                "Fecha y hora actual, obtenida por default"
                                "con herramienta 'to_day'."
                            ),
                        }
                    },
                    "required": [],
                },
            },
        ]

    # ------------------------------------------------------------------
    # 2. Implementación de las herramientas
    # ------------------------------------------------------------------
    def list_files_in_dir(self, directory="."):
        print("  [herramienta] list_files_in_dir")
        try:
            return {"files": os.listdir(directory)}
        except Exception as e:
            return {"error": str(e)}

    def read_file(self, path):
        print("  [herramienta] read_file")
        try:
            with open(path, encoding="utf-8") as f:
                return f.read()
        except Exception:
            err = f"Error al leer el archivo {path}"
            print(err)
            return err

    def edit_file(self, path, new_text, prev_text=""):
        print("  [herramienta] edit_file")
        try:
            existed = os.path.exists(path)
            if existed and prev_text:
                content = self.read_file(path)
                if prev_text not in content:
                    return f"Texto {prev_text} no encontrado en el archivo"
                content = content.replace(prev_text, new_text)
            else:
                dir_name = os.path.dirname(path)
                if dir_name:
                    os.makedirs(dir_name, exist_ok=True)
                content = new_text

            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

            action = "editado" if existed and prev_text else "creado"
            return f"Archivo {path} {action} exitosamente"
        except Exception:
            err = f"Error al crear o editar el archivo {path}"
            print(err)
            return err

    ########################### mis herramientas

    def load_jsons(self):
        """Lee archivos json."""
        if os.path.exists(self.to_do_file):
            try:
                with open(self.to_do_file, encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                return []
        return []

    def save_tasks(self):
        """Persiste la lista de pendientes en disco."""
        with open(self.to_do_file, "w", encoding="utf-8") as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=2)

    def to_day(self):
        print("  [herramienta] to_day")
        return {"fecha_hora_actual": datetime.datetime.now().strftime(DATE_FORMAT)}

    def to_do_tasks(self, reminder, fecha):
        print("  [herramienta] to_do_tasks")
        for task in self.tasks:
            if task["reminder"] == reminder and task["fecha"] == fecha:
                self.tasks.remove(task)
                self.save_tasks()
                return {"accion": "eliminado", "fecha": fecha, "reminder": reminder}

        self.tasks.append({"fecha": fecha, "reminder": reminder})
        self.save_tasks()
        return {"accion": "creado", "fecha": fecha, "reminder": reminder}

    def verify_task(self, actual=None):
        print("  [herramienta] verify_task")

        if actual:
            try:
                ahora = datetime.datetime.strptime(actual, DATE_FORMAT)
            except ValueError:
                ahora = datetime.datetime.now()
        else:
            ahora = datetime.datetime.now()

        vencidos = []
        vigentes = []
        for task in self.tasks:
            try:
                fecha_task = datetime.datetime.strptime(task["fecha"], DATE_FORMAT)
            except (ValueError, KeyError):
                continue
            if fecha_task <= ahora:
                vencidos.append(task)
            else:
                vigentes.append(task)

        return {"pendientes_vencidos": vencidos, "pendientes_vigentes": vigentes}

    ##########################

    def run_tool(self, name, args):
        if name == "list_files_in_dir":
            return self.list_files_in_dir(**args)
        if name == "read_file":
            return self.read_file(**args)
        if name == "edit_file":
            return self.edit_file(**args)
        if name == "to_day":
            return self.to_day(**args)
        if name == "to_do_tasks":
            return self.to_do_tasks(**args)
        if name == "verify_task":
            return self.verify_task(**args)
        return {"error": f"Herramienta desconocida: {name}"}

    # ------------------------------------------------------------------
    # 3. Memoria y decisión
    # ------------------------------------------------------------------
    def add_user_message(self, text):
        self.history.append(
            {"type": "user_input",
             "content": [{"type": "text", "text": text}]}
        )

    def process_interaction(self, interaction):
        """Devuelve True si el modelo pidió usar al menos una herramienta."""

        # a) Todo lo que produjo el modelo entra a la memoria
        for step in interaction.steps:
            self.history.append(step.model_dump())

        # b) ¿Pidió herramientas? Ejecutarlas y devolver el resultado
        called_tool = False
        for step in interaction.steps:
            if step.type != "function_call":
                continue

            called_tool = True
            args = step.arguments or {}
            print(f"  - El modelo considera llamar a la herramienta {step.name}")
            print(f"  - Argumentos: {args}")

            result = self.run_tool(step.name, args)

            self.history.append(
                {
                    "type": "function_result",
                    "name": step.name,
                    "call_id": step.id,
                    "result": [
                        {"type": "text",
                         "text": json.dumps(result, ensure_ascii=False)}
                    ],
                }
            )

        # c) Si no hubo herramientas, esta es la respuesta final
        if not called_tool:
            print(f"Asistente: {interaction.output_text}")

        return called_tool
