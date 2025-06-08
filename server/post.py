from sqlalchemy.ext.asyncio import AsyncSession
from base.post import DataBasePost
from schema.post import SchemaPost, SchemaPostUpdate
from datetime import datetime
from typing import Any, Dict, List, Union


class MiddleLoyePost:
    """
    Промежуточный слой для операций с постами.

    Обеспечивает преобразование данных между слоем базы данных и API,
    дополнительную валидацию и обработку бизнес-логики.

    Attributes:
        database (DataBasePost): Экземпляр класса для работы с базой данных
    """

    def __init__(self, database: DataBasePost) -> None:
        """
        Инициализирует экземпляр MiddleLoyePost.

        Args:
            database (DataBasePost): Экземпляр класса для работы с БД
        """
        self.database = database

    async def get_post(self, db: AsyncSession,
                       post_id: int) -> Dict[str, Any]:
        """
        Получает и форматирует пост по ID.

        Args:
            db (AsyncSession): Асинхронная сессия базы данных
            post_id (int): ID поста

        Returns:
            dict: Отформатированные данные поста или сообщение об ошибке
        """
        try:
            post = await self.database.get_post(db=db, post_id=post_id)
            if not post:
                return {
                    "status": "error",
                    "message": f"Пост с ID {post_id} не найден"
                }

            user_name = await self.database.get_user(db=db, user_id=post.author)
            return {
                "title": post.title,
                "text": post.text,
                "author": user_name or "Неизвестный автор",
                "created_at": datetime.strftime(post.created_at, "%Y-%m-%d %H:%M")
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Ошибка при получении поста: {str(e)}"
            }

    async def get_posts(self, db: AsyncSession,
                        filter_params: Dict[str, Any]) -> Union[List[Dict[str, Any]], Dict[str, str]]:
        """
        Получает и форматирует список постов с фильтрацией.

        Args:
            db (AsyncSession): Асинхронная сессия базы данных
            filter_params (dict): Параметры фильтрации

        Returns:
            list | dict: Список постов или сообщение об ошибке
        """
        # Валидация параметра сортировки
        if "desc" in filter_params:
            valid_sort_fields = ["created_at", "title"]
            if filter_params["desc"] not in valid_sort_fields:
                return {
                    "status": "error",
                    "message": f"Недопустимое поле для сортировки. "
                               f"Допустимые значения: {', '.join(valid_sort_fields)}"
                }

        try:
            posts = await self.database.get_posts(db=db, filter_params=filter_params)
            if not posts:
                return []

            return [
                {
                    "title": post.title,
                    "id": post.id,
                    "created_at": datetime.strftime(post.created_at, "%Y-%m-%d %H:%M")
                }
                for post in posts
            ]
        except Exception as e:
            return {
                "status": "error",
                "message": f"Ошибка при получении списка постов: {str(e)}"
            }

    async def new_post(self, db: AsyncSession,
                       post: SchemaPost) -> Dict[str, Any]:
        """
        Создает новый пост.

        Args:
            db (AsyncSession): Асинхронная сессия базы данных
            post (SchemaPost): Данные для создания поста

        Returns:
            dict: Результат операции
        """
        try:
            return await self.database.create_post(db=db, post=post)
        except Exception as e:
            return {
                "status_code": 500,
                "title": "Ошибка",
                "description": f"Неизвестная ошибка при создании поста: {str(e)}"
            }

    async def update_post(self, db: AsyncSession,
                          update_data: SchemaPostUpdate) -> Dict[str, Any]:
        """
        Обновляет существующий пост.

        Args:
            db (AsyncSession): Асинхронная сессия базы данных
            update_data (SchemaPostUpdate): Данные для обновления

        Returns:
            dict: Результат операции
        """
        try:
            return await self.database.update_post(db=db, post_update=update_data)
        except Exception as e:
            return {
                "status_code": 500,
                "title": "Ошибка",
                "description": f"Неизвестная ошибка при обновлении поста: {str(e)}"
            }

    async def delete_post_user(self, db: AsyncSession,
                               user_id: int) -> Dict[str, Any]:
        """
        Удаляет все посты пользователя.

        Args:
            db (AsyncSession): Асинхронная сессия базы данных
            user_id (int): ID пользователя

        Returns:
            dict: Результат операции
        """
        try:
            result = await self.database.delete_posts_user(db=db, user_id=user_id)
            if result.get("status_code") == 200:
                return {
                    "status_code": 200,
                    "message": f"Все посты пользователя {user_id} удалены"
                }
            return result
        except Exception as e:
            return {
                "status_code": 500,
                "title": "Ошибка",
                "description": f"Неизвестная ошибка при удалении постов: {str(e)}"
            }

    async def delete_post(self, db: AsyncSession,
                          post_id: int) -> Dict[str, Any]:
        """
        Удаляет пост по ID.

        Args:
            db (AsyncSession): Асинхронная сессия базы данных
            post_id (int): ID удаляемого поста

        Returns:
            dict: Результат операции
        """
        try:
            return await self.database.delete_post(db=db, post_id=post_id)
        except Exception as e:
            return {
                "status_code": 500,
                "title": "Ошибка",
                "description": f"Неизвестная ошибка при удалении поста: {str(e)}"
            }
