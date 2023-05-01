def insert_categories_into_db(db_sess, category_class, categories):
    
    # не будет ошибки если в таблице уже есть категории
    if db_sess.query(category_class).all():
        return
    
    for cat in categories:
        categ = category_class(category=cat)
        db_sess.add(categ)
    db_sess.commit()
