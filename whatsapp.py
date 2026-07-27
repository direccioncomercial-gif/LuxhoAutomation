import webbrowser
import urllib.parse


def abrir_whatsapp(mensaje):
    """
    Abre WhatsApp Web con el mensaje precargado.
    """

    texto = urllib.parse.quote(mensaje)

    url = f"https://web.whatsapp.com/send?text={texto}"

    print("\n========================")
    print("ABRIENDO WHATSAPP")
    print("========================")
    print(url)

    webbrowser.open(url)