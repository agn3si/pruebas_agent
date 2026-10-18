# HelloWorld Agente - Clase FundamentosIA
Tomando como base el código del repositorio: 
https://github.com/carlosricardocm/simple-agent

Es un agente de IA funcional simple implementando solo memoria, herramientas y un bucle.

## Instalación y ejecución

- Requiere **Python 3.10 o superior** y una llave de la API de Gemini (gratuita): https://aistudio.google.com/apikey


```bash
# 1. Crea y activa un entorno (conda es la opción más limpia en Windows)
conda create -n agente python=3.10 -y
conda activate agente
#    o con venv:  python -m venv .venv
#                 .venv\Scripts\activate        (Windows)
#                 source .venv/bin/activate     (macOS / Linux)

# 2. Instala las dependencias
pip install -r requirements.txt

# 3. Copia .env.example a .env y pon tu llave:
#    GEMINI_API_KEY=xxxxxxxxxxxxxxxxxxxx

# 4. Ejecuta (escribe "salir" para terminar)
python main.py
```

## Implementación nueva
Se añadieron dos nuevas herramientas principales:

- **to_day**: recupera la fecha y hora actuales del sistema. Se creó para poder manejar los recordatorios con fechas relativas como "mañana", "hoy" o "el siguiente miércoles".
- **to_do_tasks**: es la función principal y crea, borra o lista los pendientes. La acción de listar además verifica si el pendiente está vencido o vigente; sirve para el nuevo prompt de la agente, que ofrecerá ayuda con los pendientes vencidos, y también para separar los pendientes en dos listas cuando se piden.

Como cereza y por claridad durante las pruebas, se añadieron colores a las salidas de "Tú", "Herramienta" y "Agente" :D

También se añadió un tope de iteraciones que se puede modificar en `max_iter` de `main.py`, en las pruebas se notó que cuenta las rondas y no la herramienta por mensaje, detiene la ejecución pero algo extraño sucede porque no regresa ningún mensaje del agente y sí envía la respuesta para seguir sin contexto al agente. 

## Pruebas y conclusiones

Las llamadas a herramientas se resumen como `[herramienta] nombre(acción: datos)`. El texto de "Tú" y "Asistente" es literal.

### Caso 1 — Reagendar un pendiente y listar (herramientas encadenadas)

```text
Tú: reagenda la junta para mañana a las 3 de la tarde, qué pendientes me quedan todavía?
  [herramienta] to_do_tasks(borrar: Junta, 1-10-2026 03:00)
  [herramienta] to_do_tasks(crear: Junta, 18-10-2026 15:00)
  [herramienta] to_do_tasks(listar)
Asistente: ¡Listo! Reagendé la **Junta** para mañana, **18 de octubre a las 15:00**.

Tus pendientes actuales son:

**Pendientes vigentes:**
- **Junta:** 18-10-2026 a las 15:00
- **Clase de baile:** 18-10-2026 a las 19:00
- **Examen de NLP:** 21-10-2026 a las 11:00
- **Examen de Minería de Datos:** 22-10-2026 a las 08:00
- **Examen de ML:** 23-10-2026 a las 11:00

**Pendientes vencidos:**
- **Entregar tarea** (15-10-2026 a las 20:01)
- **Preparar calabaza** (17-10-2026 a las 21:00)

¿Pudiste completar alguno de estos dos pendientes vencidos para borrarlo, o prefieres que te ayude con alguno de ellos?
```

**Evaluación: CORRECTO**
El agente manejó correctamente el prompt, primero borró y creó el pendiente correctamente, incluso manejó el error intencional de 1 en el día en vez de 01, se modificó el json a propósito para esta revisión. Al final agrega la lista con los recordatorios en orden y bien separados.

### Caso 2 — Datos incompletos o imposibles

```text
Tú: tengo que ir a una clase de baile la siguiente semana
  [herramienta] to_day()
  [herramienta] to_do_tasks(listar)
Asistente: ¡Hola! Claro, ¿qué día y a qué hora de la próxima semana será tu clase de baile para agendártela? (Vi que ya tienes una registrada para mañana, 18 de octubre a las 19:00).

Por otro lado, noté que tienes estos pendientes que ya vencieron:
- **Entregar tarea** (15-10-2026)
- **Junta** (01-10-2026)
- **Preparar calabaza** (17-10-2026)

¿Lograste completarlos para borrarlos de tu lista, o necesitas ayuda con alguno de ellos?

Tú: me recuerdas que tengo que terminar un proyecto el 32 de octubre?
Asistente: Octubre solo tiene 31 días, ¿te refieres al **31 de octubre** o al **1 de noviembre**? También confírmame la hora para poder agendártelo.

Por cierto, ¿lograste completar los pendientes vencidos (**Entregar tarea** y **Preparar calabaza**) para eliminarlos, o necesitas que te ayude con ellos?
```

**Evaluación: CORRECTO**
El agente responde adecuadamente, no agrega pendientes sin los requerimientos: fecha y hora específicas. Además observa los que ya se tienen a cada llamada y comenta uno similar.
Sobre la fecha imposible, el modelo de Gemini detecta la falacia antes de entrar a las herramientas, pasó la respuesta pero gracias al modelo usado y no llegó a probarse la herramienta.

### Caso 3 — Tope de iteraciones

```text
Tú: hola, puedes poner 4 actividades en mi agenda? escalar, bailar, escribir y leer, todos el domingo de 1 a 4 pm
  [herramienta] to_day()
  [herramienta] to_do_tasks(listar)
  [herramienta] list_files_in_dir()
  [herramienta] read_file(reminders.json)
Llegamos al límite de iteraciones para este mensaje,¿quieres seguir? :)

Tú: sí :)
  [herramienta] to_do_tasks(crear: Escalar, 18-10-2026 13:00)
  [herramienta] to_do_tasks(crear: Bailar, 18-10-2026 14:00)
  [herramienta] to_do_tasks(crear: Escribir, 18-10-2026 15:00)
  [herramienta] to_do_tasks(crear: Leer, 18-10-2026 16:00)
  [herramienta] to_do_tasks(borrar: Entregar tarea, 15-10-2026 20:01)
  [herramienta] to_do_tasks(borrar: Preparar calabaza, 17-10-2026 21:00)
  [herramienta] to_do_tasks(listar)
Asistente: ¡Listo! He agregado tus 4 actividades para este domingo 18 de octubre:

* **Escalar:** 1:00 pm (13:00)
* **Bailar:** 2:00 pm (14:00)
* **Escribir:** 3:00 pm (15:00)
* **Leer:** 4:00 pm (16:00)

*(Nota: tienes también una "Junta" a las 3:00 pm por si deseas reprogramar alguna).*
Además, como ya completaste los pendientes que habían vencido ("Entregar tarea" y "Preparar calabaza"), los he eliminado de tu lista. ¿Hay algo más en lo que te pueda ayudar?
```

**Evaluación: INCORRECTO**
Al poner el tope de iteraciones en 3, detiene el modelo al llegar a la 4 iteración y pregunta si se desea continuar, con la respuesta positiva vuelve a funcionar pero además de hacer lo requerido, BORRA los pendientes vencidos. Esto puede deberse a que hay una respuesta que no se imprimió del modelo o a que se interrumpió y sólo recibió el "sí" sin contexto, lo que asumió como una respuesta a la pregunta que hace en cada llamada: si ya se completaron los pendientes vencidos.
Por lo demás, el modelo maneja con suposiciones el poner una actividad por hora y agenda dos al mismo tiempo, no es un impedimento y además avisa el choque, aunque la suposición de las horas fue hecha por el modelo. 

Aquí se observa un grave error: una respuesta sin contexto puede activar una acción importante como borrar pendientes. Al intentar investigar el error, se quedó sin límite la API y ahí se vió otro error de código, el agente reintenta llamar a la API sin éxito y se atasca sin dar solución o respuesta en medio de tiempos de `.sleep()`.


## Conclusiones

**Resultado:** De las 5 pruebas reportadas aquí, podemos decir que pasó 4 pero que no todas prueban al código sino a la combinación de modelo generativo y código, al parecer las limitaciones encontradas fueron con el `max_iter` por la forma en la que se maneja el envío de mensajes al modelo y las herramientas implementadas parecen tener un buen funcionamiento.

**Limitaciones encontradas:**
- Como se mencionó anteriormente, el tope de iteraciones considera rondas y no llamadas individuales a herramientas.
- Se debe modificar el envío de historia al modelo y la recuperación de mensajes, para evitar errores como el "sí" ambiguo que borró dos recordatorios.
- El prompt se puede modificar, aquí pide explícitamente que si algún pendiente está vencido entonces ofrezca ayuda, lo que gasta necesariamente la herramienta para verificarlo en cada uno de los mensajes. 
- Las API's gratuitas probadas de Gemini tienen solo 20 mensajes por día, lo que es una cuota muy limitada para poder ver el funcionamiento del agente completo, debido a que la memoria se mantiene solo mientras la sesión está activa, lo que se guarda es el `reminders.json`.