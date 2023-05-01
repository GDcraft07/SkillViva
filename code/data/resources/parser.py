from flask_restful import reqparse


parser = reqparse.RequestParser()
parser.add_argument('user_id', required=True, type=int)
parser.add_argument('heading', required=True)
parser.add_argument('content', required=True)
parser.add_argument('category_id', required=True, type=int)
