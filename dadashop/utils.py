import hashlib
import jwt
from django.conf import settings

def md5(str):
    md5 = hashlib.md5()
    md5.update(str.encode('utf-8'))
    return md5.hexdigest()

'''
 def encode(
        self,
        payload: Dict[str, Any],
        key: str,
        algorithm: Optional[str] = "HS256",
        headers: Optional[Dict] = None,
        json_encoder: Optional[Type[json.JSONEncoder]] = None,
    )
'''
def jwt_encode(payload):
    jwt_str = jwt.encode(

        payload=payload,
        key='dadashop',
        algorithm='HS256'
    )
    return jwt_str


def jwt_decode(jwt_str):
    payload = jwt.decode(
        jwt=jwt_str,
        key='dadashop',
        algorithms='HS256'
    )
    return payload
