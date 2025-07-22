# main_app.py
import datetime
import streamlit as st
st.set_page_config(page_title="AI Summary Tool", layout="wide")

# Import functions and data from other modules
from data_config import TAM_SURVEY_QUESTIONS, CURRICULUM_STANDARDS
from vocabulary_loader import MOE_VOCABULARIES, get_vocabulary_for_grade, analyze_vocabulary_level
from ai_services import extract_keywords, translate_keywords_to_korean, generate_ai_summary, provide_feedback, OPENAI_OK
from utils import count_words

# Streamlit 앱 설정
st.set_page_config(
    page_title="AI English Summary Assistant for Teachers", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 세션 상태 초기화
if "stage" not in st.session_state:
    st.session_state.update({
        "stage": "input",
        "teacher_info": {"grade": "", "school_type": "", "experience": ""},
        "original_text": "",
        "source_type": "",
        "year": "",
        "grade_level": "",
        "subject_type": "",
        "item_info": "",
        "keywords": [],
        "keyword_translations": {},
        "user_summary": "",
        "ai_summary": "",
        "feedback": "",
        "vocab_analysis": {},
        "survey_submitted": False
    })

def display_tam_survey():
    """TAM 설문조사 표시 및 수집"""
    st.markdown("---")
    st.subheader("연구 참여: TAM 설문조사")
    st.markdown("**도구 체험이 완료되었습니다. 연구 참여를 위해 간단한 설문에 응답해주세요.** (약 3분 소요)")
    
    with st.form("tam_survey"):
        st.markdown("### 1. 인지된 유용성 (Perceived Usefulness)")
        st.caption("이 AI 도구가 영어 교육에 얼마나 도움이 될 것 같은지 평가해주세요")
        
        usefulness_scores = {}
        for i, question in enumerate(TAM_SURVEY_QUESTIONS["인지된_유용성"]):
            usefulness_scores[f"PU_{i+1}"] = st.select_slider(
                f"PU{i+1}. {question}",
                options=[1, 2, 3, 4, 5],
                format_func=lambda x: ["전혀 그렇지 않다", "그렇지 않다", "보통이다", "그렇다", "매우 그렇다"][x-1],
                value=3,
                key=f"pu_{i+1}"
            )
        
        st.markdown("### 2. 인지된 사용용이성 (Perceived Ease of Use)")  
        st.caption("이 AI 도구가 얼마나 사용하기 쉬운지 평가해주세요")
        
        ease_scores = {}
        for i, question in enumerate(TAM_SURVEY_QUESTIONS["인지된_사용용이성"]):
            ease_scores[f"PEOU_{i+1}"] = st.select_slider(
                f"PEOU{i+1}. {question}",
                options=[1, 2, 3, 4, 5],
                format_func=lambda x: ["전혀 그렇지 않다", "그렇지 않다", "보통이다", "그렇다", "매우 그렇다"][x-1],
                value=3,
                key=f"peou_{i+1}"
            )
        
        st.markdown("### 3. 자기효능감 (Self-Efficacy)")
        st.caption("이 AI 도구를 교육현장에서 효과적으로 활용할 수 있는 자신감을 평가해주세요")
        
        efficacy_scores = {}
        for i, question in enumerate(TAM_SURVEY_QUESTIONS["자기효능감"]):
            efficacy_scores[f"SE_{i+1}"] = st.select_slider(
                f"SE{i+1}. {question}",
                options=[1, 2, 3, 4, 5],
                format_func=lambda x: ["전혀 그렇지 않다", "그렇지 않다", "보통이다", "그렇다", "매우 그렇다"][x-1],
                value=3,
                key=f"se_{i+1}"
            )
        
        st.markdown("### 4. 활용의도 (Behavioral Intention)")
        st.caption("향후 이 AI 도구를 실제로 활용할 의향을 평가해주세요")
        
        intention_scores = {}
        for i, question in enumerate(TAM_SURVEY_QUESTIONS["활용의도"]):
            intention_scores[f"BI_{i+1}"] = st.select_slider(
                f"BI{i+1}. {question}",
                options=[1, 2, 3, 4, 5],
                format_func=lambda x: ["전혀 그렇지 않다", "그렇지 않다", "보통이다", "그렇다", "매우 그렇다"][x-1],
                value=3,
                key=f"bi_{i+1}"
            )
        
        st.markdown("### 5. 추가 문항")
        st.caption("AI 교육 도구에 대한 전반적인 인식을 평가해주세요")
        
        additional_scores = {}
        for i, question in enumerate(TAM_SURVEY_QUESTIONS["추가문항"]):
            additional_scores[f"AD_{i+1}"] = st.select_slider(
                f"AD{i+1}. {question}",
                options=[1, 2, 3, 4, 5],
                format_func=lambda x: ["전혀 그렇지 않다", "그렇지 않다", "보통이다", "그렇다", "매우 그렇다"][x-1],
                value=3,
                key=f"ad_{i+1}"
            )
        
        # 주관식 피드백
        st.markdown("### 6. 자유 응답")
        feedback_text = st.text_area(
            "이 AI 도구에 대한 추가 의견이나 개선사항이 있다면 자유롭게 작성해주세요. (선택사항)",
            height=100,
            key="feedback_text"
        )
        
        # 연구 참여 동의
        research_consent = st.checkbox(
            "본 설문 응답이 연구 목적으로 사용되는 것에 동의합니다. (개인정보는 익명 처리됩니다)",
            key="research_consent"
        )
        
        # 제출 버튼
        submitted = st.form_submit_button("설문 제출하기", type="primary", use_container_width=True)
        
        if submitted:
            if not research_consent:
                st.error("연구 참여 동의가 필요합니다.")
            else:
                # 설문 데이터 저장
                survey_data = {
                    "timestamp": datetime.datetime.now().isoformat(),
                    "teacher_info": st.session_state.get("teacher_info", {}),
                    "tool_usage": {
                        "grade_level": st.session_state.get("grade_level", ""),
                        "subject_type": st.session_state.get("subject_type", ""),
                        "source_type": st.session_state.get("source_type", ""),
                        "completed_summary": bool(st.session_state.get("user_summary", "")),
                        "received_feedback": bool(st.session_state.get("feedback", "")),
                        "vocab_analysis_completed": bool(st.session_state.get("vocab_analysis", {}))
                    },
                    "tam_scores": {
                        **usefulness_scores,
                        **ease_scores, 
                        **efficacy_scores,
                        **intention_scores,
                        **additional_scores
                    },
                    "feedback_text": feedback_text
                }
                
                # 세션에 저장 (실제로는 DB나 파일에 저장)
                st.session_state.survey_submitted = True
                st.session_state.survey_data = survey_data
                
                st.success("설문이 성공적으로 제출되었습니다! 연구 참여에 감사드립니다.")
                
                # 결과 요약 표시
                st.markdown("### 당신의 응답 요약")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    avg_pu = sum(usefulness_scores.values()) / len(usefulness_scores)
                    st.metric("유용성", f"{avg_pu:.1f}/5.0")
                
                with col2:
                    avg_peou = sum(ease_scores.values()) / len(ease_scores)
                    st.metric("사용용이성", f"{avg_peou:.1f}/5.0")
                
                with col3:
                    avg_se = sum(efficacy_scores.values()) / len(efficacy_scores)
                    st.metric("자기효능감", f"{avg_se:.1f}/5.0")
                
                with col4:
                    avg_bi = sum(intention_scores.values()) / len(intention_scores)
                    st.metric("활용의도", f"{avg_bi:.1f}/5.0")


# Main application content
st.title("AI 영어 요약 지원 도구 (중.고등학교 영어교사용)")
st.markdown("**고등학교 영어 지문을 15-20단어로 효과적으로 요약하는 AI 도구입니다**")
st.markdown("*수능, 내신, 모의고사 지문 요약에 최적화된 교사 전용 도구*")

if not OPENAI_OK:
    st.warning("OpenAI API 키가 설정되지 않았거나 문제가 있습니다. 일부 기능이 제한됩니다.")
if not MOE_VOCABULARIES.get("combined"):
    st.warning("교육부 기본 어휘 목록을 로드하지 못하여 어휘 수준 평가 기능이 제한될 수 있습니다.")

# 1단계: 교사 정보 및 텍스트 입력
if st.session_state.stage == "input":
    st.subheader("1단계: 교사 정보 및 영어 지문 입력")
    
    # 교사 기본 정보 (연구용)
    st.markdown("**교사 정보 (연구 참여용)**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        grade_taught = st.selectbox(
            "담당 학년",
            ["", "고1", "고2", "고3", "고1-2", "고2-3", "고1-3"],
            key="grade_select",
            help="현재 주로 가르치시는 학년을 선택해주세요",
            index=["", "고1", "고2", "고3", "고1-2", "고2-3", "고1-3"].index(st.session_state.teacher_info["grade"]) if st.session_state.teacher_info["grade"] else 0
        )
    
    with col2:
        school_type = st.selectbox(
            "학교 유형",
            ["", "일반고", "특목고", "특성화고", "자사고", "중학교", "기타"],
            key="school_type_select",
            index=["", "일반고", "특목고", "특성화고", "자사고", "중학교", "기타"].index(st.session_state.teacher_info["school_type"]) if st.session_state.teacher_info["school_type"] else 0
        )
    
    with col3:
        teaching_experience = st.selectbox(
            "교직 경력",
            ["", "5년 미만", "5-10년", "11-15년", "16-20년", "20년 이상"],
            key="experience_select",
            index=["", "5년 미만", "5-10년", "11-15년", "16-20년", "20년 이상"].index(st.session_state.teacher_info["experience"]) if st.session_state.teacher_info["experience"] else 0
        )
    
    st.markdown("---")
    
    # 텍스트 입력
    st.markdown("**영어 지문 입력**")
    original_text = st.text_area(
        "요약하고 싶은 영어 텍스트를 입력하세요",
        value=st.session_state.original_text,
        height=200,
        key="text_input",
        help="수능, 모의고사, 교과서 지문 등을 입력해주세요"
    )
    
    # 출처 정보
    st.markdown("**지문 출처 정보**")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        source_type = st.selectbox(
            "출처 유형",
            ["", "수능 기출", "모의고사", "EBS 교재", "교과서", "사설 문제집", "기타"],
            key="source_select",
            index=["", "수능 기출", "모의고사", "EBS 교재", "교과서", "사설 문제집", "기타"].index(st.session_state.source_type) if st.session_state.source_type else 0
        )
    
    with col2:
        year = st.selectbox(
            "연도",
            ["", "2025", "2024", "2023", "2022", "2021", "2020", "2019", "그 이전"],
            key="year_select",
            index=["", "2025", "2024", "2023", "2022", "2021", "2020", "2019", "그 이전"].index(st.session_state.year) if st.session_state.year else 0
        )
    
    with col3:
        grade_level = st.selectbox(
            "학년 수준",
            ["", "고1", "고2", "고3"],
            key="grade_level_select",
            help="고1: 2022 개정 교육과정 / 고2,고3: 2015 개정 교육과정",
            index=["", "고1", "고2", "고3"].index(st.session_state.grade_level) if st.session_state.grade_level else 0
        )
    
    with col4:
        subject_type = st.selectbox(
            "과목 유형",
            ["", "일반선택+진로선택", "전문교과"],
            key="subject_type_select",
            help="일반선택+진로선택: 대부분 학교 개설 / 전문교과: 특목고.자사고 중심",
            index=["", "일반선택+진로선택", "전문교과"].index(st.session_state.subject_type) if st.session_state.subject_type else 0
        )
    
    item_info = st.text_input(
        "상세 정보 (선택사항)",
        value=st.session_state.item_info,
        key="item_input",
        help="예: 6월 모의고사 22번, 수능완성 유형편 3강, 천재교육 고2 5단원 등"
    )
    
    st.markdown("---")
    
    # 다음 단계 버튼
    if st.button("다음 단계: 요약 작성하기", type="primary", use_container_width=True):
        if not grade_taught or not school_type or not teaching_experience:
            st.error("교사 정보를 모두 입력해주세요. (연구 참여를 위해 필요합니다)")
        elif not original_text.strip():
            st.error("영어 지문을 입력해주세요.")
        elif not source_type or not grade_level or not subject_type:
            st.error("출처 유형, 학년 수준, 과목 유형을 모두 선택해주세요.")
        else:
            st.session_state.teacher_info = {
                "grade": grade_taught,
                "school_type": school_type,
                "experience": teaching_experience
            }
            
            st.session_state.original_text = original_text
            st.session_state.source_type = source_type
            st.session_state.year = year
            st.session_state.grade_level = grade_level
            st.session_state.subject_type = subject_type
            st.session_state.item_info = item_info
            
            with st.spinner("지문을 분석하고 주요 키워드를 추출하는 중입니다..."):
                keywords = extract_keywords(original_text, 5)
                keyword_translations = translate_keywords_to_korean(keywords) if keywords else {}
                
                st.session_state.keywords = keywords
                st.session_state.keyword_translations = keyword_translations
            
            st.session_state.stage = "summary"
            st.rerun()

# 2단계: 요약 작성
elif st.session_state.stage == "summary":
    st.subheader("2단계: 요약문 작성")
    
    with st.expander("지문 및 출처 정보 보기", expanded=False):
        st.markdown(f"**교사 정보:** {st.session_state.teacher_info['grade']} | {st.session_state.teacher_info['school_type']} | 경력 {st.session_state.teacher_info['experience']}")
        
        # 적용 교육과정 표시
        curriculum_year = "2022" if st.session_state.grade_level == "고1" else "2015"
        st.markdown(f"**적용 교육과정:** {curriculum_year} 개정 교육과정 ({st.session_state.grade_level})")
        
        st.markdown(f"**출처:** {st.session_state.source_type}" + 
                   (f" ({st.session_state.year})" if st.session_state.year else "") +
                   f" | 수준: {st.session_state.grade_level}" +
                   f" | 과목: {st.session_state.subject_type}" +
                   (f" | {st.session_state.item_info}" if st.session_state.item_info else ""))
        st.markdown("**지문:**")
        st.info(st.session_state.original_text)
    
    if st.session_state.keywords:
        st.markdown("**주요 키워드**")
        keyword_display = []
        for keyword in st.session_state.keywords:
            korean = st.session_state.keyword_translations.get(keyword, "")
            if korean:
                keyword_display.append(f"**{keyword}** ({korean})")
            else:
                keyword_display.append(f"**{keyword}**")
        
        st.markdown(" | ".join(keyword_display))
        st.markdown("---")
    
    st.markdown("**요약문 작성 (15-20단어)**")
    user_summary = st.text_area(
        "영어로 요약문을 작성해주세요",
        value=st.session_state.user_summary,
        height=100,
        key="summary_input",
        help="핵심 내용을 15-20단어로 간결하게 요약해주세요"
    )
    
    word_count = count_words(user_summary)
    if word_count == 0:
        st.caption("단어 수: 0")
    elif 15 <= word_count <= 20:
        st.success(f"단어 수: {word_count} (적절)")
    else:
        st.warning(f"단어 수: {word_count} (15-20단어 권장)")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("이전 단계로", use_container_width=True):
            st.session_state.stage = "input"
            st.rerun()
    
    with col2:
        if st.button("피드백 받기", type="primary", use_container_width=True):
            if not user_summary.strip():
                st.error("요약문을 작성해주세요.")
            else:
                st.session_state.user_summary = user_summary
                
                with st.spinner("AI 피드백과 모범 요약을 생성하는 중입니다..."):
                    ai_summary = generate_ai_summary(st.session_state.original_text, st.session_state.grade_level, st.session_state.subject_type)
                    st.session_state.ai_summary = ai_summary
                    
                    # 어휘 분석 수행
                    target_vocab = get_vocabulary_for_grade(st.session_state.grade_level, MOE_VOCABULARIES)
                    vocab_analysis = analyze_vocabulary_level(user_summary, target_vocab, MOE_VOCABULARIES)
                    st.session_state.vocab_analysis = vocab_analysis
                    
                    feedback = provide_feedback(user_summary, st.session_state.original_text, st.session_state.grade_level, st.session_state.subject_type, MOE_VOCABULARIES)
                    st.session_state.feedback = feedback
                
                st.rerun()
    
    if st.session_state.feedback:
        st.markdown("---")
        st.subheader("AI 피드백 및 개선 제안")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**당신의 요약문**")
            st.info(st.session_state.user_summary)
            
            # 어휘 분석 결과 표시
            if st.session_state.vocab_analysis:
                analysis = st.session_state.vocab_analysis
                curriculum_year = "2022" if st.session_state.grade_level == "고1" else "2015"
                
                st.markdown(f"**어휘 수준 분석 ({curriculum_year}년 교육부 기본 어휘 기준)**")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("전체 고유 단어", f"{analysis['total_unique_words']}개")
                    st.metric("해당 학년 기준", f"{analysis['target_vocab_words']}개")
                with col_b:
                    st.metric("기준 부합률", f"{analysis['target_vocab_ratio']:.0%}")
                    st.metric("기준 외 어휘", f"{analysis['non_target_vocab_words']}개")
                
                # 2015/2022 비교
                st.markdown("**교육과정별 비교:**")
                col_15, col_22 = st.columns(2)
                with col_15:
                    st.caption(f"2015년 기준: {analysis['vocab_2015_words']}개 ({analysis['vocab_2015_ratio']:.0%})")
                with col_22:
                    st.caption(f"2022년 기준: {analysis['vocab_2022_words']}개 ({analysis['vocab_2022_ratio']:.0%})")
                
                if analysis['non_target_examples']:
                    with st.expander("기준 외 어휘 예시"):
                        st.write(", ".join(analysis['non_target_examples']))
            
            st.markdown("**AI 피드백**")
            st.markdown(st.session_state.feedback)
        
        with col2:
            st.markdown("**AI 모범 요약 (참고용)**")
            st.success(st.session_state.ai_summary)
            ai_word_count = count_words(st.session_state.ai_summary)
            st.caption(f"단어 수: {ai_word_count}")
            curriculum_year = "2022" if st.session_state.grade_level == "고1" else "2015"
            st.caption(f"수준: {st.session_state.grade_level} ({st.session_state.subject_type}) 맞춤")
            st.caption(f"기준: {curriculum_year} 개정 교육과정")
        
        st.markdown("---")
        st.markdown("**교육과정 기준 활용 팁**")
        
        current_curriculum_key = st.session_state.grade_level
        if st.session_state.grade_level in ["고2", "고3"]:
            current_curriculum_key = f"{st.session_state.grade_level}_{st.session_state.subject_type}"

        if current_curriculum_key in CURRICULUM_STANDARDS:
            standard = CURRICULUM_STANDARDS[current_curriculum_key]
            
            st.info(f"""
**{st.session_state.grade_level} ({st.session_state.subject_type}) {standard['curriculum_type']}:**
주요 성취기준: {standard.get('main_achievement_desc', '정보 없음')}
어휘 기준: {standard.get('vocabulary_reference', '교육부 기본 어휘')}
{'과목별 성취기준:' if 'subjects' in standard else ''}
{chr(10).join([f"- {s_name}: {s_desc}" for s_name, s_desc in standard.get('subjects', {}).items()])}

**수업 활용 방안:**
- {standard['subject_range']} 지문으로 요약 연습
- "{standard['summary_level_desc']}" 수준 달성을 위한 단계별 지도
- {standard['vocabulary_level']} 중심의 어휘 지도 연계
- {standard.get('text_familiarity', '다양한 텍스트')} 다루기
{standard.get('assessment_tips', '')}
            """)
        else:
            st.info(f"""
**선택된 학년 및 과목 유형에 대한 상세 교육과정 기준을 불러올 수 없습니다.**
**일반적인 수업 활용 방안:**
- 학생들에게 같은 지문으로 요약 연습 과제 제시
- 모범 답안과 학생 답안 비교 분석 활동
- 15-20단어 제한의 교육적 효과 설명  
- 핵심 키워드 중심의 요약 전략 지도

**평가 기준 제안:**
- 내용: 핵심 아이디어 포함 여부
- 정확성: 문법 및 어휘 사용의 정확성
- 간결성: 15-20단어 제한 준수
- 완성도: 완전한 문장으로 구성
- 어휘: 해당 학년 교육부 기본 어휘 수준 적절성
            """)
        
        st.markdown("---")
        st.markdown("**요약문 수정하기**")
        
        revised_summary = st.text_area(
            "피드백을 참고하여 요약문을 수정해보세요",
            value=st.session_state.user_summary,
            height=100,
            key="revised_input"
        )
        
        revised_word_count = count_words(revised_summary)
        if revised_word_count == 0:
            st.caption("단어 수: 0")
        elif 15 <= revised_word_count <= 20:
            st.success(f"단어 수: {revised_word_count} (적절)")
        else:
            st.warning(f"단어 수: {revised_word_count} (15-20단어 권장)")
        
        # 수정된 요약문에 대한 실시간 어휘 분석
        if revised_summary.strip() and revised_summary != st.session_state.user_summary:
            target_vocab = get_vocabulary_for_grade(st.session_state.grade_level, MOE_VOCABULARIES)
            revised_analysis = analyze_vocabulary_level(revised_summary, target_vocab, MOE_VOCABULARIES)
            
            st.markdown("**수정된 요약문 어휘 분석:**")
            col_r1, col_r2 = st.columns(2)
            with col_r1:
                st.caption(f"기준 부합률: {revised_analysis['target_vocab_ratio']:.0%}")
            with col_r2:
                st.caption(f"기준 외 어휘: {revised_analysis['non_target_vocab_words']}개")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("처음부터 다시", use_container_width=True):
                st.session_state.update({
                    "stage": "input",
                    "teacher_info": {"grade": "", "school_type": "", "experience": ""},
                    "original_text": "",
                    "source_type": "",
                    "year": "",
                    "grade_level": "",
                    "subject_type": "",
                    "item_info": "",
                    "keywords": [],
                    "keyword_translations": {},
                    "user_summary": "",
                    "ai_summary": "",
                    "feedback": "",
                    "vocab_analysis": {},
                    "survey_submitted": False
                })
                st.rerun()
        
        with col2:
            if st.button("새 지문으로", use_container_width=True):
                st.session_state.update({
                    "stage": "input",
                    "original_text": "",
                    "source_type": "",
                    "year": "",
                    "grade_level": "",
                    "subject_type": "",
                    "item_info": "",
                    "keywords": [],
                    "keyword_translations": {},
                    "user_summary": "",
                    "ai_summary": "",
                    "feedback": "",
                    "vocab_analysis": {},
                    "survey_submitted": False
                })
                st.rerun()
        
        with col3:
            if not st.session_state.survey_submitted:
                if st.button("TAM 설문조사 시작하기", type="secondary", use_container_width=True):
                    st.session_state.stage = "survey"
                    st.rerun()

# 3단계: TAM 설문조사
elif st.session_state.stage == "survey":
    display_tam_survey()
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("요약/피드백으로 돌아가기", use_container_width=True):
            st.session_state.stage = "summary"
            st.rerun()
    with col2:
        if st.button("새로운 요약 시작하기", use_container_width=True):
            st.session_state.update({
                "stage": "input",
                "original_text": "",
                "source_type": "",
                "year": "",
                "grade_level": "",
                "subject_type": "",
                "item_info": "",
                "keywords": [],
                "keyword_translations": {},
                "user_summary": "",
                "ai_summary": "",
                "feedback": "",
                "vocab_analysis": {},
                "survey_submitted": False
            })
            st.rerun()

# 사이드바 정보
with st.sidebar:
    st.markdown("### 대상")
    st.markdown("중.고등학교 영어교사 전용")
    st.markdown("(특히 고1~고3 담당 교사)")
    
    st.markdown("### 사용 방법")
    st.markdown("""
    1. **교사 정보**: 담당학년, 학교유형, 교직경력 입력
    2. **지문 입력**: 영어 지문과 상세한 출처 정보 입력  
    3. **키워드 확인**: 자동 추출된 주요 키워드와 한국어 번역
    4. **요약 작성**: 15-20단어로 핵심 내용 요약
    5. **AI 피드백**: 교육과정 맞춤 피드백 및 수업 활용 팁 (2015/2022 어휘 수준 분석 포함)
    """)
    
    st.markdown("### 요약 작성 가이드")
    st.markdown("""
    **고등학교 영어 요약의 핵심:**
    - 주제문(Topic sentence) 중심으로
    - 핵심 논점만 간결하게
    - 완전한 문장 구조 유지
    - 학년 수준에 맞는 어휘 사용
    - 수능/내신 출제 경향 반영
    """)
    
    st.markdown("### 교육과정 연계 효과")
    st.markdown("""
    - **성취기준 완전 준수**: 2015/2022 개정 교육과정 정확 반영
    - **단계적 수준 향상**: 고1.고2.고3 체계적 발전
    - **수업-평가 연계**: 실제 수업에서 바로 활용 가능
    - **교육과정-수능 연계**: 수능 출제 경향과 일치
    - **어휘 수준 맞춤**: 2015/2022 교육부 공식 어휘 목록 기준
    """)
    
    st.markdown("### 시스템 상태")
    if OPENAI_OK:
        st.success("AI 기능 정상 작동")
    else:
        st.error("AI 기능 제한")
    
    if MOE_VOCABULARIES.get("combined"):
        st.success(f"교육부 기본 어휘 목록 로드됨")
        vocab_info = f"""
**어휘 통계:**
- 2015년: {len(MOE_VOCABULARIES.get('2015', set()))}개
- 2022년: {len(MOE_VOCABULARIES.get('2022', set()))}개  
- 통합: {len(MOE_VOCABULARIES.get('combined', set()))}개
        """
        st.caption(vocab_info)
    else:
        st.warning("교육부 기본 어휘 목록 로드 안됨")

    if st.session_state.get("teacher_info", {}).get("grade"):
        st.success("교사 정보 입력 완료")
    if st.session_state.get("original_text"):
        st.success("지문 입력 완료")
    if st.session_state.get("keywords"):
        st.success("키워드 분석 완료")
    if st.session_state.get("user_summary"):
        st.success("요약문 작성 완료")
    if st.session_state.get("vocab_analysis"):
        st.success("어휘 수준 분석 완료")
    if st.session_state.get("feedback"):
        st.success("교육과정 피드백 완료")
    if st.session_state.get("survey_submitted"):
        st.success("TAM 설문조사 완료")
    
    st.markdown("### 연구 참여 안내")
    st.markdown("""
    **완전한 도구 체험 후 TAM 설문조사 자동 연결:**
    - 지문 입력 → 요약 작성 → AI 피드백 체험 완료 시
    - TAM 기반 25문항 설문조사 자동 표시
    - 약 3분 소요, 익명 처리, 연구용으로만 사용
    - 응답 완료 후 개인 결과 요약 제공
    """)
