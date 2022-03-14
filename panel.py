from flask import Flask, request, jsonify, Response, render_template, send_file, session, redirect
import json

from manager import Manager

app = Flask(__name__, static_folder="./static", static_url_path="/", template_folder="./templates")
manager = Manager()
strategy = manager.strategy
database = manager.database


def login_required(func):
    def wrapper(*args, **kwargs):
        if "session_key" in session:
            if session["session_key"] is not None:
                return func(*args, **kwargs)
        return redirect("/login")
    return wrapper


@app.route("/")
@login_required
def home():
    return render_template("panel.html")


@app.route("/login", methods=["GET"])
def login():
    if "session_key" in session:
        if session["session_key"]:
            redirect("/")
    return render_template("Login.html")


@app.route("/logout", methods=["GET"])
def logout():
    session["session_key"] = None
    session["email"] = None


@app.route("/authenticate", methods=["POST"])
def login_auth():
    data = request.data
    data = json.loads(data)
    # email, password
    auth = manager.authenticate(data["email"], data["password"])
    if auth:
        session["session_key"] = manager.make_hash(data["email"])
        session["email"] = data["email"]
        return {"data": "authenticated", "status": "ok"}
    return {"data": "authentication failed", "status": "ok"}


@app.route("/report", methods=["POST"])
def get_report():
    data = json.loads(request.data)
    # broker 
    data = manager.report(data)
    res = jsonify({"data": data, "status": "ok"})
    res.status_code = 200
    return res


@app.route("/report_file", methods=["POST"])
def get_report_file():
    data = json.loads(request.data)
    f = manager.report_file(data)
    return send_file(f)


@app.route("/read_all_brokers", methods=["GET"])
def read_all_brokers():
    broker_list = ["kucoin"]
    res = jsonify({"data": broker_list})
    res.status_code = 200
    return res


@app.route("/add_strategy", methods=["POST"])
def add_strategy():
    data = request.data
    data = json.loads(data)
    strategy.write(data)
    return {"data": "strategy added", "status": "ok"}


@app.route("/read_all_strategies", methods=["POST"])
def read_all_strategies():
    data = request.data
    # broker
    data = json.loads(data)
    strategies = strategy.read_all(data)
    res = jsonify({"data": strategies, "status": "ok"})
    res.status_code = 200
    return res


@app.route("/read_strategy", methods=["POST"])
def read_strategy():
    try:
        data = request.data
        data = json.loads(data)
        s = strategy.read(data["name"], data["symbol"], data["time_frame"], data["broker"])
        res = jsonify({"data": s, "status": "ok"})
        res.status_code = 200
        return res
    except Exception as error:
        print("flask error: ", error)
        res = jsonify({"data": "error", "status": "failed"})
        res.status_code = 500
        return res


@app.route("/read_user_strategy", methods=["POST"])
def read_user_strategy():
    try:
        data = request.data
        # email , broker
        data = json.loads(data)
        strategy_list = strategy.strategy_by_user(data["email"], data["broker"])
        res = jsonify({"data": strategy_list, "status": "ok"})
        res.status_code = 500
        return res
    except Exception as error:
        print("flask error: ", error)
        res = jsonify({"data": "error", "status": "failed"})
        res.status_code = 500
        return res


@app.route("/add_user", methods=["POST"])
def add_user():
    try:
        data = request.data
        data = json.loads(data)
        # email, password, api_key, secret_key, passphrase, broker
        manager.add_user(data)
        res = jsonify({"data": "user added", "status": "ok"})
        res.status_code = 200
        return res
    except Exception as error:
        print("flask error: ", error)
        res = jsonify({"data": "error", "status": "failed"})
        res.status_code = 500
        return res


@app.route("/add_strategy_to_user", methods=["POST"])
def add_strategy_to_user():
    try:
        data = request.data
        # email, broker, strategy_name, symbol, time_frame
        data = json.loads(data)
        manager.strategy_to_user(data)
        res = jsonify({"data": "user added", "status": "ok"})
        res.status_code = 200
        return res
    except Exception as error:
        print("flask error: ", error)
        res = jsonify({"data": "error", "status": "failed"})
        res.status_code = 500
        return res


@app.route("/add_user_strategy_setting", methods=["POST"])
def add_user_strategy_setting():
    try:
        data = request.data
        # email, strategy_name, symbol, time_frame, amount, value_type
        data = json.loads(data)
        database.write_asset_strategy(data)
        res = jsonify({"data": "setting saved", "status": "ok"})
        res.status_code = 200
        return res
    except Exception as error:
        print("flask error: ", error)
        res = jsonify({"data": "error", "status": "failed"})
        res.status_code = 500
        return res


@app.route("/read_user_strategy_setting", methods=["POST"])
def read_user_strategy_setting():
    # if request.headers["token"] == "1234":
    #     Response("token is valid")
    # else:
    #     Response("token is invalid")

    try:
        data = request.data
        # email, strategy_name
        data = json.loads(data)
        database.read_asset_strategy(data["email"], data["strategy_name"])
        res = jsonify({"data": "setting saved", "status": "ok"})
        res.status_code = 200
        return res
    except Exception as error:
        print("flask error: ", error)
        res = jsonify({"data": "error", "status": "failed"})
        res.status_code = 500
        return res


app.run("0.0.0.0", 4000)
