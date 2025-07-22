# vocabulary_loader.py
import streamlit as st
import os

from data_config import VOCAB_FILE_PATH_2015, VOCAB_FILE_PATH_2022

def load_moe_vocabulary(file_path: str, year: str) -> set:
    """교육부 기본 어휘 목록 파일을 읽어 단어 집합으로 반환합니다."""
    vocabulary_set = set()
    try:
        if not os.path.exists(file_path):
            st.warning(f"교육부 기본 어휘 파일 '{file_path}'을(를) 찾을 수 없습니다.")
            return set()

        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                # 형식: "word : meaning, meaning"
                parts = line.split(' : ', 1)
                if parts:
                    word = parts[0].strip()
                    if word:
                        vocabulary_set.add(word.lower())
        
        st.success(f"{year}년 교육부 기본 어휘 목록 ({len(vocabulary_set)}개) 로드 완료")
    except Exception as e:
        st.error(f"{year}년 교육부 기본 어휘 목록 로드 중 오류 발생: {e}")
    return vocabulary_set

def load_combined_moe_vocabulary() -> dict:
    """2015년과 2022년 교육부 기본 어휘를 모두 로드하여 반환합니다."""
    result = {
        "2015": set(),
        "2022": set(),
        "combined": set()
    }
    
    # 2015년 어휘 로드
    vocab_2015 = load_moe_vocabulary(VOCAB_FILE_PATH_2015, "2015")
    result["2015"] = vocab_2015
    
    # 2022년 어휘 로드  
    vocab_2022 = load_moe_vocabulary(VOCAB_FILE_PATH_2022, "2022")
    result["2022"] = vocab_2022
    
    # 통합 어휘 (합집합)
    result["combined"] = vocab_2015.union(vocab_2022)
    
    if result["combined"]:
        st.info(f"""
**교육부 기본 어휘 로드 완료:**
- 2015년: {len(result['2015'])}개
- 2022년: {len(result['2022'])}개  
- 통합: {len(result['combined'])}개 (중복 제거)
- 공통 어휘: {len(vocab_2015.intersection(vocab_2022))}개
- 2015년 고유: {len(vocab_2015 - vocab_2022)}개
- 2022년 고유: {len(vocab_2022 - vocab_2015)}개
        """)
    
    return result

def get_vocabulary_for_grade(grade_level: str, all_vocabularies: dict) -> set:
    """학년에 따라 적절한 어휘 집합을 반환합니다."""
    if grade_level == "고1":
        # 고1은 2022 개정 교육과정
        return all_vocabularies.get("2022", set())
    elif grade_level in ["고2", "고3"]:
        # 고2, 고3는 2015 개정 교육과정
        return all_vocabularies.get("2015", set())
    else:
        # 기타의 경우 통합 어휘 사용
        return all_vocabularies.get("combined", set())

def analyze_vocabulary_level(text: str, target_vocab: set, all_vocabularies: dict) -> dict:
    """텍스트의 어휘 수준을 분석합니다."""
    import re
    
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    unique_words = set(words)
    
    # 대상 어휘 집합 기준 분석
    target_vocab_words = unique_words.intersection(target_vocab)
    non_target_vocab_words = unique_words - target_vocab
    
    # 2015/2022 각각 기준 분석
    vocab_2015_words = unique_words.intersection(all_vocabularies.get("2015", set()))
    vocab_2022_words = unique_words.intersection(all_vocabularies.get("2022", set()))
    
    return {
        "total_unique_words": len(unique_words),
        "target_vocab_words": len(target_vocab_words),
        "non_target_vocab_words": len(non_target_vocab_words),
        "target_vocab_ratio": len(target_vocab_words) / len(unique_words) if unique_words else 0,
        "vocab_2015_words": len(vocab_2015_words),
        "vocab_2022_words": len(vocab_2022_words),
        "vocab_2015_ratio": len(vocab_2015_words) / len(unique_words) if unique_words else 0,
        "vocab_2022_ratio": len(vocab_2022_words) / len(unique_words) if unique_words else 0,
        "non_target_examples": sorted(list(non_target_vocab_words))[:10]  # 최대 10개 예시
    }

# 모듈 로드 시 어휘 데이터 초기화
MOE_VOCABULARIES = load_combined_moe_vocabulary()

# 하위 호환성을 위한 기본 어휘 집합 (통합 버전)
MOE_VOCABULARY = MOE_VOCABULARIES.get("combined", set())
