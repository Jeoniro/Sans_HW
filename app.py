from flask import Flask, render_template, jsonify
from flask_bootstrap import Bootstrap5
from news_crawler import generate_markdown_report, get_korean_time
import os
import json
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Flask 세션을 위한 시크릿 키
bootstrap = Bootstrap5(app)

# 뉴스 데이터를 저장할 JSON 파일 경로
NEWS_DATA_FILE = 'news_data.json'

def save_news_data(news_data):
    """뉴스 데이터를 JSON 파일로 저장합니다."""
    try:
        with open(NEWS_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(news_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving news data: {e}")
        return False

def load_news_data():
    """저장된 뉴스 데이터를 불러옵니다."""
    try:
        if os.path.exists(NEWS_DATA_FILE):
            with open(NEWS_DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'news': []}
    except Exception as e:
        print(f"Error loading news data: {e}")
        return {'news': []}

@app.route('/')
def index():
    """메인 페이지를 렌더링합니다."""
    try:
        news_data = load_news_data()
        today = get_korean_time()
        return render_template('index.html', news_data=news_data, today=today)
    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/update')
def update_news():
    """뉴스 데이터를 업데이트합니다."""
    try:
        # 뉴스 크롤링 및 마크다운 생성
        news_data = generate_markdown_report()
        # JSON 파일로 저장
        if save_news_data(news_data):
            return jsonify({'status': 'success', 'message': '뉴스가 업데이트되었습니다.'})
        else:
            return jsonify({'status': 'error', 'message': '뉴스 데이터 저장 중 오류가 발생했습니다.'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error='페이지를 찾을 수 없습니다.'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', error='서버 오류가 발생했습니다.'), 500

if __name__ == '__main__':
    app.run(debug=True, port=5050) 