from django.core.management.base import BaseCommand
from core.models import Course, Site
from training.models import Question, Option
from django.db import transaction

COURSES = [
    "Comunicación (SCI)",
    "Evacuación",
    "Primeros Auxilios",
    "Uso y manejo de extintores y manta ignífuga",
]

SITES = ["Sede 1", "Sede 2", "Sede 3"]

# Each item: (course_name, qtype, [ {text, options:[(text,is_correct),...]} ])
DATA = []


DATA = [
    ("Comunicación (SCI)", "PRE", [
        {
          "text": "¿Qué significa “SCI” en el contexto de emergencias?",
          "options": [
            ("Sistema de Control Industrial", False),
            ("Sistema de Comando de Incidentes", True),
            ("Sistema de Comunicación Interna", False),
            ("Servicio de Coordinación de Incendios", False),
          ]
        },
        {
          "text": "¿Cuál es el objetivo principal del SCI?",
          "options": [
            ("Evitar que existan emergencias", False),
            ("Coordinar personas y recursos con estructura clara durante un incidente", True),
            ("Sustituir a Protección Civil municipal", False),
            ("Hacer reportes administrativos al final", False),
          ]
        },
        {
          "text": "¿Cuál es una regla básica de comunicación durante una emergencia?",
          "options": [
            ("Hablar todos al mismo tiempo para ser rápidos", False),
            ("Usar mensajes claros, breves y confirmados", True),
            ("Usar apodos para identificar a las personas", False),
            ("Omitir información para no alarmar", False),
          ]
        },
        {
          "text": "En una emergencia, ¿qué significa “confirmar” un mensaje?",
          "options": [
            ("Repetirlo con otras palabras sin decir datos", False),
            ("Responder “ok” sin repetir el contenido", False),
            ("Repetir la instrucción recibida para asegurar comprensión", True),
            ("Guardar silencio para no saturar el canal", False),
          ]
        },
        {
          "text": "¿Qué información NO debe faltar en un reporte inicial (tipo “qué pasa”)?",
          "options": [
            ("Qué ocurrió", False),
            ("Dónde ocurrió", False),
            ("Quién reporta y cómo contactarlo", False),
            ("Opinión personal sobre culpables", True),
          ]
        },
        {
          "text": "Si un radio/canal se satura, ¿qué acción es mejor?",
          "options": [
            ("Seguir hablando igual para que te escuchen", False),
            ("Enviar mensajes cortos y priorizar lo urgente", True),
            ("Cambiar el mensaje por uno más largo y detallado", False),
            ("Usar bromas para bajar tensión", False),
          ]
        },
        {
          "text": "¿Quién debe emitir instrucciones operativas principales para evitar confusión?",
          "options": [
            ("Cualquier persona que “sepa más”", False),
            ("La persona designada con mando/coord. según el SCI", True),
            ("El último que llegó al sitio", False),
            ("Todos por votación rápida", False),
          ]
        },
        {
          "text": "¿Qué práctica reduce errores de comunicación?",
          "options": [
            ("Mensajes largos con muchos detalles técnicos", False),
            ("Hablar rápido para terminar pronto", False),
            ("Uso de frases estandarizadas y datos concretos", True),
            ("Cambiar términos cada vez para que no suene repetitivo", False),
          ]
        },
        {
          "text": "¿Qué se recomienda al pedir apoyo por radio/teléfono?",
          "options": [
            ("Pedirlo sin decir ubicación para ahorrar tiempo", False),
            ("Decir solo “urgente” y colgar", False),
            ("Indicar qué necesitas, dónde y situación actual", True),
            ("Decir “vengan ya” y esperar", False),
          ]
        },
        {
          "text": "Un ejemplo de comunicación incorrecta sería:",
          "options": [
            ("“Incendio en cocina, planta baja. Humo visible. Solicito extintor y brigada.”", False),
            ("“Hay algo pasando, creo que por allá… vengan.”", True),
            ("“Les confirmo: evacuar por ruta norte, punto de reunión A.”", False),
            ("“Repetido: corten energía en tablero principal, confirmo recepción.”", False),
          ]
        },
    ]),
    ("Comunicación (SCI)", "POST", [
        {
          "text": "¿Cuál es un beneficio directo de aplicar SCI en emergencias?",
          "options": [
            ("Evita que ocurra cualquier incidente", False),
            ("Reduce confusión al definir roles, comunicación y cadena de mando", True),
            ("Elimina la necesidad de simulacros", False),
            ("Sustituye a los servicios externos", False),
          ]
        },
        {
          "text": "En comunicación operativa, ¿qué significa “mensaje estandarizado”?",
          "options": [
            ("Mensaje con chistes para bajar tensión", False),
            ("Mensaje con estructura fija: qué–dónde–estado–qué se requiere", True),
            ("Mensaje sin ubicación para no generar pánico", False),
            ("Mensaje largo con todos los antecedentes", False),
          ]
        },
        {
          "text": "Cuando se da una instrucción crítica (evacuar/cortar energía), lo correcto es:",
          "options": [
            ("Ejecutarla sin decir nada", False),
            ("Confirmar repitiendo la instrucción y después reportar ejecución", True),
            ("Esperar a que alguien más confirme", False),
            ("Cambiar la instrucción si no te gusta", False),
          ]
        },
        {
          "text": "¿Qué dato es más útil para activar apoyo externo (911/brigadas) de forma efectiva?",
          "options": [
            ("“Está feo”", False),
            ("“Vengan rápido”", False),
            ("Ubicación exacta + tipo de incidente + riesgos presentes", True),
            ("Nombre completo de todos los empleados", False),
          ]
        },
        {
          "text": "En un incidente, los rumores son peligrosos porque:",
          "options": [
            ("Hacen más entretenida la espera", False),
            ("Pueden desorganizar decisiones y provocar acciones incorrectas", True),
            ("Sirven para completar datos faltantes", False),
            ("Aceleran la evacuación siempre", False),
          ]
        },
        {
          "text": "¿Cuál es una buena práctica para evitar “dobles órdenes”?",
          "options": [
            ("Que dos mandos den instrucciones para cubrirse", False),
            ("Centralizar instrucciones en el mando asignado y usar canales definidos", True),
            ("Dar órdenes por WhatsApp y por radio al mismo tiempo, sin coordinación", False),
            ("Que cada brigada haga lo que crea correcto", False),
          ]
        },
        {
          "text": "¿Qué es “canal” en comunicación de emergencia?",
          "options": [
            ("Un pasillo de evacuación", False),
            ("El medio o frecuencia acordada para transmitir mensajes operativos", True),
            ("Un documento del programa interno", False),
            ("Una lista de asistencia", False),
          ]
        },
        {
          "text": "Si no entendiste una instrucción, lo correcto es:",
          "options": [
            ("Adivinar", False),
            ("Ejecutar la mitad", False),
            ("Pedir aclaración inmediata y confirmar lo entendido", True),
            ("No hacer nada hasta que termine la emergencia", False),
          ]
        },
        {
          "text": "Una frase correcta al reportar es:",
          "options": [
            ("“Hay un problema, creo que es grave”", False),
            ("“Fuego. Bye.”", False),
            ("“Reporte: conato en bodega, 2 m², sin lesionados, humo leve, iniciamos control.”", True),
            ("“Yo ya lo vi todo, tranquilos”", False),
          ]
        },
        {
          "text": "¿Cuál es el error más común en comunicación durante emergencias?",
          "options": [
            ("Usar datos concretos", False),
            ("Confirmar mensajes", False),
            ("Mensajes vagos sin ubicación ni requerimientos", True),
            ("Reportar avances", False),
          ]
        },
    ]),
    ("Evacuación", "PRE", [
        {
          "text": "¿Cuál es el objetivo principal de una evacuación?",
          "options": [
            ("Salir lo más rápido posible sin orden", False),
            ("Trasladar a las personas a un lugar seguro de forma organizada", True),
            ("Evitar que llegue ayuda externa", False),
            ("Desalojar solo a los visitantes", False),
          ]
        },
        {
          "text": "¿Qué es una ruta de evacuación?",
          "options": [
            ("El camino más corto aunque tenga obstáculos", False),
            ("El trayecto señalizado y seguro para salir del inmueble", True),
            ("Cualquier pasillo disponible", False),
            ("El camino que use el personal de mantenimiento", False),
          ]
        },
        {
          "text": "¿Qué debe hacerse antes de iniciar una evacuación?",
          "options": [
            ("Correr para ganar tiempo", False),
            ("Esperar instrucciones claras del responsable o brigada", True),
            ("Apagar luces solamente", False),
            ("Gritar para alertar a todos", False),
          ]
        },
        {
          "text": "¿Cuál es una conducta incorrecta durante la evacuación?",
          "options": [
            ("Mantener la calma", False),
            ("Seguir indicaciones del personal designado", False),
            ("Empujar para salir primero", True),
            ("Caminar sin correr", False),
          ]
        },
        {
          "text": "¿Qué se debe hacer con personas con movilidad reducida durante una evacuación?",
          "options": [
            ("Dejarlas para que salgan solas", False),
            ("Apoyarlas conforme al protocolo establecido", True),
            ("Evacuarlas al final sin apoyo", False),
            ("Pedirles que corran", False),
          ]
        },
        {
          "text": "¿Qué es un punto de reunión?",
          "options": [
            ("El área donde inicia la evacuación", False),
            ("El lugar designado para concentrarse después de evacuar", True),
            ("El sitio donde se guardan los extintores", False),
            ("La salida principal del inmueble", False),
          ]
        },
        {
          "text": "¿Por qué no se deben usar elevadores durante una evacuación?",
          "options": [
            ("Porque tardan en llegar", False),
            ("Porque pueden fallar o detenerse", True),
            ("Porque no están señalizados", False),
            ("Porque hacen ruido", False),
          ]
        },
        {
          "text": "¿Qué se debe hacer si una ruta de evacuación está bloqueada?",
          "options": [
            ("Detener la evacuación", False),
            ("Regresar al punto inicial", False),
            ("Usar la ruta alterna señalizada", True),
            ("Romper paredes o puertas", False),
          ]
        },
        {
          "text": "¿Quién es responsable de verificar que no queden personas en el área evacuada?",
          "options": [
            ("Cualquier persona", False),
            ("Visitantes", False),
            ("Brigadistas o personal asignado", True),
            ("Seguridad pública", False),
          ]
        },
        {
          "text": "¿Qué acción es correcta al llegar al punto de reunión?",
          "options": [
            ("Regresar al inmueble", False),
            ("Dispersarse", False),
            ("Permanecer y reportarse con el responsable", True),
            ("Irse a casa sin avisar", False),
          ]
        },
    ]),
    ("Evacuación", "POST", [
        {
          "text": "¿Cuál es el primer criterio para decidir evacuar un inmueble?",
          "options": [
            ("Que alguien lo sugiera", False),
            ("La presencia de un riesgo que comprometa la seguridad", True),
            ("Que suene cualquier alarma", False),
            ("Que haya visita de Protección Civil", False),
          ]
        },
        {
          "text": "Una evacuación eficiente debe ser:",
          "options": [
            ("Rápida y desordenada", False),
            ("Silenciosa y sin instrucciones", False),
            ("Ordenada, segura y sin pánico", True),
            ("Solo para personal operativo", False),
          ]
        },
        {
          "text": "¿Qué información debe conocer el personal antes de una evacuación?",
          "options": [
            ("Quién diseñó el edificio", False),
            ("Rutas, salidas, puntos de reunión y roles asignados", True),
            ("Solo el número de salidas", False),
            ("El horario de trabajo", False),
          ]
        },
        {
          "text": "Durante una evacuación, ¿qué se debe hacer con puertas y ventanas?",
          "options": [
            ("Dejarlas abiertas siempre", False),
            ("Cerrarlas solo si hay tiempo y es seguro hacerlo", True),
            ("Romperlas", False),
            ("Asegurarlas con llave", False),
          ]
        },
        {
          "text": "¿Cuál es una función específica de la brigada de evacuación?",
          "options": [
            ("Controlar incendios", False),
            ("Dirigir y agilizar el desalojo sin generar pánico", True),
            ("Atender primeros auxilios", False),
            ("Llamar a familiares", False),
          ]
        },
        {
          "text": "¿Qué se debe hacer si una persona entra en crisis o pánico?",
          "options": [
            ("Ignorarla", False),
            ("Gritarle para que se apure", False),
            ("Tranquilizarla y guiarla fuera del inmueble", True),
            ("Forzarla físicamente", False),
          ]
        },
        {
          "text": "¿Por qué es importante no regresar al inmueble evacuado sin autorización?",
          "options": [
            ("Porque se pierde tiempo", False),
            ("Porque el riesgo puede continuar o agravarse", True),
            ("Porque se rompe el simulacro", False),
            ("Porque lo indica el reglamento interno", False),
          ]
        },
        {
          "text": "¿Qué se evalúa al realizar simulacros de evacuación?",
          "options": [
            ("Solo la velocidad", False),
            ("El orden, tiempos, uso de rutas y conducta del personal", True),
            ("La asistencia del personal", False),
            ("La estructura del edificio", False),
          ]
        },
        {
          "text": "¿Cuál es una causa común de accidentes durante evacuaciones reales?",
          "options": [
            ("Uso de señalización", False),
            ("Falta de iluminación", False),
            ("Empujones, correr y pánico", True),
            ("Presencia de brigadas", False),
          ]
        },
        {
          "text": "Al finalizar una evacuación real o simulacro, ¿qué se debe hacer?",
          "options": [
            ("Reanudar actividades sin comentar", False),
            ("Registrar observaciones y áreas de mejora", True),
            ("Olvidar el evento", False),
            ("Retirar señalización", False),
          ]
        },
    ]),
    ("Primeros Auxilios", "PRE", [
        {
          "text": "¿Qué son los primeros auxilios?",
          "options": [
            ("Tratamientos médicos especializados", False),
            ("Atención inmediata y temporal antes de recibir ayuda médica", True),
            ("Procedimientos quirúrgicos básicos", False),
            ("Atención exclusiva del personal de salud", False),
          ]
        },
        {
          "text": "¿Cuál es la primera acción al encontrar a una persona lesionada?",
          "options": [
            ("Moverla de inmediato", False),
            ("Darle agua", False),
            ("Evaluar la escena y verificar que sea segura", True),
            ("Llamar a familiares", False),
          ]
        },
        {
          "text": "¿Qué se debe hacer primero al atender a una persona inconsciente?",
          "options": [
            ("Darle alimentos", False),
            ("Verificar respiración y pulso", True),
            ("Sentarla", False),
            ("Retirarla del lugar sin revisar", False),
          ]
        },
        {
          "text": "¿Cuál es una prioridad en primeros auxilios?",
          "options": [
            ("Curar completamente la lesión", False),
            ("Evitar que la condición empeore", True),
            ("Sustituir al médico", False),
            ("Determinar responsabilidades", False),
          ]
        },
        {
          "text": "¿Qué se debe hacer ante una hemorragia externa?",
          "options": [
            ("Lavar con agua y jabón", False),
            ("Aplicar presión directa con material limpio", True),
            ("Retirar objetos incrustados", False),
            ("Dejar que sangre", False),
          ]
        },
        {
          "text": "¿Qué se recomienda hacer en caso de una quemadura leve?",
          "options": [
            ("Aplicar hielo directamente", False),
            ("Colocar cremas o remedios caseros", False),
            ("Enfriar con agua limpia y cubrir", True),
            ("Reventar ampollas", False),
          ]
        },
        {
          "text": "¿Cuál es un signo de emergencia médica?",
          "options": [
            ("Dolor leve", False),
            ("Mareo momentáneo", False),
            ("Dificultad para respirar", True),
            ("Cansancio", False),
          ]
        },
        {
          "text": "¿Qué se debe hacer si una persona presenta convulsiones?",
          "options": [
            ("Sujetarla con fuerza", False),
            ("Introducir objetos en la boca", False),
            ("Proteger su cabeza y retirar objetos cercanos", True),
            ("Darle agua", False),
          ]
        },
        {
          "text": "¿Cuándo se debe solicitar apoyo médico externo (911)?",
          "options": [
            ("Solo si lo pide el lesionado", False),
            ("Cuando la situación supera la atención básica", True),
            ("Al final del turno", False),
            ("Únicamente en incendios", False),
          ]
        },
        {
          "text": "¿Cuál es una función básica del botiquín de primeros auxilios?",
          "options": [
            ("Sustituir al hospital", False),
            ("Guardar medicamentos personales", False),
            ("Proporcionar material para atención inmediata", True),
            ("Almacenar documentos", False),
          ]
        },
    ]),
    ("Primeros Auxilios", "POST", [
        {
          "text": "¿Por qué es importante evaluar la escena antes de atender a una persona?",
          "options": [
            ("Para no perder tiempo", False),
            ("Para evitar ponerse en riesgo y agravar la situación", True),
            ("Para identificar culpables", False),
            ("Para mover a la víctima rápido", False),
          ]
        },
        {
          "text": "¿Qué información es clave al pedir apoyo médico externo?",
          "options": [
            ("Nombre completo del lesionado", False),
            ("Tipo de lesión, ubicación y estado de la persona", True),
            ("Opiniones personales", False),
            ("Turno de trabajo", False),
          ]
        },
        {
          "text": "¿Cuál es la posición recomendada para una persona inconsciente que respira?",
          "options": [
            ("Sentada", False),
            ("Boca arriba con piernas elevadas", False),
            ("Posición lateral de seguridad", True),
            ("Boca abajo", False),
          ]
        },
        {
          "text": "¿Qué se debe hacer si una persona presenta una hemorragia grave que no cede?",
          "options": [
            ("Quitar la presión para revisar", False),
            ("Mantener presión y solicitar ayuda médica urgente", True),
            ("Dejarla descansar", False),
            ("Aplicar alcohol", False),
          ]
        },
        {
          "text": "¿Qué acción es incorrecta en primeros auxilios?",
          "options": [
            ("Usar guantes si se cuenta con ellos", False),
            ("Tranquilizar al lesionado", False),
            ("Administrar medicamentos sin indicación médica", True),
            ("Solicitar apoyo externo", False),
          ]
        },
        {
          "text": "En caso de quemaduras, ¿qué se debe evitar?",
          "options": [
            ("Cubrir con material limpio", False),
            ("Enfriar con agua", False),
            ("Aplicar pomadas, mantequilla o remedios caseros", True),
            ("Evaluar la gravedad", False),
          ]
        },
        {
          "text": "¿Qué indica una posible fractura?",
          "options": [
            ("Enrojecimiento leve", False),
            ("Dolor intenso, deformidad o imposibilidad de mover", True),
            ("Sudoración", False),
            ("Cansancio", False),
          ]
        },
        {
          "text": "¿Cuál es el objetivo de inmovilizar una lesión?",
          "options": [
            ("Curarla", False),
            ("Evitar movimiento y prevenir mayor daño", True),
            ("Eliminar el dolor", False),
            ("Sustituir cirugía", False),
          ]
        },
        {
          "text": "Durante una convulsión, una acción correcta es:",
          "options": [
            ("Introducir un objeto en la boca", False),
            ("Sujetar brazos y piernas", False),
            ("Retirar objetos cercanos y vigilar", True),
            ("Dar medicamentos", False),
          ]
        },
        {
          "text": "¿Por qué es importante registrar la atención brindada en primeros auxilios?",
          "options": [
            ("Para sancionar al personal", False),
            ("Para tener control y seguimiento del evento", True),
            ("Para cumplir horarios", False),
            ("Para archivar sin revisar", False),
          ]
        },
    ]),
    ("Uso y manejo de extintores y manta ignífuga", "PRE", [
        {
          "text": "¿Cuál es la función principal de un extintor portátil?",
          "options": [
            ("Apagar cualquier incendio sin importar su tamaño", False),
            ("Controlar o sofocar incendios en su etapa inicial", True),
            ("Sustituir a los bomberos", False),
            ("Enfriar áreas calientes", False),
          ]
        },
        {
          "text": "¿Qué significa que un incendio sea de clase A?",
          "options": [
            ("Incendios por líquidos inflamables", False),
            ("Incendios por equipos eléctricos energizados", False),
            ("Incendios por metales combustibles", False),
            ("Incendios de materiales sólidos comunes", True),
          ]
        },
        {
          "text": "¿Qué tipo de fuego se genera por líquidos inflamables como gasolina o solventes?",
          "options": [
            ("Clase A", False),
            ("Clase B", True),
            ("Clase C", False),
            ("Clase K", False),
          ]
        },
        {
          "text": "¿Qué indica el manómetro de un extintor?",
          "options": [
            ("El peso del extintor", False),
            ("La fecha de fabricación", False),
            ("El estado de presión del agente", True),
            ("El tipo de fuego que apaga", False),
          ]
        },
        {
          "text": "¿Cuál es una condición indispensable para usar un extintor de forma segura?",
          "options": [
            ("Estar solo", False),
            ("Tener una ruta de evacuación libre a la espalda", True),
            ("Usarlo desde la parte superior del fuego", False),
            ("Colocarse de espaldas al incendio", False),
          ]
        },
        {
          "text": "¿Qué significa la letra “C” en la clasificación de incendios?",
          "options": [
            ("Combustibles sólidos", False),
            ("Combustibles líquidos", False),
            ("Equipos eléctricos energizados", True),
            ("Aceites y grasas", False),
          ]
        },
        {
          "text": "¿Cuál es el primer paso correcto al operar un extintor portátil?",
          "options": [
            ("Dirigir la manguera al fuego", False),
            ("Presionar la manija", False),
            ("Retirar el seguro o pasador", True),
            ("Agitar el extintor", False),
          ]
        },
        {
          "text": "¿En qué situación es más adecuada la manta ignífuga?",
          "options": [
            ("Incendios grandes en bodegas", False),
            ("Fuego en equipos eléctricos industriales", False),
            ("Incendio incipiente en ropa o pequeños recipientes", True),
            ("Incendios estructurales avanzados", False),
          ]
        },
        {
          "text": "¿Qué se debe hacer si el fuego no se controla con el extintor?",
          "options": [
            ("Insistir hasta vaciarlo", False),
            ("Cambiar de posición y seguir", False),
            ("Abandonar el área y evacuar", True),
            ("Acercarse más al fuego", False),
          ]
        },
        {
          "text": "¿Qué práctica es incorrecta al usar un extintor?",
          "options": [
            ("Apuntar a la base del fuego", False),
            ("Usar el extintor con el viento a favor", False),
            ("Probar el extintor antes de acercarse", False),
            ("Dar la espalda a la salida de evacuación", True),
          ]
        },
    ]),
    ("Uso y manejo de extintores y manta ignífuga", "POST", [
        {
          "text": "¿Por qué solo se deben combatir incendios incipientes con extintores portátiles?",
          "options": [
            ("Porque son más fáciles", False),
            ("Porque el extintor tiene capacidad limitada", True),
            ("Porque siempre se gana tiempo", False),
            ("Porque lo indica el reglamento interno", False),
          ]
        },
        {
          "text": "¿Qué riesgo existe al usar un extintor en un incendio incorrecto?",
          "options": [
            ("Ninguno", False),
            ("Solo se desperdicia el agente", False),
            ("Puede agravar el incendio o poner en riesgo a la persona", True),
            ("El extintor deja de funcionar", False),
          ]
        },
        {
          "text": "¿Cuál es la técnica correcta para aplicar un extintor?",
          "options": [
            ("De arriba hacia abajo", False),
            ("A la base del fuego con barrido lateral", True),
            ("Directo al humo", False),
            ("En círculos amplios sobre el área", False),
          ]
        },
        {
          "text": "Antes de usar un extintor se debe verificar:",
          "options": [
            ("El color del extintor", False),
            ("El tipo de incendio, presión y estado general", True),
            ("La marca comercial", False),
            ("El peso exacto", False),
          ]
        },
        {
          "text": "¿Cuál es una ventaja de la manta ignífuga?",
          "options": [
            ("Apaga incendios grandes", False),
            ("No requiere capacitación", False),
            ("Permite sofocar el fuego sin dispersarlo", True),
            ("Sustituye al extintor", False),
          ]
        },
        {
          "text": "¿Cómo se debe colocar una manta ignífuga sobre una persona con fuego en la ropa?",
          "options": [
            ("De abajo hacia arriba", False),
            ("Desde la cabeza descubriendo el rostro", False),
            ("De arriba hacia abajo protegiendo rostro y vías respiratorias", True),
            ("Lanzándola a distancia", False),
          ]
        },
        {
          "text": "¿Qué se debe hacer después de usar un extintor, aunque no se haya vaciado?",
          "options": [
            ("Guardarlo nuevamente", False),
            ("Recargarlo o enviarlo a mantenimiento", True),
            ("Limpiarlo externamente", False),
            ("Dejarlo sin seguro", False),
          ]
        },
        {
          "text": "¿Cuál es una señal para NO intentar combatir un incendio con extintor?",
          "options": [
            ("El fuego es pequeño", False),
            ("Hay humo denso y calor intenso", True),
            ("El extintor es nuevo", False),
            ("El incendio es de papel", False),
          ]
        },
        {
          "text": "¿Por qué no se debe usar agua en incendios eléctricos energizados?",
          "options": [
            ("Porque no enfría", False),
            ("Porque daña el equipo", False),
            ("Porque puede provocar electrocución", True),
            ("Porque no es efectiva", False),
          ]
        },
        {
          "text": "¿Qué acción correcta complementa el uso de extintores en un inmueble?",
          "options": [
            ("Colocarlos sin señalización", False),
            ("Capacitar al personal y realizar simulacros", True),
            ("Usarlos solo personal externo", False),
            ("Guardarlos bajo llave", False),
          ]
        },
    ]),
]

class Command(BaseCommand):
    help = "Seed initial data: sites, courses, questions/options, and an admin user if missing."

    def add_arguments(self, parser):
        parser.add_argument("--admin-email", default="admin@example.com")
        parser.add_argument("--admin-password", default="admin12345")

    @transaction.atomic
    def handle(self, *args, **opts):
        from users.models import User

        # Sites
        for s in SITES:
            Site.objects.get_or_create(name=s)

        # Courses
        course_map = {}
        for c in COURSES:
            course, _ = Course.objects.get_or_create(name=c, defaults={"is_active": True})
            course_map[c] = course

        # Questions + options
        for cname, qtype, questions in DATA:
            course = course_map[cname]
            for q in questions:
                qobj, created = Question.objects.get_or_create(course=course, qtype=qtype, text=q["text"])
                # ensure options exist
                if not qobj.options.exists():
                    for text, is_correct in q["options"]:
                        Option.objects.create(question=qobj, text=text, is_correct=is_correct)

        # Admin user
        email = opts["admin_email"]
        pwd = opts["admin_password"]
        if not User.objects.filter(email=email).exists():
            User.objects.create_superuser(email=email, password=pwd, full_name="Admin")

        self.stdout.write(self.style.SUCCESS("Seed completado."))
