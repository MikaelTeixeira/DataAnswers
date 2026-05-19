from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings


engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def ensure_database_exists() -> None:
    url = make_url(settings.database_url)
    if not url.drivername.startswith("mysql") or not url.database:
        return

    server_url = url.set(database=None)
    database_name = url.database.replace("`", "``")
    server_engine = create_engine(server_url, pool_pre_ping=True)

    try:
        with server_engine.begin() as connection:
            connection.execute(
                text(
                    f"CREATE DATABASE IF NOT EXISTS `{database_name}` "
                    "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                )
            )
    finally:
        server_engine.dispose()


def init_db() -> None:
    import app.models  # noqa: F401

    ensure_database_exists()
    Base.metadata.create_all(bind=engine)
    ensure_schema_updates()
    seed_default_admin()
    ensure_default_admin()
    seed_default_platforms()
    seed_default_responses()


def ensure_schema_updates() -> None:
    inspector = inspect(engine)
    if "users" not in inspector.get_table_names():
        return

    user_columns = {column["name"] for column in inspector.get_columns("users")}
    response_columns = set()
    if "response_templates" in inspector.get_table_names():
        response_columns = {column["name"] for column in inspector.get_columns("response_templates")}

    with engine.begin() as connection:
        if "is_admin" not in user_columns:
            connection.execute(text("ALTER TABLE users ADD COLUMN is_admin BOOL NOT NULL DEFAULT 0"))
        if "response_templates" in inspector.get_table_names() and "owner_id" not in response_columns:
            connection.execute(text("ALTER TABLE response_templates ADD COLUMN owner_id INT NULL"))
            connection.execute(text("CREATE INDEX ix_response_templates_owner_id ON response_templates (owner_id)"))


def seed_default_platforms() -> None:
    from app.models import Platform

    default_platforms = [
        (
            "WhatsApp",
            "Ola, {responsavel}. Tudo bem? Passando para informar que {aluno} ja recebeu o atendimento e seguimos acompanhando {o_a} aluno com atencao. Qualquer duvida, fico a disposicao.",
        ),
        (
            "E-mail",
            "Prezado(a) {responsavel},\n\nInformamos que {aluno} recebeu o atendimento solicitado. Nossa equipe permanecera acompanhando o desenvolvimento {dele_dela} e retornara caso haja novas orientacoes.\n\nAtenciosamente.",
        ),
        (
            "Sistema interno",
            "Atendimento registrado para {aluno}. Responsavel: {responsavel}. Genero informado: {genero}. Encaminhamento concluido e disponivel para acompanhamento.",
        ),
    ]

    with SessionLocal() as db:
        if db.query(Platform).count() > 0:
            return
        for name, template_text in default_platforms:
            db.add(Platform(name=name, template_text=template_text))
        db.commit()


def seed_default_responses() -> None:
    from app.models import Platform, ResponseTemplate

    with SessionLocal() as db:
        if db.query(ResponseTemplate).count() > 0:
            return

        platforms = db.query(Platform).order_by(Platform.id).all()
        for platform in platforms:
            if platform.template_text.strip():
                db.add(
                    ResponseTemplate(
                        platform_id=platform.id,
                        title="Resposta padrao",
                        template_text=platform.template_text,
                        is_active=platform.is_active,
                    )
                )

        db.commit()


def ensure_default_admin() -> None:
    from app.models import User

    with SessionLocal() as db:
        has_admin = db.query(User).filter(User.is_admin.is_(True)).first()
        if has_admin:
            return

        first_user = db.query(User).order_by(User.id).first()
        if not first_user:
            return

        first_user.is_admin = True
        db.commit()


def seed_default_admin() -> None:
    from app.auth import hash_password
    from app.models import User

    with SessionLocal() as db:
        if db.query(User).count() > 0:
            return

        db.add(
            User(
                name="mikael",
                email="mikael@ursula.com.br",
                password_hash=hash_password("mikael10#"),
                is_admin=True,
            )
        )
        db.commit()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
