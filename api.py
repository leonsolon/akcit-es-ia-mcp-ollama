"""API de cadastro de clientes. Um sistema comum, sem nada de IA."""
from flask import Flask, jsonify, request

app = Flask(__name__)
clientes = {}
proximo_id = 1


@app.get("/clientes")
def listar():
    return jsonify(list(clientes.values()))


@app.post("/clientes")
def cadastrar():
    global proximo_id
    dados = request.get_json()
    cliente = {"id": proximo_id, "nome": dados["nome"], "email": dados["email"]}
    clientes[proximo_id] = cliente
    proximo_id += 1
    return jsonify(cliente), 201


@app.delete("/clientes/<int:id>")
def remover(id):
    if id not in clientes:
        return jsonify({"erro": "cliente não encontrado"}), 404
    return jsonify(clientes.pop(id))


if __name__ == "__main__":
    app.run(port=5001)  # a porta 5000 costuma estar ocupada no Mac (AirPlay)
