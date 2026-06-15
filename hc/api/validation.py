"""Validation and normalization for the public Healthchecks API."""

from __future__ import annotations

from datetime import datetime, timezone
from datetime import timedelta as td
from ipaddress import ip_address
from typing import Any, Literal

from cronsim import CronSim, CronSimError
from oncalendar import OnCalendar, OnCalendarError
from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator
from pydantic_core import PydanticCustomError

from hc.lib.tz import all_timezones, legacy_timezones


class BadChannelException(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


def guess_kind(schedule: str) -> str:
    """Classify a schedule as cron or systemd OnCalendar syntax."""

    if "\n" not in schedule.strip() and len(schedule.split()) == 5:
        return "cron"

    return "oncalendar"


class Spec(BaseModel):
    channels: str | None = None
    desc: str | None = None
    failure_kw: str | None = Field(None, max_length=200)
    filter_subject: bool | None = None
    filter_body: bool | None = None
    filter_http_body: bool | None = None
    filter_default_fail: bool | None = None
    grace: td | None = Field(None, ge=60, le=31536000)
    manual_resume: bool | None = None
    methods: Literal["", "POST"] | None = None
    name: str | None = Field(None, max_length=100)
    schedule: str | None = Field(None, max_length=100)
    slug: str | None = Field(None, max_length=100, pattern="^[a-z0-9-_]*$")
    start_kw: str | None = Field(None, max_length=200)
    subject: str | None = Field(None, max_length=200)
    subject_fail: str | None = Field(None, max_length=200)
    success_kw: str | None = Field(None, max_length=200)
    tags: str | None = None
    timeout: td | None = Field(None, ge=60, le=31536000)
    tz: str | None = None
    unique: list[Literal["name", "slug", "tags", "timeout", "grace"]] | None = None

    @model_validator(mode="before")
    @classmethod
    def check_nulls(cls, data: dict[str, Any]) -> dict[str, Any]:
        # None is rejected by the strict field types. Use a float sentinel so
        # clients receive the normal field-specific validation error.
        return {key: 0.0 if value is None else value for key, value in data.items()}

    @field_validator("timeout", "grace", mode="before")
    @classmethod
    def convert_to_timedelta(cls, value: Any) -> Any:
        if isinstance(value, int):
            return td(seconds=value)
        return value

    @field_validator("tz")
    @classmethod
    def check_tz(cls, value: str) -> str:
        value = legacy_timezones.get(value, value)
        if value not in all_timezones:
            raise PydanticCustomError("tz_syntax", "not a valid timezone")
        return value

    @field_validator("schedule")
    @classmethod
    def check_schedule(cls, value: str) -> str:
        if guess_kind(value) == "cron":
            try:
                iterator = CronSim(value, datetime(2000, 1, 1))
                next(iterator)
            except (CronSimError, StopIteration):
                raise PydanticCustomError(
                    "cron_syntax", "not a valid cron expression"
                )
        else:
            try:
                iterator = OnCalendar(value, datetime(2000, 1, 1, tzinfo=timezone.utc))
                next(iterator)
            except (OnCalendarError, StopIteration):
                raise PydanticCustomError("cron_syntax", "not a valid expression")

        return value

    def kind(self) -> str | None:
        if self.schedule:
            return guess_kind(self.schedule)
        if self.timeout:
            return "simple"
        return None


CUSTOM_ERRORS = {
    "too_long": "%s is too long",
    "string_too_long": "%s is too long",
    "string_type": "%s is not a string",
    "string_pattern_mismatch": "%s does not match pattern",
    "less_than_equal": "%s is too large",
    "greater_than_equal": "%s is too small",
    "int_type": "%s is not a number",
    "bool_type": "%s is not a boolean",
    "literal_error": "%s has unexpected value",
    "list_type": "%s is not an array",
    "cron_syntax": "%s is not a valid cron or OnCalendar expression",
    "tz_syntax": "%s is not a valid timezone",
    "time_delta_type": "%s is not a number",
}


def format_first_error(exc: ValidationError) -> str:
    first_error = exc.errors()[0]
    subject = first_error["loc"][0]
    if len(first_error["loc"]) == 2:
        subject = f"an item in '{subject}'"

    template = CUSTOM_ERRORS.get(first_error["type"], "%s is invalid")
    return "json validation error: " + template % subject


def valid_ip(value: str) -> bool:
    try:
        ip_address(value)
        return True
    except ValueError:
        return False
