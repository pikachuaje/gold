import requests
import re
import os

# 텔레그램 설정
TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

def get_gold_price(code):
    # 모바일 페이지보다 안정적인 API 데이터를 직접 찌릅니다.
    url = f"https://polling.finance.naver.com/api/realtime/world/index/{code}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        res = requests.get(url, headers=headers)
        data = res.json()
        # 네이버 API 구조에서 가격 추출
        price = data['result']['areas'][0]['datas'][0]['nm']
        # 가격이 숫자가 아닌 텍스트로 올 수 있어 숫자로 변환
        return float(data['result']['areas'][0]['datas'][0]['nv'])
    except Exception as e:
        print(f"❌ {code} 가격 가져오기 실패: {e}")
        return None

def send_message():
    print("🚀 작업을 시작합니다...")
    
    krx_price = get_gold_price("M04020000") # KRX 금
    shinhan_price = get_gold_price("CMDT_GD") # 신한은행(국제금)
    
    if krx_price and shinhan_price:
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
        
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        params = {'chat_id': CHAT_ID, 'text': msg}
        res = requests.post(url, params=params)
        
        if res.status_code == 200:
            print("✅ 메시지 전송 성공!")
        else:
            print(f"❌ 텔레그램 전송 실패: {res.text}")
    else:
        print("❌ 가격 데이터를 불러오지 못해 메시지를 보내지 않았습니다.")

if __name__ == "__main__":
    send_message()
