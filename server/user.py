from sqlalchemy.ext.asyncio import AsyncSession
from base.user import DataBaseUser
from base.model import User
from schema.user import SchemaUser, SchemaVerification
from uuid import uuid4
from typing import Dict, Any, Optional


class MiddleLoyeUser:
    """
    Промежуточный слой для операций с пользователями.

    Обеспечивает бизнес-логику между API и слоем базы данных,
    включая генерацию токенов и обработку аутентификации.

    Attributes:
        database (DataBaseUser): Экземпляр класса для работы с базой данных
    """

    def __init__(self, database: DataBaseUser) -> None:
        """
        Инициализирует экземпляр MiddleLoyeUser.

        Args:
            database (DataBaseUser): Экземпляр класса для работы с БД
        """
        self.database = database

    async def get_user(self, db: AsyncSession,
                       user_id: int) -> Optional[User]:
        """
        Получает пользователя по ID.

        Args:
            db (AsyncSession): Асинхронная сессия базы данных
            user_id (int): ID пользователя

        Returns:
            User | None: Объект пользователя или None
        """
        try:
            return await self.database.get_user(db=db, user_id=user_id)
        except Exception as e:
            return None

    async def new_user(self, db: AsyncSession,
                       user_data: SchemaUser) -> Dict[str, Any]:
        """
        Создает нового пользователя с уникальным токеном.

        Args:
            db (AsyncSession): Асинхронная сессия базы данных
            user_data (SchemaUser): Данные нового пользователя

        Returns:
            dict: Результат операции создания
        """
        try:
            user_data.token = str(uuid4())

            result = await self.database.create_user(db=db, user=user_data)

            return result

        except Exception as e:
            return {
                "status_code": 500,
                "title": "Ошибка",
                "description": f"Неизвестная ошибка при создании пользователя: {str(e)}"
            }

    async def verification(self, db: AsyncSession,
                           credentials: SchemaVerification) -> Dict[str, Any]:
        """
        Проверяет учетные данные и возвращает токен аутентификации.

        Args:
            db (AsyncSession): Асинхронная сессия базы данных
            credentials (SchemaVerification): Логин и пароль

        Returns:
            dict: Токен или сообщение об ошибке
        """
        try:
            result = await self.database.get_verification(
                db=db,
                verification=credentials
            )

            if result.get("status_code") == 200:
                token_str = result.get("description", "")
                if token_str.startswith("token="):
                    return {"token": token_str.split("=")[1]}

            return {
                "status": "error",
                "message": result.get("description", "Ошибка аутентификации")
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Неизвестная ошибка при проверке учетных данных: {str(e)}"
            }

    async def check_token(self, db: AsyncSession,
                          token: str) -> bool:
        """
        Проверяет валидность токена аутентификации.

        Args:
            db (AsyncSession): Асинхронная сессия базы данных
            token (str): Токен для проверки

        Returns:
            bool: True если токен действителен, иначе False
        """
        try:
            user = await self.database.find_token(db=db, token=token)
            return user is not None
        except Exception as e:
            return False

    async def delete_user(self, db: AsyncSession,
                          user_id: int) -> Dict[str, Any]:
        """
        Удаляет пользователя по ID.

        Args:
            db (AsyncSession): Асинхронная сессия базы данных
            user_id (int): ID удаляемого пользователя

        Returns:
            dict: Результат операции удаления
        """
        try:
            return await self.database.delete_user(db=db, user_id=user_id)
        except Exception as e:
            return {
                "status_code": 500,
                "title": "Ошибка",
                "description": f"Неизвестная ошибка при удалении пользователя: {str(e)}"
            }
