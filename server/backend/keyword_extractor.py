import re
from typing import Dict

BANKING_COMMANDS = {
    "transfer": ["انتقال", "واریز", "پرداخت", "ارسال پول", "تراکنش"],
    "balance": ["موجودی", "بالانس", "حساب چند شد", "چند دارم"],
    "check": ["بررسی", "چک کن", "نگاه کن"],
    "cancel": ["لغو", "حذف", "انصراف"],
    "confirm": ["تأیید", "تایید", "درست", "بله"],
    "alert": ["اطلاع", "خبر", "هشدار", "بگو"],
    "fee": ["کارمزد", "سرویس"],
}

def extract_amount(text: str) -> list:
    amounts = []
    
    patterns = [
        (r'(\d+)\s*میلیون\s*و\s*(\d+)\s*هزار', 'both'),
        (r'(\d+)\s*میلیون', 'million'),
        (r'(\d+)\s*هزار', 'thousand'),
        (r'(\d+)\s*(?:تومان|ریال)', 'direct'),
    ]
    
    for pattern, ptype in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            if ptype == 'both':
                million = int(match.group(1))
                thousand = int(match.group(2))
                total = (million * 1000000) + (thousand * 1000)
                amounts.append(f"{total:,}")
            elif ptype == 'million':
                amount = int(match.group(1)) * 1000000
                amounts.append(f"{amount:,}")
            elif ptype == 'thousand':
                amount = int(match.group(1)) * 1000
                amounts.append(f"{amount:,}")
            elif ptype == 'direct':
                amounts.append(match.group(1))
    
    return amounts

def extract_keywords(text: str) -> Dict:
    text_lower = text.lower()
    
    # Extract card/account numbers
    card_numbers = re.findall(r'\d{4}-\d{4}-\d{4}-\d{4}', text)
    account_numbers = re.findall(r'\d{4}-\d{4}-\d{4}-\d{4}-\d{4}-\d{4}', text)
    
    amounts = extract_amount(text)
    
    # Detect commands
    detected_commands = []
    for cmd_type, keywords in BANKING_COMMANDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                detected_commands.append(cmd_type)
                break
    
    # Extract fee threshold
    fee_threshold = None
    if "fee" in detected_commands:
        fee_pattern = r'کارمزد(?:\s+این)?\s+ترکنش\s+بیش\s+از\s+(\d+)'
        fee_match = re.search(fee_pattern, text_lower)
        if fee_match:
            fee_threshold = fee_match.group(1)
        else:
            fee_pattern2 = r'بیش\s+از\s+(\d+)\s+(?:تومان|ریال)'
            fee_match = re.search(fee_pattern2, text_lower)
            if fee_match:
                fee_threshold = fee_match.group(1)
    
    # Extract alert threshold
    alert_threshold = None
    if "alert" in detected_commands or "fee" in detected_commands:
        # Pattern: "بیش از 1000 تومان"
        threshold_pattern = r'بیش\s+از\s+(\d+)\s*(?:هزار)?\s*(?:تومان|ریال)?'
        threshold_match = re.search(threshold_pattern, text_lower)
        if threshold_match:
            alert_threshold = threshold_match.group(1)
    
    return {
        "card_numbers": card_numbers,
        "account_numbers": account_numbers,
        "amounts": amounts,
        "commands": list(set(detected_commands)),
        "alert_threshold": alert_threshold,
        "fee_threshold": fee_threshold,
        "transaction_detected": (
            "transfer" in detected_commands or
            len(card_numbers) > 0 and len(amounts) > 0
        ),
        "has_alert": "alert" in detected_commands or "fee" in detected_commands,
    }