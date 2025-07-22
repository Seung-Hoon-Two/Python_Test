import openai

# GPT API 키 설정
client = openai.OpenAI(api_key="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")

def ask_gpt_for_answer(question_text):
    prompt = f"""
다음 객관식 또는 OX 문제에 대해 정답 번호만 숫자로 대답해주세요. 해설이나 설명은 필요 없습니다. OX 문제는 1, 2 중 하나로 대답해주세요.

문제:
{question_text}

정답 번호만 숫자로 대답하세요.
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",  # 또는 "gpt-4"
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        answer_text = response.choices[0].message.content.strip()
        return answer_text  # 예: '2', '4', '1' 등
    except Exception as e:
        print(f"❌ GPT 응답 오류: {e}")
        return None