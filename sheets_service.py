# sheets_service.py
import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
import json
import datetime
import traceback

# 상수 정의
WORKSHEET_NAME = "TAM_Survey_Data"
BACKUP_WORKSHEET_NAME = "TAM_Survey_Backup"
SPREADSHEET_ROWS = 1000
SPREADSHEET_COLS = 35

# Google Sheets API 스코프
GOOGLE_SHEETS_SCOPE = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets'
]

# 헤더 정의 (상수로 관리)
SURVEY_HEADERS = [
    # 기본 정보
    "timestamp", "participant_id", "teacher_grade", "school_type", "teaching_experience",
    
    # 도구 사용 정보
    "tool_grade_level", "tool_subject_type", "tool_source_type", 
    "completed_summary", "received_feedback", "vocab_analysis_completed",
    
    # TAM 점수 - 인지된 유용성 (PU)
    "PU_1", "PU_2", "PU_3", "PU_4", "PU_5",
    
    # TAM 점수 - 인지된 사용용이성 (PEOU)
    "PEOU_1", "PEOU_2", "PEOU_3", "PEOU_4", "PEOU_5",
    
    # TAM 점수 - 자기효능감 (SE)
    "SE_1", "SE_2", "SE_3", "SE_4", "SE_5",
    
    # TAM 점수 - 활용의도 (BI)
    "BI_1", "BI_2", "BI_3", "BI_4", "BI_5",
    
    # TAM 점수 - 추가문항 (AD)
    "AD_1", "AD_2", "AD_3", "AD_4", "AD_5",
    
    # 자유 응답
    "feedback_text"
]

def check_secrets_configuration():
    """Secrets 설정 상태 확인"""
    missing_configs = []
    
    if "gcp_service_account" not in st.secrets:
        missing_configs.append("gcp_service_account")
    else:
        required_gcp_keys = ["type", "project_id", "private_key", "client_email"]
        for key in required_gcp_keys:
            if key not in st.secrets["gcp_service_account"]:
                missing_configs.append(f"gcp_service_account.{key}")
    
    if "google_sheets" not in st.secrets or "spreadsheet_id" not in st.secrets["google_sheets"]:
        missing_configs.append("google_sheets.spreadsheet_id")
    
    return missing_configs

def setup_google_sheets():
    """Google Sheets 연결 설정 (개선된 오류 처리)"""
    try:
        # Secrets 설정 확인
        missing_configs = check_secrets_configuration()
        if missing_configs:
            st.warning(f"❌ 다음 설정이 누락되었습니다: {', '.join(missing_configs)}")
            st.info("💡 Streamlit Settings > Secrets에서 Google Sheets 연동 정보를 설정해주세요.")
            return None
        
        # 인증 정보 가져오기
        credentials_dict = dict(st.secrets["gcp_service_account"])
        
        # 인증 정보 유효성 간단 체크
        if not credentials_dict.get("private_key") or not credentials_dict.get("client_email"):
            st.error("❌ Google Cloud 인증 정보가 올바르지 않습니다.")
            return None
        
        # 크리덴셜 생성
        credentials = Credentials.from_service_account_info(
            credentials_dict, scopes=GOOGLE_SHEETS_SCOPE
        )
        
        # gspread 클라이언트 인증
        client = gspread.authorize(credentials)
        
        # 스프레드시트 열기
        spreadsheet_id = st.secrets["google_sheets"]["spreadsheet_id"]
        
        try:
            spreadsheet = client.open_by_key(spreadsheet_id)
            return spreadsheet
        except gspread.SpreadsheetNotFound:
            st.error("❌ 지정된 Google Sheets를 찾을 수 없습니다.")
            st.info("💡 스프레드시트 ID가 올바른지, 서비스 계정에 공유 권한이 있는지 확인해주세요.")
            return None
        
    except Exception as e:
        st.error(f"❌ Google Sheets 연결 실패: {str(e)}")
        
        # 디버그 모드에서만 상세 오류 표시
        if st.secrets.get("debug_mode", False):
            st.error(f"상세 오류 정보:")
            st.code(traceback.format_exc())
        else:
            st.info("🔧 문제가 지속되면 관리자에게 연락해주세요.")
        
        return None

def initialize_survey_worksheet(spreadsheet):
    """설문 데이터 워크시트 초기화 (개선된 버전)"""
    try:
        # 기존 워크시트 확인
        try:
            worksheet = spreadsheet.worksheet(WORKSHEET_NAME)
            
            # 헤더 확인 (첫 번째 행이 올바른 헤더인지 체크)
            existing_headers = worksheet.row_values(1)
            if existing_headers == SURVEY_HEADERS:
                return worksheet
            else:
                st.warning(f"⚠️ 기존 워크시트의 헤더가 현재 버전과 다릅니다.")
                # 백업 워크시트 생성 후 새로 만들기
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"{BACKUP_WORKSHEET_NAME}_{timestamp}"
                worksheet.update_title(backup_name)
                st.info(f"💾 기존 데이터를 '{backup_name}'으로 백업했습니다.")
                
        except gspread.WorksheetNotFound:
            pass
        
        # 새 워크시트 생성
        worksheet = spreadsheet.add_worksheet(
            title=WORKSHEET_NAME,
            rows=SPREADSHEET_ROWS,
            cols=SPREADSHEET_COLS
        )
        
        # 헤더 추가
        worksheet.append_row(SURVEY_HEADERS)
        
        # 헤더 행 서식 설정
        try:
            worksheet.format('A1:AI1', {
                "backgroundColor": {"red": 0.8, "green": 0.9, "blue": 1.0},
                "textFormat": {"bold": True, "fontSize": 10},
                "horizontalAlignment": "CENTER"
            })
        except Exception as format_error:
            # 서식 설정 실패는 치명적이지 않으므로 경고만 표시
            st.warning(f"⚠️ 헤더 서식 설정 실패: {format_error}")
        
        st.success(f"✅ 새로운 워크시트 '{WORKSHEET_NAME}' 생성 완료")
        return worksheet
        
    except Exception as e:
        st.error(f"❌ 워크시트 초기화 실패: {str(e)}")
        return None

def save_survey_to_sheets(survey_data):
    """설문 데이터를 Google Sheets에 저장 (개선된 버전)"""
    try:
        # Google Sheets 연결
        spreadsheet = setup_google_sheets()
        if not spreadsheet:
            return False, "Google Sheets 연결 실패"
        
        # 워크시트 준비
        worksheet = initialize_survey_worksheet(spreadsheet)
        if not worksheet:
            return False, "워크시트 초기화 실패"
        
        # 참여자 고유 ID 생성 (더 안전한 방식)
        timestamp = datetime.datetime.now()
        participant_id = f"P{timestamp.strftime('%Y%m%d_%H%M%S')}_{hash(str(survey_data)) % 1000:03d}"
        
        # 데이터 행 준비 (헤더 순서와 정확히 일치)
        row_data = [
            # 기본 정보
            survey_data["timestamp"],
            participant_id,
            survey_data["teacher_info"].get("grade", ""),
            survey_data["teacher_info"].get("school_type", ""),
            survey_data["teacher_info"].get("experience", ""),
            
            # 도구 사용 정보
            survey_data["tool_usage"].get("grade_level", ""),
            survey_data["tool_usage"].get("subject_type", ""),
            survey_data["tool_usage"].get("source_type", ""),
            survey_data["tool_usage"].get("completed_summary", False),
            survey_data["tool_usage"].get("received_feedback", False),
            survey_data["tool_usage"].get("vocab_analysis_completed", False),
        ]
        
        # TAM 점수 추가 (정확한 순서로)
        tam_categories = ["PU", "PEOU", "SE", "BI", "AD"]
        for category in tam_categories:
            for i in range(1, 6):
                score = survey_data["tam_scores"].get(f"{category}_{i}", "")
                row_data.append(score)
        
        # 자유 응답 추가
        feedback_text = survey_data.get("feedback_text", "").replace("\n", " ").replace("\r", " ")
        row_data.append(feedback_text)
        
        # 데이터 길이 검증
        if len(row_data) != len(SURVEY_HEADERS):
            return False, f"데이터 길이 불일치: 예상 {len(SURVEY_HEADERS)}, 실제 {len(row_data)}"
        
        # 데이터 저장
        worksheet.append_row(row_data)
        
        return True, participant_id
        
    except Exception as e:
        error_msg = f"데이터 저장 실패: {str(e)}"
        
        # 디버그 모드에서만 상세 오류 표시
        if st.secrets.get("debug_mode", False):
            error_msg += f"\n상세 오류:\n{traceback.format_exc()}"
        
        return False, error_msg

def get_survey_statistics():
    """저장된 설문 통계 조회 (관리자용)"""
    try:
        spreadsheet = setup_google_sheets()
        if not spreadsheet:
            return None
        
        try:
            worksheet = spreadsheet.worksheet(WORKSHEET_NAME)
            records = worksheet.get_all_records()
            
            if not records:
                return {"total_responses": 0, "message": "아직 응답이 없습니다."}
            
            # 기본 통계 계산
            stats = {
                "total_responses": len(records),
                "latest_response": records[-1].get("timestamp", "알 수 없음"),
                "school_types": {},
                "grade_levels": {},
                "tam_averages": {}
            }
            
            # 학교 유형별 분포
            for record in records:
                school_type = record.get("school_type", "기타")
                stats["school_types"][school_type] = stats["school_types"].get(school_type, 0) + 1
                
                grade_level = record.get("tool_grade_level", "기타")
                stats["grade_levels"][grade_level] = stats["grade_levels"].get(grade_level, 0) + 1
            
            # TAM 평균 점수 계산
            tam_categories = ["PU", "PEOU", "SE", "BI", "AD"]
            for category in tam_categories:
                scores = []
                for i in range(1, 6):
                    column_name = f"{category}_{i}"
                    for record in records:
                        score = record.get(column_name)
                        if score and str(score).isdigit():
                            scores.append(int(score))
                
                if scores:
                    stats["tam_averages"][category] = round(sum(scores) / len(scores), 2)
                else:
                    stats["tam_averages"][category] = 0
            
            return stats
            
        except gspread.WorksheetNotFound:
            return {"total_responses": 0, "message": "설문 워크시트가 없습니다."}
            
    except Exception as e:
        st.error(f"통계 조회 실패: {str(e)}")
        return None

def test_sheets_connection():
    """Google Sheets 연결 테스트 (상세한 진단)"""
    st.markdown("### 🔧 Google Sheets 연결 테스트")
    
    # 1. Secrets 설정 확인
    missing_configs = check_secrets_configuration()
    if missing_configs:
        st.error(f"❌ 누락된 설정: {', '.join(missing_configs)}")
        return False
    else:
        st.success("✅ Secrets 설정 완료")
    
    # 2. 스프레드시트 연결 테스트
    try:
        with st.spinner("스프레드시트 연결 중..."):
            spreadsheet = setup_google_sheets()
            
        if spreadsheet:
            st.success(f"✅ 스프레드시트 연결 성공: **{spreadsheet.title}**")
            
            # 3. 워크시트 목록 표시
            worksheets = spreadsheet.worksheets()
            worksheet_names = [ws.title for ws in worksheets]
            st.info(f"📋 사용 가능한 워크시트: {', '.join(worksheet_names)}")
            
            # 4. 설문 워크시트 확인
            try:
                survey_worksheet = spreadsheet.worksheet(WORKSHEET_NAME)
                record_count = len(survey_worksheet.get_all_records())
                st.success(f"✅ 설문 워크시트 확인: **{record_count}**개 응답 저장됨")
            except gspread.WorksheetNotFound:
                st.warning(f"⚠️ 설문 워크시트('{WORKSHEET_NAME}')가 없습니다. 첫 설문 제출 시 자동 생성됩니다.")
            
            # 5. 쓰기 권한 테스트
            if st.button("📝 쓰기 권한 테스트"):
                try:
                    test_worksheet = initialize_survey_worksheet(spreadsheet)
                    if test_worksheet:
                        st.success("✅ 쓰기 권한 확인됨")
                    else:
                        st.error("❌ 쓰기 권한 없음")
                except Exception as e:
                    st.error(f"❌ 쓰기 테스트 실패: {e}")
            
            return True
        else:
            st.error("❌ 스프레드시트 연결 실패")
            return False
            
    except Exception as e:
        st.error(f"❌ 연결 테스트 중 오류: {str(e)}")
        return False

# 사용 예시 및 디버그용 함수
def display_debug_info():
    """디버그 정보 표시 (개발자용)"""
    if not st.secrets.get("debug_mode", False):
        return
    
    st.markdown("### 🐛 디버그 정보")
    
    with st.expander("Secrets 설정 상태"):
        st.write("OpenAI API:", "✅" if "openai" in st.secrets else "❌")
        st.write("GCP Service Account:", "✅" if "gcp_service_account" in st.secrets else "❌")
        st.write("Google Sheets ID:", "✅" if "google_sheets" in st.secrets else "❌")
    
    with st.expander("연결 상태 테스트"):
        if st.button("전체 연결 테스트 실행"):
            test_sheets_connection()
    
    with st.expander("통계 정보"):
        if st.button("설문 통계 조회"):
            stats = get_survey_statistics()
            if stats:
                st.json(stats)
            else:
                st.error("통계 조회 실패")
