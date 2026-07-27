from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Luxho Automation Webhook OK"

@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.json

    print("========================")
    print("WEBHOOK RECIBIDO")
    print("========================")
    print(data)

    return jsonify({
        "status": "ok"
    })

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )