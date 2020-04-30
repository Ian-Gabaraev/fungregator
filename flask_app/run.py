from flask import Flask, render_template
from models.articles import ArticleModel
import random


app = Flask(__name__)


@app.route("/")
def template_test():
    article_objects = ArticleModel.retrieve()
    random.shuffle(article_objects)
    return render_template('template.html', objects=article_objects)


@app.route("/<string:publisher>")
def template_pub(publisher):
    article_objects = ArticleModel.retrieve(pid=publisher)
    random.shuffle(article_objects)
    return render_template('template.html', objects=article_objects)


if __name__ == '__main__':
    app.run(debug=True)
