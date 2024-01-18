import json
from aiohttp import web
from sqlalchemy.exc import IntegrityError

from models import Ad, engine, init_orm, Session


@web.middleware
async def session_middleware(request: web.Request, handler):
    async with Session() as session:
        request.session = session
        response = await handler(request)
        return response


def get_http_error(error_class, message):
    return error_class(
        text=json.dumps({'error': message}),
        content_type="application/json"
    )


async def get_user_by_id(session: Session, ad_id: int):
    ad = await session.get(Ad, ad_id)
    if ad is None:
        raise get_http_error(web.HTTPNotFound, message=f"User with {ad_id} not found")
    return ad


async def get_ad_by_id(session: Session, ad_id: int):
    ad = await session.get(Ad, ad_id)
    if ad is None:
        raise get_http_error(web.HTTPNotFound, message=f"Ad with {ad_id} not found")
    return ad


async def add_ad(session: Session, ad: int):
    try:
        session.add(ad)
        await session.commit()
    except IntegrityError:
        raise get_http_error(web.HTTPConflict, f'Ad already exists')
    return ad


class AdView(web.View):
    @property
    def session(self) -> Session:
        return self.request.session

    @property
    def ad_id(self):
        return int(self.request.match_info['ad_id'])

    async def get_ad(self):
        return await get_ad_by_id(self.session, self.ad_id)

    async def get(self):
        ad = await self.get_ad()
        return web.json_response(ad.dict)

    async def post(self):
        json_data = await self.request.json()
        ad = Ad(**json_data)
        await add_ad(self.session, ad)
        # print(user.id, user.name)
        return web.json_response({'id': ad.id})

    async def patch(self):
        json_data = await self.request.json()
        ad = await self.get_ad()
        for field, value in json_data.items():
            setattr(ad, field, value)
        await add_ad(self.session, ad)
        return web.json_response(ad.dict)

    async def delete(self):
        ad = await self.get_ad()
        await self.session.delete(ad)
        await self.session.commit()
        return web.json_response({'status': 'delete'})


async def init_db(app: web.Application):
    print('START')
    await init_orm()
    yield
    print('FINISH')
    await engine.dispose()


def run_server():
    app = web.Application()
    app.cleanup_ctx.append(init_db)
    app.middlewares.append(session_middleware)
    app.add_routes([
        web.get('/ad/{ad_id:\d+}', AdView),
        web.patch('/ad/{ad_id:\d+}', AdView),
        web.delete('/ad/{ad_id:\d+}', AdView),
        web.post('/ad', AdView),
    ])
    web.run_app(app, port=8080)
