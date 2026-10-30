from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from datetime import date, datetime, timezone, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ["SECRET_KEY"]
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    PERMANENT_SESSION_LIFETIME=timedelta(minutes=30),
    SESSION_REFRESH_EACH_REQUEST=True
)

@app.before_request
def verificar_inatividade():
    if "usuario_id" not in session:
        return

    agora = datetime.now(timezone.utc).timestamp()
    ultima_atividade = session.get("ultima_atividade")

    if ultima_atividade is not None:
        if agora - ultima_atividade > 30 * 60:
            registrar_log(
                session["usuario_id"],
                "SESSAO_EXPIRADA",
                "Sessão encerrada após 30 minutos de inatividade"
            )

            session.clear()
            flash("Sua sessão expirou por inatividade. Faça login novamente.")
            return redirect(url_for("login"))

    session["ultima_atividade"] = agora


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Banco SQLite
PASTA_BANCO = os.path.join(BASE_DIR, "instance")
os.makedirs(PASTA_BANCO, exist_ok=True)

DB_PATH = os.getenv(
    "DATABASE_PATH",
    os.path.join(PASTA_BANCO, "agrovita.db")
)


def conectar_banco():
    """Abre uma conexão com o banco SQLite."""
    conexao = sqlite3.connect(DB_PATH, timeout=20)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def registrar_log(usuario_id, acao, detalhes=None):
    conexao = conectar_banco()

    try:
        conexao.execute("""
            INSERT INTO logs_auditoria (usuario_id, acao, detalhes)
            VALUES (?, ?, ?)
        """, (usuario_id, acao, detalhes))

        conexao.commit()
    finally:
        conexao.close()


def criar_tabelas():
    """Cria as tabelas do AgroVita caso ainda não existam."""
    conexao = conectar_banco()

    try:
        conexao.executescript("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                senha TEXT NOT NULL,
                tipo TEXT NOT NULL DEFAULT 'usuario'
            );

            CREATE TABLE IF NOT EXISTS animais (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                identificacao TEXT NOT NULL,
                especie TEXT NOT NULL,
                raca TEXT,
                data_nascimento TEXT,
                usuario_id INTEGER NOT NULL,
                FOREIGN KEY (usuario_id)
                    REFERENCES usuarios(id)
            );

            CREATE TABLE IF NOT EXISTS manejos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                animal_id INTEGER NOT NULL,
                usuario_id INTEGER NOT NULL,
                tipo_manejo TEXT NOT NULL,
                data_manejo TEXT NOT NULL,
                produto TEXT,
                dose TEXT,
                responsavel TEXT NOT NULL,
                observacoes TEXT,
                FOREIGN KEY (animal_id)
                    REFERENCES animais(id),
                FOREIGN KEY (usuario_id)
                    REFERENCES usuarios(id)
            );

            CREATE TABLE IF NOT EXISTS vacinacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                animal_id INTEGER NOT NULL,
                usuario_id INTEGER NOT NULL,
                vacina TEXT NOT NULL,
                lote TEXT,
                fabricante TEXT,
                data_aplicacao TEXT NOT NULL,
                proxima_dose TEXT,
                dose TEXT,
                responsavel TEXT,
                observacoes TEXT,
                FOREIGN KEY (animal_id)
                    REFERENCES animais(id),
                FOREIGN KEY (usuario_id)
                    REFERENCES usuarios(id)
            );

            CREATE TABLE IF NOT EXISTS logs_auditoria (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER,
                acao TEXT NOT NULL,
                detalhes TEXT,
                data_hora TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id)
                    REFERENCES usuarios(id)
                    ON DELETE SET NULL
            );
        """)
        conexao.commit()
    finally:
        conexao.close()


criar_tabelas()



# controle de animais
def criar_animal(dados, usuario_id):
    conexao = conectar_banco()
    cursor = conexao.cursor()

    try:
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

        animal_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO logs_auditoria (usuario_id, acao, detalhes)
            VALUES (?, ?, ?)
        """, (
            usuario_id,
            "CRIAR_ANIMAL",
            f"Animal ID {animal_id} cadastrado"
        ))

        conexao.commit()

    except Exception:
        conexao.rollback()
        raise

    finally:
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

    try:
        cursor = conexao.execute("""
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

        if cursor.rowcount > 0:
            conexao.execute("""
                INSERT INTO logs_auditoria (usuario_id, acao, detalhes)
                VALUES (?, ?, ?)
            """, (
                usuario_id,
                "EDITAR_ANIMAL",
                f"Animal ID {id} atualizado"
            ))

        conexao.commit()

    except Exception:
        conexao.rollback()
        raise

    finally:
        conexao.close()


def remover_animal(id, usuario_id):
    conexao = conectar_banco()

    try:
        cursor = conexao.execute(
            "DELETE FROM animais WHERE id = ? AND usuario_id = ?",
            (id, usuario_id)
        )

        if cursor.rowcount > 0:
            conexao.execute("""
                INSERT INTO logs_auditoria (usuario_id, acao, detalhes)
                VALUES (?, ?, ?)
            """, (
                usuario_id,
                "EXCLUIR_ANIMAL",
                f"Animal ID {id} excluído"
            ))

        conexao.commit()

    except Exception:
        conexao.rollback()
        raise

    finally:
        conexao.close()

# controle de manejo
def _resolver_animal_id(conexao, identificacao, usuario_id):
    """Resolve o ID ou a identificação de um animal pertencente ao usuário."""
    valor = str(identificacao or "").strip()
    if not valor:
        raise ValueError("Selecione um animal válido.")

    # O formulário pode enviar o ID ou a identificação do animal.
    if valor.isdecimal():
        animal = conexao.execute(
            "SELECT id FROM animais WHERE id = ? AND usuario_id = ?",
            (int(valor), usuario_id),
        ).fetchone()
        if animal is not None:
            return animal["id"]

    animal = conexao.execute(
        "SELECT id FROM animais WHERE TRIM(identificacao) = TRIM(?) "
        "AND usuario_id = ? ORDER BY id LIMIT 1",
        (valor, usuario_id),
    ).fetchone()
    if animal is None:
        raise ValueError(
            "O animal selecionado não foi encontrado na sua conta. "
            "Confira se ele está cadastrado para este usuário."
        )
    return animal["id"]


def criar_manejo(dados, usuario_id):
    conexao = conectar_banco()
    try:
        animal_id = _resolver_animal_id(conexao, dados.get("animal"), usuario_id)
        cursor = conexao.execute("""
            INSERT INTO manejos (animal_id, usuario_id, tipo_manejo, data_manejo,
                produto, dose, responsavel, observacoes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (animal_id, usuario_id, dados.get("tipo_manejo"), dados.get("data_manejo"),
              dados.get("produto"), dados.get("dose"), dados.get("responsavel"),
              dados.get("observacoes")))
        manejo_id = cursor.lastrowid
        conexao.execute("INSERT INTO logs_auditoria (usuario_id, acao, detalhes) VALUES (?, ?, ?)",
                        (usuario_id, "CRIAR_MANEJO", f"Manejo ID {manejo_id} cadastrado"))
        conexao.commit()
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()


def listar_manejos(usuario_id):
    conexao = conectar_banco()
    try:
        return conexao.execute("""
            SELECT m.id, m.animal_id, a.identificacao AS animal, m.usuario_id,
                   m.tipo_manejo, m.data_manejo, m.produto, m.dose,
                   m.responsavel, m.observacoes
            FROM manejos m JOIN animais a ON a.id = m.animal_id
            WHERE m.usuario_id = ? ORDER BY m.id DESC
        """, (usuario_id,)).fetchall()
    finally:
        conexao.close()


def buscar_manejo(id, usuario_id):
    conexao = conectar_banco()
    try:
        return conexao.execute("""
            SELECT m.id, m.animal_id, a.identificacao AS animal, m.usuario_id,
                   m.tipo_manejo, m.data_manejo, m.produto, m.dose,
                   m.responsavel, m.observacoes
            FROM manejos m JOIN animais a ON a.id = m.animal_id
            WHERE m.id = ? AND m.usuario_id = ?
        """, (id, usuario_id)).fetchone()
    finally:
        conexao.close()


def atualizar_manejo(id, dados, usuario_id):
    conexao = conectar_banco()
    try:
        animal_id = _resolver_animal_id(conexao, dados.get("animal"), usuario_id)
        cursor = conexao.execute("""
            UPDATE manejos SET animal_id = ?, tipo_manejo = ?, data_manejo = ?,
                produto = ?, dose = ?, responsavel = ?, observacoes = ?
            WHERE id = ? AND usuario_id = ?
        """, (animal_id, dados.get("tipo_manejo"), dados.get("data_manejo"),
              dados.get("produto"), dados.get("dose"), dados.get("responsavel"),
              dados.get("observacoes"), id, usuario_id))
        if cursor.rowcount > 0:
            conexao.execute("INSERT INTO logs_auditoria (usuario_id, acao, detalhes) VALUES (?, ?, ?)",
                            (usuario_id, "EDITAR_MANEJO", f"Manejo ID {id} atualizado"))
        conexao.commit()
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()


def remover_manejo(id, usuario_id):
    conexao = conectar_banco()
    try:
        cursor = conexao.execute("DELETE FROM manejos WHERE id = ? AND usuario_id = ?", (id, usuario_id))
        if cursor.rowcount > 0:
            conexao.execute("INSERT INTO logs_auditoria (usuario_id, acao, detalhes) VALUES (?, ?, ?)",
                            (usuario_id, "EXCLUIR_MANEJO", f"Manejo ID {id} excluído"))
        conexao.commit()
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        usuario_id = session.get("usuario_id")

        if usuario_id is None:
            return redirect(url_for("login"))

        conexao = conectar_banco()

        usuario = conexao.execute(
            "SELECT id FROM usuarios WHERE id = ?",
            (usuario_id,)
        ).fetchone()

        conexao.close()

        if usuario is None:
            session.clear()
            return redirect(url_for("login"))

        return f(*args, **kwargs)

    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        usuario_id = session.get("usuario_id")

        if usuario_id is None:
            return redirect(url_for("login"))

        conexao = conectar_banco()

        usuario = conexao.execute(
            "SELECT tipo FROM usuarios WHERE id = ?",
            (usuario_id,)
        ).fetchone()

        conexao.close()

        if usuario is None:
            session.clear()
            return redirect(url_for("login"))

        if usuario["tipo"] != "admin":
            registrar_log(
                usuario_id,
                "ACESSO_NEGADO",
                "Tentativa de acesso a uma área administrativa"
            )

            session["usuario_tipo"] = usuario["tipo"]
            flash("Acesso permitido apenas para administradores.")
            return redirect(url_for("inicio"))

        return f(*args, **kwargs)

    return decorated_function

@app.route("/cadastro-usuario", methods=["GET", "POST"])
def cadastro_usuario():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")

        if not nome or not email or not senha.strip():
            return render_template(
                "cadastro_usuario.html",
                erro="Preencha todos os campos obrigatórios."
            )

        if "@" not in email or "." not in email.rsplit("@", 1)[-1]:
            return render_template(
                "cadastro_usuario.html",
                erro="Informe um e-mail válido."
            )

        conexao = conectar_banco()

        try:
            usuario_existente = conexao.execute(
                "SELECT id FROM usuarios WHERE email = ?",
                (email,)
            ).fetchone()
        finally:
            conexao.close()

        if usuario_existente:
            return render_template(
                "cadastro_usuario.html",
                erro="Já existe uma conta com esse e-mail."
            )

        criar_usuario(nome, email, senha, "usuario")
        flash("Conta criada com sucesso! Faça login.", "sucesso")
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
            session.clear()
            session.permanent = True
            session["usuario_id"] = usuario["id"]
            session["usuario_nome"] = usuario["nome"]
            session["usuario_tipo"] = usuario["tipo"]
            session["ultima_atividade"] = datetime.now(timezone.utc).timestamp()
            registrar_log(
                usuario["id"],
                "LOGIN",
                "Login realizado com sucesso"
            )

            return redirect(url_for("inicio"))

        return render_template(
            "login.html",
            erro="E-mail ou senha inválidos."
        )

    return render_template("login.html")

@app.route("/logout")
def logout():
    registrar_log(
    session.get("usuario_id"),
    "LOGOUT",
    "Logout realizado pelo usuário"
)
    session.clear()
    return redirect(url_for("login"))

# Rota de Registro de Manejo
@app.route("/manejo", methods=["GET", "POST"])
@login_required
def manejo():
    if request.method == "POST":
        dados = {
            "animal": request.form.get("animal", "").strip(),
            "tipo_manejo": request.form.get("tipo_manejo", "").strip(),
            "data_manejo": request.form.get("data_manejo", "").strip(),
            "produto": request.form.get("produto", "").strip(),
            "dose": request.form.get("dose", "").strip(),
            "responsavel": request.form.get("responsavel", "").strip(),
            "observacoes": request.form.get("observacoes", "").strip(),
        }

        obrigatorios = ("animal", "tipo_manejo", "data_manejo", "responsavel")

        if any(not dados[campo] for campo in obrigatorios):
            flash("Preencha todos os campos obrigatórios.", "erro")
            return render_template("manejo.html")

        try:
            date.fromisoformat(dados["data_manejo"])
        except ValueError:
            flash("Informe uma data de manejo válida.", "erro")
            return render_template("manejo.html")

        try:
            criar_manejo(dados, session["usuario_id"])
        except ValueError as erro:
            flash(str(erro), "erro")
            return render_template("manejo.html")
        flash("Manejo cadastrado com sucesso!", "sucesso")
        return redirect(url_for("listagem"))

    return render_template("manejo.html")

@app.route("/manejo/atualizar/<int:id>", methods=["GET", "POST"])
@login_required
def atualizar_manejo_route(id):
    registro = buscar_manejo(id, session["usuario_id"])

    if registro is None:
        return redirect(url_for("listagem"))

    if request.method == "POST":
        dados = {
            "animal": request.form.get("animal", "").strip(),
            "tipo_manejo": request.form.get("tipo_manejo", "").strip(),
            "data_manejo": request.form.get("data_manejo", "").strip(),
            "produto": request.form.get("produto", "").strip(),
            "dose": request.form.get("dose", "").strip(),
            "responsavel": request.form.get("responsavel", "").strip(),
            "observacoes": request.form.get("observacoes", "").strip(),
        }

        obrigatorios = ("animal", "tipo_manejo", "data_manejo", "responsavel")

        if any(not dados[campo] for campo in obrigatorios):
            flash("Preencha todos os campos obrigatórios.", "erro")
            return render_template("manejo.html", registro=registro)

        try:
            date.fromisoformat(dados["data_manejo"])
        except ValueError:
            flash("Informe uma data de manejo válida.", "erro")
            return render_template("manejo.html", registro=registro)

        try:
            atualizar_manejo(id, dados, session["usuario_id"])
        except ValueError as erro:
            flash(str(erro), "erro")
            return render_template("manejo.html", registro=registro)
        flash("Manejo atualizado com sucesso!", "sucesso")
        return redirect(url_for("listagem"))

    return render_template("manejo.html", registro=registro)


@app.route("/manejo/remover/<int:id>", methods=["POST"])
@login_required
def remover_manejo_route(id):
    remover_manejo(id, session["usuario_id"])
    flash("Manejo excluído com sucesso!", "sucesso")
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
    try:
        animal_id = _resolver_animal_id(conexao, dados.get("animal"), usuario_id)
        cursor = conexao.execute("""
            INSERT INTO vacinacoes (animal_id, usuario_id, vacina, lote, fabricante,
                data_aplicacao, proxima_dose, dose, responsavel, observacoes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (animal_id, usuario_id, dados.get("vacina"), dados.get("lote"),
              dados.get("fabricante"), dados.get("data_aplicacao"), dados.get("proxima_dose"),
              dados.get("dose"), dados.get("responsavel"), dados.get("observacoes")))
        vacinacao_id = cursor.lastrowid
        conexao.execute("INSERT INTO logs_auditoria (usuario_id, acao, detalhes) VALUES (?, ?, ?)",
                        (usuario_id, "CRIAR_VACINACAO", f"Vacinação ID {vacinacao_id} cadastrada"))
        conexao.commit()
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()


def listar_vacinacoes(usuario_id):
    conexao = conectar_banco()
    try:
        registros = conexao.execute("""
            SELECT v.id, v.animal_id, a.identificacao AS animal, v.usuario_id,
                   v.vacina, v.lote, v.fabricante, v.data_aplicacao, v.proxima_dose,
                   v.dose, v.responsavel, v.observacoes
            FROM vacinacoes v JOIN animais a ON a.id = v.animal_id
            WHERE v.usuario_id = ? ORDER BY v.id DESC
        """, (usuario_id,)).fetchall()
        vacinacoes = []
        for registro in registros:
            vacinacao = dict(registro)
            vacinacao["status"] = status_vacina(vacinacao.get("proxima_dose"))
            vacinacoes.append(vacinacao)
        return vacinacoes
    finally:
        conexao.close()


def buscar_vacinacao(id, usuario_id):
    conexao = conectar_banco()
    try:
        return conexao.execute("""
            SELECT v.id, v.animal_id, a.identificacao AS animal, v.usuario_id,
                   v.vacina, v.lote, v.fabricante, v.data_aplicacao, v.proxima_dose,
                   v.dose, v.responsavel, v.observacoes
            FROM vacinacoes v JOIN animais a ON a.id = v.animal_id
            WHERE v.id = ? AND v.usuario_id = ?
        """, (id, usuario_id)).fetchone()
    finally:
        conexao.close()


def atualizar_vacinacao(id, dados, usuario_id):
    conexao = conectar_banco()
    try:
        animal_id = _resolver_animal_id(conexao, dados.get("animal"), usuario_id)
        cursor = conexao.execute("""
            UPDATE vacinacoes SET animal_id = ?, vacina = ?, lote = ?, fabricante = ?,
                data_aplicacao = ?, proxima_dose = ?, dose = ?, responsavel = ?, observacoes = ?
            WHERE id = ? AND usuario_id = ?
        """, (animal_id, dados.get("vacina"), dados.get("lote"), dados.get("fabricante"),
              dados.get("data_aplicacao"), dados.get("proxima_dose"), dados.get("dose"),
              dados.get("responsavel"), dados.get("observacoes"), id, usuario_id))
        if cursor.rowcount > 0:
            conexao.execute("INSERT INTO logs_auditoria (usuario_id, acao, detalhes) VALUES (?, ?, ?)",
                            (usuario_id, "EDITAR_VACINACAO", f"Vacinação ID {id} atualizada"))
        conexao.commit()
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()


def remover_vacinacao(id, usuario_id):
    conexao = conectar_banco()
    try:
        cursor = conexao.execute("DELETE FROM vacinacoes WHERE id = ? AND usuario_id = ?", (id, usuario_id))
        if cursor.rowcount > 0:
            conexao.execute("INSERT INTO logs_auditoria (usuario_id, acao, detalhes) VALUES (?, ?, ?)",
                            (usuario_id, "EXCLUIR_VACINACAO", f"Vacinação ID {id} excluída"))
        conexao.commit()
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()

def status_vacina(proxima_dose):
    if not proxima_dose:
        return None

    try:
        prox = proxima_dose if isinstance(proxima_dose, date) else date.fromisoformat(str(proxima_dose))
    except (ValueError, TypeError):
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
    total_manejos=total_manejos,
    nome_usuario=session.get("usuario_nome", "usuário")
)


# Cadastro de animal
@app.route("/cadastro", methods=["GET", "POST"])
@login_required
def cadastro():
    if request.method == "POST":
        dados = {
            "identificacao": request.form.get("identificacao", "").strip(),
            "especie": request.form.get("especie", "").strip(),
            "raca": request.form.get("raca", "").strip(),
            "data_nascimento": request.form.get("data_nascimento", "").strip(),
        }

        if not dados["identificacao"] or not dados["especie"]:
            flash("Identificação e espécie são obrigatórias.", "erro")
            return render_template("cadastro.html")

        if dados["data_nascimento"]:
            try:
                date.fromisoformat(dados["data_nascimento"])
            except ValueError:
                flash("Informe uma data de nascimento válida.", "erro")
                return render_template("cadastro.html")

        criar_animal(dados, session["usuario_id"])
        flash("Animal cadastrado com sucesso!", "sucesso")
        return redirect(url_for("listagem"))

    return render_template("cadastro.html")

#usuarios
@app.route("/usuarios", methods=["GET", "POST"])
@admin_required
def usuarios():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")
        tipo = request.form.get("tipo", "").strip()

        if not nome or not email or not senha.strip() or not tipo:
            flash("Preencha todos os campos obrigatórios.", "erro")
            return redirect(url_for("usuarios"))

        if tipo not in ("usuario", "admin"):
            flash("Tipo de usuário inválido.", "erro")
            return redirect(url_for("usuarios"))

        if "@" not in email or "." not in email.rsplit("@", 1)[-1]:
            flash("Informe um e-mail válido.", "erro")
            return redirect(url_for("usuarios"))

        conexao = conectar_banco()
        try:
            usuario_existente = conexao.execute(
                "SELECT id FROM usuarios WHERE email = ?",
                (email,)
            ).fetchone()
        finally:
            conexao.close()

        if usuario_existente:
            flash("Já existe uma conta com esse e-mail.", "erro")
            return redirect(url_for("usuarios"))

        criar_usuario(nome, email, senha, tipo)
        flash("Usuário cadastrado com sucesso!", "sucesso")
        return redirect(url_for("usuarios"))

    usuarios = listar_usuarios()
    return render_template("usuarios.html", usuarios=usuarios)

# Edição de animal
@app.route("/animais/atualizar/<int:id>", methods=["GET", "POST"])
@login_required
def atualizar_animal_route(id):
    animal = buscar_animal(id, session["usuario_id"])

    if animal is None:
        return redirect(url_for("listagem"))

    if request.method == "POST":
        dados = {
            "identificacao": request.form.get("identificacao", "").strip(),
            "especie": request.form.get("especie", "").strip(),
            "raca": request.form.get("raca", "").strip(),
            "data_nascimento": request.form.get("data_nascimento", "").strip(),
        }

        if not dados["identificacao"] or not dados["especie"]:
            flash("Identificação e espécie são obrigatórias.", "erro")
            return render_template("cadastro.html", animal=animal)

        if dados["data_nascimento"]:
            try:
                date.fromisoformat(dados["data_nascimento"])
            except ValueError:
                flash("Informe uma data de nascimento válida.", "erro")
                return render_template("cadastro.html", animal=animal)

        atualizar_animal(id, dados, session["usuario_id"])

        flash("Animal atualizado com sucesso!", "sucesso")
        return redirect(url_for("listagem"))

    return render_template("cadastro.html", animal=animal)



# Remoção de um animal
@app.route("/animais/remover/<int:id>", methods=["POST"])
@login_required
def remover_animal_route(id):
    try:
        remover_animal(id, session["usuario_id"])
        flash("Animal excluído com sucesso!", "sucesso")
    except sqlite3.IntegrityError:
        flash(
            "Este animal possui manejos ou vacinações vinculados. "
            "Exclua primeiro esses registros ou mantenha o animal cadastrado.",
            "erro",
        )
    return redirect(url_for("listagem"))


# Registro de vacinação
@app.route("/vacinacao", methods=["GET", "POST"])
@login_required
def vacinacao():
    if request.method == "POST":
        dados = {
            "animal": request.form.get("animal", "").strip(),
            "vacina": request.form.get("vacina", "").strip(),
            "lote": request.form.get("lote", "").strip(),
            "fabricante": request.form.get("fabricante", "").strip(),
            "data_aplicacao": request.form.get("data_aplicacao", "").strip(),
            "proxima_dose": request.form.get("proxima_dose", "").strip(),
            "dose": request.form.get("dose", "").strip(),
            "responsavel": request.form.get("responsavel", "").strip(),
            "observacoes": request.form.get("observacoes", "").strip(),
        }

        if not dados["animal"] or not dados["vacina"] or not dados["data_aplicacao"]:
            flash("Animal, vacina e data de aplicação são obrigatórios.", "erro")
            return render_template("vacinacao.html")

        for campo in ("data_aplicacao", "proxima_dose"):
            if dados[campo]:
                try:
                    date.fromisoformat(dados[campo])
                except ValueError:
                    flash("Informe datas válidas no formato AAAA-MM-DD.", "erro")
                    return render_template("vacinacao.html")

        try:
            criar_vacinacao(dados, session["usuario_id"])
        except ValueError as erro:
            flash(str(erro), "erro")
            return render_template("vacinacao.html")
        flash("Vacinação cadastrada com sucesso!", "sucesso")
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
        dados = {
            "animal": request.form.get("animal", "").strip(),
            "vacina": request.form.get("vacina", "").strip(),
            "lote": request.form.get("lote", "").strip(),
            "fabricante": request.form.get("fabricante", "").strip(),
            "data_aplicacao": request.form.get("data_aplicacao", "").strip(),
            "proxima_dose": request.form.get("proxima_dose", "").strip(),
            "dose": request.form.get("dose", "").strip(),
            "responsavel": request.form.get("responsavel", "").strip(),
            "observacoes": request.form.get("observacoes", "").strip(),
        }

        if not dados["animal"] or not dados["vacina"] or not dados["data_aplicacao"]:
            flash("Animal, vacina e data de aplicação são obrigatórios.", "erro")
            return render_template("vacinacao.html", registro=registro)

        for campo in ("data_aplicacao", "proxima_dose"):
            if dados[campo]:
                try:
                    date.fromisoformat(dados[campo])
                except ValueError:
                    flash("Informe datas válidas no formato AAAA-MM-DD.", "erro")
                    return render_template("vacinacao.html", registro=registro)

        try:
            atualizar_vacinacao(id, dados, session["usuario_id"])
        except ValueError as erro:
            flash(str(erro), "erro")
            return render_template("vacinacao.html", registro=registro)
        flash("Vacinação atualizada com sucesso!", "sucesso")
        return redirect(url_for("listagem"))

    return render_template("vacinacao.html", registro=registro)

@app.route("/vacinacao/remover/<int:id>", methods=["POST"])
@login_required
def remover_vacinacao_route(id):
    remover_vacinacao(id, session["usuario_id"])
    flash("Vacinação excluída com sucesso!", "sucesso")
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
# API REST — CRUD de animais, manejos e vacinações

API_RECURSOS = {
    "animais": {
        "colunas": (
            "identificacao", "especie", "raca", "data_nascimento"
        ),
        "obrigatorios": ("identificacao", "especie"),
        "datas": ("data_nascimento",),
    },
    "manejos": {
        "colunas": (
            "animal", "tipo_manejo", "data_manejo",
            "produto", "dose", "responsavel", "observacoes"
        ),
        "obrigatorios": ("animal", "tipo_manejo", "data_manejo"),
        "datas": ("data_manejo",),
    },
    "vacinacoes": {
        "colunas": (
            "animal", "vacina", "lote", "fabricante",
            "data_aplicacao", "proxima_dose", "dose",
            "responsavel", "observacoes"
        ),
        "obrigatorios": ("animal", "vacina", "data_aplicacao"),
        "datas": ("data_aplicacao", "proxima_dose"),
    },
}


def validar_dados_api(recurso, dados):
    """Valida os campos recebidos pela API antes de acessar o banco."""
    if not isinstance(dados, dict):
        return "Envie um objeto JSON válido."

    config = API_RECURSOS[recurso]
    permitidas = set(config["colunas"])

    campos_desconhecidos = set(dados) - permitidas
    if campos_desconhecidos:
        return "Existem campos não permitidos na requisição."

    for campo in config["obrigatorios"]:
        valor = dados.get(campo)

        if not isinstance(valor, str) or not valor.strip():
            return f"O campo '{campo}' é obrigatório."

    for campo in config["colunas"]:
        valor = dados.get(campo)

        if valor is not None and not isinstance(valor, str):
            return f"O campo '{campo}' deve ser texto."

    for campo in config["datas"]:
        valor = dados.get(campo)

        if valor:
            try:
                date.fromisoformat(valor)
            except ValueError:
                return f"O campo '{campo}' deve usar o formato AAAA-MM-DD."

    return None


@app.route("/api/<string:recurso>", methods=["GET", "POST"])
@login_required
def api_colecao(recurso):
    if recurso not in API_RECURSOS:
        return jsonify({"erro": "Recurso não encontrado."}), 404
    usuario_id = session["usuario_id"]
    config = API_RECURSOS[recurso]
    conexao = conectar_banco()
    try:
        if request.method == "GET":
            if recurso in ("manejos", "vacinacoes"):
                alias = "m" if recurso == "manejos" else "v"
                registros = conexao.execute(
                    f"SELECT {alias}.*, a.identificacao AS animal FROM {recurso} {alias} "
                    f"JOIN animais a ON a.id = {alias}.animal_id WHERE {alias}.usuario_id = ?",
                    (usuario_id,)).fetchall()
            else:
                registros = conexao.execute(f"SELECT * FROM {recurso} WHERE usuario_id = ?", (usuario_id,)).fetchall()
            return jsonify([dict(registro) for registro in registros]), 200

        dados = request.get_json(silent=True)
        erro = validar_dados_api(recurso, dados)
        if erro:
            return jsonify({"erro": erro}), 400

        colunas = config["colunas"]
        valores = [dados.get(campo) or None for campo in colunas]
        nomes_sql = ", ".join(colunas)
        marcadores = ", ".join("?" for _ in colunas)
        if recurso in ("manejos", "vacinacoes"):
            animal_id = _resolver_animal_id(conexao, dados.get("animal"), usuario_id)
            nomes_sql = nomes_sql.replace("animal", "animal_id", 1)
            valores[0] = animal_id
        cursor = conexao.execute(
            f"INSERT INTO {recurso} ({nomes_sql}, usuario_id) VALUES ({marcadores}, ?)",
            (*valores, usuario_id))
        registro_id = cursor.lastrowid
        conexao.execute("INSERT INTO logs_auditoria (usuario_id, acao, detalhes) VALUES (?, ?, ?)",
                        (usuario_id, f"CRIAR_{recurso.upper()}", f"Registro ID {registro_id} criado pela API"))
        conexao.commit()
        if recurso in ("manejos", "vacinacoes"):
            alias = "m" if recurso == "manejos" else "v"
            registro = conexao.execute(
                f"SELECT {alias}.*, a.identificacao AS animal FROM {recurso} {alias} "
                f"JOIN animais a ON a.id = {alias}.animal_id WHERE {alias}.id = ? AND {alias}.usuario_id = ?",
                (registro_id, usuario_id)).fetchone()
        else:
            registro = conexao.execute(f"SELECT * FROM {recurso} WHERE id = ? AND usuario_id = ?", (registro_id, usuario_id)).fetchone()
        return jsonify(dict(registro)), 201
    except ValueError as erro:
        conexao.rollback()
        return jsonify({"erro": str(erro)}), 400
    finally:
        conexao.close()


@app.route("/api/<string:recurso>/<int:registro_id>", methods=["GET", "PUT", "DELETE"])
@login_required
def api_registro(recurso, registro_id):
    if recurso not in API_RECURSOS:
        return jsonify({"erro": "Recurso não encontrado."}), 404
    usuario_id = session["usuario_id"]
    config = API_RECURSOS[recurso]
    conexao = conectar_banco()
    try:
        if recurso in ("manejos", "vacinacoes"):
            alias = "m" if recurso == "manejos" else "v"
            registro = conexao.execute(
                f"SELECT {alias}.*, a.identificacao AS animal FROM {recurso} {alias} "
                f"JOIN animais a ON a.id = {alias}.animal_id WHERE {alias}.id = ? AND {alias}.usuario_id = ?",
                (registro_id, usuario_id)).fetchone()
        else:
            registro = conexao.execute(f"SELECT * FROM {recurso} WHERE id = ? AND usuario_id = ?", (registro_id, usuario_id)).fetchone()
        if registro is None:
            return jsonify({"erro": "Registro não encontrado."}), 404
        if request.method == "GET":
            return jsonify(dict(registro)), 200
        if request.method == "DELETE":
            conexao.execute(f"DELETE FROM {recurso} WHERE id = ? AND usuario_id = ?", (registro_id, usuario_id))
            conexao.execute("INSERT INTO logs_auditoria (usuario_id, acao, detalhes) VALUES (?, ?, ?)",
                            (usuario_id, f"EXCLUIR_{recurso.upper()}", f"Registro ID {registro_id} excluído pela API"))
            conexao.commit()
            return jsonify({"mensagem": "Registro excluído com sucesso."}), 200

        dados = request.get_json(silent=True)
        erro = validar_dados_api(recurso, dados)
        if erro:
            return jsonify({"erro": erro}), 400
        colunas = config["colunas"]
        valores = [dados.get(campo) or None for campo in colunas]
        if recurso in ("manejos", "vacinacoes"):
            valores[0] = _resolver_animal_id(conexao, dados.get("animal"), usuario_id)
            colunas_sql = ["animal_id", *colunas[1:]]
        else:
            colunas_sql = list(colunas)
        atribuicoes = ", ".join(f"{campo} = ?" for campo in colunas_sql)
        conexao.execute(f"UPDATE {recurso} SET {atribuicoes} WHERE id = ? AND usuario_id = ?",
                        (*valores, registro_id, usuario_id))
        conexao.execute("INSERT INTO logs_auditoria (usuario_id, acao, detalhes) VALUES (?, ?, ?)",
                        (usuario_id, f"ATUALIZAR_{recurso.upper()}", f"Registro ID {registro_id} atualizado pela API"))
        conexao.commit()
        if recurso in ("manejos", "vacinacoes"):
            alias = "m" if recurso == "manejos" else "v"
            atualizado = conexao.execute(
                f"SELECT {alias}.*, a.identificacao AS animal FROM {recurso} {alias} "
                f"JOIN animais a ON a.id = {alias}.animal_id WHERE {alias}.id = ? AND {alias}.usuario_id = ?",
                (registro_id, usuario_id)).fetchone()
        else:
            atualizado = conexao.execute(f"SELECT * FROM {recurso} WHERE id = ? AND usuario_id = ?", (registro_id, usuario_id)).fetchone()
        return jsonify(dict(atualizado)), 200
    except ValueError as erro:
        conexao.rollback()
        return jsonify({"erro": str(erro)}), 400
    finally:
        conexao.close()


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")