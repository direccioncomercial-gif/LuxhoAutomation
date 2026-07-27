import requests
from config import ODOO_URL, HEADERS

r = requests.post(
    f"{ODOO_URL}/json/2/x_ordenes_de_servicio/fields_get",
    headers=HEADERS,
    json={
        "attributes": [
            "string",
            "type",
            "selection"
        ]
    }
)

print(r.status_code)
print(r.json())