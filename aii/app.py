import os

from flask import Flask
from sqlalchemy import create_engine
from flask_wtf.csrf import CSRFProtect

# 각 layer import 하기
from views import create_endpoints
from service.aii_service import OcrService, UserService
from model.ocr_dao import UserDao, MedDao

# 빈 Services class 생성 -> 여기에 service 폴더 안의 service class들을 멤버로 추가함
class Services:
    pass

app = Flask(__name__, static_url_path='/static')
app.config.from_pyfile("config.py")

if __name__ == '__main__':    

    basedir = os.path.abspath(os.path.dirname(__file__)) #db파일을 절대경로로 생성
    img_dir = os.path.join(basedir, 'static/assets/img/img_dir')
    
    # mysql DB 연결 부분
    database = create_engine(app.config['DB_URL'], max_overflow=0)
    app.database = database

    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True 
    #사용자 요청의 끝마다 커밋(데이터베이스에 저장,수정,삭제등의 동작을 쌓아놨던 것들의 실행명령)을 한다.
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
    #수정사항에 대한 track을 하지 않는다. True로 한다면 warning 메시지유발
    app.config['SECRET_KEY'] = 'wcsfeufhwiquehfdx'
    # 파일 업로드 위치
    app.config['UPLOAD_FOLDER'] = img_dir 

    csrf = CSRFProtect()
    csrf.init_app(app)

    # Model layer
    UserDao = UserDao(database)
    MedDao = MedDao(database)
    
    # Business layer 
    services = Services # 빈 services Class 생성
    services.ocr_service = OcrService(MedDao, app.config) # user_dao class 넘겨줌
    services.user_service = UserService(UserDao, app.config)

    # view layer - endpoint 생성
    create_endpoints(app, services)

    app.run(host='127.0.0.1', port=5000, debug=True)


