import os
from flask import Flask, jsonify, request, render_template


from flask_jwt_extended import JWTManager, create_access_token, unset_jwt_cookies
from flask_jwt_extended import jwt_required, get_jwt_identity
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId

from datetime import datetime, timedelta

import hashlib

app = Flask(__name__)

app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token'
app.config['JWT_SECRET_KEY'] = 'DEV'
# app.config["JWT_COOKIE_SECURE"] = False
app.config["JWT_COOKIE_CSRF_PROTECT"] = False

jwt = JWTManager(app)
load_dotenv()
uri = os.getenv("MONGO_URI")
client = MongoClient(uri,server_api=ServerApi('1'))
db = client.jungmo
#JWt 토큰을 만들 때 필요한 Secret Key

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/main')
@jwt_required()
def main():
    jwt_id = get_jwt_identity()
    user = db.users.find_one({'id': jwt_id})
    return render_template('main.html', user_id=user['id'])

@app.route('/joinMeet')
@jwt_required()
def joinMeet():
    jwt_id = get_jwt_identity()
    user = db.users.find_one({'id': jwt_id})
    return render_template('joinMeet.html', user_id=user['id'])


# 회원가입 API
@app.route('/api/register', methods=["POST"])
def register():
   getID = request.form['id_give']
   getPW = request.form['pw_give']
   getclass = request.form['class_give']

   #아이디 중복검증
   user = db.users.find_one({'id':getID})

   if user:
    return jsonify({
        'result': 'fail',
        'msg': '중복 아이디입니다.'
    })
   
    #비밀번호 암호화
   crypted_pw = hashlib.sha256(getPW.encode('utf-8')).hexdigest()

    #약속된 변수 이름에 맞추어 수정 요함
   db.users.insert_one({
        'id': getID,
        'pw': crypted_pw,
        'class': getclass
    })

   return jsonify({'result':'success'})

#사용자 아이디 중복여부 확인(사용자가 가입하기 버튼 클릭전 중복확인을 누를경우를 대비해 따로처리함)
@app.route('/checkID', methods=["POST"])

def checkID():
   id_give = request.form['id_give'] #사용자가 입력한 아이디 받아 디비에 중복된 아이디를찾는다
   user = db.users.find_one({'id':id_give})

   if user:
      return jsonify({
         'result':'fail',
         'msg':'중복아이디 입니다'})
   return jsonify({
        'result': 'success',
        'msg': '사용 가능한 아이디입니다.'
        })

#로그인 기능


# 로그인 API
@app.route('/api/login', methods=["POST"])
def login():
    # print("1. 로그인 함수 진입")
    getID = request.form['id_give']
    getPW = request.form['pw_give']
    # print("2. id.pw 받음", getID)
    crypted_pw = hashlib.sha256(getPW.encode('utf-8')).hexdigest()
    # print("3. PW hasing")
    result = db.users.find_one({'id':getID, 'pw':crypted_pw})
    # print("4. DB searched.")
    if result :
        # JWT 토큰 생성 (timedelta의 매개변수로 유효시간 조절)
        # print("5. Login Success")
        expires = timedelta(minutes=60)
        access_token = create_access_token(
            identity = getID,
            expires_delta = expires,
        )
        # print("6. JWT Created.")
        response = jsonify({'result' : 'success', 'msg':'로그인 되었습니다.', "token": access_token})
        response.set_cookie('access_token', access_token, secure = False, samesite = 'Lax', httponly=True)
        # print("7. Cookies set")
        # return jsonify({'result':'success', 'token':token})
        return response, 200
    else:
        # print("5 Login Fail")
        return jsonify({'result':'fail','msg':'아이디 또는 비밀번호가 일치하지 않습니다.'})
        # return render_template('login.html', form=form)
@app.route('/api/logout', methods = ["POST"])
def logout():
    response = jsonify({
        'result':'success',
        'msg': '로그아웃 되었습니다'
    })

    unset_jwt_cookies(response)

    return response, 200


#crud 기능
@app.route('/post')
@jwt_required()
def post():
    jwt_id = get_jwt_identity()
    user = db.users.find_one({'id': jwt_id})
    return render_template('post.html', user_id=user['id'])

@app.route('/post/update', methods=['GET'])
@jwt_required()
def postUpdate():
    jwt_id = get_jwt_identity()
    user = db.users.find_one({'id': jwt_id})
    return render_template('postUpdate.html', user_id=user['id'])

@app.route('/meetDetail', methods=['GET'])
@jwt_required()
def meets_detail():
    meet_id = request.args.get('meet_id')
    meet = db.meet.find_one({'_id': ObjectId(meet_id)})
    jwt_id = get_jwt_identity()
    user = db.users.find_one({'id': jwt_id})
    return render_template('meetDetail.html', meet=meet, user_id=user['id'])

@app.route('/makeMeet', methods=['POST'])
@jwt_required()
def post_MakeMeet():
    title_receive = request.form['title_give']
    content_receive = request.form['content_give']
    people_receive = 1
    peopleCapacity_receive = request.form['peopleCapacity_give']
    month_receive = request.form['month_give']
    day_receive = request.form['day_give']
    time_receive = request.form['time_give']
    closeWhenFull_receive = request.form['closeWhenFull_give'] == 'true'

    user_id = get_jwt_identity()

    meet = {
        'title': title_receive,
        'content': content_receive,
        'people': people_receive,
        'peopleCapacity': peopleCapacity_receive,
        'month': month_receive,
        'day': day_receive,
        'time': time_receive,
        'closeWhenFull': closeWhenFull_receive,
        'createdAt': datetime.now(),
        'user_id': user_id,
        'user_ids': [user_id],
        'visible': True
    }

    db.meet.insert_one(meet)
    return jsonify({'result': 'success', 'msg': 'success'})

@app.route('/updateMeet', methods=['PATCH'])
def post_update_meet():
    meet_id_receive = request.form['meet_id_give']
    title_receive = request.form['title_give']
    content_receive = request.form['content_give']
    people_receive = request.form['people_give']
    month_receive = request.form['month_give']
    day_receive = request.form['day_give']
    time_receive = request.form['time_give']
    close_when_full_receive = request.form['closeWhenFull_give'] == 'true'

    db.meet.update_one(
        {'_id': ObjectId(meet_id_receive)},
        {'$set': {
            'title': title_receive,
            'content': content_receive,
            'people': people_receive,
            'month': month_receive,
            'day': day_receive,
            'time': time_receive,
            'closeWhenFull': close_when_full_receive,
            'updatedAt': datetime.now()
        }}
    )

    return jsonify({'result': 'success', 'msg': '수정되었습니다.'})


@app.route('/meets', methods=['GET'])
def read_meets():
    order_type = request.args.get('orderType', 'latest')

    if order_type == 'participants':
        result = list(
            db.meet.find({'visible': True}).sort('people', -1)
        )
    else:
        result = list(
            db.meet.find({'visible': True}).sort('createdAt', -1)
        )

    for meet in result:
        meet['_id'] = str(meet['_id'])
        meet['createdAt'] = meet['createdAt'].strftime('%Y.%m.%d %H:%M')

    return jsonify({
        'result': 'success',
        'meets': result
    })


@app.route('/joinMeets', methods=['GET'])
@jwt_required()
def read_join_meets():
    user_id = request.args.get('user_id')
    order_type = request.args.get('orderType', 'latest')

    query = db.meet.find({'user_ids': user_id})

    if order_type == "latest":
        query = query.sort("createdAt", -1)
    else:
        query = query.sort("people", -1)

    result = list(query)

    for meet in result:
        meet['_id'] = str(meet['_id'])
        meet['createdAt'] = meet['createdAt'].strftime('%Y.%m.%d %H:%M')

    return jsonify({
        'result': 'success',
        'meets': result
    })


@app.route('/meetData', methods=['GET'])
def get_meet_data():
    meet_id = request.args.get('meet_id')

    if not meet_id:
        return jsonify({'result': 'error', 'msg': 'meet_id가 없습니다.'})

    meet = db.meet.find_one({'_id': ObjectId(meet_id)})

    if not meet:
        return jsonify({'result': 'error', 'msg': '모임을 찾을 수 없습니다.'})

    meet['_id'] = str(meet['_id'])
    meet['createdAt'] = meet['createdAt'].strftime('%Y.%m.%d %H:%M')

    return jsonify({'result': 'success', 'meet': meet})



@app.route('/post/delete', methods=['DELETE'])
def meet_delete():
    meet_id = request.form.get('meet_id')

    if not meet_id:
        return jsonify({'result': 'error', 'msg': 'meet_id가 없습니다.'}), 400

    db.meet.delete_one({'_id': ObjectId(meet_id)})

    return jsonify({'result': 'success', 'msg': '삭제되었습니다.'})


@app.route('/post/join', methods=['POST'])
@jwt_required()
def meet_join():
    meet_id = request.form.get('meet_id')
    user_id = request.form.get('user_id')

    if not meet_id:
        return jsonify({'result': 'error', 'msg': 'meet_id가 없습니다.'})

    meet = db.meet.find_one({'_id': ObjectId(meet_id)})

    if not meet:
        return jsonify({'result': 'error', 'msg': '모임을 찾을 수 없습니다.'})

    if user_id in meet.get("user_ids", []):
        return jsonify({
            "result": "fail",
            "msg": "이미 참여한 모임입니다."
        })

    if int(meet["people"]) >= int(meet["peopleCapacity"]):
        return jsonify({
            "result": "error",
            "msg": "모집이 마감되었습니다."
        })

    db.meet.update_one(
        {'_id': ObjectId(meet_id)},
        {
            '$inc': {'people': 1},
            '$push': {'user_ids': user_id}
        }
    )

    current_people = int(meet["people"]) + 1

    if current_people >= int(meet["peopleCapacity"]):
        db.meet.update_one(
            {'_id': ObjectId(meet_id)},
            {
                '$set': {'visible': False}
            }
        )

    return jsonify({'result': 'success'})
scheduler = APScheduler()
@scheduler.task('interval', id='schedule_check', seconds = 5, misfire_grace_time = 900)
def schedule_check():
    query = {
        "$expr" :{
            "$gte" : ["$people", "$peopleCapacity"]
        }
    }
    results = db.find(query) # 고정 사이즈 컬렉션에서 기본 순서는 삽입 순서와 같기 때문에 먼저 추가 된 순으로 탐색

    for result in results:
        document_id = result["_id"]

        if document_id not in notified_ids:
            notification_queue.put(result) # queue에 넣었다가 빼면서 알람을 주는 대신 바로 날리면 어떻지? / 알람을 날리는 방법?
            notified_ids.add(document_id)

@app.route("/notifications")
def notifications():

    def generate():
        while True:

            time.sleep(1)
            yield f"data: 테스트 알림 \n\n" # data에는 알람 보낼 내용 채워야함

    return Response(
        generate(),
        mimetype="text/event-stream"
    )

if __name__ == '__main__':
    app.run('0.0.0.0', port=5001, debug=True)