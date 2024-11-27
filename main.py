from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import time
import json
from datetime import datetime
from src.react import send_chat_message

app = Flask(__name__)
CORS(app)

# Memory DB
conversations = {}
conversation_id_list = []
new_conversation_id = 0

# GET /conversations/id-list
@app.route('/conversations/id-list', methods=['GET'])
def get_id_list():
    return jsonify({"list": conversation_id_list})

# GET /conversations/{conversation_id}
@app.route('/conversations/<int:conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    conversation = conversations.get(conversation_id)
    if conversation:
        return jsonify(conversation)
    else:
        return jsonify({"error": "Conversation not found"}), 404

# POST /conversations
# @app.route('/conversations', methods=['POST'])
# def create_conversation():
#     data = request.get_json()

#     # 요청으로부터 필요 데이터 추출
#     conversation_id = 0
#     conversation_id = data.get('data', {}).get('conversation_id', None)
#     question = data.get('data', {}).get('question', None)
#     engine = data.get('data', {}).get('engine', None)

#     # error
#     if (engine is None):
#         return jsonify({"error": "Engine is not specified"}), 404

#     # 기존 대화가 없으면 새로 생성
#     if conversation_id is None:
#         global new_conversation_id
#         conversation_id = new_conversation_id
#         new_conversation_id += 1
#         conversation_id_list.append(conversation_id)
#         conversations[conversation_id] = {
#             "title": '${conversation_id}', # 일단 대화 id로 지정
#             "engine": engine,
#             "create_time": datetime.now(),
#             "update_time": datetime.now(),
#             "pairing": []
#         }
#     elif conversation_id not in conversations:
#         return jsonify({"error": "Conversation not found"}), 404

#     # 답변 생성 및 저장
#     answer = "세종대왕은 한글을 창제하셨습니다."  # 여기를 우리가 만든 모델에서 받아오게 추후 수정
#     response_data = {
#         'data': {
#             'conversation_id': conversation_id,
#             'title': conversations[conversation_id]['title'],
#             'answer': answer
#         }
#     }

#     # 요청 메시지와 응답 메시지 저장
#     conversation_data = {
#         "id": len(conversations[conversation_id]['pairing']),
#         "request_message": question,
#         "response_message": answer,
#         "create_time": datetime.now()
#     }
#     conversations[conversation_id]['pairing'].append(conversation_data)

#     return jsonify(response_data)

@app.route('/conversations', methods=['POST'])
def mvp_create_conversation():
    data = request.get_json()

    # 요청으로부터 필요 데이터 추출
    conversation_id = data.get('data', {}).get('conversation_id', 0)
    question = data.get('data', {}).get('question', None)
    engine = data.get('data', {}).get('engine', None)

    # error
    if (engine is None):
        return jsonify({"error": "Engine is not specified"}), 404

    # 기존 대화가 없으면 새로 생성
    if conversation_id is None:
        global new_conversation_id
        conversation_id = new_conversation_id
        new_conversation_id += 1
        conversation_id_list.append(conversation_id)
        conversations[conversation_id] = {
            "title": '${conversation_id}', # 일단 대화 id로 지정
            "engine": engine,
            "create_time": datetime.now(),
            "update_time": datetime.now(),
            "pairing": []
        }
    elif conversation_id not in conversations:
        return jsonify({"error": "Conversation not found"}), 404

    # 답변 생성 및 저장
    answer = send_chat_message(question)  # 여기를 우리가 만든 모델에서 받아오는 부분
    response_data = {
        'data': {
            'conversation_id': conversation_id,
            'title': "",
            'answer': answer
        }
    }

    # 요청 메시지와 응답 메시지 저장
    conversation_data = {
        "id": len(conversations[conversation_id]['pairing']),
        "request_message": question,
        "response_message": answer,
        "create_time": datetime.now()
    }
    conversations[conversation_id]['pairing'].append(conversation_data)

    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True)
