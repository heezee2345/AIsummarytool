# data_config.py
import os
from pathlib import Path

# 프로젝트 루트 디렉토리
PROJECT_ROOT = Path(__file__).parent

# 데이터 디렉토리
DATA_DIR = PROJECT_ROOT / "data"

# 교육부 기본 어휘 파일 경로 (data 폴더 안에 있음)
VOCAB_FILE_PATH_2015 = DATA_DIR / "2015년 교육부 기본 어휘 3000개_전체.txt"
VOCAB_FILE_PATH_2022 = DATA_DIR / "2022년 교육부 기본 어휘 3000개_전체.txt"

# 기타 설정
DEFAULT_ENCODING = "utf-8"
VOCAB_SEPARATOR = " : "

def ensure_data_directory():
    """데이터 디렉토리가 존재하는지 확인하고 없으면 생성합니다."""
    DATA_DIR.mkdir(exist_ok=True)
    return DATA_DIR

def get_vocab_file_paths():
    """어휘 파일 경로들을 반환합니다."""
    return {
        "2015": str(VOCAB_FILE_PATH_2015),
        "2022": str(VOCAB_FILE_PATH_2022)
    }

def check_vocab_files_exist():
    """어휘 파일들이 존재하는지 확인합니다."""
    paths = get_vocab_file_paths()
    status = {}
    
    for year, path in paths.items():
        file_path = Path(path)
        status[year] = {
            "exists": file_path.exists(),
            "path": str(file_path),
            "size": file_path.stat().st_size if file_path.exists() else 0
        }
    
    return status

TAM_SURVEY_QUESTIONS = {
    "인지된_유용성": [
        "이 AI 영어 요약 도구를 사용하면 영어 요약 수업을 더 효과적으로 진행할 수 있을 것이다.",
        "이 도구를 사용하면 학생들의 영어 요약 능력 향상에 도움이 될 것이다.",
        "이 도구는 영어 요약 수업 준비 시간을 단축시켜 줄 것이다.",
        "이 도구를 사용하면 더 질 높은 영어 요약 수업을 할 수 있을 것이다.",
        "전반적으로 이 도구는 영어 요약 교육에 유용할 것이다."
    ],
    "인지된_사용용이성": [
        "이 AI 영어 요약 도구는 사용하기 쉽다.",
        "이 도구의 사용법을 익히는 것은 어렵지 않다.",
        "이 도구를 능숙하게 사용하는 것은 쉬울 것이다.",
        "이 도구와의 상호작용은 명확하고 이해하기 쉽다.",
        "전반적으로 이 도구는 사용하기 편리하다."
    ],
    "자기효능감": [
        "나는 이 AI 영어 요약 도구를 수업에 효과적으로 활용할 수 있다.",
        "나는 이 도구의 기능들을 잘 이해하고 활용할 수 있다.",
        "나는 이 도구를 사용하여 학생들에게 적절한 피드백을 제공할 수 있다.",
        "나는 이 도구를 교육과정과 연계하여 활용할 수 있다.",
        "나는 이 도구 사용에 대해 자신감이 있다."
    ],
    "활용의도": [
        "나는 앞으로 이 AI 영어 요약 도구를 수업에서 사용할 의향이 있다.",
        "나는 이 도구를 정기적으로 사용할 계획이 있다.",
        "나는 다른 동료 교사들에게 이 도구를 추천하고 싶다.",
        "나는 이 도구를 내 수업 방식에 통합하여 사용하고 싶다.",
        "기회가 된다면 이 도구를 지속적으로 활용하겠다."
    ],
    "추가문항": [
        "이 도구가 우리 학교 교육과정에 적합하다고 생각한다.",
        "이 도구는 학생들의 학습 동기를 향상시킬 것이다.",
        "이 도구는 교사의 업무 효율성을 높여줄 것이다.",
        "이 도구의 AI 피드백은 신뢰할 만하다.",
        "이런 유형의 AI 도구가 교육현장에서 더 활용되어야 한다."
    ]
}

CURRICULUM_STANDARDS = {
    "고1": {
        "curriculum_type": "2022 개정 교육과정",
        "curriculum_year": "2022",
        "subject": "공통영어1/공통영어2",
        "achievement_level_desc": {
            "A": "듣거나 읽은 내용 요약을 정확하게 할 수 있다",
            "B": "듣거나 읽은 내용 요약을 비교적 정확하게 할 수 있다",
            "C": "듣거나 읽은 내용 요약을 대략적으로 할 수 있다"
        },
        "subject_range": "친숙한 일반적 주제, 우리 문화와 타 문화",
        "summary_level_desc": "다양한 전략을 활용하여 정확하게 요약",
        "key_features": ["친숙한", "일반적", "문화간 맥락", "정확하게"],
        "vocabulary_level": "실생활에서 자주 사용되는 어휘",
        "vocabulary_reference": "2022년 교육부 기본 어휘",
        "grammar_complexity": "다양한 구조의 문장",
        "text_familiarity": "일상생활, 기본적 지식, 문화 예술",
        "assessment_tips": """
**2022 개정 교육과정 평가 기준 (A~E 5단계):**
- A수준: 정확하게 요약 + 다양하고 적절한 어휘 및 언어 형식 활용, 적절한 쓰기 전략 다양하게 적용
- B수준: 비교적 정확하게 요약
- C수준: 대략적으로 요약  
- 표현: 다양한 구조의 문장, 정확한 언어 사용
- 어휘: 2022년 교육부 기본 어휘 3000개 기준
"""
    },
    "고2_일반선택+진로선택": {
        "curriculum_type": "2015 개정 교육과정",
        "curriculum_year": "2015",
        "subjects": {
            "영어I": "[12영I04-02] 친숙한 일반적 주제에 관하여 듣거나 읽고 간단하게 요약할 수 있다.",
            "영어II": "[12영II04-02] 비교적 다양한 주제에 관하여 듣거나 읽고 간단하게 요약할 수 있다.",
            "영어독해와작문": "[12영독04-02] 일반적 주제에 관하여 듣거나 읽고 주요 내용을 요약하여 쓸 수 있다."
        },
        "main_achievement_desc": "친숙한~비교적 다양한 주제, 간단하게 요약",
        "subject_range": "친숙한~비교적 다양한 주제",
        "summary_level_desc": "간단하게 요약",
        "key_features": ["친숙한", "일반적", "문화간 맥락", "간단하게"],
        "vocabulary_level": "기본~중급 어휘",
        "vocabulary_reference": "2015년 교육부 기본 어휘",
        "grammar_complexity": "단순문~복문 구조",
        "text_familiarity": "일반적 주제 중심",
        "assessment_tips": """
**평가 기준 제안:**
- 내용: 친숙한~비교적 다양한 주제 수준의 핵심 아이디어 포함
- 정확성: 단순문~복문 구조 적절히 활용
- 어휘: 기본~중급 수준 어휘 적절성 (2015년 교육부 기본 어휘 3000개 기준)
- 표현: 간단하지만 논리적 연결
"""
    },
    "고2_전문교과": {
        "curriculum_type": "2015 개정 교육과정",
        "curriculum_year": "2015",
        "subjects": {
            "심화영어I": "[12심영I04-02] 다양한 장르의 글을 읽고 요약하여 쓴다.",
            "심화영어II": "[12심영II04-02] 다양한 장르의 글을 읽고 조리 있게 요약하여 쓴다.",
            "심화영어작문I": "[12심작I04-03] 일반적인 주제의 글을 읽고 주요 내용을 요약하여 쓴다."
        },
        "main_achievement_desc": "다양한 장르, 조리있게 요약",
        "subject_range": "다양한 주제/장르",
        "summary_level_desc": "조리있게 요약",
        "key_features": ["다양한", "조리있게", "전문적"],
        "vocabulary_level": "고급 어휘, 학술적 표현",
        "vocabulary_reference": "2015년 교육부 기본 어휘 + 고급 어휘",
        "grammar_complexity": "복합문, 고급 문법 구조",
        "text_familiarity": "학술적, 전문적 텍스트",
        "assessment_tips": """
**평가 기준 제안:**
- 내용: 다양한 주제/장르의 심화 텍스트의 핵심 아이디어 포함
- 정확성: 복합문, 고급 문법 구조 활용
- 어휘: 고급 어휘, 학술적 표현 사용 적절성 (2015년 교육부 기본 어휘 기반)
- 표현: 조리있고 체계적인 구성
"""
    },
    "고3_일반선택+진로선택": {
        "curriculum_type": "2015 개정 교육과정",
        "curriculum_year": "2015",
        "subjects": {
            "영어I": "[12영I04-02] 친숙한 일반적 주제에 관하여 듣거나 읽고 간단하게 요약할 수 있다.",
            "영어II": "[12영II04-02] 비교적 다양한 주제에 관하여 듣거나 읽고 간단하게 요약할 수 있다.",
            "영어독해와작문": "[12영독04-02] 일반적 주제에 관하여 듣거나 읽고 주요 내용을 요약하여 쓸 수 있다."
        },
        "main_achievement_desc": "친숙한~비교적 다양한 주제, 간단하게 요약",
        "subject_range": "친숙한~비교적 다양한 주제",
        "summary_level_desc": "간단하게 요약",
        "key_features": ["친숙한", "일반적", "문화간 맥락", "간단하게"],
        "vocabulary_level": "기본~중급 어휘",
        "vocabulary_reference": "2015년 교육부 기본 어휘",
        "grammar_complexity": "단순문~복문 구조",
        "text_familiarity": "수능 출제 경향 반영",
        "assessment_tips": """
**평가 기준 제안:**
- 내용: 친숙한~비교적 다양한 주제 수준의 핵심 아이디어 포함 (수능 출제 경향 반영)
- 정확성: 단순문~복문 구조 적절히 활용
- 어휘: 기본~중급 수준 어휘 (수능 연계 어휘 중심, 2015년 교육부 기본 어휘 기준) 적절성
- 표현: 간단하지만 정확한 요약
"""
    },
    "고3_전문교과": {
        "curriculum_type": "2015 개정 교육과정",
        "curriculum_year": "2015",
        "subjects": {
            "심화영어I": "[12심영I04-02] 다양한 장르의 글을 읽고 요약하여 쓴다.",
            "심화영어II": "[12심영II04-02] 다양한 장르의 글을 읽고 조리 있게 요약하여 쓴다.",
            "심화영어작문II": "[12심작II04-03] 다양한 주제의 글을 읽고 주요 내용을 요약하여 쓴다."
        },
        "main_achievement_desc": "다양한 주제/장르, 조리있게 요약",
        "subject_range": "다양한 주제/장르",
        "summary_level_desc": "조리있게 요약",
        "key_features": ["다양한", "조리있게", "심화학습"],
        "vocabulary_level": "고급 어휘, 학술적 표현",
        "vocabulary_reference": "2015년 교육부 기본 어휘 + 고급 어휘",
        "grammar_complexity": "복합문, 고급 문법 구조",
        "text_familiarity": "대학 수준 텍스트",
        "assessment_tips": """
**평가 기준 제안:**
- 내용: 다양한 주제/장르의 심화 텍스트의 핵심 아이디어 포함
- 정확성: 복합문, 최고급 문법 구조 활용
- 어휘: 대학 수준 고급 어휘, 학술적 표현 사용 적절성 (2015년 교육부 기본 어휘 기반)
- 표현: 대학 진학 대비 수준의 조리있고 체계적인 구성
"""
    }
}

WRITING_GUIDELINES = {
    "고1": {
        "curriculum": "2022 개정 교육과정",
        "curriculum_year": "2022",
        "length_target": "15-20 단어 (정확하고 명료하게)",
        "sentence_structure": "다양한 구조의 문장 활용",
        "vocabulary_focus": "실생활 친숙 어휘 중심",
        "vocabulary_reference": "2022년 교육부 기본 어휘",
        "content_focus": "친숙한 주제의 핵심 내용과 문화적 맥락",
        "level_descriptor": "A~E 성취수준 기반 평가"
    },
    "고2": {
        "curriculum": "2015 개정 교육과정",
        "curriculum_year": "2015",
        "length_target": "15-20 단어 (논리적 연결)",
        "sentence_structure": "연결어를 활용한 복문 구조 가능",
        "vocabulary_focus": "다양한 주제 관련 어휘 확장",
        "vocabulary_reference": "2015년 교육부 기본 어휘",
        "content_focus": "주제 확장과 세부 정보 통합",
        "level_descriptor": "성취기준 달성 여부 평가"
    },
    "고3": {
        "curriculum": "2015 개정 교육과정",
        "curriculum_year": "2015",
        "length_target": "15-20 단어 (조리있고 정교함)",
        "sentence_structure": "고급 문법과 복합 구조 활용",
        "vocabulary_focus": "학술적, 전문적 어휘 사용",
        "vocabulary_reference": "2015년 교육부 기본 어휘",
        "content_focus": "다양한 장르의 주요 논점 종합",
        "level_descriptor": "성취기준 달성 여부 평가"
    }
}

# 어휘 파일 경로 설정
VOCAB_FILE_PATH_2015 = "2015년 교육부 기본 어휘 3000개_전체.txt"
VOCAB_FILE_PATH_2022 = "2022년 교육부 기본 어휘 3000개_전체.txt"

# 하위 호환성을 위한 기본 경로 (2022년 기준)
VOCAB_FILE_PATH = VOCAB_FILE_PATH_2022
