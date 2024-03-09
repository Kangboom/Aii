import os
from flask import Flask
from flask import request, render_template, redirect, url_for, g, flash
from forms import RegisterForm, UserLoginForm, UploadForm
from flask import session
import functools
from werkzeug.security import generate_password_hash, check_password_hash

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session:
            _next = request.url if request.method == 'GET' else ''
            return redirect(url_for('login', next=_next))
        return view(*args, **kwargs)
    return wrapped_view

def create_endpoints(app, services):
    ocr_service = services.ocr_service # OCR 메인 서비스
    user_service = services.user_service # 회원가입, 로그인 서비스
    # product_information = []
    # similar_product = []

    def login_check():
        return 'username' not in session
    
    # home page
    @app.route('/')
    def home():
        return render_template('home.html')
    
    # 회원가입
    @app.route('/register', methods=['GET','POST'])  # GET, POST 메소드 둘다 사용
    def register():   # get 요청 단순히 페이지 표시 post요청 회원가입-등록을 눌렀을때 정보 가져오는것
        form = RegisterForm()
        useremail = form.data.get('useremail')
        user = user_service.login(useremail)
        if form.validate_on_submit() and not user : # POST검사의 유효성검사가 정상적으로 되었는지 확인할 수 있다. 입력 안한것들이 있는지 확인됨.
            new_user ={'username' : form.data.get('username'),
                       'useremail' : useremail,
                       'password' : generate_password_hash(form.data.get('password')),
                       'allergy' : form.data.get('allergy')}
            
            user_service.create_new_user(new_user)
            flash("회원가입이 완료되었습니다!", 'success')
            return redirect(url_for('login')) # post요청일시는 'login.html'주소로 이동. (회원가입 완료시 화면이동)
        if user:
            flash("존재하는 아이디입니다.", 'fail')        
        return render_template('register.html', form=form)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = UserLoginForm()
        if request.method == 'POST' and form.validate_on_submit():
            error = None

            # user_service의 login 함수로 form으로 받은 email의 username, password 가져오기
            user = user_service.login(form.useremail.data)
            
            # 사용자 확인 + password 비교
            if not user:
                error = "존재하지 않는 사용자입니다."
           
            elif not check_password_hash(user['password'], form.password.data):
                error = "비밀번호가 올바르지 않습니다."
            if error is None:
                # 세션에 해당 user 정보 저장
                session.clear()
                session['username'] = user['username']
                return render_template('home.html')
            flash(error,'fail')
        return render_template('/login.html', form=form)

    # 로그아웃
    @app.route('/logout', methods=['GET', 'POST'])
    def logout():

        # 현재 세션 정보 초기화 하기
        session.clear()
        return redirect('/')

    # OCR 서비스 화면
    @app.route('/photo', methods=['GET','POST'])
    # @login_required
    def photo():
        # 로그인 체크

        if login_check():
            return redirect('/login')
        session.pop('ocr_information', None)

        form = UploadForm()
        if request.method =='POST' and form.validate_on_submit():
            error = None
            # form에서 업로드된 img 가져오기
            uploaded_file_front = form.file_front.data
            uploaded_file_back = form.file_back.data

            if uploaded_file_front and uploaded_file_back:
                # 파일을 업로드 폴더에 저장
                if not os.path.splitext(uploaded_file_front.filename)[1].lower() in ['.png', '.jpg', '.jpeg'] or not os.path.splitext(uploaded_file_back.filename)[1].lower() in ['.png', '.jpg', '.jpeg']:
                    error = '이미지 파일만 업로드 가능합니다.'
                    
                else:
                    # 업로드 된 이미지 파일 저장   
                    file_path_front = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file_front.filename)
                    uploaded_file_front.save(file_path_front)
                    
                    file_path_back = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file_back.filename)
                    uploaded_file_back.save(file_path_back)
                    
                    # ocr_service의 get_text() 메서드를 호출하여 각 이미지를 텍스트로 변환
                    text_front = ocr_service.get_text(uploaded_file_front.filename) # 제품명
                    text_back = ocr_service.get_text(uploaded_file_back.filename) # 성분
                    
                    # test
                    text_back =['아세트아미노펜']
                    # text_back == ocr_service.product_information['ingredient'] 동일


                    # 제품명 전달해서 제품관련 정보들 받아오기, /information1
                    ocr_service.product_information = ocr_service.get_product_info('타이레놀')
                    print(f'제품정보: {ocr_service.product_information}')
                    # 제품에 대한 주의 사항 정보 불러오기, /information2

                    ocr_service.product_caution = ocr_service.product_information[5]['caution']
                    print(f'주의 사항 : {ocr_service.product_caution}')

                    for ingredient in text_back:
                        # 성분-음식 상호작용, /information2
                        # ocr_service.food_caution.append(ocr_service.get_food_caution(ocr_service.product_information['ingredient']))
                        ocr_service.food_caution.append(ocr_service.get_food_caution(ingredient))
                        

                        # 성분 상호작용, /information3
                        # ocr_service.ingredient_rel.append( ocr_service.get_ingredient_rel(ocr_service.product_information['ingredient']))
                        ocr_service.ingredient_rel.append( ocr_service.get_ingredient_rel(ingredient))
                       
                    print(f'음식 상호작용 : {ocr_service.food_caution}')
                    print(f'성분 간 상호작용 : {ocr_service.ingredient_rel}')
                    # 동일 성분 약 받아오기 /information4
                    ocr_service.similar_prodcut = ocr_service.get_similar_product(ocr_service.product_information[1]['class']) # index 2번이 성분
                    print(f'비슷한 약 : {ocr_service.similar_prodcut}')
                    # 이미지 크기 조절해서 저장 - 모든 사진을 동일한 크기로 출력하기 위해

                    ocr_service.resize_and_save(uploaded_file_front, uploaded_file_back)
                    
                    session['ocr_information'] = {
                        'product_information': ocr_service.product_information,
                        'product_caution': ocr_service.product_caution,
                        'food_caution': ocr_service.food_caution,
                        'ingredient_rel': ocr_service.ingredient_rel,
                        'similar_prodcut': ocr_service.similar_prodcut
                    }
                    return render_template('/result.html', img_path_front = 'assets/img/img_dir/' + uploaded_file_front.filename, img_path_back = 'assets/img/img_dir/' + uploaded_file_back.filename, text_front=text_front, text_back=text_back)
                    
            flash(error)
        return render_template('/photo.html', form=form)
    
    @app.route("/information1", methods=['GET', 'POST'])
    def information1():
        ocr_information = session.get('ocr_information', {})
        return render_template('/information1.html',  product_info=ocr_information.get('product_information'))

    
    @app.route("/information2", methods=['GET', 'POST'])
    def information2():
        ocr_information = session.get('ocr_information', {})
        print(f"information {ocr_information.get('food_caution')}")
        return render_template('/information2.html', product_name = ocr_information.get('product_information')[0]['product'], caution=ocr_information.get('product_caution'), ingredient_food=ocr_information.get('food_caution'))
    
    @app.route("/information3", methods=['GET', 'POST'])
    def information3():
        ocr_information = session.get('ocr_information', {})
        return render_template('/information3.html', ingredient = ocr_information.get('product_information')[2]['ingredient'] ,ingredient_rel=ocr_information.get('ingredient_rel'))

    
    @app.route("/information4", methods=['GET', 'POST'])
    def information4():
        ocr_information = session.get('ocr_information', {})
        gredient_list = ['아세트아미노펜,카페인무수물,이소프로필안티피린','아세트아미노펜,카페인무수물,이소프로필안티피린', '나프록센나트륨', '알릴이소프로필아세틸요소,카페인무수물,이부프로펜,산화마그네슘', '아세트아미노펜','아세트아미노펜','아세트아미노펜', '페니라민말레산염,아세트아미노펜,페닐레프린염산염']
        print(f'information4a {ocr_service.product_information}')
        
        return render_template('/information4.html', gredient_list = gredient_list, product_name = ocr_information.get('product_information')[0]['product'],similar_product=ocr_information.get('similar_prodcut'))
    
    @app.route("/health", methods=['GET', 'POST'])
    def health():
        if login_check():
            return redirect('/login')
        return render_template('/health.html')
    
    @app.route("/contact", methods=['GET', 'POST'])
    def contact():
        if login_check():
            return redirect('/login')
        return render_template('/contact.html')
    

    
