from ..settings import Settings
from ..db.database import SessionLocal

settings = Settings()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# async def websocket_auth(websocket: WebSocket, Authorize: AuthJWT = Depends()):
#     try:
#         cookie = websocket._cookies["access_token_cookie"]
#         csrf_cookie = websocket._cookies["csrf_access_token"]
#         _verify_jwt_in_request(token = cookie, type_token='cookie', token_from='cookie')
#         if user and user.is_active:
#             return user
#         elif settings.DISABLE_AUTH == "True":
#             return True
#     except:
#         if settings.DISABLE_AUTH == "True":
#             return True
#         else:
#             return None
