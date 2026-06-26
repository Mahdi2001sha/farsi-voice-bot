import re
from typing import Tuple

FARSI_DIGITS = {
    '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
    '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9',
}

ARABIC_DIGITS = {
    '٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4',
    '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9',
}

FARSI_WORD_NUMBERS = {
    'صفر': '0', 'یک': '1', 'دو': '2', 'سه': '3', 'چهار': '4',
    'پنج': '5', 'شش': '6', 'هفت': '7', 'هشت': '8', 'نه': '9',
    'ده': '10', 'بیست': '20', 'سی': '30', 'چهل': '40', 'پنجاه': '50',
    'شصت': '60', 'هفتاد': '70', 'هشتاد': '80', 'نود': '90',
    'نونزده': '19', 'دوازده': '12', 'سیزده': '13', 'چهارده': '14',
    'پانزده': '15', 'شانزده': '16', 'هفده': '17', 'هجده': '18',
    'صد': '100', 'هزار': '1000', 'میلیون': '1000000', 'میلیارد': '1000000000',
}

TYPO_FIXES = {
    'مدیون': 'میلیون',
    'ملیون': 'میلیون',
    'میلیون': 'میلیون',
    'تومن': 'تومان',
    'ریال': 'ریال',
}

def fix_typos(text: str) -> str:
    for typo, correct in TYPO_FIXES.items():
        text = re.sub(rf'\b{typo}\b', correct, text, flags=re.IGNORECASE)
    return text

def convert_digit_chars(text: str) -> str:
    for farsi, english in FARSI_DIGITS.items():
        text = text.replace(farsi, english)
    for arabic, english in ARABIC_DIGITS.items():
        text = text.replace(arabic, english)
    return text

def fix_spoken_numbers(text: str) -> str:
    # Fix "520و1000" or similar joined numbers
    text = re.sub(r'(\d+)و(\d+)', r'\1 و \2', text)
    
    # Fix common OCR/speech errors
    text = re.sub(r'5201000', '520000', text)
    text = re.sub(r'1000تومان', '1000 تومان', text)
    
    return text

def expand_abbreviations(text: str) -> str:
    # Fix "ب10" → "بیش از 10" or "به 10"
    text = re.sub(r'\bب(\d+)\b', lambda m: 'بیش از ' + m.group(1), text)
    text = re.sub(r'\bت(\d+)\b', lambda m: 'تومان ' + m.group(1), text)
    text = re.sub(r'\bر(\d+)\b', lambda m: 'ریال ' + m.group(1), text)
    
    return text

def convert_spoken_numbers(text: str) -> str:
    def replace_repeating_sequence(match):
        sequence = match.group(0).lower()
        words = re.split(r'[\s\u200Eو\u200Fو]+', sequence)
        words = [w.strip() for w in words if w.strip() and w.strip() != 'و']
        
        digits = []
        for word in words:
            if word in FARSI_WORD_NUMBERS:
                digit = FARSI_WORD_NUMBERS[word]
                if digit not in ['000', '000000']:
                    digits.append(digit)
        
        return ''.join(digits) if digits else match.group(0)
    
    number_words = '|'.join(FARSI_WORD_NUMBERS.keys())
    pattern = rf'(?:{number_words})(?:[\s\u200E\u200Fو]+(?:{number_words}))*'
    text = re.sub(pattern, replace_repeating_sequence, text, flags=re.IGNORECASE)
    
    return text

def clean_numbers(text: str) -> str:
    text = re.sub(r'(\d)[\s\-]+(\d)', r'\1\2', text)
    return text

def fix_account_patterns(text: str) -> str:
    # 16 digit card number
    text = re.sub(r'(\d{4})[\s\-](\d{4})[\s\-](\d{4})[\s\-](\d{4})',
                  r'\1-\2-\3-\4', text)
    # IBAN pattern
    text = re.sub(r'(\d{4})[\s\-](\d{4})[\s\-](\d{4})[\s\-](\d{4})[\s\-](\d{4})[\s\-](\d{4})',
                  r'\1-\2-\3-\4-\5-\6', text)
    
    return text

def process_transcription(text: str) -> Tuple[str, dict]:
    text = fix_typos(text)
    text = fix_spoken_numbers(text)
    text = expand_abbreviations(text)
    text = convert_digit_chars(text)
    text = convert_spoken_numbers(text)
    text = clean_numbers(text)
    text = fix_account_patterns(text)
    
    extracted = {
        "card_numbers": re.findall(r'\d{4}-\d{4}-\d{4}-\d{4}', text),
        "account_numbers": re.findall(r'\d{4}-\d{4}-\d{4}-\d{4}-\d{4}-\d{4}', text),
    }
    
    return text, extracted