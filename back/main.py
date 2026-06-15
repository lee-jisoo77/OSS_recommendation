from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from recomender import recommend, get_questions

app = FastAPI(title="영화 추천 API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnswerRequest(BaseModel):
    mood:      str | None = None
    companion: str | None = None
    energy:    str | None = None
    era:       str | None = None
    ending:    str | None = None
    risk:      str | None = None
    conflict:  str | None = None
    memory:    str | None = None



@app.get("/")
def root():
    return {"message": "영화 추천 API가 실행 중입니다."}


@app.get("/questions")
def questions():
    """Streamlit이 질문 목록을 가져가는 엔드포인트"""
    return {"questions": get_questions()}


@app.post("/recommend")
def get_recommendation(body: AnswerRequest):
    """
    Streamlit이 사용자 답변을 보내면 추천 결과 반환
    요청 예시:
    {
        "mood": "친구들한테 연락해서 같이 뭔가 한다",
        "companion": "나는 어디서든 분위기 메이커다",
        ...
    }
    """
    answers = body.model_dump(exclude_none=True)
    result = recommend(answers, top_n=5)
    return result

