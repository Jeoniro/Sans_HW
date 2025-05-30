import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import os
from dateutil import parser
import re

# RSS 피드 URL 목록 (업데이트된 URL들)
RSS_FEEDS = [
    "https://rss.cnn.com/rss/money_latest.rss",  # 테스트용 영어 피드
    "https://feeds.yna.co.kr/economy",  # 연합뉴스 경제
    "https://www.hankyung.com/feed/economy",  # 한국경제 경제
    "https://rss.joins.com/joins_economy_list.xml",  # 중앙일보 경제
    "https://www.mk.co.kr/rss/30000001/"  # 매일경제 경제
]

def get_korean_time():
    """한국 시간을 반환합니다."""
    kst = pytz.timezone('Asia/Seoul')
    return datetime.now(kst)

def clean_text(text):
    """텍스트를 정리합니다."""
    # HTML 태그 제거
    text = re.sub(r'<[^>]+>', '', text)
    # 특수문자 제거
    text = re.sub(r'[^\w\s가-힣]', ' ', text)
    # 여러 공백을 하나로
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_company_names(text):
    """회사명을 찾아서 강조합니다."""
    # 주요 기업명 패턴 (예시)
    companies = ['삼성', '현대', 'LG', 'SK', '네이버', '카카오', 'KT', 'SKT', '포스코', '한화', '롯데', 'CJ', '두산', '효성']
    for company in companies:
        if company in text:
            text = text.replace(company, f'**{company}**')
    return text

def get_news_category(title, summary):
    """뉴스 카테고리를 추정합니다."""
    title_lower = title.lower()
    summary_lower = summary.lower()
    
    if any(keyword in title_lower or keyword in summary_lower for keyword in ['주식', '증시', '코스피', '코스닥', '상장']):
        return '📈 증시'
    elif any(keyword in title_lower or keyword in summary_lower for keyword in ['부동산', '아파트', '집값', '전세']):
        return '🏠 부동산'
    elif any(keyword in title_lower or keyword in summary_lower for keyword in ['금리', '은행', '대출', '금융']):
        return '💰 금융'
    elif any(keyword in title_lower or keyword in summary_lower for keyword in ['기업', '회사', '매출', '영업이익']):
        return '🏢 기업'
    elif any(keyword in title_lower or keyword in summary_lower for keyword in ['정부', '정책', '규제', '법안']):
        return '🏛️ 정책'
    else:
        return '📰 일반'

def create_sample_news():
    """샘플 뉴스 데이터를 생성합니다 (RSS 피드 접근 실패시 사용)"""
    today = get_korean_time()
    
    sample_news = [
        {
            'title': '**삼성전자** 3분기 실적 발표, 반도체 부문 회복세',
            'summary': '삼성전자가 3분기 실적을 발표하며 반도체 부문의 회복세를 보고했습니다. 메모리 반도체 가격 상승과 수요 증가가 주요 요인으로 분석됩니다.',
            'link': 'https://example.com/news1',
            'source': '한국경제',
            'published': today.strftime('%Y-%m-%d %H:%M'),
            'category': '🏢 기업',
            'days_ago': 0
        },
        {
            'title': '코스피 2600선 돌파, 외국인 순매수 지속',
            'summary': '코스피가 2600선을 돌파하며 강세를 보이고 있습니다. 외국인 투자자들의 순매수가 지속되고 있어 상승세가 이어질 것으로 전망됩니다.',
            'link': 'https://example.com/news2',
            'source': '매일경제',
            'published': today.strftime('%Y-%m-%d %H:%M'),
            'category': '📈 증시',
            'days_ago': 0
        },
        {
            'title': '한국은행 기준금리 동결, 경제 상황 지켜보기로',
            'summary': '한국은행이 기준금리를 현 수준에서 동결하기로 결정했습니다. 인플레이션과 경제성장률을 종합적으로 고려한 결과입니다.',
            'link': 'https://example.com/news3',
            'source': '연합뉴스',
            'published': today.strftime('%Y-%m-%d %H:%M'),
            'category': '💰 금융',
            'days_ago': 0
        },
        {
            'title': '서울 아파트 평균 매매가 상승세, 전세 시장도 회복',
            'summary': '서울 지역 아파트 평균 매매가가 상승세를 보이고 있으며, 전세 시장도 점진적인 회복세를 나타내고 있습니다.',
            'link': 'https://example.com/news4',
            'source': '중앙일보',
            'published': today.strftime('%Y-%m-%d %H:%M'),
            'category': '🏠 부동산',
            'days_ago': 0
        },
        {
            'title': '정부, 중소기업 지원 정책 발표',
            'summary': '정부가 중소기업의 경쟁력 강화를 위한 새로운 지원 정책을 발표했습니다. 자금 지원과 세제 혜택이 주요 내용입니다.',
            'link': 'https://example.com/news5',
            'source': '파이낸셜뉴스',
            'published': today.strftime('%Y-%m-%d %H:%M'),
            'category': '🏛️ 정책',
            'days_ago': 0
        }
    ]
    
    return sample_news

def generate_markdown_report():
    """뉴스 링크 데이터를 수집하고 반환합니다."""
    today = get_korean_time()
    date_str = today.strftime('%Y%m%d')
    
    # 모든 뉴스 아이템을 저장할 리스트
    all_news = []
    
    for feed_url in RSS_FEEDS:
        try:
            print(f"Processing feed: {feed_url}")
            
            # User-Agent 헤더 추가
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # requests를 사용하여 RSS 피드 가져오기
            try:
                response = requests.get(feed_url, headers=headers, timeout=10)
                response.raise_for_status()
                feed = feedparser.parse(response.content)
            except Exception as e:
                print(f"Failed to fetch {feed_url}: {e}")
                continue
            
            if not feed.entries:
                print(f"No entries found in feed: {feed_url}")
                continue
                
            print(f"Found {len(feed.entries)} entries in {feed_url}")
                
            for entry in feed.entries:
                try:
                    # 날짜 파싱 시도
                    if hasattr(entry, 'published'):
                        try:
                            pub_date = parser.parse(entry.published)
                            days_diff = (today.date() - pub_date.date()).days
                        except:
                            # 날짜 파싱 실패 시 최근 뉴스로 간주
                            pub_date = today
                            days_diff = 0
                    else:
                        # published 필드가 없으면 최근 뉴스로 간주
                        pub_date = today
                        days_diff = 0
                    
                    # 최근 7일 이내의 기사만 필터링 (범위 확대)
                    if days_diff <= 7:
                        title = clean_text(entry.title) if hasattr(entry, 'title') else "제목 없음"
                        summary = clean_text(entry.summary) if hasattr(entry, 'summary') else ""
                        link = entry.link if hasattr(entry, 'link') else ""
                        
                        if not title or not link:
                            continue
                        
                        # 회사명 강조
                        title = extract_company_names(title)
                        
                        # 카테고리 추정
                        category = get_news_category(title, summary)
                        
                        all_news.append({
                            'title': title,
                            'summary': summary[:200] + '...' if len(summary) > 200 else summary,
                            'link': link,
                            'source': feed.feed.title if hasattr(feed.feed, 'title') else feed_url.split('/')[-2],
                            'published': pub_date.strftime('%Y-%m-%d %H:%M'),
                            'category': category,
                            'days_ago': days_diff
                        })
                        
                except Exception as e:
                    print(f"Error processing entry: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error processing feed {feed_url}: {e}")
            continue
    
    print(f"Total news collected from RSS: {len(all_news)}")
    
    # RSS에서 뉴스를 가져오지 못한 경우 샘플 데이터 사용
    if len(all_news) == 0:
        print("No news from RSS feeds, using sample data...")
        all_news = create_sample_news()
    
    # 날짜순으로 정렬 (최신순)
    all_news.sort(key=lambda x: x['published'], reverse=True)
    
    # 상위 20개 뉴스 선택 (더 많은 링크 제공)
    top_news = all_news[:20]
    
    return {
        'date': date_str,
        'formatted_date': today.strftime('%Y년 %m월 %d일'),
        'news': top_news,
        'total_count': len(all_news)
    }

if __name__ == "__main__":
    result = generate_markdown_report()
    print(f"총 {result['total_count']}개의 뉴스 중 상위 20개를 선택했습니다.") 