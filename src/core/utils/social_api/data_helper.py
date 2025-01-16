from typing import Optional, Any, Dict
from datetime import date
import logging

logger = logging.getLogger(__name__)

def _extract_value(data: dict, field: str, key: str, default: Optional[Any] = None) -> Optional[Any]:
    """
    데이터에서 특정 필드와 키 값을 추출하고, 없으면 기본값을 반환합니다.

    Args:
        data: 전체 데이터 dict.
        field: 필드 이름 (e.g., "names").
        key: 필드 내의 값 (e.g., "displayName").
        default: 데이터가 없을 때 반환할 기본값.

    Returns:
        추출된 값 또는 기본값.
    """
    return next((item[key] for item in data.get(field, []) if key in item), default)


def _convert_date(value: Dict[str, int]) -> Optional[date]:
    """
    딕셔너리 형태의 날짜 데이터를 `datetime.date`로 변환하고,
    변환된 날짜가 과거인지 검증합니다.

    Args:
        value: {"year": int, "month": int, "day": int} 형태의 날짜 데이터.

    Returns:
        유효한 날짜 객체 또는 None.

    Raises:
        ValueError: 날짜가 잘못되었거나 미래일 경우 예외를 발생시킴.
    """
    year = value.get("year")
    month = value.get("month")
    day = value.get("day")

    if not (year and month and day):
        return None

    try:
        converted_date = date(year, month, day)
    except ValueError as ve:
        raise ValueError(f"Invalid date provided: {ve}")

    if converted_date >= date.today():
        raise ValueError("The date must be in the past.")

    return converted_date


def get_value(field: str, key: str, data: dict, is_date: bool = False) -> Optional[Any]:
    """
    API 응답 데이터에서 특정 필드 값을 추출한 뒤, 필요시 날짜 필드를 변환 및 검증합니다.

    Args:
        field: 데이터 필드 이름 e.g., "names".
        key: 필드 내의 값 e.g., "displayName".
        data: 전체 데이터 dict.
        is_date: 해당 값이 날짜 데이터인지 여부.

    Returns:
        추출된 값 또는 None.
    """
    value = _extract_value(data, field, key)
    if is_date and isinstance(value, dict):
        try:
            return _convert_date(value)
        except ValueError as e:
            logger.error(f"Invalid date encountered: {e}")
            return None

    return value