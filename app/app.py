from flask import Flask, request, jsonify

app = Flask(__name__)

# "banco de dados" em memória, uma lista de dicionários
tarefas = [
    {"id": 1, "titulo": "Estudar Flask", "concluida": False},
    {"id": 2, "titulo": "Fazer exercicios de Python", "concluida": True},
]

#  controla o próximo id disponível
proximo_id = 3


def buscar_tarefa(id):
    for tarefa in tarefas:
        if tarefa["id"] == id:
            return tarefa
    return None


# GET /tarefas — lista todas as tarefas
@app.route("/tarefas", methods=["GET"])
def listar_tarefas():
    return jsonify(tarefas)


# GET /tarefas/<id> — busca uma tarefa pelo id
@app.route("/tarefas/<int:id>", methods=["GET"])
def obter_tarefa(id):
    tarefa = buscar_tarefa(id)
    if tarefa is None:
        return jsonify({"erro": "Tarefa nao encontrada"}), 404
    return jsonify(tarefa)


# POST /tarefas — cria uma nova tarefa
@app.route("/tarefas", methods=["POST"])
def criar_tarefa():
    global proximo_id
    dados = request.get_json()

    if not dados or "titulo" not in dados:
        return jsonify({"erro": "Campo 'titulo' é obrigatorio"}), 400

    nova_tarefa = {
        "id": proximo_id,
        "titulo": dados["titulo"],
        "concluida": dados.get("concluida", False),
    }
    tarefas.append(nova_tarefa)
    proximo_id += 1

    return jsonify(nova_tarefa), 201


# PUT /tarefas/<id> — atualiza uma tarefa existente
@app.route("/tarefas/<int:id>", methods=["PUT"])
def atualizar_tarefa(id):
    tarefa = buscar_tarefa(id)
    if tarefa is None:
        return jsonify({"erro": "Tarefa nao encontrada"}), 404

    dados = request.get_json()
    if "titulo" in dados:
        tarefa["titulo"] = dados["titulo"]
    if "concluida" in dados:
        tarefa["concluida"] = dados["concluida"]

    return jsonify(tarefa)


# DELETE /tarefas/<id> — remove uma tarefa
@app.route("/tarefas/<int:id>", methods=["DELETE"])
def deletar_tarefa(id):
    tarefa = buscar_tarefa(id)
    if tarefa is None:
        return jsonify({"erro": "Tarefa nao encontrada"}), 404

    tarefas.remove(tarefa)
    return jsonify({"mensagem": "Tarefa removida com sucesso"})


app.run(host="0.0.0.0", debug=True)
