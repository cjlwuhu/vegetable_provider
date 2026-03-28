from models import Vegetable_category
from exts import db

def init_vegetable_category():
    vegetable_category = ["豌豆", "苦瓜", "蒲瓜", "茄子", "西兰花", "卷心菜", "灯笼椒", "胡萝卜", "花菜", "黄瓜", "木瓜", "土豆", "南瓜", "萝卜", "西红柿"]
    category_models = []
    for category in vegetable_category:
        categort_model = Vegetable_category(name=category)
        category_models.append(categort_model)

    db.session.add_all(category_models)
    db.session.commit()
    print("蔬菜列表初始化成功")
