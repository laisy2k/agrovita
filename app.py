from flask import Flask, render_template, request, redirect, url_for, session
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3 
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = "agrovita-chave-secreta"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CAMINHO_BANCO = os.path.join(BASE_DIR, "mediagro.db")

def conectar_banco():
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row
    return conexao

def criar_tabelas():
    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS animais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            identificacao TEXT NOT NULL,
            especie TEXT NOT NULL,
            raca TEXT,
            data_nascimento TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vacinacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            animal TEXT NOT NULL,
            vacina TEXT NOT NULL,
            lote TEXT,
            fabricante TEXT,
            data_aplicacao TEXT,
            proxima_dose TEXT,
            dose TEXT,
            responsavel TEXT,
            observacoes TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS manejos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            animal TEXT NOT NULL,
            tipo_manejo TEXT NOT NULL,
            data_manejo TEXT NOT NULL,
            produto TEXT,
            dose TEXT,
            responsavel TEXT NOT NULL,
            observacoes TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL,
            tipo TEXT NOT NULL DEFAULT 'usuario'
        )
    """)

    cursor.execute(
        "SELECT * FROM usuarios WHERE email = ?",
        ("admin@agrovita.com",)
    )
    admin = cursor.fetchone()

    if admin is None:
        senha_hash = generate_password_hash("admin123")

        cursor.execute("""
            INSERT INTO usuarios (nome, email, senha, tipo)
            VALUES (?, ?, ?, ?)
        """, ("Administrador", "admin@agrovita.com", senha_hash, "admin"))

    conexao.commit()
    conexao.close()

criar_tabelas()


# controle de animais
def criar_animal(dados):
    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO animais (
            identificacao,
            especie,
            raca,
            data_nascimento
        )
        VALUES (?, ?, ?, ?)
    """, (
        dados.get("identificacao"),
        dados.get("especie"),
        dados.get("raca"),
        dados.get("data_nascimento")
    ))

    conexao.commit()
    conexao.close()


def listar_animais():
    conexao = conectar_banco()

    animais = conexao.execute(
        "SELECT * FROM animais"
    ).fetchall()

    conexao.close()
    return animais


def buscar_animal(id):
    conexao = conectar_banco()

    animal = conexao.execute(
        "SELECT * FROM animais WHERE id = ?",
        (id,)
    ).fetchone()

    conexao.close()
    return animal


def atualizar_animal(id, dados):
    conexao = conectar_banco()

    conexao.execute("""
        UPDATE animais
        SET identificacao = ?,
            especie = ?,
            raca = ?,
            data_nascimento = ?
        WHERE id = ?
    """, (
        dados.get("identificacao"),
        dados.get("especie"),
        dados.get("raca"),
        dados.get("data_nascimento"),
        id
    ))

    conexao.commit()
    conexao.close()


def remover_animal(id):
    conexao = conectar_banco()

    conexao.execute(
        "DELETE FROM animais WHERE id = ?",
        (id,)
    )

    conexao.commit()
    conexao.close()

# controle de manejo

def criar_manejo(dados):
    conexao = conectar_banco()

    conexao.execute("""
        INSERT INTO manejos (
            animal,
            tipo_manejo,
            data_manejo,
            produto,
            dose,
            responsavel,
            observacoes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        dados.get("animal"),
        dados.get("tipo_manejo"),
        dados.get("data_manejo"),
        dados.get("produto"),
        dados.get("dose"),
        dados.get("responsavel"),
        dados.get("observacoes")
    ))

    conexao.commit()
    conexao.close()


def listar_manejos():
    conexao = conectar_banco()

    manejos = conexao.execute(
        "SELECT * FROM manejos ORDER BY id DESC"
    ).fetchall()

    conexao.close()
    return manejos


def buscar_manejo(id):
    conexao = conectar_banco()

    manejo = conexao.execute(
        "SELECT * FROM manejos WHERE id = ?",
        (id,)
    ).fetchone()

    conexao.close()
    return manejo


def atualizar_manejo(id, dados):
    conexao = conectar_banco()

    conexao.execute("""
        UPDATE manejos
        SET animal = ?,
            tipo_manejo = ?,
            data_manejo = ?,
            produto = ?,
            dose = ?,
            responsavel = ?,
            observacoes = ?
        WHERE id = ?
    """, (
        dados.get("animal"),
        dados.get("tipo_manejo"),
        dados.get("data_manejo"),
        dados.get("produto"),
        dados.get("dose"),
        dados.get("responsavel"),
        dados.get("observacoes"),
        id
    ))

    conexao.commit()
    conexao.close()


def remover_manejo(id):
    conexao = conectar_banco()

    conexao.execute(
        "DELETE FROM manejos WHERE id = ?",
        (id,)
    )

    conexao.commit()
    conexao.close()
    
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "usuario_id" not in session:
            return redirect(url_for("login"))

        return f(*args, **kwargs)

    return decorated_function

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]

        conexao = conectar_banco()

        usuario = conexao.execute(
            "SELECT * FROM usuarios WHERE email = ?",
            (email,)
        ).fetchone()

        conexao.close()

        if usuario and check_password_hash(usuario["senha"], senha):
            session["usuario_id"] = usuario["id"]
            session["usuario_nome"] = usuario["nome"]
            session["usuario_tipo"] = usuario["tipo"]

            return redirect(url_for("inicio"))

        return render_template(
            "login.html",
            erro="E-mail ou senha inválidos."
        )

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# Rota de Registro de Manejo
@app.route("/manejo", methods=["GET", "POST"])
@login_required
def manejo():
    if request.method == "POST":
        criar_manejo({
            "animal": request.form.get("animal"),
            "tipo_manejo": request.form.get("tipo_manejo"),
            "data_manejo": request.form.get("data_manejo"),
            "produto": request.form.get("produto"),
            "dose": request.form.get("dose"),
            "responsavel": request.form.get("responsavel"),
            "observacoes": request.form.get("observacoes")
        })
        return redirect(url_for("listagem"))
    return render_template("manejo.html")

@app.route("/manejo/atualizar/<int:id>", methods=["GET", "POST"])
@login_required
def atualizar_manejo_route(id):
    registro = buscar_manejo(id)

    if registro is None:
        return redirect(url_for("listagem"))

    if request.method == "POST":
        atualizar_manejo(id, {
            "animal": request.form.get("animal"),
            "tipo_manejo": request.form.get("tipo_manejo"),
            "data_manejo": request.form.get("data_manejo"),
            "produto": request.form.get("produto"),
            "dose": request.form.get("dose"),
            "responsavel": request.form.get("responsavel"),
            "observacoes": request.form.get("observacoes")
        })

        return redirect(url_for("listagem"))

    return render_template("manejo.html", registro=registro)


@app.route("/manejo/remover/<int:id>", methods=["POST"])
@login_required
def remover_manejo_route(id):
    remover_manejo(id)
    return redirect(url_for("listagem"))

# Atualize a rota de listagem existente para enviar também os manejos
@app.route("/listagem")
@login_required
def listagem():
    vacinacoes = listar_vacinacoes()

    return render_template(
        "listagem.html",
        animais=listar_animais(),
        vacinacoes=vacinacoes,
        manejos=listar_manejos()
    )
    
def criar_vacinacao(dados):
    conexao = conectar_banco()

    conexao.execute("""
        INSERT INTO vacinacoes (
            animal,
            vacina,
            lote,
            fabricante,
            data_aplicacao,
            proxima_dose,
            dose,
            responsavel,
            observacoes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        dados.get("animal"),
        dados.get("vacina"),
        dados.get("lote"),
        dados.get("fabricante"),
        dados.get("data_aplicacao"),
        dados.get("proxima_dose"),
        dados.get("dose"),
        dados.get("responsavel"),
        dados.get("observacoes")
    ))

    conexao.commit()
    conexao.close()


def listar_vacinacoes():
    conexao = conectar_banco()

    registros = conexao.execute(
        "SELECT * FROM vacinacoes"
    ).fetchall()

    conexao.close()

    vacinacoes = []

    for registro in registros:
        vacinacao = dict(registro)
        vacinacao["status"] = status_vacina(
            vacinacao.get("proxima_dose")
        )
        vacinacoes.append(vacinacao)

    return vacinacoes


def buscar_vacinacao(id):
    conexao = conectar_banco()

    vacinacao = conexao.execute(
        "SELECT * FROM vacinacoes WHERE id = ?",
        (id,)
    ).fetchone()

    conexao.close()
    return vacinacao


def atualizar_vacinacao(id, dados):
    conexao = conectar_banco()

    conexao.execute("""
        UPDATE vacinacoes
        SET animal = ?,
            vacina = ?,
            lote = ?,
            fabricante = ?,
            data_aplicacao = ?,
            proxima_dose = ?,
            dose = ?,
            responsavel = ?,
            observacoes = ?
        WHERE id = ?
    """, (
        dados.get("animal"),
        dados.get("vacina"),
        dados.get("lote"),
        dados.get("fabricante"),
        dados.get("data_aplicacao"),
        dados.get("proxima_dose"),
        dados.get("dose"),
        dados.get("responsavel"),
        dados.get("observacoes"),
        id
    ))

    conexao.commit()
    conexao.close()


def remover_vacinacao(id):
    conexao = conectar_banco()

    conexao.execute(
        "DELETE FROM vacinacoes WHERE id = ?",
        (id,)
    )

    conexao.commit()
    conexao.close()

def status_vacina(proxima_dose):
    if not proxima_dose:
        return None

    try:
        prox = date.fromisoformat(proxima_dose)
    except ValueError:
        return None

    hoje = date.today()

    if prox < hoje:
        return "atrasada"
    elif prox == hoje:
        return "hoje"
    else:
        return "em_dia"

# Página inicial
@app.route("/")
@login_required
def inicio():
    total_animais = len(listar_animais())
    total_vacinacoes = len(listar_vacinacoes())
    total_manejos = len(listar_manejos())

    return render_template(
        "index.html",
        total_animais=total_animais,
        total_vacinacoes=total_vacinacoes,
        total_manejos=total_manejos
    )


# Cadastro de animal
@app.route("/cadastro", methods=["GET", "POST"])
@login_required
def cadastro():

    if request.method == "POST":

        criar_animal({
            "identificacao": request.form.get("identificacao"),
            "especie": request.form.get("especie"),
            "raca": request.form.get("raca"),
            "data_nascimento": request.form.get("data_nascimento"),
        })

        return redirect(url_for("listagem"))

    return render_template("cadastro.html")

# Edição de animal
@app.route("/animais/atualizar/<int:id>", methods=["GET", "POST"])
@login_required
def atualizar_animal_route(id):
    animal = buscar_animal(id)

    if animal is None:
        return redirect(url_for("listagem"))

    if request.method == "POST":
        atualizar_animal(id, {
            "identificacao": request.form.get("identificacao"),
            "especie": request.form.get("especie"),
            "raca": request.form.get("raca"),
            "data_nascimento": request.form.get("data_nascimento"),
        })

        return redirect(url_for("listagem"))

    return render_template("cadastro.html", animal=animal)

# Remoção de um animal
@app.route("/animais/remover/<int:id>", methods=["POST"])
@login_required
def remover_animal_route(id):
    remover_animal(id)
    return redirect(url_for("listagem"))


# Registro de vacinação
@app.route("/vacinacao", methods=["GET", "POST"])
@login_required
def vacinacao():

    if request.method == "POST":
        criar_vacinacao({
            "animal": request.form.get("animal"),
            "vacina": request.form.get("vacina"),
            "lote": request.form.get("lote"),
            "fabricante": request.form.get("fabricante"),
            "data_aplicacao": request.form.get("data_aplicacao"),
            "proxima_dose": request.form.get("proxima_dose"),
            "dose": request.form.get("dose"),
            "responsavel": request.form.get("responsavel"),
            "observacoes": request.form.get("observacoes"),
        })

        return redirect(url_for("listagem"))

    return render_template("vacinacao.html")


# Edição de um registro de vacinação
@app.route("/vacinacao/atualizar/<int:id>", methods=["GET", "POST"])
@login_required
def atualizar_vacinacao_route(id):

    registro = buscar_vacinacao(id)

    if registro is None:
        return redirect(url_for("listagem"))

    if request.method == "POST":
        atualizar_vacinacao(id, {
            "animal": request.form.get("animal"),
            "vacina": request.form.get("vacina"),
            "lote": request.form.get("lote"),
            "fabricante": request.form.get("fabricante"),
            "data_aplicacao": request.form.get("data_aplicacao"),
            "proxima_dose": request.form.get("proxima_dose"),
            "dose": request.form.get("dose"),
            "responsavel": request.form.get("responsavel"),
            "observacoes": request.form.get("observacoes"),
        })

        return redirect(url_for("listagem"))

    return render_template("vacinacao.html", registro=registro)

@app.route("/vacinacao/remover/<int:id>", methods=["POST"])
@login_required
def remover_vacinacao_route(id):
    remover_vacinacao(id)
    return redirect(url_for("listagem"))

@app.route("/dashboard")
@login_required
def dashboard():
    animais = listar_animais()
    vacinacoes = listar_vacinacoes()
    manejos = listar_manejos()

    # Métricas gerais
    total_animais = len(animais)
    total_vacinacoes = len(vacinacoes)
    total_manejos = len(manejos)

    vacinacoes_em_dia = sum(
        1 for vacinacao in vacinacoes
        if vacinacao.get("status") == "em_dia"
    )

    vacinacoes_hoje = sum(
        1 for vacinacao in vacinacoes
        if vacinacao.get("status") == "hoje"
    )

    vacinacoes_atrasadas = sum(
        1 for vacinacao in vacinacoes
        if vacinacao.get("status") == "atrasada"
    )

    # Registros que precisam de atenção
    vacinacoes_atencao = [
        vacinacao for vacinacao in vacinacoes
        if vacinacao.get("status") == "atrasada"
    ]

   # Últimos 5 manejos cadastrados
    manejos_recentes = manejos[:5]

    return render_template(
        "dashboard.html",
        total_animais=total_animais,
        total_vacinacoes=total_vacinacoes,
        total_manejos=total_manejos,
        vacinacoes_atrasadas=vacinacoes_atrasadas,
        vacinacoes_atencao=vacinacoes_atencao,
        manejos_recentes=manejos_recentes,
        vacinacoes_em_dia=vacinacoes_em_dia,
        vacinacoes_hoje=vacinacoes_hoje,
    )

if __name__ == "__main__":
    app.run(debug=True)