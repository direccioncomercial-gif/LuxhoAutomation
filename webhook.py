from datetime import datetime

@app.before_request
def log_request():
    print("=" * 60)
    print(f"[{datetime.now()}] {request.method} {request.path}")

from flask import Flask, request, jsonify

from odoo import (
    encuesta_por_id,
    respuestas,
    crear_orden,
    leer_orden,
    publicar_en_canal,
    orden_existente,
    registrar_log,
)

app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    return "Luxho Automation Webhook OK"


@app.route("/webhook", methods=["POST"])
def webhook():

    print("\n====================================")
    print("WEBHOOK RECIBIDO")
    print("====================================")

    print("\nJSON:")
    print(request.get_json(silent=True))

    print("\nFORM:")
    print(request.form.to_dict())

    print("\nRAW:")
    print(request.data)

    data = request.get_json(silent=True) or {}

    print("\nTIPO DE DATA:")
    print(type(data))

    id_encuesta = data.get("id")

    print(f"\nID ENCUESTA: {id_encuesta}")

    if not id_encuesta:
        print("No llegó el ID de la encuesta")

        return jsonify({
            "status": "error",
            "message": "No llegó el ID de la encuesta"
        }), 400

    print("\nValidando duplicados...")

    if orden_existente(id_encuesta):

        registrar_log(
            id_encuesta=id_encuesta,
            estado="duplicada",
            error="La encuesta ya tenía una Orden de Servicio."
        )

        print("La orden ya existe.")

        return jsonify({
            "status": "ok",
            "message": "Orden ya creada"
        })

    print("Buscando encuesta...")

    encuesta = encuesta_por_id(id_encuesta)

    if encuesta is None:

        print("Encuesta no encontrada.")

        return jsonify({
            "status": "error",
            "message": "Encuesta no encontrada"
        }), 404

    print("Leyendo respuestas...")

    orden = respuestas(id_encuesta)

    orden["x_studio_id_survey"] = id_encuesta

    print("Creando Orden de Servicio...")

    respuesta = crear_orden(orden)

    if respuesta.status_code != 200:

        registrar_log(
            id_encuesta=id_encuesta,
            cliente=orden.get("x_studio_nombre_del_huesped", ""),
            servicio=orden.get("x_studio_tipo_de_servicio", ""),
            estado="error",
            canal=False,
            correo=False,
            error=respuesta.text
        )

        print("ERROR AL CREAR LA ORDEN")
        print(respuesta.text)

        return jsonify({
            "status": "error",
            "message": respuesta.text
        }), 500


    print("Orden creada correctamente.")
    id_orden = respuesta.json()[0]

    print(f"ID ORDEN: {id_orden}")

    print("Leyendo Orden creada...")

    orden_creada = leer_orden(id_orden)

    mensaje = orden_creada.get(
        "x_studio_mensaje_de_whatsapp",
        ""
    )

    if mensaje:

        print("Publicando mensaje en el canal...")

        publicar_en_canal(mensaje)

        print("Canal publicado correctamente.")

    else:

        print("La Orden no contiene mensaje para publicar.")

    print("Registrando auditoría...")

    registrar_log(
        id_encuesta=id_encuesta,
        cliente=orden.get("x_studio_nombre_del_huesped", ""),
        servicio=orden.get("x_studio_tipo_de_servicio", ""),
        id_orden=id_orden,
        estado="procesada",
        canal=True,
        correo=False,
        error=""
    )

    print("Log registrado correctamente.")

    print("\n====================================")
    print("PROCESO FINALIZADO CORRECTAMENTE")
    print("====================================")

    return jsonify({
        "status": "ok"
    })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )