from flask import Flask, request, jsonify, Response
import time
import json
from datetime import datetime

app = Flask(__name__)

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
@app.route('/conversations', methods=['POST'])
def create_conversation():
    data = request.get_json()

    # 요청으로부터 필요 데이터 추출
    conversation_id = 0
    conversation_id = data.get('data', {}).get('conversation_id', None)
    question = data.get('data', {}).get('question', None)

    # 기존 대화가 없으면 새로 생성
    if conversation_id is None:
        global new_conversation_id
        conversation_id = new_conversation_id
        new_conversation_id += 1
        conversation_id_list.append(conversation_id)
        conversations[conversation_id] = {
            "title": '${conversation_id}', # 일단 대화 id로 지정
            "engine": "Gemini",
            "create_time": datetime.now(),
            "update_time": datetime.now(),
            "pairing": []
        }

    # 답변 생성 및 저장
    response_data = {
        'data': {
            'answer': "세종대왕은 한글을 창제하셨습니다."
        }
    }

    # 요청 메시지와 응답 메시지 저장
    conversation_data = {
        "id": len(conversations[conversation_id]['pairing']),
        "request_message": question,
        "response_message": response_data,  # 아직 응답은 없으므로 빈 문자열
        "create_time": datetime.now()
    }
    conversations[conversation_id]['pairing'].append(conversation_data)

    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True)
