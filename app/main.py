from typing import Annotated
import logging

from fastapi import Depends, FastAPI, Form, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.sessions import SessionMiddleware

from app.ai import AiGenerationError, generate_reply
from app.auth import authenticate_user, get_user_by_email, hash_password
from app.config import settings
from app.database import get_db, init_db
from app.models import Platform, ResponseTemplate, User


app = FastAPI(title=settings.app_name)
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")
logging.basicConfig(
    filename="app-error.log",
    level=logging.ERROR,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


def current_user(request: Request, db: Annotated[Session, Depends(get_db)]) -> User | None:
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return db.get(User, user_id)


def require_user(user: Annotated[User | None, Depends(current_user)]) -> User:
    if user is None:
        raise LoginRedirect()
    return user


def require_admin(user: Annotated[User, Depends(require_user)]) -> User:
    if not user.is_admin:
        raise AdminRedirect()
    return user


class LoginRedirect(Exception):
    pass


class AdminRedirect(Exception):
    pass


@app.exception_handler(LoginRedirect)
async def login_redirect_handler(request: Request, exc: LoginRedirect) -> RedirectResponse:
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)


@app.exception_handler(AdminRedirect)
async def admin_redirect_handler(request: Request, exc: AdminRedirect) -> RedirectResponse:
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)


@app.exception_handler(Exception)
async def unexpected_error_handler(request: Request, exc: Exception) -> HTMLResponse:
    if isinstance(exc, StarletteHTTPException):
        raise exc
    logger.exception("Erro inesperado em %s %s", request.method, request.url.path)
    return HTMLResponse("Internal Server Error. Veja app-error.log.", status_code=500)


@app.get("/", response_class=HTMLResponse)
def home(request: Request, user: Annotated[User | None, Depends(current_user)]):
    if user:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request, user: Annotated[User | None, Depends(current_user)]):
    if user:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("login.html", {"request": request, "user": user, "error": None})


@app.post("/login", response_class=HTMLResponse)
def login(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
):
    user = authenticate_user(db, email, password)
    if not user:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "user": None, "error": "E-mail ou senha invalidos."},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    request.session["user_id"] = user.id
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request, user: Annotated[User | None, Depends(current_user)]):
    if user:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("register.html", {"request": request, "user": user, "error": None})


@app.post("/register", response_class=HTMLResponse)
def register(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    name: Annotated[str, Form()],
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
):
    name = name.strip()
    email = email.lower().strip()

    if len(password) < 6:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "user": None, "error": "A senha precisa ter pelo menos 6 caracteres."},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if len(password.encode("utf-8")) > 72:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "user": None, "error": "A senha precisa ter no maximo 72 bytes."},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if get_user_by_email(db, email):
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "user": None, "error": "Este e-mail ja esta cadastrado."},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    try:
        is_first_user = db.scalar(select(func.count()).select_from(User)) == 0
        user = User(
            name=name,
            email=email,
            password_hash=hash_password(password),
            is_admin=is_first_user,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Erro de banco de dados ao cadastrar usuario com email %s", email)
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "user": None, "error": "Nao foi possivel salvar o cadastro no banco de dados."},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    except Exception:
        logger.exception("Erro inesperado ao cadastrar usuario com email %s", email)
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "user": None, "error": "Erro inesperado ao criar cadastro. Veja app-error.log."},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    request.session["user_id"] = user.id
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(
    request: Request,
    user: Annotated[User, Depends(require_user)],
    db: Annotated[Session, Depends(get_db)],
):
    platforms = db.scalars(select(Platform).where(Platform.is_active.is_(True)).order_by(Platform.name)).all()
    platform_payload = [
        {
            "id": platform.id,
            "name": platform.name,
            "structures": [
                {"id": structure.id, "title": structure.title}
                for structure in db.scalars(
                    select(ResponseTemplate)
                    .where(
                        ResponseTemplate.platform_id == platform.id,
                        ResponseTemplate.is_active.is_(True),
                        or_(ResponseTemplate.owner_id.is_(None), ResponseTemplate.owner_id == user.id),
                    )
                    .order_by(ResponseTemplate.title)
                ).all()
            ],
        }
        for platform in platforms
    ]
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "user": user, "platforms": platforms, "platform_payload": platform_payload},
    )


def first_name(name: str) -> str:
    return name.strip().split()[0].title() if name.strip() else ""


def build_ai_prompt(
    platform: Platform,
    structures: list[ResponseTemplate],
    selected_structure: ResponseTemplate | None,
    responsible_name: str,
    student_name: str,
    situation: str,
    extra_details: str,
) -> str:
    structure_text = "\n\n".join(
        f"Titulo: {structure.title}\nTexto/estrutura:\n{structure.template_text}"
        for structure in structures
    )
    if not structure_text:
        structure_text = "Nenhuma estrutura cadastrada para esta plataforma."
    selected_structure_text = "Nenhuma estrutura especifica selecionada."
    if selected_structure:
        selected_structure_text = (
            f"Titulo: {selected_structure.title}\n"
            f"Texto/estrutura principal:\n{selected_structure.template_text}"
        )

    return f"""
Crie uma resposta curta, educada e profissional para atendimento escolar.

Dados:
- Plataforma: {platform.name}
- Responsavel: {first_name(responsible_name)}
- Aluno: {first_name(student_name)}
- Situacao: {situation.strip() or "Usar a estrutura selecionada como base principal"}
- Detalhes ou pedido extra: {extra_details.strip() or "Nenhum"}

Estrutura selecionada:
{selected_structure_text}

Estruturas cadastradas para esta plataforma:
{structure_text}

Regras:
- Use apenas o primeiro nome do responsavel e do aluno.
- Infira pelo nome se deve usar Sr. ou Sra. para o responsavel.
- Infira pelo nome se deve usar do/da, o/a, ele/ela para o aluno.
- Nas estruturas, <responsible> representa o responsavel e <student> representa o aluno.
- Ao usar uma estrutura, substitua <responsible> e <student> pelos nomes corretos e ajuste pronomes/artigos naturalmente.
- Se a estrutura selecionada existir, use-a como base principal.
- Se nao houver estrutura selecionada, use as estruturas cadastradas apenas quando ajudarem na situacao.
- Qualquer conteudo entre asteriscos (*) nas estruturas deve ser usado apenas como instrucao interna.
- Nao copie para a mensagem final nenhum texto que esteja entre asteriscos.
- Nao invente links, senhas, codigos, prazos ou informacoes que nao foram dadas.
- Retorne apenas a mensagem final, sem explicacoes.
""".strip()


@app.post("/api/generate-reply")
def generate_ai_reply(
    user: Annotated[User, Depends(require_user)],
    db: Annotated[Session, Depends(get_db)],
    responsible_name: Annotated[str, Form()],
    student_name: Annotated[str, Form()],
    platform_id: Annotated[int, Form()],
    situation: Annotated[str, Form()] = "",
    extra_details: Annotated[str, Form()] = "",
    use_structure: Annotated[str | None, Form()] = None,
    structure_id: Annotated[int | None, Form()] = None,
):
    platform = db.get(Platform, platform_id)
    if not platform or not platform.is_active:
        return JSONResponse({"error": "Escolha uma plataforma ativa."}, status_code=400)

    if not responsible_name.strip() or not student_name.strip():
        return JSONResponse(
            {"error": "Informe responsavel e aluno."},
            status_code=400,
        )

    selected_structure = None
    if use_structure == "on":
        if not structure_id:
            return JSONResponse({"error": "Escolha uma estrutura."}, status_code=400)
        selected_structure = db.get(ResponseTemplate, structure_id)
        if (
            not selected_structure
            or selected_structure.platform_id != platform.id
            or not selected_structure.is_active
            or (selected_structure.owner_id is not None and selected_structure.owner_id != user.id)
        ):
            return JSONResponse({"error": "Escolha uma estrutura ativa da plataforma selecionada."}, status_code=400)
    elif not situation.strip():
        return JSONResponse({"error": "Informe a situacao ou marque a opcao de usar estrutura."}, status_code=400)

    structures = db.scalars(
        select(ResponseTemplate)
        .where(
            ResponseTemplate.platform_id == platform.id,
            ResponseTemplate.is_active.is_(True),
            or_(ResponseTemplate.owner_id.is_(None), ResponseTemplate.owner_id == user.id),
        )
        .order_by(ResponseTemplate.title)
    ).all()
    prompt = build_ai_prompt(
        platform=platform,
        structures=structures,
        selected_structure=selected_structure,
        responsible_name=responsible_name,
        student_name=student_name,
        situation=situation,
        extra_details=extra_details,
    )

    try:
        reply = generate_reply(prompt)
    except AiGenerationError as exc:
        logger.warning("Nao foi possivel gerar resposta com IA: %s", exc)
        return JSONResponse({"error": str(exc)}, status_code=400)

    return {"reply": reply}


@app.get("/admin/platforms", response_class=HTMLResponse)
def platforms_page(
    request: Request,
    user: Annotated[User, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    platforms = db.scalars(select(Platform).order_by(Platform.name)).all()
    return templates.TemplateResponse(
        "platforms.html",
        {"request": request, "user": user, "platforms": platforms, "error": None},
    )


@app.post("/admin/platforms", response_class=HTMLResponse)
def create_platform(
    request: Request,
    user: Annotated[User, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
    name: Annotated[str, Form()],
):
    name = name.strip()
    if not name:
        platforms = db.scalars(select(Platform).order_by(Platform.name)).all()
        return templates.TemplateResponse(
            "platforms.html",
            {
                "request": request,
                "user": user,
                "platforms": platforms,
                "error": "Informe o nome da plataforma.",
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    db.add(Platform(name=name, template_text=""))
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        platforms = db.scalars(select(Platform).order_by(Platform.name)).all()
        return templates.TemplateResponse(
            "platforms.html",
            {
                "request": request,
                "user": user,
                "platforms": platforms,
                "error": "Nao foi possivel salvar. Talvez ja exista uma plataforma com esse nome.",
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    return RedirectResponse(url="/admin/platforms", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/admin/platforms/{platform_id}/update")
def update_platform(
    platform_id: int,
    user: Annotated[User, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
    name: Annotated[str, Form()],
    is_active: Annotated[str | None, Form()] = None,
):
    platform = db.get(Platform, platform_id)
    if platform:
        platform.name = name.strip()
        platform.is_active = is_active == "on"
        db.commit()
    return RedirectResponse(url="/admin/platforms", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/admin/platforms/{platform_id}/delete")
def delete_platform(
    platform_id: int,
    user: Annotated[User, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    platform = db.get(Platform, platform_id)
    if platform:
        db.delete(platform)
        db.commit()
    return RedirectResponse(url="/admin/platforms", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/admin/responses", response_class=HTMLResponse)
def responses_page(
    request: Request,
    user: Annotated[User, Depends(require_user)],
    db: Annotated[Session, Depends(get_db)],
    platform_id: int | None = None,
):
    platforms = db.scalars(select(Platform).order_by(Platform.name)).all()
    selected_platform_id = platform_id or (platforms[0].id if platforms else None)
    responses = []
    if selected_platform_id:
        responses = db.scalars(
            select(ResponseTemplate)
            .where(
                ResponseTemplate.platform_id == selected_platform_id,
                or_(ResponseTemplate.owner_id.is_(None), ResponseTemplate.owner_id == user.id),
            )
            .order_by(ResponseTemplate.title)
        ).all()

    return templates.TemplateResponse(
        "responses.html",
        {
            "request": request,
            "user": user,
            "platforms": platforms,
            "selected_platform_id": selected_platform_id,
            "responses": responses,
            "error": None,
        },
    )


@app.post("/admin/responses", response_class=HTMLResponse)
def create_response(
    request: Request,
    user: Annotated[User, Depends(require_user)],
    db: Annotated[Session, Depends(get_db)],
    platform_id: Annotated[int, Form()],
    title: Annotated[str, Form()],
    template_text: Annotated[str, Form()],
):
    title = title.strip()
    template_text = template_text.strip()
    platform = db.get(Platform, platform_id)
    if not platform or not title or not template_text:
        platforms = db.scalars(select(Platform).order_by(Platform.name)).all()
        responses = db.scalars(
            select(ResponseTemplate)
            .where(
                ResponseTemplate.platform_id == platform_id,
                or_(ResponseTemplate.owner_id.is_(None), ResponseTemplate.owner_id == user.id),
            )
            .order_by(ResponseTemplate.title)
        ).all()
        return templates.TemplateResponse(
            "responses.html",
            {
                "request": request,
                "user": user,
                "platforms": platforms,
                "selected_platform_id": platform_id,
                "responses": responses,
                "error": "Escolha a plataforma e informe titulo e texto da resposta.",
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    owner_id = None if user.is_admin else user.id
    db.add(ResponseTemplate(platform_id=platform_id, owner_id=owner_id, title=title, template_text=template_text))
    db.commit()
    return RedirectResponse(
        url=f"/admin/responses?platform_id={platform_id}",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@app.post("/admin/responses/{response_id}/update")
def update_response(
    response_id: int,
    user: Annotated[User, Depends(require_user)],
    db: Annotated[Session, Depends(get_db)],
    platform_id: Annotated[int, Form()],
    title: Annotated[str, Form()],
    template_text: Annotated[str, Form()],
    is_active: Annotated[str | None, Form()] = None,
):
    response = db.get(ResponseTemplate, response_id)
    can_edit = response and (user.is_admin or response.owner_id == user.id)
    if can_edit and db.get(Platform, platform_id):
        response.platform_id = platform_id
        response.title = title.strip()
        response.template_text = template_text.strip()
        response.is_active = is_active == "on"
        db.commit()

    redirect_platform_id = platform_id if response else ""
    return RedirectResponse(
        url=f"/admin/responses?platform_id={redirect_platform_id}",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@app.post("/admin/responses/{response_id}/delete")
def delete_response(
    response_id: int,
    user: Annotated[User, Depends(require_user)],
    db: Annotated[Session, Depends(get_db)],
):
    response = db.get(ResponseTemplate, response_id)
    platform_id = response.platform_id if response else ""
    if response and (user.is_admin or response.owner_id == user.id):
        db.delete(response)
        db.commit()
    return RedirectResponse(
        url=f"/admin/responses?platform_id={platform_id}",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@app.get("/admin/users", response_class=HTMLResponse)
def users_page(
    request: Request,
    user: Annotated[User, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    users = db.scalars(select(User).order_by(User.name)).all()
    return templates.TemplateResponse(
        "users.html",
        {"request": request, "user": user, "users": users, "error": None},
    )


@app.post("/admin/users/{user_id}/role", response_class=HTMLResponse)
def update_user_role(
    user_id: int,
    request: Request,
    current_admin: Annotated[User, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
    is_admin: Annotated[str | None, Form()] = None,
):
    target_user = db.get(User, user_id)
    if not target_user:
        return RedirectResponse(url="/admin/users", status_code=status.HTTP_303_SEE_OTHER)

    wants_admin = is_admin == "on"
    admin_count = db.scalar(select(func.count()).select_from(User).where(User.is_admin.is_(True)))
    if target_user.is_admin and not wants_admin and admin_count <= 1:
        users = db.scalars(select(User).order_by(User.name)).all()
        return templates.TemplateResponse(
            "users.html",
            {
                "request": request,
                "user": current_admin,
                "users": users,
                "error": "Mantenha pelo menos um administrador.",
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    target_user.is_admin = wants_admin
    db.commit()
    return RedirectResponse(url="/admin/users", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
