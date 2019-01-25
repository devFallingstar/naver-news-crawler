from urllib.request import urlopen
from bs4 import BeautifulSoup
import re

# 불필요한 텍스트를 잘라낼 때 사용할 수 있는 token의 list 및 정규식입니다.
delete_reg = "[\\\\{}<>/!@#$%^&*='_■]"
delete_word_list = ['나우뉴스', '서울신문', '서울연합뉴스', '사진연합뉴스', '이데일리', '플레이어', '뉴스1코리아', '서울경제', '오류를 우회하기 위한 함수 추가', '본문 내용', '무단 전재 및 재배포 금지', '및 재배포금지', '배포금지', '네이버 홈에서 뉴스 확인하기', '사진', 'ⓒ', '세계를 보는 창', '경제를 보는 눈', '아시아경제', '무단전재',
                '배포금지.', '뉴스가 재밌다', '세상의 모든 재미', '티잼', '네이버 뉴스', '뉴스 스탠드에서도 만나세요', '뉴시스 페이스북 트위터', '공감언론', '뉴시스통신사', '( 연합뉴스)',
                '02)3701-5555', '구독신청:', '대한민국 오후를 여는 유일석간', '문화일보', '모바일 웹', '문화닷컴 바로가기', '▶', '()',  '【', '】', '.."', '[', ']', '©', '  ', '<!-- 본문 내용 -->', '<!-- TV플레이어 -->', '<!-- // TV플레이어 -->'
                    , '<script type="text/javascript">', '// flash 오류를 우회하기 위한 함수 추가', 'function _flash_removeCallback() {}', '</script>', '<strong class="media_end_summary">', '</strong><span class="end_photo_org">',
                    '</script>', '</strong>', '\n', 'flash', 'function', 'removeCallback', 'lt;', 'gt;', '★', '무료만화']


'''
네이버의 뉴스 페이지를 크롤링하여 각 뉴스의 url 집합(set)을 구해주는 class

https://news.naver.com/main/main.nhn?mode=LSD&mid=shm&sid1=100#&date=%2000:00:00&page=1   <- 정치 첫 페이지
sid1 -> 카테고리
page = 페이지
정치 경제 사회 생활문화 세계 IT과학
'''
class NaverCrawler:
    def __init__(self, _category, _page_list):
        self.wrong_category = False
        if type(_category) is str:
            if "정치" in str(_category):
                self.category_id = 100
            elif "경제" in str(_category):
                self.category_id = 101
            elif "사회" in str(_category):
                self.category_id = 102
            elif "생활" in str(_category):
                self.category_id = 103
            elif "문화" in str(_category):
                self.category_id = 103
            elif "세계" in str(_category):
                self.category_id = 104
            elif "IT" in str(_category):
                self.category_id = 105
            elif "과학" in str(_category):
                self.category_id = 106
            else:
                self.wrong_category = True
        elif type(_category) is int:
            if len(str(_category)) is not 3:
                self.wrong_category = True
            else:
                self.category_id = _category
        if self.wrong_category:
            self.category_id = _category

        print(self.category_id)
        self.pages_tuple = tuple(_page_list)

    '''
        지정된 카테고리 및 페이지에 속한 뉴스 url을 집합의 형태로 전부 가져옵니다.
        중복된 뉴스를 방지하기 위해 list가 아닌 set을 사용합니다.
    '''
    def crawl_all_urls(self):
        if self.wrong_category:
            print("잘못된 카테고리 값입니다 >> "+self.category_id)

            return []
        else:
            urls_to_crawl = list()

            url_with_category = 'http://news.naver.com/main/main.nhn?mode=LSD&mid=shm&sid1=' + str(self.category_id)
            url_with_page = '#&date=%2000:00:00&page='

            for each_page in self.pages_tuple:
                url_complete = url_with_category + url_with_page + str(each_page)
                urls_to_crawl.append(url_complete)

            news_url_list = set()

            for each_page in urls_to_crawl:
                response = urlopen(each_page)
                response_raw = response.read()
                response_soup = BeautifulSoup(response_raw, 'html.parser')

                for link in response_soup.find_all('a'):
                    href_data = str(link.get('href'))
                    if href_data.startswith('https://news.naver.com/main/read.nhn') \
                            and "sid1="+str(self.category_id) in href_data:
                        news_url_list.add(href_data)

            print(news_url_list)
            return news_url_list

    '''
    특정 url 집합에 대한 뉴스 내용을 전부 가져옵니다.
    '''
    def get_news_contents_from_urls(self, urls):
        all_contents = set()
        for each_URL in urls:
            all_contents.add(self.get_news_content_from_url(each_URL))
        return all_contents

    '''
    뉴스 내용을 하나 씩 가져옵니다.
    '''
    def get_news_content_from_url(self, url):
        response = urlopen(url)
        response_raw = response.read()
        response_soup = BeautifulSoup(response_raw, 'html.parser', from_encoding='utf-8')

        result_content_raw = str(response_soup.find('div', id='articleBodyContents'))
        result_content_raw = self.trim_content(result_content_raw)

        return result_content_raw

    '''
    뉴스 내용으로부터 불필요한 내용을 잘라냅니다.
    '''
    def trim_content(self, contents):
        contents = re.sub('<.+?>', '', contents, 0)
        contents = re.sub('＜.+?＞', '', contents, 0)
        contents = re.sub(delete_reg, ' ', contents, 0)

        for tok in delete_word_list:
            contents = " ".join(contents.replace(tok, '').split())

        return contents


if __name__ == '__main__':
    naverCrawler = NaverCrawler(_category='IT', _page_list=[1])
    naverNewsUrls = naverCrawler.crawl_all_urls()
    naverNewsContents = naverCrawler.get_news_contents_from_urls(naverNewsUrls)

    print(naverNewsUrls)

    print(naverNewsContents)
