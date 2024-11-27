import requests
from vertexai.generative_models import (
    FunctionDeclaration,
    GenerationConfig,
    GenerativeModel,
    Part,
    Tool,
)
from .vertex_ai_search import search_pdf

def delcare_functions() -> Tool:
    # 항공사 운송 약관(탑승 수속, 수하물 규정 등)을 조회
    get_airline_policy = FunctionDeclaration(
        name="get_airline_policy",  # python에서 처리해야하는 함수는 뒤에 _python postfix
        description="Retrieve airlilne policies sush as baggage rules",
        parameters={
            "type": "object",
            "properties": {
                "airline_name": {"type": "string", "description": "Airline name of the flight to be retrived about"},
            },
            "required": ["airline_name"]
        },
    )

    # 공항 정책(환승 규정, 편의 시설 위치 등)을 조회
    get_airport_policy = FunctionDeclaration(
        name="get_airport_policy",
        description="Retrieve airport policies",
        parameters={
            "type": "object",
            "properties": {
                "airport_name": {
                    "type": "string",
                    "description": "The name of the airport to retrieve policy information for."
                }
            },
            "required": ["airport_name"]
        }
    )

    # 항공편 정보 조회
    get_flight_information = FunctionDeclaration(
        name="get_flight_information",
        description="Retrieve flight detail informations",
        parameters={
            "type": "object",
            # api대로 필요한 params 수정하기
            "properties": {
                "airline_name": {"type": "string", "description": "Airline name of the flight to be retrived about"},
            },
            "required": ["airline_name"]
        },
    )

    # 항공편 예약
    book_flight = FunctionDeclaration(
        name="book_flight",
        description="Book a flight requested by the user",
        # 여기 parameters는 API에 따라 수정 필요
        parameters={
            "type": "object",
            "properties": {
                "airline_name": {"type": "string", "description": "Airline name of the flight to be retrived about"},
            },
            "required": ["airline_name"]
        },
    )
    
    # google calendar에서 비행 일정 조회
    get_schedule_to_google_calendar = FunctionDeclaration(
        name="add_schedule_to_google_calendar",
        description="Look up the flight schedule requested by the user in Google Calendar",
        # parameters는 API에 따라 수정 필요
        parameters={
            "type": "object",
            "properties": {
                "airline_name": {"type": "string", "description": "Airline name of the flight to be retrived about"},
            },
            "required": ["airline_name"]
        },
    )

    flight_tool = Tool(
        function_declarations=[
            # get_flight_fare_info,
            get_airline_policy,
            # get_airport_policy,
            get_flight_information,
            book_flight,
            # get_schedule_to_google_calendar
        ],
    )
    return flight_tool

def handle_airline_policy(prompt):
    return search_pdf(prompt)

def handle_flight_information(prompt):
    return "handle_flight_information is called."

def send_chat_message(prompt:str) -> str:
    # (멘토님 추천) Gemini 활용 사전 질문 정제 필요? (ex. 나리타-도쿄 못 찾는 경우 등)

    operations = {
        "get_airline_policy": handle_airline_policy,
        "get_flight_information": handle_flight_information
    }

    flight_tool = delcare_functions()
    system_instruction = """
    system_instruction ="Analyze the user's request and process it using the appropriate function.
    There are 3 functions, get_airline_policy, get_flight_information, and book_flight.

    <example1>
    User prompt : Can I take a knife on board the Korean Air flight?
    Predicted Tool : flight_tool
    Predicted Function : get_airline_policy
    Function parameters : {"airport_name": "Koeran Air"}
    </example1>
    <example2>
    User prompt: Can you book a flight for me from San Francisco to Tokyo next Friday?
    Predicted Tool: flight_tool
    Predicted Function: book_flight
    Function parameters: {"departure_city": "San Francisco", "destination_city": "Tokyo", "departure_date": "2024-12-01"}
    </example2>
    <example3>
    User prompt: Are there any restrictions on carrying liquids on Qatar Airways?
    Predicted Tool: flight_tool
    Predicted Function: get_airline_policy
    Function parameters: {"airline_name": "Qatar Airways"}
    </example3>
    <example4>
    User prompt: What is the baggage allowance for Emirates economy class?
    Predicted Tool: flight_tool
    Predicted Function: get_airline_policy
    Function parameters: {"airline_name": "Emirates"}
    </exampl4>
    <example5>
    User prompt: What time does Delta flight DL123 arrive in New York?
    Predicted Tool: flight_tool
    Predicted Function: get_flight_information
    Function parameters: {"flight_number": "DL123", "destination": "New York"}
    </example5>

    If you are unsure which function to use, ask the user for more information in the user's language.
    Don't answer the question directly, just find the appropriate function or ask about the additional information you need if you can't find the right function.
    """
    
    model = GenerativeModel(
        "gemini-1.5-pro-002",
        generation_config=GenerationConfig(temperature=0),
        tools=[flight_tool],
        system_instruction=system_instruction
    )
    chat = model.start_chat()

    # Gemini로 채팅 메시지 보내기
    response = chat.send_message(prompt).candidates[0].content.parts[0]

    # 함수 호출의 응답에서 값 추출
    if (response.function_call is not None):
        function_name = response.function_call.name
        ret = operations[function_name](prompt)
    else:
        ret = response.text
    # function_call = response.candidates[0].content.parts[0].function_call

    # 함수 선택
    # selected_function_name = function_call.name
    
    # answer_response = search_pdf(prompt)
    return ret
    
    