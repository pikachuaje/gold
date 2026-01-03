import requests
from bs4 import BeautifulSoup
import os
import re

# 텔레그램 설정
TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

def get_price(code):
    url = f"https://m.stock.naver.com/marketindex/metals/{code}"
    headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'}
    
    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        price_tag = soup.find("strong", class_=lambda x: x and 'price' in x.lower())
        
        if price_tag:
            raw_text = price_tag.text
            # 숫자와 소수점만 골라내기
            price_text = re.sub(r'[^0-9.]', '', raw_text)
            return float(price_text)
        else:
            return None
    except Exception as e:
        print(f"❌ {code} 가져오기 오류: {e}")
        return None

def send_message():
    print("🚀 전략적 금 시세 분석을 시작합니다...")
    
    krx_price = get_price("M04020000") # KRX 금
    shinhan_price = get_price("CMDT_GD") # 신한은행 금
    
    if krx_price and shinhan_price:
        spread = krx_price - shinhan_price
        disparity = (spread / shinhan_price) * 100
        
        # --- 상혁님의 매수 타이밍 전략 로직 ---
        if abs(disparity) >= 10:
            status = "💎 매수 타임 (괴리 10% 돌파!)"
        else:
            status = "✅ 정상 범위"
        # ----------------------------------
        
        msg = (
            f"🥇 오늘의 금값 괴리 보고서\n\n"
            f"- 한국거래소(KRX): {krx_price:,.0f}원\n"
            f"- 신한은행(고시): {shinhan_price:,.2f}원\n"
            f"--------------------------\n"
            f"💰 스프레드: {spread:,.2f}원\n"
            f"📈 괴리율: {disparity:.2f}%\n"
            f"📊 투자 판단: {status}"
        )
        
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        params = {'chat_id': CHAT_ID, 'text': msg}
        res = requests.post(url, params=params)
        
        if res.status_code == 200:
            print("✅ 전략 리포트 전송 성공!")
    else:
        print("❌ 데이터 부족으로 전송 취소")

if __name__ == "__main__":
    send_message()
