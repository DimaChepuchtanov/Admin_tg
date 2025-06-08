from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from base.model import User
from schema.user import SchemaUser, SchemaVerification
from setting import color
from typing import Dict, Optional, Union


class DataBaseUser:
    """
    Класс для выполнения операций CRUD с пользователями в базе данных.

    Содержит методы для:
    - получения информации о пользователях
    - аутентификации пользователей
    - создания и удаления пользователей
    - управления токенами
    """

    async def get_user(self, db: AsyncSession, user_id: int) -> Optional[User]:
        """
        Получает пользователя по его ID.

        Args:
            db (AsyncSession): Асинхронная сессия базы данных
            user_id (int): ID пользователя

        Returns:
            User | None: Объект пользователя или None при ошибке/отсутствии
        """
        try:
            result = await db.execute(select(User).where(User.id == user_id))
            return result.scalars().first()
        except SQLAlchemyError as e:
            print(
                f"{color.FAIL}ERROR:    {color.ENDC}"
                f"Ошибка получения пользователя с id={user_id}: {e}"
            )
            return None

    async def find_token(self, db: AsyncSession, token: str) -> Optional[User]:
        """
        Находит пользователя по токену аутентификации.

        Args:
            db (AsyncSession): Асинхронная сессия базы данных
            token (str): Токен аутентификации

        Returns:
            User | None: Объект пользователя или None при ошибке/отсутствии
        """
        try:
            result = await db.execute(select(User).where(User.token == token))
            return result.scalars().first()
        except SQLAlchemyError as e:
            print(
                f"{color.FAIL}ERROR:    {color.ENDC}"
                f"Ошибка получения пользователя по токену {token}: {e}"
            )
            return None

    async def get_verification(self, db: AsyncSession,
                               verification: SchemaVerification) -> Dict[str, Union[int, str]]:
        """
        Проверяет учетные данные пользователя и возвращает токен.

        Args:
            db (AsyncSession): Асинхронная сессия базы данных
            verification (SchemaVerification): Данные для аутентификации

        Returns:
            dict: Результат операции с ключами:
                - status_code (int)
                - title (str)
                - description (str)
        """
        try:
            result = await db.execute(
                select(User.token).where(
                    User.login == verification.login,
                    User.password == verification.password
                )
            )
            user_token = result.scalars().first()

            if not user_token:
                return {
                    "status_code": 404,
                    "title": "Ошибка",
                    "description": "Пользователь с указанными данными не найден"
                }

            return {
                "status_code": 200,
                "title": "Успешно",
                "description": f"token={user_token}"
            }

        except SQLAlchemyError as e:
            print(
                f"{color.FAIL}ERROR:    {color.ENDC}"
                f"Ошибка аутентификации пользователя: {e}"
            )
            return {
                "status_code": 500,
                "title": "Ошибка",
                "description": "Внутренняя ошибка сервера при аутентификации"
            }

    async def create_user(self, db: AsyncSession,
                          user: SchemaUser) -> Dict[str, Union[int, str]]:
        """
        Создает нового пользователя.

        Args:
            db (AsyncSession): Асинхронная сессия базы данных
            user (SchemaUser): Данные нового пользователя

        Returns:
            dict: Результат операции
        """
        try:
            new_user = User(
                name=user.name,
                token=user.token,
                login=user.login,
                password=user.password
            )

            db.add(new_user)
            await db.commit()

            return {
                "status_code": 201,
                "title": "Успешно",
                "description": "Пользователь успешно создан"
            }

        except IntegrityError:
            print(
                f"{color.FAIL}ERROR:    {color.ENDC}"
                "Ошибка целостности: возможно, логин или токен уже существуют"
            )
            await db.rollback()
            return {
                "status_code": 409,
                "title": "Ошибка",
                "description": "Пользователь с таким логином или токеном уже существует"
            }
        except SQLAlchemyError as e:
            print(
                f"{color.FAIL}ERROR:    {color.ENDC}"
                f"Ошибка при создании пользователя: {e}"
            )
            await db.rollback()
            return {
                "status_code": 500,
                "title": "Ошибка",
                "description": "Внутренняя ошибка сервера при создании пользователя"
            }

    async def delete_user(self, db: AsyncSession,
                          user_id: int) -> Dict[str, Union[int, str]]:
        """
        Удаляет пользователя по ID.

        Args:
            db (AsyncSession): Асинхронная сессия базы данных
            user_id (int): ID удаляемого пользователя

        Returns:
            dict: Результат операции
        """
        try:
            user = await self.get_user(db, user_id)
            if not user:
                return {
                    "status_code": 404,
                    "title": "Ошибка",
                    "description": f"Пользователь с ID {user_id} не найден"
                }

            await db.delete(user)
            await db.commit()

            return {
                "status_code": 200,
                "title": "Успешно",
                "description": f"Пользователь с ID {user_id} успешно удален"
            }

        except SQLAlchemyError as e:
            print(
                f"{color.FAIL}ERROR:    {color.ENDC}"
                f"Ошибка при удалении пользователя {user_id}: {e}"
            )
            await db.rollback()
            return {
                "status_code": 500,
                "title": "Ошибка",
                "description": "Внутренняя ошибка сервера при удалении пользователя"
            }
