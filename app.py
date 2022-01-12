from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta


app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

client = MongoClient('localhost', 27017)
db = client.week1Project


#####메인페이지 토큰을 가져와서 해당유저데이터 불러오기('/')######
@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        return render_template('index.html', user_info=user_info)

    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


#####로그인하면 메세지 띄우기(/login)######
@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


#####유저네임을 통해서 프로필 페이지 보여주기(/user)######
@app.route('/user/<username>')
def user(username):
    # 각 사용자의 프로필과 글을 모아볼 수 있는 공간
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        status = (username == payload["id"])  # 내 프로필이면 True, 다른 사람 프로필 페이지면 False

        user_info = db.users.find_one({"username": username}, {"_id": False})
        return render_template('user.html', user_info=user_info, status=status)  #status를 이용해서 프로필 수정 보이기/숨기기
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


#####유저네임과 pw 데이터 받고 payload, 토큰 넘겨주기(/login)######
@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
            'id': username_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})



#####유저네임과 pw, 프로필이름, 프로필사진, 프로필 한 마디 db에 저장(/login)######
@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,  # 아이디
        "password": password_hash,  # 비밀번호
        "profile_name": username_receive,  # 프로필 이름 기본값은 아이디
        "profile_pic": "",  # 프로필 사진 파일 이름
        "profile_pic_real": "profile_pics/profile_placeholder.png",  # 프로필 사진 기본 이미지
        "profile_info": ""  # 프로필 한 마디
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


#####아이디 중복체크(/login)######
@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})


#####프로필페이지에서 프로필 사진업로드(/user)######
@app.route('/update_profile', methods=['POST'])
def save_img():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username = payload["id"]
        name_receive = request.form["name_give"]
        about_receive = request.form["about_give"]
        new_doc = {
            "profile_name": name_receive,
            "profile_info" : about_receive
        }

        if 'file_give' in request.files:
            file = request.files["file_give"]
            filename = secure_filename(file.filename)
            extension = filename.split(".")[-1]
            file_path = f"profile_pics/{username}.{extension}"

            file.save("./static/"+file_path)
            new_doc["profile_pic"] = filename
            new_doc["profile_pic_real"] = file_path
        db.users.update_one({'username': payload['id']}, {'$set': new_doc})

        return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


#게시물 포스팅
@app.route('/posting', methods=['POST'])
def posting():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        # 포스팅하기
        user_info = db.users.find_one({"username": payload["id"]})
        contents_receive = request.form["contents_give"]
        place_pic = request.files["place_pic_give"]
        date_receive = request.form["date_give"]

        filename = secure_filename(place_pic.filename)
        extension = filename.split('.')[-1]
        today = datetime.now()
        mytime = today.strftime('%Y%m%d%H%M%S')

        picname = f'place_pic-{mytime}'
        save_to = f'static/place_pic/{picname}.{extension}'

        place_pic.save(save_to)

        doc = {
            "username": user_info["username"],
            "profile_name": user_info["profile_name"],
            "contents": contents_receive,
            "place_pic": f'{picname}.{extension}',
            "date": date_receive
        }

        db.posts.insert_one(doc)
        return jsonify({"result": "success", 'msg': '포스팅 성공~'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


# 전체게시물 보여주기
@app.route('/listing', methods=['GET'])
def listing():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username_receive = request.args.get("username_give")
        if username_receive == "":
            posts = list(db.posts.find())
        else:
            posts = list(db.posts.find({"username": username_receive}))
        for post in posts:
            post["_id"] = str(post["_id"])
            post["count_heart"] = db.likes.count_documents({"post_id": post["_id"], "type": "heart"}) #해당 글의 like 갯수를 파악
            post["heart_by_me"] = bool(db.likes.find_one({"post_id": post["_id"], "type": "heart", "username": payload['id']}))#jwt토큰을 확인해서 username을 꺼내고 like타입을 확인해서 해당 게시글에 내 정보가 있으면 내가 좋아요를 눌렀는지 알게 됨
        return jsonify({"result": "success", "msg": "포스팅을 가져왔습니다.", "posts": posts})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))



@app.route('/update_like', methods=['POST'])
def update_like():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])  # 토큰 가져와서
        user_info = db.users.find_one({"username": payload["id"]})  # 누가 좋아요를 눌렀는지 확인하고
        post_id_receive = request.form["post_id_give"]  # 포스트의 오브젝트를 확인하고
        type_receive = request.form["type_give"]  # 어떤 종류의 좋아요인지
        action_receive = request.form["action_give"]  # 실행하는건지 취소하는건지 액션확인해서
        doc = {
            "post_id": post_id_receive,
            "username": user_info["username"],
            "type": type_receive
        }
        if action_receive == "like":  # 실행하는거면 저장
            db.likes.insert_one(doc)
        else:  # 아니면 삭제
            db.likes.delete_one(doc)

        count = db.likes.count_documents({"post_id": post_id_receive, "type": type_receive})  # 동작 완료 후 좋아요 개수 확인해서
        return jsonify({"result": "success", 'msg': 'updated', "count": count})  # 클라이언트로 넘겨줌
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))



# 게시물 상세페이지 보여주기
@app.route('/pic_detail', methods=['GET'])
def showing():
    post = list(db.post.find({}, {'_id': False}))

    return render_template("detail.html", post=post)



if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)