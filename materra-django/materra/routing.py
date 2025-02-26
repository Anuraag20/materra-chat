from channels.auth import AuthMiddlewareStack
from channels.routing import URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
import chat.routing
#The AllowedHostOriginValidator was added later

router = AllowedHostsOriginValidator(
            AuthMiddlewareStack(
                URLRouter(
                    chat.routing.websocket_urlpatterns,
                )
            )
        )
