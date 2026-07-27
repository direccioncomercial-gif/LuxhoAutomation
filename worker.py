import time
from main import main

print("🚀 Worker Luxho iniciado")

while True:
    try:
        print("\n🔍 Buscando nuevas encuestas...")
        main()
    except Exception as e:
        print(f"❌ Error: {e}")

    time.sleep(10)