from sqlalchemy import update, delete, select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union
from db.models.users import User, UserRole
from db.dals.base_dal import BaseDAL
from db.session import async_session
from datetime import datetime

class UserDAL(BaseDAL):
    async def create_user(self, name: str, surname: str, username: str, email: str, hashed_password: str, role: UserRole) -> User:
        new_user = User(
            name=name,
            surname=surname,
            username=username,
            email=email,
            hashed_password=hashed_password,
            role=role
        )
        self.db_session.add(new_user)
        await self.db_session.flush()
        await self.db_session.commit()
        return new_user
    
    async def delete_user(self, user_id: int) -> Union[User, None]:
        query = update(User).where(and_(
            User.user_id == user_id,
            User.is_active == True
        )).values(is_active=False).returning(User.user_id)
        result = await self.db_session.execute(query)
        deleted_user_by_id = result.fetchone()
        if deleted_user_by_id is not None:
            await self.db_session.commit()
            return deleted_user_by_id[0]
        return None
    
    async def get_user(self, user_id: int) -> Union[User, None]:
        query = select(User).where(User.user_id == user_id)
        result = await self.db_session.execute(query)
        user_by_id = result.fetchone()
        if user_by_id is not None:
            return user_by_id[0]
        return None
    
    async def get_user_by_username(self, username: str) -> Union[User, None]:
        query = select(User).where(User.username == username)
        result = await self.db_session.execute(query)
        user_by_username = result.fetchone()
        if user_by_username is not None:
            return user_by_username[0]
        return None
    
    async def get_users(self) -> list[User]:
        query = select(User).where(User.is_active == True)
        result = await self.db_session.execute(query)
        users = result.fetchall()
        return [user[0] for user in users]

    async def update_user(self, user_id: int, **kwargs) -> Union[int, None]:
        query = update(User).\
            where(and_(User.user_id == user_id, User.is_active == True)).\
            values(kwargs).\
            returning(User.user_id)
        res = await self.db_session.execute(query)
        update_user_id_row = res.fetchone()
        if update_user_id_row is not None:
            await self.db_session.commit()
            return update_user_id_row[0]
        return None
    
    async def get_user_by_email(self, email: str) -> Union[User, None]:
        query = select(User).where(User.email == email)
        res = await self.db_session.execute(query)
        user_row = res.fetchone()
        if user_row is not None:
            return user_row[0]
        return None

    async def get_user_by_id(self, user_id: int) -> Union[User, None]:
        query = select(User).where(User.user_id == user_id)
        result = await self.db_session.execute(query)
        user = result.fetchone()
        if user is not None:
            return user[0]
        return None

    async def update_user_role(self, user_id: int, new_role: UserRole) -> Union[User, None]:
        query = update(User).\
            where(and_(User.user_id == user_id, User.is_active == True)).\
            values(role=new_role, updated_at=datetime.now()).\
            returning(User)
        res = await self.db_session.execute(query)
        updated_user = res.fetchone()
        if updated_user is not None:
            await self.db_session.commit()
            return updated_user[0]
        return None

async def get_user_dal():
    async with async_session() as session:
        async with session.begin():
            yield UserDAL(session)
