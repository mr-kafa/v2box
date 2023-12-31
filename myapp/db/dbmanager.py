import datetime
import json
from myapp.utils.stats import UsersUsage
from myapp.db import database
from sqlalchemy.ext.asyncio import AsyncSession
from myapp.db.tables import Users
from collections.abc import AsyncIterator
from sqlalchemy import select, update
from v2client.v2ray import stats
from myapp.utils import stats as mystats
from typing import List


async def get_user(email: str) -> Users | bool:
    async_session: AsyncSession = await get_session()
    async with async_session.__call__() as session:
        query = select(Users).where(Users.email == email)
        result = await session.execute(query)
        if user := result.scalars().first():
            return user
        else:
            return False


async def get_session():
    async_iterator: AsyncIterator[AsyncSession] = database.session()
    return await anext(async_iterator)


async def db_add_vmess_user(user: mystats.User) -> mystats.Detail:
    if not await get_user(email=user.v2user.email):
        async_session: AsyncSession = await get_session()
        protocol_detail = str(json.dumps(vars(user.v2user)))
        async with async_session.__call__() as session:
            async with session.begin():
                session.add(Users(
                    email=user.v2user.email,
                    uuid=user.v2user.userUuid,
                    active=user.active,
                    protocol=user.protocol,
                    traffic=user.traffic,
                    expire=user.expireDate,
                    protocol_detail=protocol_detail
                ))
        return mystats.Detail(flag=True, status="user added in db")
    else:
        return mystats.Detail(flag=False, status="user not found in db")


async def db_add_vless_user(email: str):
    pass


async def db_add_trojan_user():
    pass


async def db_remove_user(email: str) -> mystats.Detail:
    if user := await get_user(email=email):
        async_session: AsyncSession = await get_session()
        async with async_session.__call__() as session:
            await session.delete(user)
            await session.commit()
            return mystats.Detail(flag=True, status="user removed in db")
    else:
        return mystats.Detail(flag=False, status="user not found in db")


async def db_update_activity(email: str, active: bool) -> mystats.Detail:
    if user := await get_user(email=email):
        async_session: AsyncSession = await get_session()
        async with async_session.__call__() as session:
            user.active = active
            # user_dict = vars(user)
            # user_dict.pop("_sa_instance_state")
            # query = update(Users).values(user_dict).where(Users.id == user.id)
            query = update(Users).values({"active": active}).where(Users.id == user.id)
            await session.execute(query)
            await session.commit()
            return mystats.Detail(flag=True, status=user)
    else:
        return mystats.Detail(flag=False, status="user not found in db")


async def db_user_usage(email: str) -> mystats.Detail:
    if user := await get_user(email=email):
        return mystats.Detail(flag=True, status=stats.UsageResponse(user.download, user.upload))
    else:
        return mystats.Detail(flag=False, status="user not found in db")


async def db_users_usage() -> mystats.Detail:
    async_session: AsyncSession = await get_session()
    async with async_session.__call__() as session:
        query = select(Users).order_by(Users.id)
        result = await session.execute(query)
        if users := result.scalars().all():
            list_user_usage = list()
            for user in users:
                list_user_usage.append(
                    UsersUsage(email=user.email, upload=int(user.upload), download=int(user.download))
                )
            return mystats.Detail(flag=True, status=list_user_usage)
        else:
            return mystats.Detail(flag=False, status="user not found in db")


async def db_update_user_usage(email: str, download: int, upload: int) -> mystats.Detail:
    if user := await get_user(email=email):
        async_session: AsyncSession = await get_session()
        async with async_session.__call__() as session:
            user.download += download
            user.upload += upload
            query = update(Users).values(
                {
                    "download": user.download,
                    "upload": user.upload
                }
            ).where(Users.email == user.email)
            await session.execute(query)
            await session.commit()
            # print(f"download: {download}. upload: {upload}. user: {user.email} / {user.download} / {user.upload}")
            return mystats.Detail(flag=True, status=user)
    else:
        return mystats.Detail(flag=False, status="user not found in db")


async def db_set_user_usage(expire: datetime.datetime, email: str, upload: int, download: int, traffic: int):
    if user := await get_user(email=email):
        async_session: AsyncSession = await get_session()
        async with async_session.__call__() as session:
            original = {
                    "download": download,
                    "upload": upload,
                    "traffic": traffic,
                    "expire": expire
                }
            filtered = {k: v for k, v in original.items() if v is not None}
            if filtered:
                query = update(Users).values(
                    filtered
                ).where(Users.email == user.email)
                await session.execute(query)
                await session.commit()
                return mystats.Detail(flag=True, status="traffic success set")
            else:
                return mystats.Detail(flag=False, status="query is empty")
    else:
        return mystats.Detail(flag=False, status="user not found in db")


async def db_update_users_usage(users: List[dict]):
    # not working
    async_session: AsyncSession = await get_session()
    async with async_session.__call__() as session:
        await session.execute(
            update(Users),
            [{"id": 1, "download": Users.__table__.c.download + 1, "upload": +43984}]
        )
        await session.commit()


async def get_all_users() -> mystats.Detail:
    async_session: AsyncSession = await get_session()
    async with async_session.__call__() as session:
        query = select(Users)
        result = await session.execute(query)
        if users := result.scalars().all():
            return mystats.Detail(flag=True, status=users)
        else:
            return mystats.Detail(flag=False, status="users list is empty from db")


def db_traffic_all():
    pass
