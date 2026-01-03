import requests
from bs4 import BeautifulSoup
import os

# 텔레그램 설정 (GitHub Secrets에서 가져옴)
TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

def get_price(code):
    url = f"https://finance.naver.com/marketindex/goldDetail.naver?goldCode={code}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    
    # 현재가 추출 (네이버 PC 버전 기준이 가장 안정적입니다)
    price_text = soup.select_one("p.no_today em.no_up span.blind")
    if not price_text:
        price_text = soup.select_one("p.no_today em.no_down span.blind")
    if not price_text:
        price_text = soup.select_one("p.no_today em span.blind")
        
    return float(price_text.text.replace(",", ""))

def send_message():
    try:
        krx_price = get_price("M04020000") # 한국거래소 금
        shinhan_price = get_price("CMDT_GD") # 신한은행 금
        
        spread = krx_price - shinhan_price
        disparity = (spread / shinhan_price) * 100
        
        status = "🚨 국내 과열 주의" if disparity > 3.5 else "✅ 정상 범위"
        
        msg = (
            f"🥇 오늘의 금값 괴리 보고서\n\n"
            f"- 한국거래소(KRX): {krx_price:,.0f}원\n"
            f"- 신한은행(고시): {shinhan_price:,.2f}원\n"
            f"--------------------------\n"
            f"💰 스프레드: {spread:,.2f}원\n"
            f"📈 괴리율: {disparity:.2f}%\n"
            f"📊 상태: {status}"
        )
        
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}"
        requests.get(url)
        print("메시지 전송 완료!")
        
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    send_message()
