from dotenv import load_dotenv
import os

load_dotenv()

ODOO_URL = os.getenv("ODOO_URL")
ODOO_API_KEY = os.getenv("ODOO_API_KEY")

HEADERS = {
    "Authorization": f"Bearer {ODOO_API_KEY}",
    "Content-Type": "application/json"
}