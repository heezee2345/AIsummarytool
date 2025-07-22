# ai_services.py
import os
import re
from collections import Counter
import streamlit as st
from openai import OpenAI, APIError

from data_config import CURRICULUM_STANDARDS
from vocabulary_loader import MOE_VOCABULARIES, get_vocabulary_for_grade, analyze_vocabulary_level

# 환경 설정
try:
    OPENAI_KEY = st.secrets["openai"]["api_key"]
except KeyError:
    OPENAI_KEY = ""

OPENAI_OK = bool(OPENAI_KEY)

client = None
if OPENAI_OK:
    try:
        client = OpenAI(api_key=OPENAI_KEY)
    except Exception as e:
        st.error(f"OpenAI 초기화 실패: {e}")
        OPENAI_OK = False

def extract_keywords(text: str, top_n: int = 5) -> list:
    """텍스트에서 주요 키워드 추출 (지시대명사, 문법어휘 제외)"""
    if not text.strip():
        return []
    
    # 제외할 단어들 (지시대명사, 문법어휘, 관사, 전치사 등)
    stopwords = {
        'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
        'this', 'that', 'these', 'those', 'my', 'your', 'his', 'her', 'its', 'our', 'their',
        'a', 'an', 'the', 'and', 'or', 'but', 'so', 'if', 'because', 'when', 'where', 'how', 'why',
        'in', 'on', 'at', 'by', 'for', 'with', 'without', 'to', 'from', 'of', 'about', 'into', 'through',
        'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
        'will', 'would', 'could', 'should', 'may', 'might', 'can', 'must', 'shall',
        'not', 'no', 'yes', 'very', 'more', 'most', 'much', 'many', 'some', 'any', 'all', 'each', 'every',
        'also', 'just', 'only', 'even', 'up', 'down', 'out', 'over', 'under', 'here', 'there', 'where',
        'then', 'now', 'always', 'never', 'often', 'seldom', 'sometimes', 'usually', 'rarely', 'already',
        'still', 'yet', 'away', 'back', 'forth', 'further', 'once', 'twice', 'enough', 'indeed', 'perhaps',
        'possibly', 'probably', 'surely', 'truly', 'actually', 'obviously', 'simply', 'really', 'almost',
        'among', 'amongst', 'around', 'above', 'below', 'between', 'before', 'after', 'along', 'beside',
        'besides', 'inside', 'outside', 'near', 'off', 'past', 'round', 'since', 'until', 'upon', 'within',
        'without', 'across', 'against', 'amongst', 'amid', 'amidst', 'around', 'concerning', 'despite',
        'during', 'except', 'inside', 'like', 'minus', 'outside', 'plus', 'regarding', 'save', 'than',
        'towards', 'unlike', 'versus', 'via', 'whether', 'whilst', 'whom', 'whose', 'though', 'throughout',
        'till', 'together', 'too', 'underneath', 'unless', 'whither', 'yet', 'hence', 'thereby', 'therein',
        'thereof', 'thereto', 'thereupon', 'whereby', 'wherein', 'whereof', 'whereto', 'whereupon', 'whoever',
        'whatever', 'whenever', 'wherever', 'whichever', 'whomever'
    }
    
    # 텍스트를 소문자로 변환하고 단어 추출
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    
    # 불용어 제거 및 길이 3 이상인 단어만 선택
    filtered_words = [word for word in words if word not in stopwords and len(word) >= 3]
    
    # 빈도 계산 후 상위 n개 반환
    word_counts = Counter(filtered_words)
    return [word for word, count in word_counts.most_common(top_n)]

def translate_keywords_to_korean(keywords: list) -> dict:
    """키워드를 한국어로 번역"""
    if not OPENAI_OK or client is None or not keywords:
        return {}
    
    keywords_str = ", ".join(keywords)
    prompt = f"다음 영어 단어들을 한국어로 번역해주세요. 각 단어마다 가장 적절한 의미 하나씩만 제시해주세요:\n{keywords_str}\n\n형식: 영어단어1: 한국어뜻1, 영어단어2: 한국어뜻2, ..."
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=300
        )
        result = response.choices[0].message.content.strip()
        
        # 결과 파싱
        translations = {}
        pairs = result.split(", ")
        for pair in pairs:
            if ":" in pair:
                eng, kor = pair.split(":", 1)
                translations[eng.strip()] = kor.strip()
            elif " - " in pair:
                eng, kor = pair.split(" - ", 1)
                translations[eng.strip()] = kor.strip()
            elif "=" in pair:
                eng, kor = pair.split("=", 1)
                translations[eng.strip()] = kor.strip()
        
        return translations
    except APIError as e:
        st.error(f"OpenAI API 호출 오류 (키워드 번역): {e}")
        return {}
    except Exception as e:
        st.error(f"키워드 번역 중 오류 발생: {e}")
        return {}

def generate_ai_summary(text: str, grade_level: str, subject_type: str) -> str:
    """교육과정별 맞춤 요약문 생성 (2022 개정 + 2015 개정)"""
    if not OPENAI_OK or client is None:
        return "GPT 요약 불가: API 오류"
    if not text.strip():
        return "GPT 요약 불가: 텍스트가 없습니다."
    
    curriculum_key = grade_level
    if grade_level in ["고2", "고3"]:
        curriculum_key = f"{grade_level}_{subject_type}"
    
    curriculum_info = CURRICULUM_STANDARDS.get(curriculum_key)
    
    if not curriculum_info:
        return f"GPT 요약 불가: {grade_level} ({subject_type})에 대한 교육과정 정보가 없습니다."

    curriculum_guide_parts = [
        f"{curriculum_info['curriculum_type']} - "
    ]
    if curriculum_key == "고1":
        curriculum_guide_parts.append(f"{curriculum_info['subject']}\n")
        curriculum_guide_parts.append(f"성취수준: 듣거나 읽은 내용 요약을 정확하게 할 수 있다 (A수준 목표)\n")
    else:
        curriculum_guide_parts.append(f"{subject_type} 과목\n")
        curriculum_guide_parts.append(f"주요 성취기준: {curriculum_info['main_achievement_desc']}\n")

    curriculum_guide_parts.extend([
        f"- 주제: {curriculum_info['subject_range']}",
        f"- 어휘: {curriculum_info['vocabulary_level']} ({curriculum_info['vocabulary_reference']})",
        f"- 구조: {curriculum_info['grammar_complexity']}",
        f"- 내용: {curriculum_info.get('text_familiarity', '핵심 내용 포함')}",
        f"- 표현: {curriculum_info['summary_level_desc']}"
    ])
    
    curriculum_guide = "\n".join(curriculum_guide_parts)

    prompt = f"""한국 고등학교 {grade_level} ({subject_type}) 영어과 교육과정에 따라 다음 텍스트를 정확히 15-20단어로 요약해주세요.

{curriculum_guide}

요약 시, 교육부 {grade_level} 수준에 맞는 어휘와 문법을 사용하고, 해당 학년 성취기준/성취수준에 부합하도록 작성해주세요.

텍스트: {text}

요구사항:
- 정확히 15-20단어
- 완전한 문장 구조
- 핵심 아이디어 포함
- 해당 학년 성취기준/성취수준에 부합
- {curriculum_info['vocabulary_reference']} 어휘 수준 고려"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=100
        )
        return response.choices[0].message.content.strip()
    except APIError as e:
        return f"GPT 요약 실패: OpenAI API 오류: {e}"
    except Exception as e:
        return f"GPT 요약 실패: {e}"

def provide_feedback(user_summary: str, original_text: str, grade_level: str, subject_type: str, all_vocabularies: dict) -> str:
    """교육과정별 + 과목유형별 맞춤 피드백 제공 (2015/2022 어휘 통합 분석)"""
    if not OPENAI_OK or client is None:
        return "피드백 제공 불가: API 오류"
    if not user_summary.strip():
        return "피드백 제공 불가: 요약문이 없습니다."
    
    curriculum_key = grade_level
    if grade_level in ["고2", "고3"]:
        curriculum_key = f"{grade_level}_{subject_type}"
    
    curriculum_info = CURRICULUM_STANDARDS.get(curriculum_key)

    if not curriculum_info:
        return f"피드백 제공 불가: {grade_level} ({subject_type})에 대한 교육과정 정보가 없습니다."

    curriculum_context_parts = [
        f"{curriculum_info['curriculum_type']} - "
    ]
    if curriculum_key == "고1":
        curriculum_context_parts.append(f"{curriculum_info['subject']}\n")
        curriculum_context_parts.append(f"A수준: \"{curriculum_info['achievement_level_desc']['A']}\"\n")
        curriculum_context_parts.append(curriculum_info['assessment_tips'])
    else:
        curriculum_context_parts.append(f"{subject_type} 과목\n")
        curriculum_context_parts.append(f"주요 성취기준: {curriculum_info['main_achievement_desc']}\n")
        if "subjects" in curriculum_info:
            for sub_name, sub_desc in curriculum_info["subjects"].items():
                curriculum_context_parts.append(f"- {sub_name}: {sub_desc}")
        curriculum_context_parts.append(curriculum_info['assessment_tips'])
    
    curriculum_context = "\n".join(curriculum_context_parts)

    # 해당 학년에 맞는 어휘 집합 가져오기
    target_vocab = get_vocabulary_for_grade(grade_level, all_vocabularies)
    
    # 어휘 수준 분석
    vocab_analysis = analyze_vocabulary_level(user_summary, target_vocab, all_vocabularies)
    
    vocab_feedback_info = f"""
**어휘 수준 분석 ({curriculum_info['vocabulary_reference']} 기준):**
- 전체 고유 단어: {vocab_analysis['total_unique_words']}개
- 해당 학년 기준 어휘: {vocab_analysis['target_vocab_words']}개 ({vocab_analysis['target_vocab_ratio']:.1%})
- 기준 외 어휘: {vocab_analysis['non_target_vocab_words']}개
- 2015년 기준 어휘: {vocab_analysis['vocab_2015_words']}개 ({vocab_analysis['vocab_2015_ratio']:.1%})
- 2022년 기준 어휘: {vocab_analysis['vocab_2022_words']}개 ({vocab_analysis['vocab_2022_ratio']:.1%})
"""
    
    if vocab_analysis['non_target_examples']:
        vocab_feedback_info += f"- 기준 외 어휘 예시: {', '.join(vocab_analysis['non_target_examples'][:5])} (최대 5개)"

    prompt = f"""다음은 한국 {grade_level} ({subject_type}) 영어교사가 작성한 요약문입니다. 해당 교육과정 기준에 따라 평가해주세요:

{curriculum_context}
{vocab_feedback_info}

원문: {original_text}

교사 요약문: {user_summary}

다음 항목별로 구체적인 평가와 개선 제안을 해주세요:

1.  **교육과정 부합도**: 해당 학년.과목유형 기준에 얼마나 부합하는가?
2.  **과목 특성 반영**: {subject_type} 과목의 특성이 잘 반영되었는가?
3.  **어휘 수준 적절성**: {grade_level} ({subject_type}) 학습자에게 적절한 어휘인가? ({curriculum_info['vocabulary_reference']} 기준 분석 결과 참고)
4.  **문법 정확성**: 해당 과목 수준에 맞는 문장 구조인가?
5.  **내용 완성도**: 핵심 내용이 교육과정 기준에 맞게 포함되었는가?
6.  **교육적 활용도**: 실제 {subject_type} 수업에서 활용 가능한가?
7.  **길이 준수**: 15-20단어 기준 준수 여부
8.  **어휘 분석**: 2015년/2022년 교육부 기본 어휘 기준 적절성

특목고.자사고와 일반고의 차이, 교육과정 전환기 특성을 고려하여 실용적인 개선 방안을 제시해주세요."""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=1500
        )
        return response.choices[0].message.content.strip()
    except APIError as e:
        return f"피드백 생성 실패: OpenAI API 오류: {e}"
    except Exception as e:
        return f"피드백 생성 실패: {e}"
