import streamlit as st
import requests

BACKEND_URL = "http://localhost:8000"

st.set_page_config(
    page_title="🎬 한국영화 추천",
    page_icon="🎬",
    layout="centered"
)

# ─────────────────────────────────────────────
# 질문 목록 가져오기
# ─────────────────────────────────────────────
@st.cache_data
def fetch_questions():
    try:
        res = requests.get(f"{BACKEND_URL}/questions", timeout=5)
        return res.json()["questions"]
    except Exception as e:
        st.error(f"백엔드 연결 실패: {e}")
        return []

questions = fetch_questions()

# ─────────────────────────────────────────────
# session_state 초기화
# ─────────────────────────────────────────────
if "step" not in st.session_state:
    st.session_state.step = 0         # 현재 질문 번호
if "answers" not in st.session_state:
    st.session_state.answers = {}     # 누적 답변
if "result" not in st.session_state:
    st.session_state.result = None    # 추천 결과

# ─────────────────────────────────────────────
# 진행 상태 표시
# ─────────────────────────────────────────────
total = len(questions)
step = st.session_state.step

st.title("🎬 나에게 딱 맞는 한국영화 추천")
st.caption("8가지 질문으로 당신의 성향을 파악해 영화를 추천해드립니다.")

# ─────────────────────────────────────────────
# 질문 화면
# ─────────────────────────────────────────────
if questions and step < total and st.session_state.result is None:

    # 진행 바
    st.progress(step / total, text=f"{step + 1} / {total}")
    st.divider()

    q = questions[step]
    st.subheader(q["question"])
    st.write("")

    selected = st.radio(
        label=q["question"],
        options=q["options"],
        index=None,
        label_visibility="collapsed",
        key=f"radio_{step}"
    )

    st.write("")
    col1, col2 = st.columns([1, 1])

    # 이전 버튼
    with col1:
        if step > 0:
            if st.button("◀ 이전", use_container_width=True):
                st.session_state.step -= 1
                st.rerun()

    # 다음 버튼
    with col2:
        if step < total - 1:
            if st.button("다음 ▶", use_container_width=True):
                if not selected:
                    st.warning("선택해주세요!")
                else:
                    st.session_state.answers[q["id"]] = selected
                    st.session_state.step += 1
                    st.rerun()
        else:
            # 마지막 질문 — 추천 버튼
            if st.button("🎬 영화 추천받기", use_container_width=True):
                if not selected:
                    st.warning("선택해주세요!")
                else:
                    st.session_state.answers[q["id"]] = selected
                    with st.spinner("당신의 성향을 분석 중입니다..."):
                        try:
                            res = requests.post(
                                f"{BACKEND_URL}/recommend",
                                json=st.session_state.answers,
                                timeout=10
                            )
                            st.session_state.result = res.json()
                            st.rerun()
                        except Exception as e:
                            st.error(f"추천 요청 실패: {e}")

# ─────────────────────────────────────────────
# 결과 화면
# ─────────────────────────────────────────────
elif st.session_state.result:
    result = st.session_state.result

    st.success(f"당신은 **{result['type']}** 입니다!")
    st.info(f"💡 {result['description']}")
    st.divider()
    st.subheader("🍿 추천 영화 5선")

    for i, movie in enumerate(result["recommendations"], 1):
        with st.expander(f"{i}. {movie['title']} ({movie['year']})  |  {movie['genre']}"):
            st.markdown(f"**감독** : {movie['director']}")
            st.markdown(f"**줄거리** : {movie['summary']}")

    st.divider()
    # 다시 하기 버튼
    if st.button("🔄 다시 추천받기", use_container_width=True):
        st.session_state.step = 0
        st.session_state.answers = {}
        st.session_state.result = None
        st.rerun()

else:
    st.error("질문을 불러오지 못했습니다. 백엔드 서버를 확인해주세요.")