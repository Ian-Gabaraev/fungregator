from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer, String, Column, MetaData, create_engine
from parsers.parsers import Video

engine = create_engine('sqlite:////Users/ian/PycharmProjects/fungregator/models/articles.db')
metadata = MetaData(bind=engine)
Base = declarative_base(bind=engine, metadata=metadata)


class Article(Base):
    __tablename__ = 'article'
    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True)
    title = Column(String, unique=False)
    """
    SQLite does not offer
    max string length limit
    """
    caption = Column(String(150))
    source = Column(String)
    pid = Column(String)


class ArticleModel:
    s_names = [subclass.__name__ for subclass in Video.__subclasses__()]
    Base.metadata.create_all()
    Session = sessionmaker(bind=engine)
    session = Session()

    @staticmethod
    def update():
        rows = ArticleModel.session.query(Article.title).all()
        fresh = [obj for child in Video.__subclasses__()
                 for obj in child().collect()]
        articles = list(filter(lambda x:
                               x.title not in
                               [heading for tup in rows
                                for heading in tup], fresh))
        if articles:
            for obj in articles:
                article = Article(
                        url=obj.article_url,
                        title=obj.title,
                        caption=obj.description,
                        source=obj.source,
                        pid=obj.pid,
                )
                ArticleModel.session.add(article)
            ArticleModel.session.commit()

    @staticmethod
    def retrieve(pid=None):
        if pid and pid in ArticleModel.s_names:
            return ArticleModel.session.query(Article).filter_by(pid=pid).all()
        return ArticleModel.session.query(Article).all()
