# utils.py

def count_words(text: str) -> int:
    """단어 수 계산"""
    return len(text.split()) if text.strip() else 0