from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
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
    cursor.execute("PRAGMA table_info(animais)")
    colunas_animais = [coluna[1] for coluna in cursor.fetchall()]

    if "usuario_id" not in colunas_animais:
        cursor.execute("""
            ALTER TABLE animais
            ADD COLUMN usuario_id INTEGER
            REFERENCES usuarios(id)
        """)

    # Adiciona usuario_id em manejos, caso ainda não exista
    cursor.execute("PRAGMA table_info(manejos)")
    colunas_manejos = [coluna[1] for coluna in cursor.fetchall()]

    if "usuario_id" not in colunas_manejos:
        cursor.execute("""
            ALTER TABLE manejos
            ADD COLUMN usuario_id INTEGER
            REFERENCES usuarios(id)
        """)

    # Adiciona usuario_id em vacinacoes, caso ainda não exista
    cursor.execute("PRAGMA table_info(vacinacoes)")
    colunas_vacinacoes = [coluna[1] for coluna in cursor.fetchall()]

    if "usuario_id" not in colunas_vacinacoes:
        cursor.execute("""
            ALTER TABLE vacinacoes
            ADD COLUMN usuario_id INTEGER
            REFERENCES usuarios(id)
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

    cursor.execute(
        "SELECT id FROM usuarios WHERE email = ?",
        ("admin@agrovita.com",)
    )
    admin_id = cursor.fetchone()["id"]
    

    cursor.execute("""
        UPDATE animais
        SET usuario_id = ?
        WHERE usuario_id IS NULL
    """, (admin_id,))

    cursor.execute("""
        UPDATE manejos
        SET usuario_id = ?
        WHERE usuario_id IS NULL
    """, (admin_id,))

    cursor.execute("""
        UPDATE vacinacoes
        SET usuario_id = ?
        WHERE usuario_id IS NULL
    """, (admin_id,))

    conexao.commit()
    conexao.close()

criar_tabelas()


# controle de animais
def criar_animal(dados, usuario_id):
    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO animais (
            identificacao,
            especie,
            raca,
            data_nascimento,
            usuario_id
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        dados.get("identificacao"),
        dados.get("especie"),
        dados.get("raca"),
        dados.get("data_nascimento"),
        usuario_id
    ))

    conexao.commit()
    conexao.close()
    
def listar_animais(usuario_id):
    conexao = conectar_banco()

    animais = conexao.execute(
        "SELECT * FROM animais WHERE usuario_id = ?",
        (usuario_id,)
    ).fetchall()

    conexao.close()
    return animais

def listar_usuarios():
    conexao = conectar_banco()

    usuarios = conexao.execute("""
        SELECT id, nome, email, tipo
        FROM usuarios
        ORDER BY nome
    """).fetchall()

    conexao.close()
    return usuarios

def criar_usuario(nome, email, senha, tipo):
    conexao = conectar_banco()

    senha_hash = generate_password_hash(senha)

    conexao.execute("""
        INSERT INTO usuarios (nome, email, senha, tipo)
        VALUES (?, ?, ?, ?)
    """, (
        nome,
        email,
        senha_hash,
        tipo
    ))

    conexao.commit()
    conexao.close()
def buscar_usuario(id):
    conexao = conectar_banco()

    usuario = conexao.execute(
        "SELECT id, nome, email, tipo FROM usuarios WHERE id = ?",
        (id,)
    ).fetchone()

    conexao.close()
    return usuario

def atualizar_usuario(id, nome, email, tipo):
    conexao = conectar_banco()

    conexao.execute("""
        UPDATE usuarios
        SET nome = ?,
            email = ?,
            tipo = ?
        WHERE id = ?
    """, (
        nome,
        email,
        tipo,
        id
    ))

    conexao.commit()
    conexao.close()
    
def remover_usuario(id):
    conexao = conectar_banco()

    conexao.execute(
        "DELETE FROM usuarios WHERE id = ?",
        (id,)
    )

    conexao.commit()
    conexao.close()

def buscar_animal(id, usuario_id):
    conexao = conectar_banco()

    animal = conexao.execute(
        "SELECT * FROM animais WHERE id = ? AND usuario_id = ?",
        (id, usuario_id)
    ).fetchone()

    conexao.close()
    return animal


def atualizar_animal(id, dados, usuario_id):
    conexao = conectar_banco()

    conexao.execute("""
        UPDATE animais
        SET identificacao = ?,
            especie = ?,
            raca = ?,
            data_nascimento = ?
        WHERE id = ? AND usuario_id = ?
    """, (
        dados.get("identificacao"),
        dados.get("especie"),
        dados.get("raca"),
        dados.get("data_nascimento"),
        id,
        usuario_id
    ))

    conexao.commit()
    conexao.close()


def remover_animal(id, usuario_id):
    conexao = conectar_banco()

    conexao.execute(
        "DELETE FROM animais WHERE id = ? AND usuario_id = ?",
        (id, usuario_id)
    )

    conexao.commit()
    conexao.close()
    

# controle de manejo
def criar_manejo(dados, usuario_id):
    conexao = conectar_banco()

    conexao.execute("""
        INSERT INTO manejos (
            animal,
            tipo_manejo,
            data_manejo,
            produto,
            dose,
            responsavel,
            observacoes,
            usuario_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        dados.get("animal"),
        dados.get("tipo_manejo"),
        dados.get("data_manejo"),
        dados.get("produto"),
        dados.get("dose"),
        dados.get("responsavel"),
        dados.get("observacoes"),
        usuario_id
    ))

    conexao.commit()
    conexao.close()


def listar_manejos(usuario_id):
    conexao = conectar_banco()

    manejos = conexao.execute(
        "SELECT * FROM manejos WHERE usuario_id = ? ORDER BY id DESC",
        (usuario_id,)
    ).fetchall()

    conexao.close()
    return manejos


def buscar_manejo(id, usuario_id):
    conexao = conectar_banco()

    manejo = conexao.execute(
        "SELECT * FROM manejos WHERE id = ? AND usuario_id = ?",
        (id, usuario_id)
    ).fetchone()

    conexao.close()
    return manejo


def atualizar_manejo(id, dados, usuario_id):
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
        WHERE id = ? AND usuario_id = ?
    """, (
        dados.get("animal"),
        dados.get("tipo_manejo"),
        dados.get("data_manejo"),
        dados.get("produto"),
        dados.get("dose"),
        dados.get("responsavel"),
        dados.get("observacoes"),
        id,
        usuario_id
    ))

    conexao.commit()
    conexao.close()


def remover_manejo(id, usuario_id):
    conexao = conectar_banco()

    conexao.execute(
        "DELETE FROM manejos WHERE id = ? AND usuario_id = ?",
        (id, usuario_id)
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

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "usuario_id" not in session:
            return redirect(url_for("login"))

        if session.get("usuario_tipo") != "admin":
            flash("Acesso permitido apenas para administradores.")
            return redirect(url_for("inicio"))

        return f(*args, **kwargs)

    return decorated_function

@app.route("/cadastro-usuario", methods=["GET", "POST"])
def cadastro_usuario():
    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        senha = request.form["senha"]

        conexao = conectar_banco()

        usuario_existente = conexao.execute(
            "SELECT id FROM usuarios WHERE email = ?",
            (email,)
        ).fetchone()

        conexao.close()

        if usuario_existente:
            return render_template(
                "cadastro_usuario.html",
                erro="Já existe uma conta com esse e-mail."
            )

        criar_usuario(nome, email, senha, "usuario")

        return redirect(url_for("login"))

    return render_template("cadastro_usuario.html")

@app.route("/usuarios/editar/<int:id>", methods=["GET", "POST"])
@admin_required
def editar_usuario(id):
    usuario = buscar_usuario(id)

    if usuario is None:
        return redirect(url_for("usuarios"))

    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        tipo = request.form["tipo"]

        if id == session["usuario_id"] and tipo != "admin":
            flash("Você não pode remover seu próprio acesso de administrador.")
            return redirect(url_for("editar_usuario", id=id))

        atualizar_usuario(id, nome, email, tipo)

        return redirect(url_for("usuarios"))

    return render_template(
        "editar_usuario.html",
        usuario=usuario
    )

@app.route("/usuarios/excluir/<int:id>", methods=["POST"])
@admin_required
def excluir_usuario(id):
    if id == session["usuario_id"]:
        flash("Você não pode excluir sua própria conta.")
        return redirect(url_for("usuarios"))

    remover_usuario(id)

    return redirect(url_for("usuarios"))

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
        }, session["usuario_id"])

        return redirect(url_for("listagem"))
    return render_template("manejo.html")

@app.route("/manejo/atualizar/<int:id>", methods=["GET", "POST"])
@login_required
def atualizar_manejo_route(id):
    registro = buscar_manejo(id, session["usuario_id"])

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
        }, session["usuario_id"])

        return redirect(url_for("listagem"))

    return render_template("manejo.html", registro=registro)


@app.route("/manejo/remover/<int:id>", methods=["POST"])
@login_required
def remover_manejo_route(id):
    remover_manejo(id, session["usuario_id"])
    return redirect(url_for("listagem"))

# Atualize a rota de listagem existente para enviar também os manejos
@app.route("/listagem")
@login_required
def listagem():
    vacinacoes = listar_vacinacoes(session["usuario_id"])

    return render_template(
        "listagem.html",
        animais = listar_animais(session["usuario_id"]),
        vacinacoes=vacinacoes,
        manejos=listar_manejos(session["usuario_id"])
    )
    
def criar_vacinacao(dados, usuario_id):
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
            observacoes,
            usuario_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        usuario_id
    ))

    conexao.commit()
    conexao.close()


def listar_vacinacoes(usuario_id):
    conexao = conectar_banco()

    registros = conexao.execute(
        "SELECT * FROM vacinacoes WHERE usuario_id = ?",
        (usuario_id,)
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


def buscar_vacinacao(id, usuario_id):
    conexao = conectar_banco()

    vacinacao = conexao.execute(
        "SELECT * FROM vacinacoes WHERE id = ? AND usuario_id = ?",
        (id, usuario_id)
    ).fetchone()

    conexao.close()
    return vacinacao


def atualizar_vacinacao(id, dados, usuario_id):
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
        WHERE id = ? AND usuario_id = ?
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
        id,
        usuario_id
    ))

    conexao.commit()
    conexao.close()


def remover_vacinacao(id, usuario_id):
    conexao = conectar_banco()

    conexao.execute(
        "DELETE FROM vacinacoes WHERE id = ? AND usuario_id = ?",
        (id, usuario_id)
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
    total_animais = len(listar_animais(session["usuario_id"]))
    total_vacinacoes = len(listar_vacinacoes(session["usuario_id"]))
    total_manejos = len(listar_manejos(session["usuario_id"]))

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
}, session["usuario_id"])

        return redirect(url_for("listagem"))

    return render_template("cadastro.html")

#usuarios
@app.route("/usuarios", methods=["GET", "POST"])
@admin_required
def usuarios():
    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        senha = request.form["senha"]
        tipo = request.form["tipo"]

        criar_usuario(nome, email, senha, tipo)

        return redirect(url_for("usuarios"))

    usuarios = listar_usuarios()

    return render_template(
        "usuarios.html",
        usuarios=usuarios
    )

# Edição de animal
@app.route("/animais/atualizar/<int:id>", methods=["GET", "POST"])
@login_required
def atualizar_animal_route(id):
    animal = buscar_animal(id, session["usuario_id"])

    if animal is None:
        return redirect(url_for("listagem"))

    if request.method == "POST":
        atualizar_animal(id, {
            "identificacao": request.form.get("identificacao"),
            "especie": request.form.get("especie"),
            "raca": request.form.get("raca"),
            "data_nascimento": request.form.get("data_nascimento"),
        }, session["usuario_id"])
        
        

        return redirect(url_for("listagem"))

    return render_template("cadastro.html", animal=animal)



# Remoção de um animal
@app.route("/animais/remover/<int:id>", methods=["POST"])
@login_required
def remover_animal_route(id):
    remover_animal(id, session["usuario_id"])
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
        }, session["usuario_id"])

        return redirect(url_for("listagem"))

    return render_template("vacinacao.html")


# Edição de um registro de vacinação
@app.route("/vacinacao/atualizar/<int:id>", methods=["GET", "POST"])
@login_required
def atualizar_vacinacao_route(id):

    registro = buscar_vacinacao(id, session["usuario_id"])

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
        }, session["usuario_id"])

        return redirect(url_for("listagem"))

    return render_template("vacinacao.html", registro=registro)

@app.route("/vacinacao/remover/<int:id>", methods=["POST"])
@login_required
def remover_vacinacao_route(id):
    remover_vacinacao(id, session["usuario_id"])
    return redirect(url_for("listagem"))

@app.route("/dashboard")
@login_required
def dashboard():
    animais = listar_animais(session["usuario_id"])
    vacinacoes = listar_vacinacoes(session["usuario_id"])   
    manejos = listar_manejos(session["usuario_id"])

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