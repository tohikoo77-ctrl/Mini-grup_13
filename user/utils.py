import re
from typing import Optional

def normalize_phone_number(phone: Optional[str]) -> str:
    """
    Normalizes a phone number by removing any characters that are not digits,
    while preserving the leading '+' sign.
    """
    if not phone:
        return ""
    
    # Keep the leading plus and extract all digits
    clean_digits = re.sub(r'\D', '', phone)
    return f"+{clean_digits}" if phone.startswith('+') else clean_digits

def is_uzbek_phone_valid(phone: str) -> bool:
    """
    Checks if the phone number follows the Uzbekistan format (+998XXXXXXXXX).
    """
    if not phone:
        return False
    
    pattern = r'^\+998\d{9}$'
    return bool(re.match(pattern, phone))