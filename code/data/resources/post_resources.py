from flask_restful import Resource, abort
from flask import jsonify

from ..db_session import create_session
from ..posts import Post
from .parser import parser # для дальнейшей реализации добавления постов


def abort_if_post_not_found(id):
    db_sess = create_session()
    post = db_sess.get(Post, id)
    if not post:
        abort(404, message=f"Post {id} is not found")


class PostResource(Resource):
    def get(self, id):
        abort_if_post_not_found(id)
        db_sess = create_session()
        post = db_sess.get(Post, id)
        return jsonify(
            {'post': post.to_dict()}
        )


class PostListResource(Resource):
    def get(self):
        db_sess = create_session()
        posts = db_sess.query(Post).all()
        return jsonify(
            {'posts': [post.to_dict() for post in posts]}
        )
