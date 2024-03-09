import os
from transformers import TrOCRProcessor, VisionEncoderDecoderModel, TrainingArguments, AutoTokenizer, DataCollatorWithPadding
from PIL import Image
from werkzeug.security import generate_password_hash, check_password_hash
from collections import OrderedDict

class UserService:
    def __init__(self, UserDao, config):
        self.user_dao = UserDao
        self.config = config
    
    def create_new_user(self, new_user):
        self.user_dao.insert_user(new_user)
        
    def login(self,useremail):
        
        return self.user_dao.get_username_and_password(useremail)

class OcrService:
    def __init__(self, MedDao, config):
        # 모델 파일 가져오기
        self.MedDao = MedDao
        
        self.processor = TrOCRProcessor.from_pretrained("team-lucid/trocr-small-korean")
        self.model = VisionEncoderDecoderModel.from_pretrained("team-lucid/trocr-small-korean")
        self.config = config

        self.product_information = None
        self.product_caution = None
        self.food_caution = []
        self.ingredient_rel = []
        self.similar_product = None

    def load_img(form):
        pass 

    # Pillow 라이브러리를 통해 이미지 사이즈 조절 후 저장하는 메소드 구현
    def resize_and_save(self, file1, file2):
        # 업로드된 이미지를 Pillow를 사용하여 크기 조절
        img1 = Image.open(file1)
        img2 = Image.open(file2)
        
        # 이미지를 RGB로 변환
        img1 = img1.convert('RGB')
        img2 = img2.convert('RGB')
        
        resized_img1 = img1.resize((400, 200))  # 원하는 크기로 조절
        resized_img2 = img2.resize((400, 200))  # 원하는 크기로 조절
        # 조절된 이미지를 저장
        
        resized_img1.save(os.path.join(self.config['UPLOAD_FOLDER'], file1.filename))
        resized_img2.save(os.path.join(self.config['UPLOAD_FOLDER'], file2.filename))
    
    # 이미지 -> text 변형    
    def get_text(self, file_name):
        image = Image.open(f"./aii/static/assets/img/img_dir/{file_name}").convert("RGB")

        pixel_values = self.processor(image, return_tensors="pt").pixel_values

        generated_ids = self.model.generate(pixel_values)
        generated_text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

        return generated_text
    
    # text 더미에서 유효성분 내용만 추출
    def extract_ingredient(text):
        pass

    # DB에서 제품에 대한 정보(제품명, 클래스, 성분, 효과, 첨가물, 주의사항, 저장법, 복용방법)들을 받아오는 함수
    def get_product_info(self, product):
        product_info = self.MedDao.get_product_info(product) # 제품명을 넘겨서 딕셔너리 반환
    
        # ingredients = product_info['ingredient'].split(",") # 성분만 따로 빼서 가져옴, ','를 기준으로 나뉨
   
        # print('동일 제품: ', end="")
        # print(self.MedDao.get_similar_product(product_info['class']))

        # print('관계 정보: ')
        # print(self.MedDao.get_medicine_medicine_rel('벤즈트로핀메실산염'))

        # print('음식: ', end="")
        # print(self.MedDao.get_food_medicine('아세트아미노펜'))

        return product_info # 리스트안의 딕셔너리 리턴
    
    def get_similar_product(self, ingredient):

        similar_prodcut = self.MedDao.get_similar_product(ingredient)

        return similar_prodcut
    
    def get_food_caution(self, ingredient):

        food_caution = self.MedDao.get_food_medicine(ingredient)
        
        return food_caution 
    
    def get_ingredient_rel(self, ingredient):

        ingredient_rel = self.MedDao.get_medicine_medicine_rel(ingredient)

        return ingredient_rel