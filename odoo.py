import requests
from config import ODOO_URL, HEADERS


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

    print("Respuesta encuesta:")
    print(encuestas)

    for encuesta in encuestas:

        if not orden_existente(encuesta["id"]):
            return encuesta

    return None


# =====================================================
# LEER RESPUESTAS
# =====================================================

def respuestas(user_input_id):

    r = requests.post(
        f"{ODOO_URL}/json/2/survey.user_input.line/search_read",
        headers=HEADERS,
        json={
            "domain": [["user_input_id", "=", user_input_id]],
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

    print("Respuesta líneas:")
    print(datos)

    orden = {}

    for linea in datos:

        pregunta = linea["question_id"][1]

        if linea["value_char_box"]:
            valor = linea["value_char_box"]

        elif linea["value_datetime"]:
            valor = linea["value_datetime"]

        elif linea["suggested_answer_id"]:

            valor = linea["suggested_answer_id"][1]

            if " : " in valor:
                valor = valor.split(" : ")[1]

        elif linea["value_numerical_box"]:

            valor = str(int(linea["value_numerical_box"]))

        else:

            valor = ""

        if pregunta == "NOMBRE DEL EMPLEADO":
            orden["x_studio_nombre_de_empleado"] = valor

        elif pregunta == "NOMBRE DEL HUESPED":
            orden["x_studio_nombre_del_huesped"] = valor

        elif pregunta == "CONTACTO DEL HUESPED":
            orden["x_studio_contacto_del_huesped"] = valor

        elif pregunta == "SERVICIO":
            orden["x_studio_tipo_de_servicio"] = valor

        elif pregunta == "TIPO DE VEHICULO":
            orden["x_studio_tipo_de_vehiculo"] = valor

        elif pregunta == "HORA DEL SERVICIO":
            orden["x_studio_fecha_y_hora"] = valor

        elif pregunta == "NUMERO DE VUELO":
            orden["x_studio_numero_de_vuelo"] = valor

        elif pregunta == "ORIGEN":
            orden["x_studio_origen"] = valor

        elif pregunta == "DESTINO":
            orden["x_studio_destino"] = valor

        elif pregunta == "HOTEL":
            orden["x_studio_hotel"] = valor

        elif pregunta == "OBSERVACIONES EXTRA DEL SERVICIO":
            orden["x_studio_observaciones"] = valor

    # =====================================================
    # MENSAJE OPERATIVO
    # =====================================================

    mensaje = f"""
🚗 NUEVA ORDEN DE SERVICIO - LUXHO

👤 EMPLEADO:
{orden.get('x_studio_nombre_de_empleado','')}

🙋 HUESPED:
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
"""

    orden["x_studio_mensaje_de_whatsapp"] = mensaje

    return orden
# =====================================================
# CREAR ORDEN
# =====================================================

def crear_orden(orden):

    orden["x_name"] = (
        f"{orden.get('x_studio_tipo_de_servicio','')} - "
        f"{orden.get('x_studio_nombre_del_huesped','')}"
    )

    payload = {
        "vals_list": [
            orden
        ]
    }

    print("\n========================")
    print("ENVIANDO A ODOO")
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
    print("Código HTTP:", r.status_code)
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
            "fields": ["id"],
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

    return r.json()[0]


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
