"""Shared project, check, and channel access checks for the web UI."""

from __future__ import annotations

from uuid import UUID

from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.http import HttpRequest
from django.shortcuts import get_object_or_404

from hc.accounts.models import Member, Project
from hc.api.models import Channel, Check


def _project_access(request: HttpRequest, project: Project) -> bool:
    """Return whether the current user has read/write project access."""

    assert request.user.is_authenticated
    if request.user.is_superuser or request.user.id == project.owner_id:
        return True

    membership = get_object_or_404(Member, project=project, user=request.user)
    return membership.is_rw


def _require_write_access(access: bool) -> None:
    if not access:
        raise PermissionDenied


def _get_project_for_user(request: HttpRequest, code: UUID) -> tuple[Project, bool]:
    project = get_object_or_404(Project, code=code)
    return project, _project_access(request, project)


def _get_rw_project_for_user(request: HttpRequest, code: UUID) -> Project:
    project, access = _get_project_for_user(request, code)
    _require_write_access(access)
    return project


def _get_check_for_user(
    request: HttpRequest, code: UUID, preload_owner_profile: bool = False
) -> tuple[Check, bool]:
    """Return a check and the current user's read/write access to its project."""

    queryset: QuerySet[Check] = Check.objects.select_related("project")
    if preload_owner_profile:
        queryset = queryset.select_related("project__owner__profile")

    check = get_object_or_404(queryset, code=code)
    return check, _project_access(request, check.project)


def _get_rw_check_for_user(request: HttpRequest, code: UUID) -> Check:
    check, access = _get_check_for_user(request, code)
    _require_write_access(access)
    return check


def _get_channel_for_user(request: HttpRequest, code: UUID) -> tuple[Channel, bool]:
    """Return a channel and the current user's read/write access to its project."""

    channel = get_object_or_404(Channel.objects.select_related("project"), code=code)
    return channel, _project_access(request, channel.project)


def _get_rw_channel_for_user(request: HttpRequest, code: UUID) -> Channel:
    channel, access = _get_channel_for_user(request, code)
    _require_write_access(access)
    return channel
