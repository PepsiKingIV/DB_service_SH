from typing import Optional
import smtplib
import time

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, IntegerIDMixin, exceptions, models, schemas

from auth.models import User
from auth.utils import get_user_db
from config import SMTP_SERVER, EMAIL, PASSWORD

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SECRET = "SECRET"


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def create(
        self,
        user_create: schemas.UC,
        safe: bool = False,
        request: Optional[Request] = None,
    ) -> models.UP:
        await self.validate_password(user_create.password, user_create)

        existing_user = await self.user_db.get_by_email(user_create.email)
        if existing_user is not None:
            raise exceptions.UserAlreadyExists()

        user_dict = (
            user_create.create_update_dict()
            if safe
            else user_create.create_update_dict_superuser()
        )
        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)

        created_user = await self.user_db.create(user_dict)

        await self.on_after_register(created_user, request)

        return created_user

    # первичная реализация. Функция занимает слишком много времени и в дальнейшем будет перенесена в Celery
    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        msg = MIMEMultipart()
        msg["From"] = EMAIL
        msg["To"] = user.email
        msg["Subject"] = "Verification"
        text = f"Hello. \nThis email was specified for registration in the application. \
\nToken for verification: {token}. \
\n\n\nIf you have not registered, write to the mail \
\nBalanced.project.site@gmail.com"
        msg.attach(MIMEText(text, "plain"))
        with smtplib.SMTP(SMTP_SERVER, 587) as smtp_server:
            smtp_server.starttls()
            smtp_server.login(EMAIL, PASSWORD)
            smtp_server.sendmail(EMAIL, user.email, msg.as_string())


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
