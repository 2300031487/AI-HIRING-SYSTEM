import re

def extract_email(text):
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    match = re.search(email_pattern, text)
    return match.group(0) if match else None

def extract_phone(text):
    phone_pattern = r'(\+?\d[\d\-\.\s]{8,15}\d)'
    match = re.search(phone_pattern, text)
    return match.group(0) if match else None

def extract_name(text):
    lines = text.split("\n")
    for line in lines[:3]:
        line = line.strip()
        if not line:
            continue
        if "@" in line or any(char.isdigit() for char in line):
            continue
        if len(line.split()) > 4:
            continue
        return line.title()
    return None