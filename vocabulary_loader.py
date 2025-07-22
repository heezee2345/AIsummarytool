# vocabulary_loader.py
import streamlit as st
import os
from pathlib import Path

from data_config import VOCAB_FILE_PATH_2015, VOCAB_FILE_PATH_2022

def load_moe_vocabulary(file_path: str, year: str) -> set:
    """교육부 기본 어휘 목록 파일을 읽어 단어 집합으로 반환합니다."""
    vocabulary_set = set()
    
    try:
        # 파일 경로를 Path 객체로 변환
        file_path = Path(file_path)
        
        if not file_path.exists():
            st.warning(f"교육부 기본 어휘 파일 '{file_path}'을(를) 찾을 수 없습니다.")
            st.info(f"파일 위치 확인: {file_path.absolute()}")
            return set()

        # 파일 크기 확인
        file_size = file_path.stat().st_size
        if file_size == 0:
            st.warning(f"{year}년 어휘 파일이 비어있습니다.")
            return set()

        with open(file_path, 'r', encoding='utf-8') as f:
            line_count = 0
            for line in f:
                line = line.strip()
                if not line:
                    continue
                    
                line_count += 1
                
                # 형식: "word : meaning, meaning"
                if ' : ' in line:
                    parts = line.split(' : ', 1)
                    if len(parts) >= 1:
                        word = parts[0].strip()
                        if word and word.replace('.', '').replace('-', '').isalpha():
                            vocabulary_set.add(word.lower())
                else:
                    # 구분자가 없는 경우 첫 번째 단어만 추출
                    words = line.split()
                    if words:
                        word = words[0].strip()
                        if word and word.replace('.', '').replace('-', '').isalpha():
                            vocabulary_set.add(word.lower())
        
        if vocabulary_set:
            st.success(f"{year}년 교육부 기본 어휘 목록 ({len(vocabulary_set)}개) 로드 완료")
        else:
            st.warning(f"{year}년 어휘 파일에서 유효한 어휘를 찾지 못했습니다. (처리된 줄 수: {line_count})")
            
    except UnicodeDecodeError:
        try:
            # UTF-8이 안 되면 다른 인코딩 시도
            with open(file_path, 'r', encoding='cp949') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    if ' : ' in line:
                        parts = line.split(' : ', 1)
                        if len(parts) >= 1:
                            word = parts[0].strip()
                            if word and word.replace('.', '').replace('-', '').isalpha():
                                vocabulary_set.add(word.lower())
            st.success(f"{year}년 교육부 기본 어휘 목록 ({len(vocabulary_set)}개) 로드 완료 (CP949 인코딩)")
        except Exception as e:
            st.error(f"{year}년 교육부 기본 어휘 목록 로드 중 인코딩 오류: {e}")
            
    except Exception as e:
        st.error(f"{year}년 교육부 기본 어휘 목록 로드 중 오류 발생: {e}")
        st.info(f"파일 경로: {file_path.absolute()}")
        
    return vocabulary_set

def load_combined_moe_vocabulary() -> dict:
    """2015년과 2022년 교육부 기본 어휘를 모두 로드하여 반환합니다."""
    result = {
        "2015": set(),
        "2022": set(),
        "combined": set()
    }
    
    st.info("📚 교육부 기본 어휘 파일 로드 중...")
    
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
**📊 교육부 기본 어휘 로드 완료:**
- **2015년**: {len(result['2015'])}개
- **2022년**: {len(result['2022'])}개  
- **통합**: {len(result['combined'])}개 (중복 제거)
- **공통 어휘**: {len(vocab_2015.intersection(vocab_2022))}개
- **2015년 고유**: {len(vocab_2015 - vocab_2022)}개
- **2022년 고유**: {len(vocab_2022 - vocab_2015)}개
        """)
    else:
        st.error("⚠️ 어휘 파일을 로드하지 못했습니다. 파일 경로와 형식을 확인해주세요.")
        
        # 디버깅 정보 제공
        st.info(f"""
**🔍 디버깅 정보:**
- 2015년 파일 경로: `{VOCAB_FILE_PATH_2015}`
- 2022년 파일 경로: `{VOCAB_FILE_PATH_2022}`
- 현재 작업 디렉토리: `{Path.cwd()}`

**💡 해결 방법:**
1. `data` 폴더가 프로젝트 루트에 있는지 확인
2. 어휘 파일이 올바른 이름으로 `data` 폴더 안에 있는지 확인
3. 파일 내용이 `word : meaning` 형식인지 확인
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
    
    # 대상 어휘 집합이 비어있는 경우 처리
    if not target_vocab:
        st.warning("대상 어휘 집합이 비어있습니다. 어휘 파일을 확인해주세요.")
        return {
            "total_unique_words": len(unique_words),
            "target_vocab_words": 0,
            "non_target_vocab_words": len(unique_words),
            "target_vocab_ratio": 0,
            "vocab_2015_words": 0,
            "vocab_2022_words": 0,
            "vocab_2015_ratio": 0,
            "vocab_2022_ratio": 0,
            "non_target_examples": sorted(list(unique_words))[:10]
        }
    
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

def debug_vocabulary_files():
    """어휘 파일 디버깅을 위한 함수"""
    st.subheader("🔍 어휘 파일 디버깅")
    
    files_info = [
        ("2015년", VOCAB_FILE_PATH_2015),
        ("2022년", VOCAB_FILE_PATH_2022)
    ]
    
    for year, file_path in files_info:
        file_path = Path(file_path)
        
        st.write(f"**{year} 파일:**")
        st.write(f"- 경로: `{file_path}`")
        st.write(f"- 절대 경로: `{file_path.absolute()}`")
        st.write(f"- 존재 여부: {'✅' if file_path.exists() else '❌'}")
        
        if file_path.exists():
            size = file_path.stat().st_size
            st.write(f"- 크기: {size:,} bytes")
            
            # 파일 첫 몇 줄 미리보기
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = [f.readline().strip() for _ in range(5)]
                    lines = [line for line in lines if line]
                    
                st.write("- 첫 5줄 미리보기:")
                for i, line in enumerate(lines, 1):
                    st.code(f"{i}: {line}")
                    
            except Exception as e:
                st.error(f"파일 읽기 오류: {e}")
        else:
            st.error("파일이 존재하지 않습니다!")

# 모듈 로드 시 어휘 데이터 초기화
try:
    MOE_VOCABULARIES = load_combined_moe_vocabulary()
    # 하위 호환성을 위한 기본 어휘 집합 (통합 버전)
    MOE_VOCABULARY = MOE_VOCABULARIES.get("combined", set())
except Exception as e:
    st.error(f"어휘 데이터 초기화 중 오류 발생: {e}")
    MOE_VOCABULARIES = {"2015": set(), "2022": set(), "combined": set()}
    MOE_VOCABULARY = set()