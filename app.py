from flask import Flask
from handlers.check_role import role_bp
from handlers.acknowledge import ack_bp

app = Flask(__name__)
app.register_blueprint(role_bp)
app.register_blueprint(ack_bp)

@app.route("/")
def home():
    return "🟢 Сервер работает"

if __name__ == "__main__":
    app.run(debug=True)
