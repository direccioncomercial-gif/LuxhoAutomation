from flask import Flask, request, jsonify

from odoo import (
    encuesta_por_id,
    respuestas,
    crear_orden,
    leer_orden,
    publicar_en_canal,
    orden_existente,
)

app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    return "Luxho Automation Webhook OK"


@app.route("/webhook", methods=["POST"])
def webhook():

    print("\n========================")
print("WEBHOOK RECIBIDO")
print("========================")

print("JSON:")
print(request.get_json(silent=True))

print("\nFORM:")
print(request.form.to_dict())

print("\nRAW:")
print(request.data)

data = request.get_json(silent=True)

print("\nTIPO DE DATA:")
print(type(data))

    # ID enviado por Odoo
    id_encuesta = data.get("id")

    if not id_encuesta:
        return jsonify({
            "status": "error",
            "message": "No llegó el ID de la encuesta"
        }), 400

    # Evitar órdenes duplicadas
    if orden_existente(id_encuesta):

        print("La orden ya existe.")

        return jsonify({
            "status": "ok",
            "message": "Orden ya creada"
        })

    encuesta = encuesta_por_id(id_encuesta)

    if encuesta is None:

        return jsonify({
            "status": "error",
            "message": "Encuesta no encontrada"
        }), 404

    orden = respuestas(id_encuesta)

    # Guardar ID de encuesta
    orden["x_studio_id_survey"] = id_encuesta

    respuesta = crear_orden(orden)

    if respuesta.status_code != 200:

        return jsonify({
            "status": "error",
            "message": respuesta.text
        }), 500

    id_orden = respuesta.json()[0]

    orden_creada = leer_orden(id_orden)

    mensaje = orden_creada.get(
        "x_studio_mensaje_de_whatsapp",
        ""
    )

    if mensaje:
        publicar_en_canal(mensaje)

    print("\n========================")
    print("ORDEN CREADA CORRECTAMENTE")
    print("========================")

    return jsonify({
        "status": "ok"
    })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )