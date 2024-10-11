import requests
# from vertexai.generative_models import (
#     FunctionDeclaration,
#     GenerationConfig,
#     GenerativeModel,
#     Part,
#     Tool,
# )
from .vertex_ai_search import search_pdf

# def tool_declarate() -> Tool:
#     # 항공 운임표 정보를 조회하는 기능
#     get_flight_fare_info = FunctionDeclaration(
#         name="get_flight_fare_info",
#         description="Retrieve flight fare information from a PDF based on departure and destination",
#         parameters={
#             "type": "object",
#             "properties": {
#                 "departure": {"type": "string", "description": "Departure city"},
#                 "destination": {"type": "string", "description": "Destination city"},
#             },
#             "required": ["departure", "destination"]
#         },
#     )


#     # 여객 운송 약관(탑승 수속, 수하물 규정 등)을 조회하는 기능
#     get_transport_policy_info = FunctionDeclaration(
#         name="get_transport_policy_info",
#         description="Retrieve transportation policy information such as check-in and baggage rules from a PDF",
#         parameters={
#             "type": "object",
#             "properties": {
#                 "policy_type": {"type": "string", "description": "Type of policy, e.g., check-in, baggage rules"},
#             },
#             "required": ["policy_type"]
#         },
#     )

#     # # 항공편 정보 조회하는 기능
#     # get_flight_info = FunctionDeclaration(
#     #     name="get_transport_policy_info",
#     # )
    
#     flight_tool = Tool(
#         function_declarations=[
#             get_flight_fare_info,
#             get_transport_policy_info,
#             # get_flight_info,
#         ],
#     )
#     return flight_tool
    
def send_chat_message(prompt:str) -> str:
    # tools=[tool_declarate()]
    
    # model = GenerativeModel(
    #     "gemini-1.5-pro-001",
    #     generation_config=GenerationConfig(temperature=0),
    #     tools=tools,
    # )
    # chat = model.start_chat()
    
    # print("prompt: " + prompt + "\n")
    # prompt += """
    # Give a concise, high-level summary. Only use information that you learn from
    # the API responses.
    # """

    # # Gemini로 채팅 메시지 보내기
    # response = chat.send_message(prompt)

    # # 함수 호출의 응답에서 값 추출
    # function_call = response.candidates[0].content.parts[0].function_call

    # # Gemini가 판단하여 호출한 함수
    # selected_function_name = function_call.name
    # print("selected_function_name: " + selected_function_name, "\n")
    answer_response = search_pdf(prompt)
    return answer_response
    
    