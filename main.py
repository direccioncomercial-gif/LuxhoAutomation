from odoo import (
    ultima_encuesta,
    respuestas,
    crear_orden,
    orden_existente,
    leer_orden,
    publicar_en_canal,
)


def main():

    encuesta = ultima_encuesta()

    if encuesta is None:
        print("\n========================")
        print("NO HAY ENCUESTAS PENDIENTES")
        print("========================")
        return

    print("\n========================")
    print("ÚLTIMA ENCUESTA")
    print("========================")
    print(encuesta)

    orden = respuestas(encuesta["id"])

    # Guardar el ID de la encuesta
    orden["x_studio_id_survey"] = encuesta["id"]

    print("\n========================")
    print("ORDEN A CREAR")
    print("========================")

    for campo, valor in orden.items():
        print(f"{campo}: {valor}")

    print("\n========================")
    print("CREANDO ORDEN...")
    print("========================")

    respuesta = crear_orden(orden)

    print("\n========================")
    print("RESPUESTA ODOO")
    print("========================")
    print("Código HTTP:", respuesta.status_code)
    print(respuesta.text)

    if respuesta.status_code != 200:
        return

    id_orden = respuesta.json()[0]

    print("\n========================")
    print("LEYENDO ORDEN...")
    print("========================")

    orden_creada = leer_orden(id_orden)

    mensaje = orden_creada.get("x_studio_mensaje_de_whatsapp", "")

    if mensaje:

        print("\n========================")
        print("PUBLICANDO EN CANAL...")
        print("========================")

        publicar_en_canal(mensaje)

    print("\n========================")
    print("PROCESO FINALIZADO")
    print("========================")


if __name__ == "__main__":
    main()