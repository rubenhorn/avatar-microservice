from jose import jwt
import json
import urllib

_FIREBASE_CERTIFICATE_URL = 'https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com'


class AuthException(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
    pass


class FirebaseAuth(object):
    def __init__(self, project_id: str):
        assert(project_id is not None and project_id != '')
        self.project_id = project_id

    def get_user_id_from_id_token(self, id_token: str) -> str:
        certificates_json = urllib.request.urlopen(
            _FIREBASE_CERTIFICATE_URL).read()
        certificates = json.loads(certificates_json)
        try:
            claims = jwt.decode(id_token, certificates,
                                algorithms='RS256', audience=self.project_id)
            return claims['sub']
        except:
            raise AuthException('Error decoding token')
