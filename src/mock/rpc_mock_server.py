from decimal import Decimal
from functools import wraps

from flask import Flask, request, jsonify

app = Flask(__name__)

RPC_USER = "user"
RPC_PASSWORD = "pass"
RPC_PORT = 8899

balance = Decimal(0)


def check_auth(username, password):
    return username == RPC_USER and password == RPC_PASSWORD


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)

    return decorated


@app.route("/", methods=["POST"])
@require_auth
def rpc():
    global balance
    data = request.get_json(force=True)

    method = data.get("method")
    rpc_id = data.get("id", None)

    if method == "getconnectioncount":
        result = 5
    elif method == "getwalletinfo":
        balance += Decimal(1)
        result = {
            "walletname": " / [default wallet]",
            "walletversion": 169900,
            "format": "bdb",
            "balance": balance,
            "unconfirmed_balance": 0.00000000,
            "immature_balance": 0.00000000,
            "ttl_balance": balance,
            "sql_balance": balance,
            "txcount": 7,
            "keypoololdest": 123456789,
            "keypoolsize": 1000,
            "hdseedid": "5e4fe5fe54fef45b45c45545454500565065056",
            "keypoolsize_hd_internal": 1000,
            "paytxfee": 0.00000000,
            "private_keys_enabled": True,
            "avoid_reuse": False,
            "scanning": False,
            "descriptors": False
        }

    elif method == "getstakinginfo":
        result = {
            "enabled": True,
            "staking": False,
            "errors": "",
            "currentblockweight": 102524,
            "currentblocktx": 87,
            "difficulty": 300569.3897715717,
            "search-interval": 16,
            "search-time": "2025-05-29T09:06:40Z",
            "stake-time": "2025-04-21T09:51:12Z",
            "weight": 16195250107,
            "balance": 16195250107,
            "netstakeweight": 343575490874245,
            "expectedtime": 3182187
        }

    elif method == "getstakereport":
        result = {
            "2025-06-05T00:00:00Z": "2.43750003",
            "2025-06-04T00:00:00Z": "0.00",
            "2025-06-03T00:00:00Z": "0.00",
            "2025-06-02T00:00:00Z": "0.00",
            "2025-06-01T00:00:00Z": "0.00",
            "2025-05-31T00:00:00Z": "2.43750003",
            "2025-05-30T00:00:00Z": "0.00",
            "2025-05-29T00:00:00Z": "0.00",
            "2025-05-28T00:00:00Z": "0.00",
            "2025-05-27T00:00:00Z": "0.00",
            "2025-05-26T00:00:00Z": "0.00",
            "2025-05-25T00:00:00Z": "0.00",
            "2025-05-24T00:00:00Z": "2.43750003",
            "2025-05-23T00:00:00Z": "0.00",
            "2025-05-22T00:00:00Z": "0.00",
            "2025-05-21T00:00:00Z": "0.00",
            "2025-05-20T00:00:00Z": "0.00",
            "2025-05-19T00:00:00Z": "2.43750003",
            "2025-05-18T00:00:00Z": "0.00",
            "2025-05-17T00:00:00Z": "0.00",
            "2025-05-16T00:00:00Z": "0.00",
            "2025-05-15T00:00:00Z": "0.00",
            "2025-05-14T00:00:00Z": "0.00",
            "2025-05-13T00:00:00Z": "0.00",
            "2025-05-12T00:00:00Z": "0.00",
            "2025-05-11T00:00:00Z": "0.00",
            "2025-05-10T00:00:00Z": "0.00",
            "2025-05-09T00:00:00Z": "0.00",
            "2025-05-08T00:00:00Z": "0.00",
            "2025-05-07T00:00:00Z": "0.00",
            "Last 24H": "0.00",
            "Last 7 Days": "0.00",
            "Last 30 Days": "0.00",
            "Last 365 Days": "7.31250107",
            "Latest Stake": "2.43750003",
            "Latest Time": "2025-04-21T09:51:12Z",
            "Stake counted": 3,
            "time took (ms)": 2533
        }

    else:
        return jsonify({
            "result": None,
            "error": {"code": -32601, "message": "Method not found"},
            "id": rpc_id
        })

    return jsonify({
        "result": result,
        "error": None,
        "id": rpc_id
    })


def start():
    app.run(host="0.0.0.0", port=RPC_PORT)
