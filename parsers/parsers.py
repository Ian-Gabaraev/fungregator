import threading
import requests
import random
import bs4
from telegram_rpc import gateway
from parsers.parser_settings import *
from requests import ReadTimeout


class Publication:
    def __init__(self, title, article_url, description, source, pid):
        self.title = title
        self.article_url = article_url
        self.description = description
        self.source = source
        self.pid = pid


class Video:
    def __init__(self, fresh_videos_url, url_tags, caption_tags, host):

        self.result = set()
        self.threads = list()
        self.fresh_videos_url = fresh_videos_url
        self.url_tags = url_tags
        self.caption_tags = caption_tags
        self.host = host

    def get_fresh_links(self, as_dict=True):
        try:
            """
            Rotating User-Agent header to bypass
            anti-scraping tools
            """
            user_agent = user_agent_list[random.randint(0, len(user_agent_list)-1)]
            headers = {'User-Agent': user_agent}
            response = requests.request(method='GET',
                                        url=self.fresh_videos_url,
                                        headers=headers,
                                        timeout=30)
            assert response.status_code == 200
        except AssertionError:
            gateway.register_error(self, '%r status code is not 200' % self.host)
        except ConnectionError:
            gateway.register_error(self, '%r connection error' % self.host)
        except ReadTimeout:
            gateway.register_error(self, 'reading from %r timed out' % self.host)
        else:
            html = bs4.BeautifulSoup(response.content, features='html.parser')
            tag, attr = self.url_tags
            result = {
                url: caption for (url, caption) in zip
                (
                 [element.a['href'] for element in html.find_all(tag, attr)],
                 [element.a.text for element in html.find_all(tag, attr)]
                )
            }
            if as_dict:
                return result
            return list(result.keys())

    def add(self, url, heading):
            try:
                user_agent = user_agent_list[random.randint(0, len(user_agent_list)-1)]
                headers = {'User-Agent': user_agent}
                response = requests.request(method='GET',
                                            url=url,
                                            headers=headers,
                                            timeout=30)
                assert response.status_code == 200
            except AssertionError:
                gateway.register_error(self, '%r status code is not 200' % self.host)
            except ConnectionError:
                gateway.register_error(self, '%r connection error' % self.host)
            except ReadTimeout:
                gateway.register_error(self, 'reading from %r timed out' % self.host)
            else:
                html = bs4.BeautifulSoup(response.content, features='html.parser')
                if self.caption_tags:
                    tag, attr = self.caption_tags
                    div = html.find(tag, attr)
                    caption = div.p.text
                else:
                    caption = None
                self.result.add(Publication(heading,
                                            url, caption, self.host, self.__class__.__name__
                                            ))

    def collect(self):
        for url, heading in self.get_fresh_links(as_dict=True).items():
            _thread = threading.Thread(
                target=self.add, args=(url, heading,)
            )
            self.threads.append(_thread)
        for thread in self.threads:
            thread.start()
        for thread in self.threads:
            thread.join(timeout=10)
        return list(self.result)


class NYPost(Video):
    def __init__(self):
        Video.__init__(self,
                       caption_tags=NYPost_tags['caption'],
                       fresh_videos_url=NYPost_urls['fresh'],
                       url_tags=NYPost_tags['url'],
                       host='New York Post'
                       )


class CDV(Video):
    def __init__(self):
        Video.__init__(self,
                       caption_tags=None,
                       fresh_videos_url=CDV_urls['fresh'],
                       url_tags=CDV_tags['url'],
                       host='Cats Dogs Videos'
                       )


class GOA(Video):
    def __init__(self):
        Video.__init__(self,
                       caption_tags=GOA_tags['caption'],
                       fresh_videos_url=GOA_urls['fresh'],
                       url_tags=GOA_tags['url'],
                       host='Go Animals'
                       )
