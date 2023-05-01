from data import db_session
from data.posts import Post
from random import randint, shuffle


class SelectionOfPosts:
    def __init__(self, filters=False):
        self.filters = filters

    def random_selection_of_posts(self, posts, quantity):
        use_index = []
        ans = []
        for i in range(quantity):
            index = randint(0, len(posts) - 1)
            while index in use_index:
                index = randint(0, len(posts) - 1)
            ans.append(posts[index])
            use_index.append(index)

        return ans

    def selection(self):
        db_sess = db_session.create_session()
        if not self.filters:
            posts = list(reversed(db_sess.query(Post).all()))
        else:
            posts = db_sess.query(Post).filter(Post.category_id.in_(self.filters))

        current_posts = posts[:40]  # Остается только 30
        other_posts = posts[40:]  # Остается только 20
        total_number_of_relevant_posts = int(len(current_posts) * 0.75)
        if total_number_of_relevant_posts == 30:
            random_relevant_posts = self.random_selection_of_posts(current_posts, total_number_of_relevant_posts)
        else:
            random_relevant_posts = self.random_selection_of_posts(current_posts, len(current_posts))
        random_other_posts = []

        if total_number_of_relevant_posts == 30:
            if len(other_posts) <= 20:
                random_other_posts = other_posts
            else:
                random_other_posts = self.random_selection_of_posts(other_posts, 20)

        result = random_relevant_posts + random_other_posts
        shuffle(result)

        return result
