from keycloak import KeycloakOpenID
from webtool.auth import AnnoSessionBackend, KeycloakBackend

from src.core.config import settings

keycloak_openid = KeycloakOpenID(
    server_url=settings.keycloak.server_url,
    client_id=settings.keycloak.client_id,
    realm_name=settings.keycloak.realm_name,
    client_secret_key=settings.keycloak.client_secret,
)

anno_backend = AnnoSessionBackend(session_name="th-session", secure=False)
keycloak_backend = KeycloakBackend(keycloak_openid)
