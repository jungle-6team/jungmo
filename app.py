from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId

app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.dbjungmo

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/post')
def post():
    return render_template('post.html')

@app.route('/post/update', methods=['GET'])
def postUpdate():
    return render_template('postUpdate.html')


@app.route('/makeMeet', methods=['POST'])
def post_MakeMeet():
    title_receive = request.form['title_give']
    content_receive = request.form['content_give']
    people_receive = request.form['people_give']
    month_receive = request.form['month_give']
    day_receive = request.form['day_give']
    time_receive = request.form['time_give']
    closeWhenFull_receive = request.form['closeWhenFull_give'] == 'true'

    meet = {
        'title': title_receive,
        'content': content_receive,
        'people': people_receive,
        'month': month_receive,
        'day': day_receive,
        'time': time_receive,
        'closeWhenFull': closeWhenFull_receive,
        'createdAt': datetime.now()
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
    result = list(db.meet.find({}).sort('createdAt', -1))

    for meet in result:
        meet['_id'] = str(meet['_id'])
        meet['createdAt'] = meet['createdAt'].strftime('%Y.%m.%d %H:%M')

    return jsonify({'result': 'success', 'meets': result})

@app.route('/meetDetail', methods=['GET'])
def meets_detail():
    meet_id = request.args.get('meet_id')
    meet = db.meet.find_one({'_id': ObjectId(meet_id)})
    return render_template('meetDetail.html', meet=meet)

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

if __name__ == '__main__':
    app.run('0.0.0.0', port=5001, debug=True)