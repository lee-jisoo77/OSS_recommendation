import streamlit as st
import requests

BACKEND_URL = "http://back:8000"

st.set_page_config(
    page_title="🎬 한국영화 추천",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 나에게 딱 맞는 한국영화 추천")
st.caption("8가지 질문으로 당신의 성향을 파악해 영화를 추천해드립니다.")
st.divider()


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



answers = {}

if questions:
    for q in questions:
        st.subheader(q["question"])
        selected = st.radio(
            label=q["question"],
            options=q["options"],
            index=None,
            label_visibility="collapsed",
            key=q["id"]
        )
        answers[q["id"]] = selected
        st.write("")

    st.divider()


    # 추천 버튼
   
    if st.button("🎬 나에게 맞는 영화 추천받기", use_container_width=True):
        # 미응답 항목 체크
        unanswered = [q["question"] for q in questions if not answers.get(q["id"])]
        if unanswered:
            st.warning(f"아직 답하지 않은 질문이 {len(unanswered)}개 있어요! 모두 선택해주세요.")
        else:
            with st.spinner("당신의 성향을 분석 중입니다..."):
                try:
                    res = requests.post(
                        f"{BACKEND_URL}/recommend",
                        json=answers,
                        timeout=10
                    )
                    result = res.json()

                    
                    # 결과 출력
                    
                    st.success(f"당신은 **{result['type']}** 입니다!")
                    st.info(f"💡 {result['description']}")
                    st.divider()
                    st.subheader("🍿 추천 영화 5선")

                    for i, movie in enumerate(result["recommendations"], 1):
                        with st.expander(f"{i}. {movie['title']} ({movie['year']})  |  {movie['genre']}"):
                            st.markdown(f"**감독** : {movie['director']}")
                            st.markdown(f"**줄거리** : {movie['summary']}")

                except Exception as e:
                    st.error(f"추천 요청 실패: {e}")
else:
    st.error("질문을 불러오지 못했습니다. 백엔드 서버를 확인해주세요.")