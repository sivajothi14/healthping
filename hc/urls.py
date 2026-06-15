from __future__ import annotations

from urllib.parse import urlparse

from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from hc.accounts import views as accounts_views

prefix = ""
if _path := urlparse(settings.SITE_ROOT).path.lstrip("/"):
    prefix = f"{_path}/"

INTEGRATION_APPS = (
    "apprise",
    "call",
    "discord",
    "email",
    "github",
    "googlechat",
    "gotify",
    "group",
    "matrix",
    "mattermost",
    "msteamsw",
    "ntfy",
    "opsgenie",
    "pagertree",
    "pd",
    "po",
    "prometheus",
    "pushbullet",
    "rocketchat",
    "shell",
    "signal",
    "slack",
    "sms",
    "spike",
    "telegram",
    "trello",
    "victorops",
    "webhook",
    "whatsapp",
    "zulip",
)

urlpatterns = [
    path(f"{prefix}admin/login/", accounts_views.login),
    path(f"{prefix}admin/", admin.site.urls),
    path(prefix, include("hc.accounts.urls")),
    path(prefix, include("hc.api.urls")),
    path(prefix, include("hc.front.urls")),
    path(prefix, include("hc.payments.urls")),
]

urlpatterns.extend(
    path(prefix, include(f"hc.integrations.{app}.urls"))
    for app in INTEGRATION_APPS
)
