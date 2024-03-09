from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

class UserDao: # db.Model class 상속받음
    def __init__(self, database):
        self.db = database

    def insert_user(self, user):
        with self.db.connect() as conn:
            conn.execute(text("""
                INSERT INTO user_db(
                    username,
                    useremail,
                    password,
                    allergy
                ) VALUES(
                    :username,
                    :useremail,
                    :password,
                    :allergy
                )
            """), user)
            conn.commit()

    def get_username_and_password(self, useremail):
        with self.db.connect() as conn:
            row = conn.execute(text("""
                SELECT
                    username,
                    password
                FROM user_db
                WHERE useremail = :useremail
            """), {'useremail' : useremail}).fetchone()
        return {
            'username' : row[0],
            'password' : row[1]
        } if row else None

class MedDao:
    def __init__(self, database):
        self.db = database

    # 제품에 대한 정보들 가져오기
    def get_product_info(self, product):
        with self.db.connect() as conn:
            row = conn.execute(text("""
                SELECT
                    class,
                    ingredient,
                    effect,
                    additive,
                    caution,
                    storage,
                    guide
                FROM medicine_info
                WHERE product = :product
            """), {'product' : product}).fetchone()

        return [{
            'product' : product},
            {'class' : row[0]},
            {'ingredient' : row[1]},
            {'effect' : row[2]},
            {'additive' : row[3]},
            {'caution' : row[4]},
            {'storage' : row[5]},
            {'guide' : row[6]}
        ] if row else None # 딕셔너리 반환

    # 비슷한 제품 가져오기
    def get_similar_product(self, code):
        
        with self.db.connect() as conn:
            rows = conn.execute(text("""
                SELECT
                    product
                FROM medicine_info
                WHERE class = :code
            """), {'code' : code}).fetchall()
       
        products = [row[0] for row in rows]

        return products # 리스트 반환
    
    # 해당 질병에 대한 성분과의 관계 가져오기
    def get_disease_medicine(self, disease):
        with self.db.connect() as conn:
            row = conn.execute(text("""
                SELECT
                    ingredient,
                    rel
                FROM medicine_disease_rel
                WHERE disease = :disease
            """), {'disease' : disease}).fetchone()
            
        return {
            'disease' : disease,
            'ingredient' : row[0],
            'rel' : row[1]
        } if row else None # 딕셔너리 반환

    def get_medicine_medicine_rel(self, ingredient):
        # DB로 부터 영양 성분 정보 가져오기
        with self.db.connect() as conn:
            rows = conn.execute(text("""
                SELECT
                    ingredient_1,
                    ingredient_2,
                    rel
                FROM medicine_medicine_rel
                WHERE ingredient_1 = :ingredient OR ingredient_2 = :ingredient
            """), {'ingredient' : ingredient}).fetchall()
            
            ingredient_rel = [{'ingredient': row[0] if row[0] != ingredient else row[1], 'rel': row[2]} for row in rows]
            
        return ingredient_rel

    def get_food_medicine(self, ingredient):
        with self.db.connect() as conn:
            rows = conn.execute(text("""
                SELECT
                    food,
                    rel
                FROM medicine_food_rel
                WHERE ingredient = :ingredient
            """), {'ingredient' : ingredient}).fetchall()

        food_rel = [{'food': row[0], 'rel': row[1]} for row in rows]
        
        return food_rel