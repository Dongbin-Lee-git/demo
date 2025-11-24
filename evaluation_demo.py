import streamlit as st
import pandas as pd
import ast
import json
import re
import datetime  # 1. datetime 모듈 추가

# --- CONFIGURATION & CONSTANTS ---
DEMO_PASSWORD = "1234"
DATA_LOADING_HELP = "Google Drive CSV 파일의 공유 링크를 입력하거나, 아래에서 CSV 파일을 직접 업로드하세요."

# --- PAGE SETUP ---
st.set_page_config(
    page_title="추천 시스템 평가 데모",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CUSTOM CSS STYLING ---
st.markdown("""
<style>
    /* 1. 전체 폰트 및 기본 설정 */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Noto Sans KR', sans-serif;
        color: #333;
    }
    .block-container {
        padding-top: 1rem; 
        padding-bottom: 3rem;
        max-width: 100%;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    /* 2. 공통 유틸리티 */
    .section-header {
        font-size: 1.15rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 12px;
        padding-bottom: 8px;
        border-bottom: 2px solid #e2e8f0;
        display: flex;
        align-items: center;
        gap: 8px; /* 제목과 배지 사이 간격 */
        letter-spacing: -0.02em;
    }

    .time-badge {
        font-size: 0.75rem;
        color: #be123c;
        background-color: #fff1f2;
        border: 1px solid #fda4af;
        padding: 2px 8px;
        border-radius: 12px;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 4px;
        white-space: nowrap; /* 줄바꿈 방지 */
    }

    /* 3. Target Box (우측 정답지) */
    .target-box {
        background: #ffffff;
        border: 1px solid #cbd5e1;
        border-top: 4px solid #ec4899;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        height: fit-content;
        margin-bottom: 20px;
    }
    .target-label {
        color: #ec4899; 
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    .target-title {
        font-weight: 800; 
        font-size: 1.2rem; 
        color: #0f172a;
        margin-bottom: 10px;
        line-height: 1.35;
        word-break: keep-all;
    }

    /* [NEW] Quant Metric Box - Original structure preserved */
    .quant-box {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 20px;
    }
    .quant-row {
        display: flex;
        justify-content: space-between;
        margin-bottom: 6px;
        font-size: 0.85rem;
    }
    .quant-val {
        font-weight: 700;
        color: #3b82f6;
    }

    /* [NEW] Eval Box (우측 평가 영역) */
    .eval-box {
        background: #f0fdf4;
        border: 1px solid #86efac;
        border-top: 4px solid #22c55e;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .eval-label {
        color: #15803d; 
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 4px;
    }

    /* 4. 배지 & 태그 디자인 */
    .category-badge {
        background-color: #f0f9ff;
        color: #0284c7;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
        border: 1px solid #bae6fd;
    }
    .simple-tag {
        background-color: #eef2ff;
        color: #4338ca;
        border: 1px solid #c7d2fe;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 6px;
        margin-bottom: 6px;
        display: inline-block;
    }
    .simple-tag.highlight {
        background-color: #ffedd5;
        color: #c2410c;
        border-color: #fed7aa;
    }
    /* 5. 타임라인 (Timeline) 스타일 */
    .timeline-container {
        position: relative;
        padding-left: 20px;
        margin-top: 10px;
        border-left: 2px solid #e2e8f0;
    }
    .timeline-item {
        position: relative;
        margin-bottom: 24px;
        padding-left: 20px;
    }
    .timeline-dot {
        position: absolute;
        left: -29px;
        top: 2px;
        width: 14px;
        height: 14px;
        border-radius: 50%;
        background: #fff;
        border: 3px solid #cbd5e1;
        z-index: 1;
        box-shadow: 0 0 0 2px #fff;
    }
    .type-buy .timeline-dot { border-color: #3b82f6; }
    .type-search .timeline-dot { border-color: #f97316; }

    .timeline-date {
        font-size: 0.75rem;
        color: #94a3b8;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .ago-badge {
        background: #f1f5f9;
        color: #64748b;
        padding: 1px 5px;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: 600;
        border: 1px solid #e2e8f0;
    }
    .type-badge {
        font-size: 0.65rem;
        font-weight: 700;
        padding: 1px 5px;
        border-radius: 4px;
        text-transform: uppercase;
    }
    .type-badge.buy { background-color: #eff6ff; color: #2563eb; border: 1px solid #dbeafe; }
    .type-badge.search { background-color: #fff7ed; color: #ea580c; border: 1px solid #ffedd5; }

    .timeline-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 12px 16px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }
    .event-title {
        font-weight: 700;
        font-size: 0.9rem;
        color: #334155;
        margin-bottom: 4px;
    }
    .price-highlight { color: #dc2626; font-weight: 700; font-size: 0.85rem; }
    .search-term { font-size: 1rem; font-weight: 700; color: #ea580c; }
    .review-box {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 8px;
        font-size: 0.8rem;
        color: #475569;
        margin-top: 8px;
    }

    /* 6. 추천 상품 카드 (Read Only) */
    .product-card-list {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 16px;
        border: 1px solid #e2e8f0;
        margin-bottom: 12px;
        position: relative;
    }
    .product-title-rec {
        font-size: 0.95rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 6px;
    }
    .rec-meta {
        font-size: 0.8rem;
        color: #64748b;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
    }
    .price-tag-rec { color: #dc2626; font-weight: 700; font-size: 0.9rem; }

    /* 7. Tabs & Eval Box */
    .stTabs [data-baseweb="tab-list"] { gap: 4px; margin-bottom: 12px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px;
        padding: 6px 12px; font-size: 0.85rem;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #eff6ff; color: #2563eb; border-color: #bfdbfe; font-weight: 700;
    }

    .reason-box {
        padding: 14px; 
        background: linear-gradient(to right, #f8fafc, #ffffff); 
        border-left: 3px solid #6366f1; 
        border-radius: 4px; 
        color: #334155; 
        margin-bottom: 10px; 
        font-size: 0.9rem; 
        line-height: 1.5; 
        border: 1px solid #f1f5f9; 
        border-left-width: 3px;
    }

    /* 8. Stats Dashboard */
    .stats-container {
        background-color: #f1f5f9;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 20px;
        margin-top: 40px;
    }
    .stats-header {
        font-size: 1.1rem;
        font-weight: 700;
        color: #334155;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .stats-sub-header {
        font-size: 1rem;
        font-weight: 600;
        color: #475569;
        margin-top: 20px;
        margin-bottom: 10px;
        border-top: 1px dashed #cbd5e1;
        padding-top: 15px;
    }
</style>
""", unsafe_allow_html=True)


# --- UTILITY FUNCTIONS ---

def check_password():
    def password_entered():
        if st.session_state.get("password") == DEMO_PASSWORD:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        st.markdown("### 🔐 Access Required")
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        if "password_correct" in st.session_state and not st.session_state["password_correct"]:
            st.error("비밀번호가 올바르지 않습니다.")
        return False
    return True


def get_gdrive_id(url):
    patterns = [r'/file/d/([^/]+)', r'id=([^&]+)', r'/open\?id=([^&]+)']
    for pattern in patterns:
        match = re.search(pattern, url)
        if match: return match.group(1)
    return None


@st.cache_data(show_spinner=False)
def load_data_from_gdrive(url):
    file_id = get_gdrive_id(url)
    if not file_id: raise ValueError("올바르지 않은 구글 드라이브 링크입니다.")
    download_url = f'https://drive.google.com/uc?id={file_id}'
    df = pd.read_csv(download_url, dtype=str, low_memory=False)
    return df


def safe_parse(val):
    if pd.isna(val) or str(val).lower() == 'nan' or val == "": return None
    try:
        # Tries to evaluate as a Python literal (list, dict, etc.)
        return ast.literal_eval(val)
    except:
        try:
            # Tries to parse as JSON string
            return json.loads(val)
        except:
            # Returns raw string if parsing fails
            return val


def format_tags_to_html(tags_data, limit=None, highlight_tags=None):
    tags_list = []
    if isinstance(tags_data, list):
        tags_list = tags_data
    elif isinstance(tags_data, str):
        # Handle comma-separated string, even with extra whitespace/artifacts
        tags_list = [tag.strip() for tag in tags_data.split(',') if tag.strip()]

    if limit: tags_list = tags_list[:limit]

    html = ""
    for t in tags_list:
        extra_class = " highlight" if highlight_tags and t in highlight_tags else ""
        html += f"<span class='simple-tag{extra_class}'>{t}</span>"
    return html


def extract_tags_list(tags_data):
    if isinstance(tags_data, list):
        return tags_data
    elif isinstance(tags_data, str):
        return [tag.strip() for tag in tags_data.split(',') if tag.strip()]
    return []


# 2. NameError를 해결하기 위해 'parse_analysis_time' 함수 정의 추가
def parse_analysis_time(time_string):
    """
    Parses a time string (e.g., '2023-10-27 15:30') into a datetime object.

    Args:
        time_string (str): The time string to parse. Expected format: YYYY-MM-DD HH:MM

    Returns:
        datetime.datetime: The parsed datetime object, or None if parsing fails.
    """
    if not time_string: return None
    try:
        # Format adjusted to match 'YYYY-MM-DD HH:MM' in the user history logs
        return datetime.datetime.strptime(time_string, '%Y-%m-%d %H:%M')
    except ValueError as e:
        # print(f"Error parsing time string '{time_string}': {e}") # Log removed to keep console clean
        return None


# --- METRIC CALCULATION FUNCTIONS (QUANTITATIVE) ---

def calculate_jaccard_similarity(list1, list2):
    s1 = set(list1)
    s2 = set(list2)
    if not s1 and not s2: return 0.0
    return len(s1.intersection(s2)) / len(s1.union(s2))


def calculate_quantitative_metrics(target_tags_list, products_list):
    """
    Calculates A, B, C quantitative metrics for a single theme/pool.
    target_tags_list: List of strings (Ground Truth tags)
    products_list: List of dicts (Recommended products)
    """
    if not target_tags_list or not products_list:
        return 0.0, 0.0, 0.0

    # Prepare recommended tags per product
    rec_tags_per_prod = []
    for p in products_list:
        rec_tags_per_prod.append(extract_tags_list(p.get('tags', [])))

    # A. Average Theme-Level Tag coverage (Jaccard Avg)
    jaccard_sum = 0
    for prod_tags in rec_tags_per_prod:
        jaccard_sum += calculate_jaccard_similarity(prod_tags, target_tags_list)
    metric_a = jaccard_sum / len(products_list) if products_list else 0.0

    # B. Average Product-Level Tag coverage (Frequency based)
    # 분자: 타겟 태그와 매칭되는 모든 추천 태그들의 빈도 수 합계
    # 분모: 추천된 모든 상품의 전체 태그 빈도 수 합계
    numerator_b = 0
    denominator_b = 0
    target_set = set(target_tags_list)

    for prod_tags in rec_tags_per_prod:
        denominator_b += len(prod_tags)
        numerator_b += sum(1 for t in prod_tags if t in target_set)

    metric_b = numerator_b / denominator_b if denominator_b > 0 else 0.0

    # C. Average Product-Level Tag match (Relevance ratio)
    # 분자: 타겟 태그 집합과 1개 이상 매칭되는 상품 수
    match_count = 0
    for prod_tags in rec_tags_per_prod:
        if set(prod_tags).intersection(target_set):
            match_count += 1

    metric_c = match_count / len(products_list) if products_list else 0.0

    return metric_a, metric_b, metric_c


# --- TIMELINE PARSING (MODIFIED) ---

def parse_user_history(text):
    if not text: return []
    events = []
    current_event = None

    # State flags for nested parsing
    current_context = "main_product"  # possible values: main_product, review, related_product
    current_related_product = {}

    lines = text.split('\n')
    header_pattern = re.compile(r'-\s+\[(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2})\s+\|\s+(.*?)\]\s+(.*)')

    for line in lines:
        line = line.strip()

        # 1. Check for new event start (Always resets state)
        header_match = header_pattern.match(line)
        if header_match:
            if current_event:
                if current_related_product:
                    current_event["details"]["related_product"] = current_related_product
                events.append(current_event)

            date, time, ago, action_type = header_match.groups()
            current_event = {
                "date": date, "time": time, "ago": ago,
                "type": action_type.strip(), "details": {}
            }
            # Reset state for new event
            current_context = "main_product"
            current_related_product = {}
            continue

        if not current_event: continue

        # 2. Check for context switches (headers)
        if line.startswith("[상품 정보]"):
            current_context = "main_product"
            continue
        if line.startswith("[리뷰 정보]"):
            current_context = "review"
            continue
        if line.startswith("[다른 사용자가 구매한 관련 상품 (참고)]"):
            current_context = "related_product"
            current_related_product = {}  # Start new related product object
            continue

        # 3. Handle data lines

        # Check for related search terms (only in Search events, flat structure)
        if current_event.get("type") == "검색" and line.startswith("- 다른 사용자가 검색한 관련 검색어(참고):"):
            terms = line.split(":", 1)[1].strip()
            # Clean up any surrounding quotes/whitespace and split by comma
            terms_list = [t.strip() for t in terms.split(',') if t.strip()]
            current_event["details"]["related_search_terms"] = terms_list
            continue

        # Check for general detail line (starts with - and contains a colon)
        if line.startswith("-") and ":" in line:
            try:
                key_val = line[1:].split(":", 1)
                key = key_val[0].strip()
                value = key_val[1].strip()
            except IndexError:
                # Malformed line, skip it
                continue

            # Map key to internal event structure based on context
            if current_context == "related_product":
                # Store attributes for the related product being built
                if key == "name":
                    current_related_product["product_name"] = value
                elif key == "price":
                    current_related_product["price"] = value
                elif key == "category":
                    current_related_product["category"] = value
                elif key == "tags":
                    current_related_product["tags"] = value

            elif current_context == "main_product" or current_context == "review":
                # Store attributes for the main event details
                if key == "name":
                    current_event["details"]["product_name"] = value
                elif key == "price":
                    current_event["details"]["price"] = value
                elif key == "category":
                    current_event["details"]["category"] = value
                elif key == "tags":
                    current_event["details"]["tags"] = value
                elif key == "search_term":
                    current_event["details"]["search_term"] = value
                elif key == "review_score":
                    current_event["details"]["score"] = value
                elif key == "review_content":
                    # Remove surrounding quotes from review content if present
                    if value.startswith('"') and value.endswith('"'): value = value[1:-1]
                    current_event["details"]["review"] = value.strip()
                # Ignoring other specific review/purchase_option fields for simplicity

    # Final attachment of related product if parsed
    if current_event and current_related_product:
        current_event["details"]["related_product"] = current_related_product

    if current_event: events.append(current_event)
    return events


# --- TIMELINE RENDERING (MODIFIED) ---

def render_timeline(events):
    html = '<div class="timeline-container">'
    for event in events:
        details = event['details']
        is_buy = "구매" in event['type']
        type_class = "type-buy" if is_buy else "type-search"
        badge_text = "구매" if is_buy else "검색"
        badge_cls = "buy" if is_buy else "search"

        html += f'<div class="timeline-item {type_class}">'
        html += '<div class="timeline-dot"></div>'
        html += '<div class="timeline-date">'
        html += f'<span style="font-family:monospace; letter-spacing:-0.5px;">{event["date"]} {event["time"]}</span>'
        html += f'<span class="ago-badge">{event["ago"]}</span>'
        html += f'<span class="type-badge {badge_cls}">{badge_text}</span>'
        html += '</div>'
        html += '<div class="timeline-card">'

        if is_buy:
            p_name = details.get('product_name', '상품명 없음')
            p_price = details.get('price', '')
            p_cat = details.get('category', '')
            tags = details.get('tags', '')
            tags_html = format_tags_to_html(tags, limit=5)

            html += f'<div class="event-title">{p_name}</div>'
            html += '<div class="event-meta">'
            html += f'<span class="price-highlight">{p_price}</span> '
            html += '<span style="color:#cbd5e1;">|</span> '
            html += f'<span>{p_cat}</span>'
            html += '</div>'
            html += f'<div style="margin-bottom:6px;">{tags_html}</div>'

            if details.get('review'):
                review_text = details["review"].replace("\n", "<br>")
                html += '<div class="review-box">'
                html += f'<span style="font-weight:700; color:#f59e0b; display:block; margin-bottom:4px;">⭐ {details.get("score", "").split("/")[0].strip()}</span>'
                html += f'<span>"{review_text}"</span>'
                html += '</div>'

            # --- [NEW] Related Product Display ---
            related_prod = details.get('related_product')
            if related_prod and related_prod.get('product_name'):
                r_name = related_prod.get('product_name', '관련 상품명 없음')
                r_price = related_prod.get('price', '')
                r_cat = related_prod.get('category', '')
                r_tags = format_tags_to_html(related_prod.get('tags', ''), limit=3)

                html += '<div style="margin-top:12px; padding-top:12px; border-top:1px dashed #e2e8f0;">'
                html += '<div style="font-size:0.75rem; color:#1e40af; font-weight:600; margin-bottom:6px;">🔗 관련 상품 (다른 사용자 구매)</div>'
                html += f'<div style="font-size:0.85rem; font-weight:600; color:#334155;">{r_name}</div>'
                html += f'<div style="font-size:0.8rem; color:#64748b;">{r_cat} | <span style="color:#dc2626;">{r_price}</span></div>'
                html += f'<div style="margin-top:4px;">{r_tags}</div>'
                html += '</div>'
            # ------------------------------------

        else:  # is_search
            term = details.get('search_term', '-')
            html += f'<div class="search-term">"{term}"</div>'

            # --- [NEW] Related Search Terms Display ---
            related_terms = details.get('related_search_terms')
            if related_terms:
                terms_html = format_tags_to_html(related_terms, limit=5)
                html += '<div style="margin-top:8px; padding-top:8px; border-top:1px dashed #e2e8f0;">'
                html += '<div style="font-size:0.75rem; color:#ca8a04; font-weight:600; margin-bottom:4px;">🔗 관련 검색어 (다른 사용자)</div>'
                html += f'<div>{terms_html}</div>'
                html += '</div>'
            # ------------------------------------------

        html += "</div></div>"
    html += "</div>"
    return html


# --- ANALYTICS & DASHBOARD ---
# ... (display_aggregate_stats function remains unchanged) ...

def display_aggregate_stats():
    """
    Displays accumulated qualitative AND quantitative metrics.
    """

    st.markdown("""
    <div class="stats-container">
        <div class="stats-header">📊 누적 평가 리포트</div>
    </div>
    """, unsafe_allow_html=True)

    # 1. 정성 평가 집계
    total_evaluated_users = len(st.session_state.theme_evals)

    # Explainability
    all_theme_evals = [val for user_evals in st.session_state.theme_evals.values() for val in user_evals.values()]
    total_themes_checked = len(all_theme_evals)
    positive_reasons = sum(all_theme_evals)
    explainability_score = (positive_reasons / total_themes_checked * 100) if total_themes_checked > 0 else 0.0

    # Diversity (Theme 2,3)
    diversity_checks = []
    for u_id, evals in st.session_state.theme_evals.items():
        for t_idx, is_good in evals.items():
            if t_idx >= 1:
                diversity_checks.append(is_good)
    total_diversity_checked = len(diversity_checks)
    positive_diversity = sum(diversity_checks)
    diversity_score = (positive_diversity / total_diversity_checked * 100) if total_diversity_checked > 0 else 0.0

    # Semantic Reasoning - This metric seems unused/not well-defined based on original code structure
    # all_tag_counts = [len(tags) for tags in st.session_state.tag_evals.values()]
    # avg_tags_per_user = sum(all_tag_counts) / len(all_tag_counts) if all_tag_counts else 0.0

    # 2. 정량 평가 집계 (Avg of stored quant metrics)
    # st.session_state.quant_stats = {user_id: (a, b, c)}
    if 'quant_stats' not in st.session_state:
        st.session_state.quant_stats = {}

    quant_values = list(st.session_state.quant_stats.values())
    count_q = len(quant_values)

    avg_a = sum([q[0] for q in quant_values]) / count_q if count_q > 0 else 0.0
    avg_b = sum([q[1] for q in quant_values]) / count_q if count_q > 0 else 0.0
    avg_c = sum([q[2] for q in quant_values]) / count_q if count_q > 0 else 0.0

    # --- Display ---
    st.markdown(
        '<div style="font-size:0.95rem; font-weight:700; color:#475569; margin-bottom:12px;">1. 정성 평가 (Qualitative)</div>',
        unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("평가 진행 유저 수", f"{total_evaluated_users}명")
    with col2:
        st.metric("설명 가능성 (전체)", f"{explainability_score:.1f}%", f"{positive_reasons}/{total_themes_checked} 건",
                  delta_color="off")
    with col3:
        st.metric("탐색 다양성 (Theme 2,3)", f"{diversity_score:.1f}%", f"{positive_diversity}/{total_diversity_checked} 건",
                  delta_color="off")

    st.markdown('<div class="stats-sub-header">2. 보완된 정량 평가 (Quantitative Average)</div>', unsafe_allow_html=True)
    q_col1, q_col2, q_col3 = st.columns(3)
    with q_col1:
        st.metric("A. Avg Theme Tag Coverage", f"{avg_a:.3f}")
    with q_col2:
        st.metric("B. Avg Product Tag Coverage", f"{avg_b:.3f}")
    with q_col3:
        st.metric("C. Avg Product Tag Match", f"{avg_c:.3f}")


# --- MAIN APPLICATION ---

def display_main_content(df):
    if 'user_idx' not in st.session_state: st.session_state.user_idx = 0
    if 'theme_evals' not in st.session_state: st.session_state.theme_evals = {}
    if 'tag_evals' not in st.session_state: st.session_state.tag_evals = {}
    if 'quant_stats' not in st.session_state: st.session_state.quant_stats = {}  # 정량 지표 저장소

    user_ids = df['user_id'].unique()
    total_users = len(user_ids)

    # --- [MODIFIED LOGIC] END SCREEN CHECK ---
    # 유저 인덱스가 전체 유저 수 이상이면 "평가 완료" 화면(누적 리포트)만 출력
    if st.session_state.user_idx >= total_users:
        st.title("🎉 모든 평가가 완료되었습니다!")
        st.info("수고하셨습니다. 아래는 최종 집계된 누적 평가 리포트입니다.")
        display_aggregate_stats()

        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🔄 처음부터 다시 하기", use_container_width=True):
            st.session_state.user_idx = 0
            st.rerun()
        return  # 함수 종료 (개별 유저 상세 화면 렌더링 안 함)

    # --- NORMAL FLOW (평가 진행 중) ---
    curr_user_id = user_ids[st.session_state.user_idx]

    if curr_user_id not in st.session_state.theme_evals: st.session_state.theme_evals[curr_user_id] = {}
    if curr_user_id not in st.session_state.tag_evals: st.session_state.tag_evals[curr_user_id] = []

    # Navigation
    with st.container():
        col_nav_1, col_nav_2, col_nav_3 = st.columns([2, 4, 1.5], gap="small")
        with col_nav_1:
            st.markdown(f"""
            <div style="display:flex; align-items:center; gap:10px;">
                <span style="font-size:1.5rem;">👤</span>
                <div>
                    <div style="font-size:0.8rem; color:#64748b; font-weight:600;">CURRENT USER</div>
                    <div style="font-size:1.3rem; font-weight:800; color:#0f172a;">{curr_user_id}</div>
                </div>
            </div>""", unsafe_allow_html=True)
        with col_nav_2:
            current_progress_idx = st.session_state.user_idx + 1
            st.write("");
            st.progress(current_progress_idx / total_users)
            st.markdown(
                f"<div style='text-align:right; font-size:0.8rem; color:#64748b; margin-top:-5px;'>진행률: {current_progress_idx} / {total_users}</div>",
                unsafe_allow_html=True)
        with col_nav_3:
            st.write("")
            # [MODIFIED LOGIC] Next User Button
            # 마지막 유저일 때 누르면 user_idx가 total_users가 되어 위쪽 '완료 화면' 조건에 걸리게 됨
            btn_label = "다음 유저 보기 ➡️" if current_progress_idx < total_users else "평가 완료 및 리포트 보기 🏁"
            if st.button(btn_label, use_container_width=True):
                st.session_state.user_idx += 1  # 단순히 1 증가 (modulo 제거)
                st.rerun()

    user_rows = df[df['user_id'] == curr_user_id]
    row = user_rows.iloc[0]
    st.markdown("<div style='margin-bottom:20px; border-bottom:1px solid #e2e8f0;'></div>", unsafe_allow_html=True)

    # Parsing
    prompts_data = safe_parse(row.get('prompts'))
    user_history_text = prompts_data['user_prompt'] if isinstance(prompts_data, dict) else (
        row.get('prompts') if isinstance(row.get('prompts'), str) else "")

    # 3. 'parse_analysis_time' 호출 로직 수정
    analysis_time = None
    if user_history_text:
        # 사용자 기록 텍스트에서 분석 기준 시점(가장 최근 이벤트 시간) 추출
        matches = re.findall(r'\[(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})', user_history_text)
        time_string_for_parsing = matches[-1] if matches else None

        parsed_dt = parse_analysis_time(time_string_for_parsing)
        # datetime 객체를 출력용 문자열로 다시 포맷
        analysis_time = parsed_dt.strftime('%Y-%m-%d %H:%M') if parsed_dt else None

    llm_result = safe_parse(row.get('theme_results'))
    themes = llm_result if isinstance(llm_result, list) else (
        llm_result.get('recommendation_themes', llm_result.get('themes', [])) if isinstance(llm_result, dict) else [])

    # Calculate Data for Quant Metrics
    target_tags_raw = safe_parse(row.get('target_tags', ''))
    target_tags_list = extract_tags_list(target_tags_raw)

    theme_0_tags = []
    quant_metrics = (0.0, 0.0, 0.0)

    if themes:
        # Theme 1 Tags for Eval
        t0_products = themes[0].get('recommendations',
                                    themes[0].get('recommended_products', themes[0].get('products', [])))
        all_theme_tags = set()
        for prod in t0_products:
            all_theme_tags.update(extract_tags_list(prod.get('tags', [])))
        theme_0_tags = sorted(list(all_theme_tags))

        # Calculate A, B, C based on Theme 1 (First pool) vs Target
        quant_metrics = calculate_quantitative_metrics(target_tags_list, t0_products)

        # Save current user quant stats to session
        st.session_state.quant_stats[curr_user_id] = quant_metrics

    # Layout
    col1, col2, col3 = st.columns([1.1, 1.1, 0.8], gap="medium")

    # Col 1: History
    with col1:
        st.markdown('<div class="section-header">💬 User History</div>', unsafe_allow_html=True)
        history_events = parse_user_history(user_history_text)
        if history_events:
            container_style = "height: 75vh; overflow-y: auto; padding-right: 10px; scrollbar-width: thin;"
            st.markdown(f'<div style="{container_style}">{render_timeline(history_events)}</div>',
                        unsafe_allow_html=True)
        else:
            st.warning("히스토리 파싱 실패")
            st.text_area("Raw Text", user_history_text, height=600)

    # Col 2: Themes
    with col2:
        header_html = '<div class="section-header"><span>✨ Themes & Reasons</span>'
        if analysis_time: header_html += f'<span class="time-badge">🕒 기준시점 {analysis_time}</span>'
        header_html += '</div>'
        st.markdown(header_html, unsafe_allow_html=True)

        if not themes:
            st.info("추천 결과가 없습니다.")
        else:
            tab_titles = [t.get('theme_title', t.get('title', f'Theme {i + 1}')) for i, t in enumerate(themes)]
            tabs = st.tabs(tab_titles)
            for t_idx, theme in enumerate(themes):
                with tabs[t_idx]:
                    with st.container(height=700, border=False):
                        reason = theme.get('theme_reason', theme.get('reason', ''))
                        if reason:
                            st.markdown(
                                f"<div class='reason-box'><strong style='color:#4f46e5; display:block; margin-bottom:4px;'>💡 Reason</strong>{reason}</div>",
                                unsafe_allow_html=True)

                        eval_key = f"theme_eval_{curr_user_id}_{t_idx}"
                        default_val = st.session_state.theme_evals[curr_user_id].get(t_idx, False)
                        st.session_state.theme_evals[curr_user_id][t_idx] = st.toggle("이 추천 사유가 적절합니까?",
                                                                                      value=default_val, key=eval_key)

                        st.divider()
                        products = theme.get('recommendations',
                                             theme.get('recommended_products', theme.get('products', [])))
                        st.caption(f"추천 상품 목록 ({len(products)}개)")

                        highlights = st.session_state.tag_evals[curr_user_id] if t_idx == 0 else []
                        for prod in products:
                            p_name = prod.get('product_name', prod.get('name', '이름 없음'))
                            p_price = prod.get('price', 0)
                            p_cat = prod.get('category', '기타')
                            try:
                                # Safe float conversion for formatting
                                p_price_fmt = f"{int(float(str(p_price).replace(',', '').replace('원', '').strip())):,}원"
                            except:
                                p_price_fmt = f"{p_price}원"
                            p_tags = format_tags_to_html(prod.get('tags', ''), highlight_tags=highlights)

                            st.markdown(f"""
                            <div class="product-card-list">
                                <div class="product-title-rec">{p_name}</div>
                                <div class="rec-meta"><span class="price-tag-rec">{p_price_fmt}</span><span style="margin:0 6px; color:#cbd5e1;">|</span><span style="font-weight:500;">{p_cat}</span></div>
                                <div>{p_tags}</div>
                            </div>""", unsafe_allow_html=True)

    # Col 3: Target & Eval
    with col3:
        st.markdown('<div class="section-header">🎯 Actual Target</div>', unsafe_allow_html=True)

        t_name = row.get('target_product_name', '정보 없음')
        t_cat = row.get('target_category', '-')
        t_tags = format_tags_to_html(target_tags_list)

        st.markdown(f"""
        <div class="target-box">
            <div class="target-label"><span>🎯</span> GROUND TRUTH</div>
            <div class="target-title">{t_name}</div>
            <div style="margin-bottom:12px;"><span class="category-badge">{t_cat}</span></div>
            <div style="border-top:1px dashed #e2e8f0; padding-top:12px; margin-top:12px;">
                <div style="font-size:0.8rem; color:#64748b; margin-bottom:6px; font-weight:600;">Target Tags</div>
                {t_tags}
            </div>
        </div>""", unsafe_allow_html=True)

        if theme_0_tags:
            st.markdown(
                f"<div class='eval-box'><div class='eval-label'><span>📝</span> EVALUATION (Theme 1)</div></div>",
                unsafe_allow_html=True)

            # --- FIXED SECTION START: Multiselect Callback Logic ---
            saved_tags = st.session_state.tag_evals[curr_user_id]
            valid_defaults = [t for t in saved_tags if t in theme_0_tags]

            # Key for the widget
            widget_key = f"tag_select_{curr_user_id}"

            # Callback to update state immediately upon interaction
            def update_tag_state():
                st.session_state.tag_evals[curr_user_id] = st.session_state[widget_key]

            st.multiselect(
                "아래는 첫번째 테마 상품들의 태그 목록입니다. 태그 중 위 ground truth 상품의 제목, 태그, 카테고리를 참고하여 상품과 어울리는 적합한 태그를 모두 선택하세요 (정량 한계 보완):",
                options=theme_0_tags,
                default=valid_defaults,
                key=widget_key,
                on_change=update_tag_state
            )
            if st.session_state.tag_evals[curr_user_id]:
                st.info("선택된 태그는 좌측 목록에서 하이라이트 됩니다.")

    # 평가 진행 중에도 하단에 리포트가 보이길 원하시면 아래 주석을 해제하세요.
    display_aggregate_stats()


def app_runner():
    st.title("🛍️ 추천 결과 평가 데모")
    if not check_password(): return
    if 'data' not in st.session_state or st.session_state['data'] is None:
        with st.expander("📂 데이터 파일 로드", expanded=True):
            st.info(DATA_LOADING_HELP)
            gdrive_url = st.text_input("Google Drive CSV Link")
            if st.button("Load from Drive"):
                if gdrive_url:
                    try:
                        st.session_state['data'] = load_data_from_gdrive(gdrive_url);
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
            st.markdown("<div style='text-align:center; margin:10px; color:#94a3b8;'>- OR -</div>",
                        unsafe_allow_html=True)
            uploaded = st.file_uploader("Upload CSV", type="csv")
            if uploaded: st.session_state['data'] = pd.read_csv(uploaded, dtype=str, low_memory=False); st.rerun()
        return
    display_main_content(st.session_state['data'])


if __name__ == "__main__":
    app_runner()