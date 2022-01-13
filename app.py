from pymongo import MongoClient
import jwt
import datetime
import hashlib
import bcrypt
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

# DB 접속
client = MongoClient('localhost', 27017)
db = client.week1Project


##### 메인페이지 토큰을 가져와서 해당유저데이터 불러오기('/')######
@app.route('/')
def home():
    # 클라이언트로 부터 토큰이 담긴 쿠키를 받는다.
    token_receive = request.cookies.get('mytoken')
    try:
        # payload 생성
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 사용자의 정보를 user_info 에 담는다.
        user_info = db.users.find_one({"username": payload["id"]})
        # index.html 로 user_info 를 넘긴다.
        return render_template('index.html', user_info=user_info)

    # 토큰이 만료되었거나 정보가 없는 경우, 로그인 페이지로  이동
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login"))


##### 로그인하면 메세지 띄우기(/login)######
@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


##### 유저네임을 통해서 프로필 페이지 보여주기(/user)######
@app.route('/user/<username>')
def user(username):
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 내 프로필이면 True, 다른 사람의 프로필 페이지면 False 의 status 값을 가진다.
        status = (username == payload["id"])

        # 사용자의 정보를 db 에서 가져와 user_info 에 담는다.
        user_info = db.users.find_one({"username": username}, {"_id": False})
        # user.html 로 user_info 와 status 값을 넘긴다.
        return render_template('user.html', user_info=user_info, status=status)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


##### 유저네임과 pw 데이터 받고 payload, 토큰 넘겨주기(/login)######
@app.route('/sign_in', methods=['POST'])
def sign_in():
    # id, pw를 받아서 맞춰보고, 토큰을 만들어 발급한다.
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    # bcrypt 로 비밀번호를 해쉬화 한다
    hash_pw = bcrypt.hashpw(password_receive.encode('utf-8'), bcrypt.gensalt())
    hashed_pw = hash_pw.decode('utf-8')
    check_pw_match = bcrypt.checkpw(password_receive.encode('utf-8'), hash_pw)
    current_user = db.users.find_one({'username': username_receive})

    # hash화 된
    if current_user and check_pw_match:
        payload = {
            'id': username_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        print(token)

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


#####유저네임과 pw, 프로필이름, 프로필사진, 프로필 한 마디 db에 저장(/login)######
@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    # 유저 아이디, 비밀번호 받아오기
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    # bcrypt로 비밀번호를 해쉬화 한다
    hash_pw = bcrypt.hashpw(password_receive.encode("utf-8"), bcrypt.gensalt())
    hashed_pw = hash_pw.decode('utf-8')

    # password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,  # 아이디
        "password": hashed_pw,  # 비밀번호
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
            "profile_info": about_receive
        }

        if 'file_give' in request.files:
            file = request.files["file_give"]
            filename = secure_filename(file.filename)
            extension = filename.split(".")[-1]
            file_path = f"profile_pics/{username}.{extension}"

            file.save("./static/" + file_path)
            new_doc["profile_pic"] = filename
            new_doc["profile_pic_real"] = file_path
        db.users.update_one({'username': payload['id']}, {'$set': new_doc})

        return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


#####프로필페이지에서 프로필 사진업로드(/user)######
@app.route('/posting', methods=['POST'])
def posting():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        # 포스팅하기
        user_info = db.users.find_one({"username": payload["id"]})
        username = user_info["username"]
        contents_receive = request.form["contents_give"]
        place_pic = request.files["place_pic_give"]
        date_receive = request.form["date_give"]

        filename = secure_filename(place_pic.filename)
        extension = filename.split('.')[-1]
        today = datetime.now()
        mytime = today.strftime('%Y%m%d%H%M%S')
        ms = today.strftime('%H%M%S')

        num = f'{username}{ms}'
        picname = f'place_pic-{mytime}'
        save_to = f'static/place_pic/{picname}.{extension}'

        place_pic.save(save_to)

        doc = {
            "username": user_info["username"],
            "profile_name": user_info["profile_name"],
            "contents": contents_receive,
            "place_pic": f'{picname}.{extension}',
            "date": date_receive,
            "num": num
        }

        db.posts.insert_one(doc)
        return jsonify({"result": "success", 'msg': '포스팅 성공!'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


# 게시물 불러오기
@app.route('/listing', methods=['GET'])
def listing():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 클라이언트에서 넘어온 username 을 username_receive 에 받는다.
        username_receive = request.args.get("username_give")
        if username_receive == "":
            posts = list(db.posts.find({}).sort("date", -1))
        else:
            posts = list(db.posts.find({"username": username_receive}).sort("date", -1))
        for post in posts:
            post["_id"] = str(post["_id"])
            post["count_heart"] = db.likes.count_documents(
                {"post_id": post["_id"], "type": "heart"})  # 해당 글의 like 갯수를 파악
            post["heart_by_me"] = bool(db.likes.find_one({"post_id": post["_id"], "type": "heart", "username": payload[
                'id']}))  # jwt토큰을 확인해서 username을 꺼내고 like타입을 확인해서 해당 게시글에 내 정보가 있으면 내가 좋아요를 눌렀는지 알게 됨
        return jsonify({"result": "success", "msg": "포스팅을 가져왔습니다.", "posts": posts})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


# 좋아요 기능
@app.route('/update_like', methods=['POST'])
def update_like():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 사용자를 확인
        user_info = db.users.find_one({"username": payload["id"]})
        # 게시물을 확인
        post_id_receive = request.form["post_id_give"]
        # 좋아요의 종류 확인
        type_receive = request.form["type_give"]
        # 실행인지 취소인지 확인
        action_receive = request.form["action_give"]

        # db 에 저장될 형식
        doc = {
            "post_id": post_id_receive,
            "username": user_info["username"],
            "type": type_receive,
        }
        # 좋아요가 실행이면
        if action_receive == "like":
            # 저장한다.
            db.likes.insert_one(doc)
        else:  # 아니면 삭제한다.
            db.likes.delete_one(doc)
        # db 에서 해당 게시물의 좋아요 개수를 확인해서 count 에 담는다.
        count = db.likes.count_documents({"post_id": post_id_receive, "type": type_receive})

        # count 와 결과값을 클라이언트로 넘겨준다.
        return jsonify({"result": "success", "count": count})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

# num 에 해당하는 게시물의 상세페이지로 이동
@app.route('/detail/<num>')
def detail(num):
    try:
        # db 에서 해당 num 을 가진 게시물의 정보를 search_post 에 담는다.
        search_post = db.posts.find_one({'num': num})
        # search_post 를 detail.html 로 넘긴다.
        return render_template("detail.html", search_post=search_post)
    except ():
        return redirect(url_for("index"))

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
