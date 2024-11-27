import google
import google.oauth2.credentials
from google.auth import compute_engine
import google.auth.transport.requests
import requests
import json
# from langchain_google_vertexai.llms import VertexAI
# from langchain.prompts import PromptTemplate
# from langchain.chains import LLMChain
from vertexai.generative_models import (
    GenerationConfig,
    GenerativeModel,
)
#from .config import PROJECT_ID, REGION, MODEL, SEARCH_URL
PROJECT_ID = ""
REGION="asia-northeast3"
MODEL = "gemini-1.5-pro-002"
SEARCH_URL = ""

import google.auth
import google.auth.transport.requests
creds, project = google.auth.default()
auth_req = google.auth.transport.requests.Request()
creds.refresh(auth_req)
id_token = creds.token


def retrieve_vertex_ai_search(question:str, search_url:str, page_size:int) -> str:
    # stream = os.popen('gcloud auth print-access-token')
    # credential_token = stream.read().strip()
    
    """ retrieve information from enterprise search ( discovery engine )"""

    # Create a credentials token to call a REST API
    headers = {
        "Authorization": "Bearer "+ id_token,
        "Content-Type": "application/json"
    }


    query_dic ={
        "query": question,
        "page_size": str(page_size),
        "offset": 0,
        "contentSearchSpec":{
            # "snippetSpec": {"maxSnippetCount": 5,
            #                 },
            # "summarySpec": { "summaryResultCount": 5,
            #                  "includeCitations": True},
            "extractiveContentSpec":{
                #"maxExtractiveAnswerCount": 3,
                "maxExtractiveSegmentCount": 2,
                "num_previous_segments" : 1,
                "num_next_segments" : 1,
                "return_extractive_segment_score" : True
              }
        },
        # "queryExpansionSpec":{"condition":"AUTO"}
    }

    data = json.dumps(query_dic)

    # Encode data as UTF8
    data=data.encode("utf8")

    response = requests.post(search_url,headers=headers, data=data)

    print(response.text)
    return response.text

def parse_discovery_results(response_text: str) -> dict:
    """Parse response to build a context to be sent to LLM."""

    # JSON 문자열을 파이썬 객체로 변환
    dict_results = json.loads(response_text)

    result_index = 0
    searched_ctx_dic = {}

    # 결과가 있는지 확인
    if dict_results.get('results'):
        for result in dict_results['results']:
            answer_ctx = ""  # 답변 내용을 저장할 변수
            segments_ctx = ""  # 세그먼트 내용을 저장할 변수

            # 문서 링크 가져오기
            reference = result['document']['derivedStructData']['link']
            derivedStructData = result['document']['derivedStructData']

            # 'extractive_answers'가 존재하는지 확인하고, 답변을 추출
            if 'extractive_answers' in derivedStructData and derivedStructData['extractive_answers']:
                for answer in derivedStructData['extractive_answers']:
                    answer_ctx += answer.get('content', '')  # 안전하게 내용 추가

            # 'extractive_segments'가 존재하는지 확인하고, 세그먼트를 추출
            if 'extractive_segments' in derivedStructData and derivedStructData['extractive_segments']:
                for segment in derivedStructData['extractive_segments']:
                    segments_ctx += segment.get('content', '')  # 안전하게 내용 추가

            # HTML 태그 및 인코딩 제거
            answer_ctx = answer_ctx.replace("<b>", "").replace("</b>", "").replace("&quot;", "")
            segments_ctx = segments_ctx.replace("<b>", "").replace("</b>", "").replace("&quot;", "")

            # Google Cloud Storage 링크로 변환
            reference_link = reference.replace("gs://", "https://storage.cloud.google.com/")

            # 결과를 딕셔너리에 저장
            item = {
                'answer_ctx': answer_ctx,
                'segments_ctx': segments_ctx,
                'reference_link': reference_link
            }

            searched_ctx_dic[f"Searched Context {result_index}"] = item
            result_index += 1

    return searched_ctx_dic

def search_pdf(question:str, SEARCH_URL:str = SEARCH_URL) -> str:
    
    page_size = 5
    searched_ctx = retrieve_vertex_ai_search(question, SEARCH_URL, page_size)
    context = parse_discovery_results(searched_ctx)
    
    # gemini_pro = VertexAI( model_name = MODEL,
    #               project=PROJECT_ID,
    #               location=REGION,
    #               verbose=True,
    #               streaming=False,
    #               temperature = 0.2,
    #               top_p = 1,
    #               top_k = 40
    #              )
    # prompt = PromptTemplate.from_template("""
    # 당신은 항공사 CS AI 어시스턴트입니다.
    # 아래 Question 에 대해서 반드시 Context에 있는 개별 내용을 기반으로 단계적으로 추론해서 근거를 설명하고 답변해주세요.
    # Context : {context}
    # Question : {question}
    # """)
    # prompt = prompt.format(context=context, question=question)
    # print(f"Prompt : {prompt}")
    # response = gemini_pro.invoke(prompt)

    model = GenerativeModel(
        "gemini-1.5-pro-002",
        generation_config=GenerationConfig(temperature=0),
    )
    chat = model.start_chat()

    # Gemini로 채팅 메시지 보내기
    prompt = f"""
    당신은 항공사 CS AI 어시스턴트입니다.
    아래 Question 에 대해서 반드시 Context에 있는 개별 내용을 기반으로 단계적으로 추론해서 근거를 설명하고 답변해주세요.
    Context : {context}
    Question : {question}
    """
    response = chat.send_message(prompt)
    print(response)

    return response.candidates[0].content.parts[0].text