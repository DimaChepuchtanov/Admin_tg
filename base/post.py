from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from base.model import Post, User
from schema.post import SchemaPost, SchemaPostUpdate
from setting import color


class DataBasePost:
    """
    Класс для выполнения операций CRUD с постами в базе данных.

    Содержит методы для:
    - получения пользователя
    - получения постов (одного/нескольких)
    - создания, обновления и удаления постов
    - удаления всех постов пользователя
    """

    async def get_user(self, db: AsyncSession, user_id: int) -> str:
        """
        Получает имя пользователя по его ID.

        Args:
            db (AsyncSession): Асинхронная сессия базы данных
            user_id (int): ID пользователя

        Returns:
            str | None: Имя пользователя или None при ошибке
        """
        try:
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalars().first()
            return user.name if user else None
        except SQLAlchemyError as e:
            print(
                f"{color.FAIL}ERROR:    {color.ENDC}"
                f"Ошибка получения пользователя с id={user_id}: {e}"
            )
            return None

    async def get_post(self, db: AsyncSession, post_id: int) -> Post:
        """
        Получает пост по его ID.

        Args:
            db (AsyncSession): Асинхронная сессия базы данных
            post_id (int): ID поста

        Returns:
            Post | None: Объект поста или None при ошибке/отсутствии
        """
        try:
            result = await db.execute(select(Post).where(Post.id == post_id))
            return result.scalars().first()
        except SQLAlchemyError as e:
            print(
                f"{color.FAIL}ERROR:    {color.ENDC}"
                f"Ошибка получения поста с id={post_id}: {e}"
            )
            return None

    async def get_posts(self, db: AsyncSession, filter_params: dict) -> list[Post]:
        """
        Получает список постов с применением фильтров.

        Поддерживаемые фильтры:
        - desc: сортировка по убыванию (created_at/title)
        - limit: ограничение количества результатов
        - author: фильтр по автору

        Args:
            db (AsyncSession): Асинхронная сессия базы данных
            filter_params (dict): Параметры фильтрации

        Returns:
            list[Post] | None: Список постов или None при ошибке
        """
        statement = select(Post)

        if "desc" in filter_params:
            if filter_params["desc"] == "created_at":
                statement = statement.order_by(Post.created_at.desc())
            elif filter_params["desc"] == "title":
                statement = statement.order_by(Post.title.desc())
        if "limit" in filter_params:
            statement = statement.limit(filter_params["limit"])
        if "author" in filter_params:
            statement = statement.where(Post.author == filter_params["author"])

        try:
            result = await db.execute(statement)
            return result.scalars().all()
        except SQLAlchemyError as e:
            print(
                f"{color.FAIL}ERROR:    {color.ENDC}"
                f"Ошибка получения списка постов: {e}"
            )
            return None

    async def create_post(self, db: AsyncSession, post: SchemaPost) -> dict:
        """
        Создает новый пост.

        Args:
            db (AsyncSession): Асинхронная сессия базы данных
            post (SchemaPost): Данные для создания поста

        Returns:
            dict: Результат операции с ключами:
                - status_code (int)
                - title (str)
                - description (str | None)
        """
        try:
            new_post = Post(
                title=post.title,
                text=post.text,
                author=post.author
            )
            db.add(new_post)
            await db.commit()
            return {
                "status_code": 201,
                "title": "Успешно",
                "description": None
            }
        except IntegrityError:
            print(
                f"{color.FAIL}ERROR:    {color.ENDC}"
                "Ошибка целостности: указанный автор не существует"
            )
            return {
                "status_code": 404,
                "title": "Ошибка",
                "description": "Указанный автор не существует"
            }
        except SQLAlchemyError as e:
            print(
                f"{color.FAIL}ERROR:    {color.ENDC}"
                f"Ошибка при создании поста: {e}"
            )
            await db.rollback()
            return {
                "status_code": 500,
                "title": "Ошибка",
                "description": "Внутренняя ошибка сервера"
            }

    async def update_post(self, db: AsyncSession, post_update: SchemaPostUpdate) -> dict:
        """
        Обновляет существующий пост.

        Args:
            db (AsyncSession): Асинхронная сессия базы данных
            post_update (SchemaPostUpdate): Данные для обновления поста

        Returns:
            dict: Результат операции
        """
        try:
            post = await self.get_post(db, post_update.id)
            if not post:
                return {
                    "status_code": 404,
                    "title": "Ошибка",
                    "description": "Пост не найден"
                }

            if post_update.title is not None:
                post.title = post_update.title
            if post_update.text is not None:
                post.text = post_update.text

            await db.commit()
            return {
                "status_code": 200,
                "title": "Успешно",
                "description": None
            }
        except SQLAlchemyError as e:
            print(
                f"{color.FAIL}ERROR:    {color.ENDC}"
                f"Ошибка при обновлении поста: {e}"
            )
            await db.rollback()
            return {
                "status_code": 500,
                "title": "Ошибка",
                "description": "Внутренняя ошибка сервера"
            }

    async def delete_post(self, db: AsyncSession, post_id: int) -> dict:
        """
        Удаляет пост по ID.

        Args:
            db (AsyncSession): Асинхронная сессия базы данных
            post_id (int): ID удаляемого поста

        Returns:
            dict: Результат операции
        """
        try:
            post = await self.get_post(db, post_id)
            if not post:
                return {
                    "status_code": 404,
                    "title": "Ошибка",
                    "description": "Пост не найден"
                }

            await db.delete(post)
            await db.commit()
            return {
                "status_code": 200,
                "title": "Успешно",
                "description": None
            }
        except SQLAlchemyError as e:
            print(
                f"{color.FAIL}ERROR:    {color.ENDC}"
                f"Ошибка при удалении поста: {e}"
            )
            await db.rollback()
            return {
                "status_code": 500,
                "title": "Ошибка",
                "description": "Внутренняя ошибка сервера"
            }

    async def delete_posts_user(self, db: AsyncSession, user_id: int) -> dict:
        """
        Удаляет все посты указанного пользователя.

        Args:
            db (AsyncSession): Асинхронная сессия базы данных
            user_id (int): ID пользователя

        Returns:
            dict: Результат операции
        """
        try:
            posts = await self.get_posts(db, {"author": user_id})
            if not posts:
                return {
                    "status_code": 404,
                    "title": "Ошибка",
                    "description": "Посты не найдены"
                }

            for post in posts:
                await db.delete(post)
            await db.commit()
            return {
                "status_code": 200,
                "title": "Успешно",
                "description": None
            }
        except SQLAlchemyError as e:
            print(
                f"{color.FAIL}ERROR:    {color.ENDC}"
                f"Ошибка при удалении постов пользователя: {e}"
            )
            await db.rollback()
            return {
                "status_code": 500,
                "title": "Ошибка",
                "description": "Внутренняя ошибка сервера"
            }
