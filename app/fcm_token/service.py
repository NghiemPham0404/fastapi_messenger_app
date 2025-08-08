
from ..base_crud import CRUDRepository
from ..entities.fcm_token import FCMToken

class FCMMessageRepository(CRUDRepository):
    pass

crud = FCMMessageRepository(model = FCMToken)