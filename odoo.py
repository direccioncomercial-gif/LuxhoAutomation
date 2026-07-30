import requests
from config import ODOO_URL, HEADERS
from datetime import datetime


# =====================================================
# BUSCAR LA ÚLTIMA ENCUESTA QUE NO TENGA ORDEN
# =====================================================

def ultima_encuesta():

    r = requests.post(
        f"{ODOO_URL}/json/2/survey.user_input/search_read",
        headers=HEADERS,
        json={
            "domain": [["state", "=", "done"]],
            "fields": ["id", "display_name"],
            "order": "id desc",
            "limit": 20
        }
    )

    encuestas = r.json()

    print("\n========================")
    print("ENCUESTAS ENCONTRADAS")
    print("========================")
    print(encuestas)

    for encuesta in encuestas:

        if not orden_existente(encuesta["id"]):
            print(f"Se procesará la encuesta {encuesta['id']}")
            return encuesta

    print("No hay encuestas pendientes.")

    return None


# =====================================================
# BUSCAR ENCUESTA POR ID
# =====================================================

def encuesta_por_id(id_encuesta):

    r = requests.post(
        f"{ODOO_URL}/json/2/survey.user_input/read",
        headers=HEADERS,
        json={
            "ids": [id_encuesta],
            "fields": [
                "id",
                "display_name"
            ]
        }
    )

    datos = r.json()

    if not datos:
        return None

    return datos[0]


# =====================================================
# LEER RESPUESTAS
# =====================================================

def respuestas(user_input_id):

    r = requests.post(
        f"{ODOO_URL}/json/2/survey.user_input.line/search_read",
        headers=HEADERS,
        json={
            "domain": [
                ["user_input_id", "=", user_input_id]
            ],
            "fields": [
                "question_id",
                "value_char_box",
                "value_datetime",
                "value_numerical_box",
                "suggested_answer_id"
            ]
        }
    )

    datos = r.json()

    print("\n================================")
    print("RESPUESTAS DE LA ENCUESTA")
    print("================================")

    orden = {}

    mapa = {

        "NOMBRE DEL EMPLEADO":
            "x_studio_nombre_de_empleado",

        "NOMBRE DEL HUESPED":
            "x_studio_nombre_del_huesped",

        "NOMBRE DEL HUÉSPED":
            "x_studio_nombre_del_huesped",

        "NOMBRE DEL CLIENTE":
            "x_studio_nombre_del_huesped",

        "CONTACTO DEL HUESPED":
            "x_studio_contacto_del_huesped",

        "CONTACTO DEL HUÉSPED":
            "x_studio_contacto_del_huesped",

        "SERVICIO":
            "x_studio_tipo_de_servicio",

        "TIPO DE SERVICIO":
            "x_studio_tipo_de_servicio",

        "TIPO DE VEHICULO":
            "x_studio_tipo_de_vehiculo",

        "TIPO DE VEHÍCULO":
            "x_studio_tipo_de_vehiculo",

        "HORA DEL SERVICIO":
            "x_studio_fecha_y_hora",

        "FECHA":
            "x_studio_fecha_y_hora",

        "NUMERO DE VUELO":
            "x_studio_numero_de_vuelo",

        "NÚMERO DE VUELO":
            "x_studio_numero_de_vuelo",

        "ORIGEN":
            "x_studio_origen",

        "DESTINO":
            "x_studio_destino",

        "HOTEL":
            "x_studio_hotel",

        "OBSERVACIONES EXTRA DEL SERVICIO":
            "x_studio_observaciones",

        "OBSERVACIONES":
            "x_studio_observaciones",
    }

    for linea in datos:

        print("--------------------------------")
        print(linea)

        pregunta = linea["question_id"][1].strip().upper()

        valor = ""

        if linea.get("value_char_box"):
            valor = linea["value_char_box"]

        elif linea.get("suggested_answer_id"):

            print("SUGGESTED ANSWER:")
            print(linea["suggested_answer_id"])

            valor = linea["suggested_answer_id"][1]

            if " : " in valor:
                valor = valor.split(" : ", 1)[1]

        elif linea.get("value_datetime"):
            valor = linea["value_datetime"]

        elif linea.get("value_numerical_box"):
            valor = str(int(linea["value_numerical_box"]))

        print(f"PREGUNTA: {pregunta}")
        print(f"VALOR: {valor}")

        campo = mapa.get(pregunta)

        if campo:
            orden[campo] = valor

    mensaje = f"""
🚗 NUEVA ORDEN DE SERVICIO - LUXHO

🙋 CLIENTE:
{orden.get('x_studio_nombre_del_huesped','')}

🛎 SERVICIO:
{orden.get('x_studio_tipo_de_servicio','')}

🚘 VEHICULO:
{orden.get('x_studio_tipo_de_vehiculo','')}

📅 FECHA:
{orden.get('x_studio_fecha_y_hora','')}

✈ VUELO:
{orden.get('x_studio_numero_de_vuelo','')}

📍 ORIGEN:
{orden.get('x_studio_origen','')}

📍 DESTINO:
{orden.get('x_studio_destino','')}

🏨 HOTEL:
{orden.get('x_studio_hotel','')}

📝 OBSERVACIONES:
{orden.get('x_studio_observaciones','')}

💰 VALOR DEL SERVICIO:
Pendiente de asignar
""".strip()

    orden["x_studio_mensaje_de_whatsapp"] = mensaje

    print("\n================================")
    print("ORDEN CONSTRUIDA")
    print("================================")
    print(orden)

    return orden
# =====================================================
# CREAR ORDEN
# =====================================================

def crear_orden(orden):

    tipo_servicio = (
        orden.get("x_studio_tipo_de_servicio") or ""
    ).strip().upper()

    if not tipo_servicio:

        print("\n==============================")
        print("ERROR: SERVICIO VACÍO")
        print("==============================")
        print(orden)

        raise Exception(
            "La encuesta no devolvió ningún valor para la pregunta SERVICIO."
        )

    orden["x_studio_tipo_de_servicio"] = tipo_servicio

    orden["x_name"] = (
        f"{tipo_servicio} - "
        f"{orden.get('x_studio_nombre_del_huesped','')}"
    )

    payload = {
        "vals_list": [
            orden
        ]
    }

    print("\n========================")
    print("JSON QUE SE ENVIARÁ A ODOO")
    print("========================")
    print(payload)

    r = requests.post(
        f"{ODOO_URL}/json/2/x_ordenes_de_servicio/create",
        headers=HEADERS,
        json=payload
    )

    print("\n========================")
    print("RESPUESTA ODOO")
    print("========================")
    print("HTTP:", r.status_code)
    print(r.text)

    return r


# =====================================================
# VERIFICAR SI YA EXISTE UNA ORDEN
# =====================================================

def orden_existente(id_survey):

    r = requests.post(
        f"{ODOO_URL}/json/2/x_ordenes_de_servicio/search_read",
        headers=HEADERS,
        json={
            "domain": [
                ["x_studio_id_survey", "=", id_survey]
            ],
            "fields": [
                "id"
            ],
            "limit": 1
        }
    )

    datos = r.json()

    return len(datos) > 0


# =====================================================
# LEER ORDEN
# =====================================================

def leer_orden(id_orden):

    r = requests.post(
        f"{ODOO_URL}/json/2/x_ordenes_de_servicio/read",
        headers=HEADERS,
        json={
            "ids": [id_orden],
            "fields": [
                "x_studio_conductor_asignado",
                "x_studio_mensaje_de_whatsapp",
                "x_studio_estado_1"
            ]
        }
    )

    datos = r.json()

    if not datos:
        return None

    return datos[0]


# =====================================================
# BUSCAR CANAL
# =====================================================

def buscar_canal():

    r = requests.post(
        f"{ODOO_URL}/json/2/discuss.channel/search_read",
        headers=HEADERS,
        json={
            "domain": [
                ["name", "=", "ordenes-de-servicio"]
            ],
            "fields": [
                "id",
                "name"
            ],
            "limit": 1
        }
    )

    datos = r.json()

    if not datos:
        return None

    return datos[0]["id"]


# =====================================================
# PUBLICAR EN CANAL
# =====================================================

def publicar_en_canal(mensaje):

    canal = buscar_canal()

    if not canal:
        print("No se encontró el canal.")
        return

    payload = {
        "vals_list": [
            {
                "body": f"<pre>{mensaje}</pre>",
                "model": "discuss.channel",
                "res_id": canal
            }
        ]
    }

    r = requests.post(
        f"{ODOO_URL}/json/2/mail.message/create",
        headers=HEADERS,
        json=payload
    )

    print("\n========================")
    print("MENSAJE PUBLICADO EN EL CANAL")
    print("========================")
    print(r.status_code)
    print(r.text)
    # =====================================================
# CREAR CORREO
# =====================================================


# =====================================================
# ENVIAR CORREO
# =====================================================


# =====================================================
# REGISTRAR LOG DE AUTOMATIZACIÓN
# =====================================================

def registrar_log(
    id_encuesta,
    cliente="",
    servicio="",
    id_orden=0,
    estado="procesada",
    canal=False,
    correo=False,
    error=""
):

    payload = {
        "vals_list": [
            {
                "x_name": f"Encuesta {id_encuesta}",
                "x_studio_fecha_ejecucion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "x_studio_id_encuesta": id_encuesta,
                "x_studio_cliente": cliente,
                "x_studio_servicio": servicio,
                "x_studio_id_orden": id_orden,
                "x_studio_estado": estado,
                "x_studio_canal_publicado": canal,
                "x_studio_correo_enviado": correo,
                "x_studio_error": error,
            }
        ]
    }

    print("\n========================")
    print("REGISTRANDO LOG")
    print("========================")
    print(payload)

    try:

        r = requests.post(
            f"{ODOO_URL}/json/2/x_log_automatizaciones/create",
            headers=HEADERS,
            json=payload,
            timeout=30
        )

        print("\n========================")
        print("RESPUESTA LOG")
        print("========================")
        print("HTTP:", r.status_code)
        print(r.text)

        if r.status_code == 404:
            print("El modelo x_log_automatizaciones no existe. Se continúa sin registrar el log.")
            return None

        return r

    except Exception as e:

        print("\n========================")
        print("ERROR REGISTRANDO LOG")
        print("========================")
        print(str(e))

        # El log nunca debe detener la automatización
        return None