from typing import Annotated

from fastapi import APIRouter, Depends, status
from webtool.throttle import limiter

router = APIRouter()
