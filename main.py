import streamlit as st
import json
import os
import shutil
import time
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="독서 기록 웹사이트",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for cozy library/book club style
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&family=Noto+Serif+KR:wght@400;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif;
}

/* Page title styled with Serif */
.main-title {
    font-family: 'Noto Serif KR', serif;
    font-size: 2.5rem;
    font-weight: 700;
    color: #4E3629;
    text-align: center;
    margin-bottom: 5px;
}

.main-subtitle {
    font-size: 1.1rem;
    color: #8C786E;
    text-align: center;
    margin-bottom: 30px;
}

/* Sidebar Styling */
.sidebar-title {
    font-family: 'Noto Serif KR', serif;
    font-size: 1.3rem;
    font-weight: 700;
    color: #4E3629;
    margin-top: 15px;
    margin-bottom: 10px;
}

/* Book Cards */
.book-card {
    background-color: #FAF6F0;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
    border: 1px solid #EAD8C7;
    box-shadow: 0 4px 12px rgba(78, 54, 41, 0.05);
}

.card-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}

.card-date {
    font-size: 0.9rem;
    color: #8C786E;
    font-weight: 500;
}

.badge {
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 700;
}

.badge-completed {
    background-color: #EAD8C7;
    color: #4E3629;
}

.badge-reading {
    background-color: #E8F5E9;
    color: #2E7D32;
}

.card-title {
    font-family: 'Noto Serif KR', serif;
    font-size: 1.4rem;
    font-weight: 700;
    color: #4E3629;
    margin-bottom: 6px;
}

.card-info {
    font-size: 0.95rem;
    color: #6D5D55;
    margin-bottom: 12px;
}

.card-rating {
    color: #F39C12;
    font-size: 1.1rem;
    margin-bottom: 10px;
}

.card-quote {
    font-family: 'Noto Serif KR', serif;
    font-size: 1.1rem;
    font-style: italic;
    color: #5C4B43;
    background-color: #FDFCF7;
    border-left: 4px solid #4E3629;
    padding: 10px 15px;
    margin-top: 12px;
    border-radius: 0 8px 8px 0;
}

/* Star selection text styling */
.star-label {
    font-size: 0.9rem;
    font-weight: 500;
    color: #4E3629;
    margin-bottom: 2px;
}

/* Dashboard container */
.stats-container {
    background: linear-gradient(135deg, #FAF6F0 0%, #F5EFE6 100%);
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 20px;
    border: 1px solid #EAD8C7;
    box-shadow: 0 4px 12px rgba(78, 54, 41, 0.05);
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
    gap: 10px;
    margin-bottom: 12px;
}

.stat-box {
    background: #FFFFFF;
    border-radius: 8px;
    padding: 10px;
    text-align: center;
    border: 1px solid #EAD8C7;
    box-shadow: 0 2px 4px rgba(78, 54, 41, 0.02);
}

.stat-val {
    font-family: 'Noto Serif KR', serif;
    font-size: 1.5rem;
    font-weight: 700;
}

.stat-label {
    font-size: 0.78rem;
    color: #8C786E;
    margin-top: 2px;
}

.genre-title {
    font-family: 'Noto Serif KR', serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: #4E3629;
    margin-bottom: 10px;
    border-bottom: 1.5px solid #EAD8C7;
    padding-bottom: 4px;
}

.genre-section {
    background: #FFFFFF;
    border-radius: 8px;
    padding: 12px 16px;
    border: 1px solid #EAD8C7;
}

.genre-item {
    display: flex;
    align-items: center;
    margin-bottom: 6px;
}

.genre-name {
    width: 25%;
    text-overflow: ellipsis;
    overflow: hidden;
    white-space: nowrap;
    color: #5C4B43;
    font-weight: 500;
    font-size: 0.88rem;
}

.genre-bar-bg {
    flex-grow: 1;
    background-color: #F5EFE6;
    height: 6px;
    border-radius: 3px;
    margin: 0 10px;
    overflow: hidden;
    position: relative;
}

.genre-bar-fill {
    background-color: #8C786E;
    height: 100%;
    border-radius: 3px;
    transition: width 0.5s ease-in-out;
}

.genre-count {
    width: 15%;
    text-align: right;
    font-weight: 700;
    color: #4E3629;
    font-size: 0.88rem;
}
</style>
""", unsafe_allow_html=True)

DB_FILE = "reading_logs.json"

# 1. 파일 입출력 로직
def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
            
            # Migration check for keys format YYYY-MM-DD to YYYY-MM-DD_title
            migrated_data = {}
            needs_migration = False
            
            for k, v in raw_data.items():
                if "_" not in k and isinstance(v, dict):
                    title = v.get("title", "").strip()
                    if title:
                        new_key = f"{k}_{title}"
                        migrated_data[new_key] = v
                        needs_migration = True
                    else:
                        migrated_data[k] = v
                else:
                    migrated_data[k] = v
            
            if needs_migration:
                # Backup old database first
                try:
                    shutil.copy2(DB_FILE, DB_FILE + ".bak")
                except Exception as backup_err:
                    st.warning(f"데이터베이스 백업 실패: {backup_err}")
                
                # Save migrated data
                save_data(migrated_data)
                return migrated_data
                
            return raw_data
        except Exception:
            return {}
    return {}

def save_data(data):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"데이터 저장 오류: {e}")

data = load_data()

DB_TRANSCRIPTION_FILE = "transcription_logs.json"

def load_transcriptions():
    if os.path.exists(DB_TRANSCRIPTION_FILE):
        try:
            with open(DB_TRANSCRIPTION_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_transcriptions(t_data):
    try:
        with open(DB_TRANSCRIPTION_FILE, "w", encoding="utf-8") as f:
            json.dump(t_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"필사 데이터 저장 오류: {e}")

t_data = load_transcriptions()

@st.dialog("서재 이름 변경")
def edit_nickname_dialog(current_nickname):
    st.write("새로운 서재 이름을 입력해 주세요.")
    new_name = st.text_input("서재 이름", value=current_nickname, max_chars=15, key="new_nickname_dialog_input")
    if st.button("적용하기", type="primary", key="save_nickname_dialog_btn"):
        if new_name.strip():
            data["user_nickname"] = new_name.strip()
            save_data(data)
            st.rerun()

# 2. 세션 스테이트 날짜 연동
if "target_date" not in st.session_state:
    st.session_state.target_date = datetime.today().date()

# 입력창 초기화 로직 (저장 직후 실행, 위젯이 생성되기 전에 세션 상태를 미리 변경)
if st.session_state.get("should_reset_inputs"):
    date_key_str = st.session_state.target_date.strftime("%Y-%m-%d")
    selected_book_key = f"selected_book_{date_key_str}"
    st.session_state[selected_book_key] = "➕ 새 책 추가하기"
    
    # 해당 날짜와 관련된 세션 상태 키 전체 삭제
    keys_to_delete = [
        k for k in st.session_state.keys()
        if date_key_str in k and (
            "title_" in k or "author_" in k or "genre_" in k or "quote_" in k or
            "status_input_" in k or "rating_backup_" in k or "rating_input_" in k or
            "trans_source_title_" in k or "trans_author_" in k or "trans_content_" in k or
            "trans_ref_link_" in k or "trans_show_link_" in k
        )
    ]
    for k in keys_to_delete:
        del st.session_state[k]
    st.session_state.should_reset_inputs = False

# 3. 사이드바 구성
# 3.1 프로필 아바타 및 동적 닉네임
if os.path.exists("cozy_library_avatar.png"):
    st.sidebar.image("cozy_library_avatar.png", use_container_width=True)

nickname = data.get("user_nickname", "라떼")
if st.sidebar.button(f"☕ {nickname}의 서재", key="edit_nickname_btn", use_container_width=True):
    edit_nickname_dialog(nickname)
st.sidebar.markdown("<div style='text-align: center; font-size: 0.78rem; color: #8C786E; margin-top: -12px; margin-bottom: 15px;'>이름을 클릭하면 수정할 수 있습니다.</div>", unsafe_allow_html=True)

# 3.2 서재 공간 이동 선택 (selectbox)
view_mode = st.sidebar.selectbox(
    "🚪 서재 공간 이동",
    [
        "📚 오늘의 독서 기록",
        "✍️ 오늘의 필사 기록",
        "🗂️ 독서 기록 모아보기",
        "✒️ 필사 기록 모아보기"
    ]
)

# 3.3 날짜 선택 입력창
st.sidebar.markdown("---")
selected_date = st.sidebar.date_input("📅 날짜 선택", key="target_date")
date_key = selected_date.strftime("%Y-%m-%d")

# 3.4 독서 목표 챌린지 및 설정
target_year = str(data.get("challenge_year", datetime.today().year))
goals_dict = data.get("yearly_goals", {})
if not isinstance(goals_dict, dict):
    goals_dict = {}
goal = goals_dict.get(target_year, 30)

# 해당 연도에 완독한 도서 수 집계
completed_books_count = sum(1 for k, v in data.items() if isinstance(v, dict) and k.startswith(target_year) and v.get("status") == "독서완료")
pct = min(100, int((completed_books_count / goal) * 100)) if goal > 0 else 0

st.sidebar.markdown("---")
st.sidebar.markdown(f"<div style='font-size: 0.95rem; font-weight: bold; color: #4E3629; margin-top: 10px; margin-bottom: 5px; font-family: \"Noto Serif KR\", serif;'>🏆 {target_year}년 독서 목표 챌린지</div>", unsafe_allow_html=True)
st.sidebar.progress(min(1.0, completed_books_count / goal) if goal > 0 else 0.0)
st.sidebar.markdown(f"<div style='font-size: 0.82rem; text-align: right; color: #8C786E; margin-top: 4px; margin-bottom: 8px;'>{completed_books_count} / {goal}권 달성 ({pct}%)</div>", unsafe_allow_html=True)

# 챌린지 목표 설정 패널
with st.sidebar.expander("⚙️ 챌린지 목표 설정"):
    current_year = datetime.today().year
    recorded_years = set(k[:4] for k, v in data.items() if isinstance(v, dict) and len(k) >= 10 and k[:4].isdigit() and k[4] == '-' and k[7] == '-')
    for y in range(2020, current_year + 6):
        recorded_years.add(str(y))
    years_list = sorted(list(recorded_years), reverse=True)
    
    new_year = st.selectbox("목표 연도", years_list, index=years_list.index(target_year) if target_year in years_list else 0, key="challenge_year_select")
    if new_year != target_year:
        data["challenge_year"] = new_year
        save_data(data)
        st.rerun()
        
    new_goal = st.number_input(f"{new_year}년 목표 권수", min_value=1, value=goal, step=1, key="challenge_goal_input")
    if new_goal != goal:
        goals_dict[new_year] = new_goal
        data["yearly_goals"] = goals_dict
        save_data(data)
        st.rerun()

# 3.5 서재 통계 요약 카드
st.sidebar.markdown("---")
st.sidebar.markdown("<div style='font-size: 0.95rem; font-weight: bold; color: #4E3629; margin-bottom: 8px; font-family: \"Noto Serif KR\", serif;'>📊 서재 통계</div>", unsafe_allow_html=True)

total_books = sum(1 for v in data.values() if isinstance(v, dict) and "title" in v)
completed_books = sum(1 for v in data.values() if isinstance(v, dict) and v.get("status") == "독서완료")
total_transcriptions = len(t_data)

st.sidebar.markdown(f"""<div style="background-color: #FAF6F0; padding: 12px; border-radius: 8px; border: 1px solid #EAD8C7; font-size: 0.85rem; color: #5C4B43;">
<div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
<span>📖 등록 도서 수</span>
<span style="font-weight: bold; color: #4E3629;">{total_books}권</span>
</div>
<div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
<span>🏆 완독 도서 수</span>
<span style="font-weight: bold; color: #4E3629;">{completed_books}권</span>
</div>
<div style="display: flex; justify-content: space-between;">
<span>✍️ 필사 문장 수</span>
<span style="font-weight: bold; color: #4E3629;">{total_transcriptions}개</span>
</div>
</div>""", unsafe_allow_html=True)


# 4. 메인 화면 UI
if view_mode == "📚 오늘의 독서 기록":
    st.markdown('<h1 class="main-title">📚 오늘의 독서 기록</h1>', unsafe_allow_html=True)
    st.markdown('<p class="main-subtitle">오늘 읽은 책의 소중한 페이지와 마음에 남은 한 줄을 기록해 보세요.</p>', unsafe_allow_html=True)
    st.markdown(f"### 📝 {date_key} 독서 기록")
    
    # 1. 해당 날짜에 저장된 모든 기록 찾기
    records_for_date = {k: v for k, v in data.items() if k.startswith(date_key + "_")}
    
    # 책 선택 셀렉트 박스 옵션 구성
    book_options = ["➕ 새 책 추가하기"] + [v["title"] for v in records_for_date.values()]
    
    # 세션 스테이트로 선택한 책 동기화
    selected_book_key = f"selected_book_{date_key}"
    if selected_book_key not in st.session_state:
        st.session_state[selected_book_key] = "➕ 새 책 추가하기"
        
    # 날짜가 바뀌거나 하여 기존 선택값이 옵션에 없으면 기본값 복원
    if st.session_state[selected_book_key] not in book_options:
        st.session_state[selected_book_key] = "➕ 새 책 추가하기"
        
    selected_book = st.selectbox(
        "📖 기록할 책 선택",
        book_options,
        key=selected_book_key
    )
    
    # 2. 선택된 책에 따라 폼 기본값 불러오기
    if selected_book == "➕ 새 책 추가하기":
        default_title = ""
        default_author = ""
        default_genre = ""
        default_status = "독서중"
        default_rating = 4
        default_quote = ""
    else:
        db_key = f"{date_key}_{selected_book}"
        existing_record = data.get(db_key, {})
        default_title = existing_record.get("title", "")
        default_author = existing_record.get("author", "")
        default_genre = existing_record.get("genre", "")
        default_status = existing_record.get("status", "독서중")
        default_rating = existing_record.get("rating", 4)
        default_quote = existing_record.get("quote", "")
        
    # 세션 스테이트에 감정/상태 정보 바인딩 (책별로 고유 키 지정)
    status_state_key = f"status_input_{date_key}_{selected_book}"
    if status_state_key not in st.session_state:
        st.session_state[status_state_key] = default_status
        
    current_status = st.session_state[status_state_key]
    
    # 5열 혹은 6열 동적 배치
    if current_status == "독서완료":
        cols = st.columns([1.5, 3, 2, 2, 2, 2.5])
    else:
        cols = st.columns([1.5, 3, 2.5, 2, 2])
        
    with cols[0]:
        st.text_input("날짜", value=date_key, disabled=True, key=f"date_display_{date_key}_{selected_book}")
    with cols[1]:
        title = st.text_input("책 제목", value=default_title, placeholder="예: 데미안", key=f"title_{date_key}_{selected_book}")
    with cols[2]:
        author = st.text_input("작가", value=default_author, placeholder="예: 헤르만 헤세", key=f"author_{date_key}_{selected_book}")
    with cols[3]:
        genre = st.text_input("장르", value=default_genre, placeholder="예: 소설", key=f"genre_{date_key}_{selected_book}")
    with cols[4]:
        status = st.selectbox(
            "독서 상태",
            ["독서중", "독서완료"],
            key=status_state_key
        )
        
    # 독서완료 선택 시 별점 입력 추가 (책별로 고유 키 지정)
    final_rating = 4
    if status == "독서완료":
        rating_state_key = f"rating_input_{date_key}_{selected_book}"
        backup_key = f"rating_backup_{date_key}_{selected_book}"
        
        if backup_key not in st.session_state:
            st.session_state[backup_key] = default_rating
            
        with cols[5]:
            st.markdown('<p class="star-label">별점</p>', unsafe_allow_html=True)
            rating_val = st.feedback("stars", key=rating_state_key)
            if rating_val is not None:
                st.session_state[backup_key] = rating_val
                
            final_rating = st.session_state[backup_key]
            
            if final_rating is None:
                final_rating = default_rating
            if final_rating is None:
                final_rating = 4
    
    # 오늘의 한 줄 입력창 (책별로 고유 키 지정)
    st.write("")
    quote = st.text_area(
        "✍️ 오늘의 한 줄",
        value=default_quote,
        placeholder="오늘 읽은 내용 중 가장 감명 깊었던 부분을 기록해보세요...",
        height=150,
        key=f"quote_{date_key}_{selected_book}"
    )
    
    # 저장 버튼
    col_btn1, col_btn2 = st.columns([2, 8])
    with col_btn1:
        if st.button("✔️ 저장하기", type="primary", use_container_width=True):
            if not title.strip():
                st.warning("책 제목을 입력해 주세요!")
            else:
                # 데이터 구성
                record = {
                    "title": title.strip(),
                    "author": author.strip(),
                    "genre": genre.strip(),
                    "status": status,
                    "quote": quote.strip()
                }
                if status == "독서완료":
                    record["rating"] = final_rating
                    
                # 날짜_책제목 형태로 복합 키 저장
                new_db_key = f"{date_key}_{title.strip()}"
                data[new_db_key] = record
                
                # 만약 기존 책을 수정 중인데 제목이 변경된 경우라면 구버전 데이터 키 삭제 (업데이트 연동)
                if selected_book != "➕ 새 책 추가하기" and selected_book != title.strip():
                    old_db_key = f"{date_key}_{selected_book}"
                    if old_db_key in data:
                        del data[old_db_key]
                        
                save_data(data)
                st.toast("🎉 독서 기록 저장 완료!", icon="✔️")
                st.session_state.should_reset_inputs = True
                time.sleep(1)
                st.rerun()

elif view_mode == "✍️ 오늘의 필사 기록":
    st.markdown('<h1 class="main-title">✍️ 오늘의 필사 기록</h1>', unsafe_allow_html=True)
    st.markdown('<p class="main-subtitle">오늘 마음에 남은 한 줄, 간직하고 싶은 문장을 적어보세요.</p>', unsafe_allow_html=True)
    st.markdown(f"### ✍️ {date_key} 필사 기록")
    
    # 1. 출처 유형 선택
    source_type = st.selectbox(
        "🏷️ 출처 유형",
        ["📚 도서", "🎬 영화/드라마", "🎵 노래 가사", "💡 명언/속담", "📱 SNS/인터넷 글귀", "✏️ 기타(직접 입력)"],
        key=f"trans_source_type_{date_key}"
    )
    
    # 2. 동적 입력 안내 레이블 설정 및 렌더링
    col1, col2 = st.columns(2)
    with col1:
        if source_type == "📚 도서":
            title_label = "📖 책 제목"
            title_placeholder = "예: 데미안"
        elif source_type == "🎬 영화/드라마":
            title_label = "🎬 작품명"
            title_placeholder = "예: 쇼생크 탈출"
        elif source_type == "🎵 노래 가사":
            title_label = "🎵 노래 제목"
            title_placeholder = "예: 서른 즈음에"
        elif source_type == "💡 명언/속담":
            title_label = "💡 명언 주제/명칭"
            title_placeholder = "예: 링컨 명언"
        elif source_type == "📱 SNS/인터넷 글귀":
            title_label = "📱 출처 플랫폼/사이트"
            title_placeholder = "예: 브런치, 인스타그램"
        else:
            title_label = "✏️ 출처/제목"
            title_placeholder = "직접 입력"
            
        source_title = st.text_input(title_label, placeholder=title_placeholder, key=f"trans_source_title_{date_key}")
        
    with col2:
        if source_type == "📚 도서":
            author_label = "✍️ 저자/작가"
            author_placeholder = "예: 헤르만 헤세"
        elif source_type == "🎬 영화/드라마":
            author_label = "🗣️ 말한 이/캐릭터"
            author_placeholder = "예: 앤디 듀프레인"
        elif source_type == "🎵 노래 가사":
            author_label = "🎤 아티스트"
            author_placeholder = "예: 김광석"
        elif source_type == "💡 명언/속담":
            author_label = "🗣️ 화자/인물"
            author_placeholder = "예: 에이브러햄 링컨"
        elif source_type == "📱 SNS/인터넷 글귀":
            author_label = "✍️ 글쓴이"
            author_placeholder = "예: 홍길동 (또는 미상)"
        else:
            author_label = "👤 작성자/인물"
            author_placeholder = "직접 입력"
            
        author = st.text_input(author_label, placeholder=author_placeholder, key=f"trans_author_{date_key}")
        
    # 3. 필사 본문 입력
    st.write("")
    content = st.text_area(
        "📝 필사할 원문 내용",
        placeholder="이곳에 간직하고 싶은 소중한 문장을 기록하세요...",
        height=150,
        key=f"trans_content_{date_key}"
    )
    
    # 4. 참조 링크 토글 및 입력창
    show_link = st.checkbox("🔗 참조 링크 추가하기", key=f"trans_show_link_{date_key}")
    ref_link = ""
    if show_link:
        ref_link = st.text_input(
            "🔗 참조 링크",
            placeholder="예: https://example.com/quotes",
            key=f"trans_ref_link_{date_key}"
        )
    
    # 저장 버튼
    col_btn1, col_btn2 = st.columns([2, 8])
    with col_btn1:
        if st.button("✔️ 필사 기록 저장", type="primary", use_container_width=True):
            if not content.strip():
                st.warning("필사할 내용을 입력해 주세요!")
            elif not source_title.strip():
                st.warning("출처/제목을 입력해 주세요!")
            else:
                # 고유 키 생성
                unique_id = f"{date_key}_{int(time.time())}"
                t_record = {
                    "date": date_key,
                    "source_type": source_type,
                    "source_title": source_title.strip(),
                    "author": author.strip(),
                    "content": content.strip(),
                    "ref_link": ref_link.strip()
                }
                t_data[unique_id] = t_record
                save_transcriptions(t_data)
                
                st.toast("🎉 필사 기록 저장 완료!", icon="✔️")
                
                st.session_state.should_reset_inputs = True
                        
                time.sleep(1)
                st.rerun()

elif view_mode == "🗂️ 독서 기록 모아보기":
    st.markdown('<h1 class="main-title">🗂️ 독서 기록 모아보기</h1>', unsafe_allow_html=True)
    st.markdown('<p class="main-subtitle">지금까지 차곡차곡 쌓인 독서의 흔적들을 살펴보세요.</p>', unsafe_allow_html=True)
    
    # 데이터 전체에서 년-월(YYYY-MM) 고유 목록 추출
    book_keys = [k for k, v in data.items() if isinstance(v, dict) and len(k) >= 10 and k[:4].isdigit() and k[4] == '-' and k[7] == '-']
    if book_keys:
        available_months = ["전체 기간"] + sorted(list(set(k[:7] for k in book_keys)), reverse=True)
    else:
        available_months = ["전체 기간"]
        
    selected_month = st.selectbox("조회할 연도 및 월 선택", available_months, index=0)
    
    # 필터링
    if selected_month == "전체 기간":
        month_records = {k: v for k, v in data.items() if isinstance(v, dict) and len(k) >= 10 and k[:4].isdigit() and k[4] == '-' and k[7] == '-'}
    else:
        month_records = {k: v for k, v in data.items() if k.startswith(selected_month) and isinstance(v, dict) and len(k) >= 10 and k[:4].isdigit()}
    
    if month_records:
        from collections import defaultdict
        
        # 요약 데이터 계산
        total_books = len(month_records)
        completed_books = sum(1 for v in month_records.values() if v.get("status") == "독서완료")
        reading_books = total_books - completed_books
        
        # ── 세션 상태 초기화 ──
        if "archive_filter" not in st.session_state:
            st.session_state.archive_filter = "전체"

        cur_filter = st.session_state.archive_filter
        type1 = "primary" if cur_filter == "전체" else "secondary"
        type2 = "primary" if cur_filter == "독서완료" else "secondary"
        type3 = "primary" if cur_filter == "독서중" else "secondary"

        # ── 통계 카드 CSS (stVerticalBlock + :has 스코프로 정확히 타게팅) ──
        st.markdown("""
<style>
/* 컨테이너 외곽 테두리/배경 오버라이드 */
[data-testid="stVerticalBlockBorderWrapper"]:has(.stat-scope-marker) {
    background: linear-gradient(135deg, #FAF6F0 0%, #F5EFE6 100%) !important;
    border: 1px solid #EAD8C7 !important;
    border-radius: 16px !important;
    box-shadow: 0 2px 8px rgba(78,54,41,0.06) !important;
}
/* 내부 패딩 */
[data-testid="stVerticalBlock"]:has(.stat-scope-marker) {
    padding: 4px 4px 8px 4px !important;
}
/* ── 버튼 카드 스타일 ── */
[data-testid="stVerticalBlock"]:has(.stat-scope-marker) [data-testid="stHorizontalBlock"] button {
    background: #FFFFFF !important;
    border: 1.5px solid #EAD8C7 !important;
    border-radius: 12px !important;
    height: 110px !important;
    white-space: pre-line !important;
    box-shadow: 0 1px 4px rgba(78,54,41,0.04) !important;
    transition: all 0.2s cubic-bezier(.4,0,.2,1) !important;
}
[data-testid="stVerticalBlock"]:has(.stat-scope-marker) [data-testid="stHorizontalBlock"] button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 12px rgba(78,54,41,0.12) !important;
}
/* 버튼 텍스트 */
[data-testid="stVerticalBlock"]:has(.stat-scope-marker) [data-testid="stHorizontalBlock"] button p {
    white-space: pre-line !important;
    margin: 0 !important;
    font-size: 0.72rem !important;
    color: #8C786E !important;
    font-weight: 500 !important;
    line-height: 1.7 !important;
    font-family: 'Noto Sans KR', sans-serif !important;
}
/* 첫 줄 (숫자) 크게 */
[data-testid="stVerticalBlock"]:has(.stat-scope-marker) [data-testid="stHorizontalBlock"] button p::first-line {
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    font-family: 'Noto Serif KR', serif !important;
}
/* 각 열 색상 (비활성) */
[data-testid="stVerticalBlock"]:has(.stat-scope-marker) [data-testid="stHorizontalBlock"] > div:nth-child(1) button p::first-line { color: #4E3629 !important; }
[data-testid="stVerticalBlock"]:has(.stat-scope-marker) [data-testid="stHorizontalBlock"] > div:nth-child(2) button p::first-line { color: #2E7D32 !important; }
[data-testid="stVerticalBlock"]:has(.stat-scope-marker) [data-testid="stHorizontalBlock"] > div:nth-child(3) button p::first-line { color: #C84B11 !important; }
/* 활성 버튼 (primary) */
[data-testid="stVerticalBlock"]:has(.stat-scope-marker) [data-testid="stHorizontalBlock"] > div:nth-child(1) button[kind="primary"] {
    background: #F5EFE6 !important; border: 2.5px solid #8C786E !important;
    box-shadow: 0 4px 14px rgba(140,120,110,0.22) !important; transform: translateY(-2px) !important;
}
[data-testid="stVerticalBlock"]:has(.stat-scope-marker) [data-testid="stHorizontalBlock"] > div:nth-child(2) button[kind="primary"] {
    background: #EDFAED !important; border: 2.5px solid #2E7D32 !important;
    box-shadow: 0 4px 14px rgba(46,125,50,0.20) !important; transform: translateY(-2px) !important;
}
[data-testid="stVerticalBlock"]:has(.stat-scope-marker) [data-testid="stHorizontalBlock"] > div:nth-child(3) button[kind="primary"] {
    background: #FFF0EA !important; border: 2.5px solid #C84B11 !important;
    box-shadow: 0 4px 14px rgba(200,75,17,0.18) !important; transform: translateY(-2px) !important;
}
/* 활성 버튼 텍스트 */
[data-testid="stVerticalBlock"]:has(.stat-scope-marker) [data-testid="stHorizontalBlock"] > div:nth-child(1) button[kind="primary"] p { color: #5C4B43 !important; }
[data-testid="stVerticalBlock"]:has(.stat-scope-marker) [data-testid="stHorizontalBlock"] > div:nth-child(2) button[kind="primary"] p { color: #2E7D32 !important; }
[data-testid="stVerticalBlock"]:has(.stat-scope-marker) [data-testid="stHorizontalBlock"] > div:nth-child(3) button[kind="primary"] p { color: #C84B11 !important; }
</style>
""", unsafe_allow_html=True)

        # ── 통합 요약 카드 (한 박스 안에 모두) ──
        with st.container(border=True):
            st.markdown(f"""
<div class="stat-scope-marker"></div>
<div style="font-family:'Noto Serif KR',serif;font-size:0.88rem;font-weight:700;color:#8C786E;margin-bottom:10px;">
  📊 {selected_month} 독서 요약
</div>
""", unsafe_allow_html=True)
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            with col_stat1:
                if st.button(f"📚 {total_books}권\n총 기록", key="btn_stat_total", type=type1, use_container_width=True):
                    st.session_state.archive_filter = "전체"
                    st.rerun()
            with col_stat2:
                if st.button(f"🏆 {completed_books}권\n독서 완료", key="btn_stat_completed", type=type2, use_container_width=True):
                    st.session_state.archive_filter = "독서완료"
                    st.rerun()
            with col_stat3:
                if st.button(f"📖 {reading_books}권\n독서 중", key="btn_stat_reading", type=type3, use_container_width=True):
                    st.session_state.archive_filter = "독서중"
                    st.rerun()
        
        # 3. 도서 목록 출력 필터 처리
        if st.session_state.archive_filter == "독서완료":
            st.write("")
            completed_books_list = []
            for db_key_str, record in month_records.items():
                if record.get("status") == "독서완료":
                    completed_books_list.append((db_key_str, record))
            
            # 별점 순으로 내림차순 정렬, 동일 별점 시 날짜 최신 순 정렬
            completed_books_list.sort(key=lambda x: (x[1].get("rating") if x[1].get("rating") is not None else 4, x[0]), reverse=True)
            
            if completed_books_list:
                book_items_html = []
                for db_key_str, record in completed_books_list:
                    parts = db_key_str.split("_", 1)
                    display_date_str = parts[0]
                    title = record.get("title", "")
                    author = record.get("author", "")
                    genre = record.get("genre", "")
                    status = record.get("status", "독서완료")
                    quote = record.get("quote", "")
                    
                    status_badge = f'<span class="badge badge-completed">독서완료</span>'
                    
                    # 별점 매칭
                    rating_val = record.get("rating", 4)
                    if rating_val is None:
                        rating_val = 4
                    stars_count = int(rating_val) + 1
                    rating_stars = "★" * stars_count + "☆" * (5 - stars_count)
                    rating_html = f'<div class="card-rating">{rating_stars}</div>'
                    
                    quote_section = f'<div class="card-quote">"{quote}"</div>' if quote else ""
                    
                    book_html = f"""<div class="book-item" style="margin-top: 10px; margin-bottom: 10px;">
<div class="card-top" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
<div class="card-title" style="font-size: 1.3rem; margin-bottom: 0;">{title}</div>
{status_badge}
</div>
<div class="card-info" style="margin-bottom: 8px;">✍️ 작가: {author} | 🏷️ 장르: {genre} | 📅 기록일: {display_date_str}</div>
{rating_html}
{quote_section}
</div>"""
                    book_items_html.append(book_html)
                
                divider = '<hr style="border: 0; border-top: 1px solid #EAD8C7; margin: 15px 0;">'
                books_joined_html = divider.join(book_items_html)
                
                st.markdown(f"""<div class="book-card">
<div style="font-size: 1.05rem; color: #8C786E; font-weight: 700; border-bottom: 1.5px solid #EAD8C7; padding-bottom: 6px; margin-bottom: 15px;">
🏆 완독 도서 목록
</div>
{books_joined_html}
</div>""", unsafe_allow_html=True)
            else:
                st.info("해당 기간의 다 읽은 책 기록이 존재하지 않습니다.")
                
        elif st.session_state.archive_filter == "독서중":
            st.write("")
            reading_books_list = []
            for db_key_str, record in month_records.items():
                if record.get("status") != "독서완료":
                    reading_books_list.append((db_key_str, record))
            
            # 날짜 최신 순 정렬
            reading_books_list.sort(key=lambda x: x[0], reverse=True)
            
            if reading_books_list:
                grouped_records = defaultdict(list)
                for db_key_str, record in reading_books_list:
                    parts = db_key_str.split("_", 1)
                    display_date_str = parts[0]
                    grouped_records[display_date_str].append(record)
                    
                for display_date_str, records in grouped_records.items():
                    book_items_html = []
                    for record in records:
                        title = record.get("title", "")
                        author = record.get("author", "")
                        genre = record.get("genre", "")
                        quote = record.get("quote", "")
                        
                        status_badge = f'<span class="badge badge-reading">독서중</span>'
                        quote_section = f'<div class="card-quote">"{quote}"</div>' if quote else ""
                        
                        book_html = f"""<div class="book-item" style="margin-top: 10px; margin-bottom: 10px;">
<div class="card-top" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
<div class="card-title" style="font-size: 1.3rem; margin-bottom: 0;">{title}</div>
{status_badge}
</div>
<div class="card-info" style="margin-bottom: 8px;">✍️ 작가: {author} | 🏷️ 장르: {genre}</div>
{quote_section}
</div>"""
                        book_items_html.append(book_html)
                        
                    divider = '<hr style="border: 0; border-top: 1px solid #EAD8C7; margin: 15px 0;">'
                    books_joined_html = divider.join(book_items_html)
                    
                    st.markdown(f"""<div class="book-card">
<div style="font-size: 1.05rem; color: #8C786E; font-weight: 700; border-bottom: 1.5px solid #EAD8C7; padding-bottom: 6px; margin-bottom: 15px;">
📅 {display_date_str}
</div>
{books_joined_html}
</div>""", unsafe_allow_html=True)
            else:
                st.info("해당 기간의 독서 중인 책 기록이 존재하지 않습니다.")
                
        else: # 전체
            st.write("")
            grouped_records = defaultdict(list)
            for db_key_str, record in sorted(month_records.items(), key=lambda x: x[0], reverse=True):
                parts = db_key_str.split("_", 1)
                display_date_str = parts[0]
                grouped_records[display_date_str].append(record)
                
            for display_date_str, records in grouped_records.items():
                book_items_html = []
                for record in records:
                    title = record.get("title", "")
                    author = record.get("author", "")
                    genre = record.get("genre", "")
                    status = record.get("status", "독서중")
                    quote = record.get("quote", "")
                    
                    status_badge = f'<span class="badge badge-completed">독서완료</span>' if status == "독서완료" else f'<span class="badge badge-reading">독서중</span>'
                    
                    rating_html = ""
                    if status == "독서완료":
                        rating_val = record.get("rating", 4)
                        if rating_val is None:
                            rating_val = 4
                        stars_count = int(rating_val) + 1
                        rating_stars = "★" * stars_count + "☆" * (5 - stars_count)
                        rating_html = f'<div class="card-rating">{rating_stars}</div>'
                        
                    quote_section = f'<div class="card-quote">"{quote}"</div>' if quote else ""
                    
                    book_html = f"""<div class="book-item" style="margin-top: 10px; margin-bottom: 10px;">
<div class="card-top" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
<div class="card-title" style="font-size: 1.3rem; margin-bottom: 0;">{title}</div>
{status_badge}
</div>
<div class="card-info" style="margin-bottom: 8px;">✍️ 작가: {author} | 🏷️ 장르: {genre}</div>
{rating_html}
{quote_section}
</div>"""
                    book_items_html.append(book_html)
                    
                divider = '<hr style="border: 0; border-top: 1px solid #EAD8C7; margin: 15px 0;">'
                books_joined_html = divider.join(book_items_html)
                
                st.markdown(f"""<div class="book-card">
<div style="font-size: 1.05rem; color: #8C786E; font-weight: 700; border-bottom: 1.5px solid #EAD8C7; padding-bottom: 6px; margin-bottom: 15px;">
📅 {display_date_str}
</div>
{books_joined_html}
</div>""", unsafe_allow_html=True)
    else:
        st.info(f"{selected_month}에 등록된 독서 기록이 존재하지 않습니다.")

elif view_mode == "✒️ 필사 기록 모아보기":
    st.markdown('<h1 class="main-title">✒️ 필사 기록 모아보기</h1>', unsafe_allow_html=True)
    st.markdown('<p class="main-subtitle">지금까지 차곡차곡 모인 소중한 문장들을 되새겨 보세요.</p>', unsafe_allow_html=True)
    
    # 1. 조회 방식 선택 (월별 / 출처 유형별)
    filter_mode = st.radio(
        "조회 방식 선택",
        ["📅 기간별 조회", "🏷️ 출처 유형별 조회"],
        key="trans_filter_mode",
        horizontal=True
    )
    
    # 데이터 소스 및 요약 문구 정의
    records_to_display = {}
    summary_text = ""
    
    if filter_mode == "📅 기간별 조회":
        if t_data:
            available_months = sorted(list(set(k[:7] for k in t_data.keys())), reverse=True)
        else:
            available_months = [datetime.today().strftime("%Y-%m")]
            
        selected_month = st.selectbox("조회할 연도 및 월 선택", available_months, key="trans_view_month_select")
        records_to_display = {k: v for k, v in t_data.items() if k.startswith(selected_month)}
        summary_text = f"📊 **{selected_month}에는 총 {len(records_to_display)}개의 문장이 기록되었습니다.**"
    else:
        available_types = ["📚 도서", "🎬 영화/드라마", "🎵 노래 가사", "💡 명언/속담", "📱 SNS/인터넷 글귀", "✏️ 기타(직접 입력)"]
        selected_type = st.selectbox("조회할 출처 유형 선택", available_types, key="trans_view_type_select")
        records_to_display = {k: v for k, v in t_data.items() if v.get("source_type") == selected_type}
        summary_text = f"📊 **{selected_type} 유형의 필사 기록은 총 {len(records_to_display)}개 있습니다.**"
        
    if records_to_display:
        st.write(summary_text)
        st.write("")
        
        # 날짜별로 그룹화 및 정렬 (오름차순)
        from collections import defaultdict
        grouped_records = defaultdict(list)
        for db_key_str, record in sorted(records_to_display.items(), key=lambda x: x[0], reverse=False):
            log_date_str = db_key_str.split("_")[0]
            grouped_records[log_date_str].append(record)
            
        for display_date_str, records in grouped_records.items():
            trans_items_html = []
            for record in records:
                s_type = record.get("source_type", "기타")
                s_title = record.get("source_title", "")
                author = record.get("author", "")
                content = record.get("content", "")
                ref_link = record.get("ref_link", "")
                
                # 출처 배지 스타일링
                badge_class = "badge-completed" if "도서" in s_type else "badge-reading"
                badge_html = f'<span class="badge {badge_class}">{s_type}</span>'
                
                # 출처 링크 표시
                link_html = ""
                if ref_link:
                    link_html = f'<div style="margin-top: 10px; font-size: 0.88rem;"><a href="{ref_link}" target="_blank" style="color: #8C786E; text-decoration: underline; font-weight: 500;">🔗 원문 바로가기</a></div>'
                
                item_html = f"""<div class="book-item" style="margin-top: 10px; margin-bottom: 10px;">
<div class="card-top" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
<div class="card-title" style="font-size: 1.2rem; margin-bottom: 0;">{s_title}</div>
{badge_html}
</div>
<div class="card-info" style="margin-bottom: 8px;">👤 {author}</div>
<div class="card-quote">"{content}"</div>
{link_html}
</div>"""
                trans_items_html.append(item_html)
                
            divider = '<hr style="border: 0; border-top: 1px solid #EAD8C7; margin: 15px 0;">'
            trans_joined_html = divider.join(trans_items_html)
            
            st.markdown(f"""<div class="book-card">
<div style="font-size: 1.05rem; color: #8C786E; font-weight: 700; border-bottom: 1.5px solid #EAD8C7; padding-bottom: 6px; margin-bottom: 15px;">
📅 {display_date_str}
</div>
{trans_joined_html}
</div>""", unsafe_allow_html=True)
    else:
        st.info("조건에 부합하는 필사 기록이 존재하지 않습니다.")
