"""
신한카드, 우리카드, 하나카드 크롤링 스크립트
카드 고릴라 사이트에서 카드 정보를 수집합니다.
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import time
import json

# URL 설정
url_1 = "https://www.card-gorilla.com/chart/corp?sub=2&term=monthly&date=2025-05-25"  # 신한
url_2 = "https://www.card-gorilla.com/chart/corp?sub=8&term=monthly&date=2025-05-25"  # 우리
url_3 = "https://www.card-gorilla.com/chart/corp?sub=8&term=monthly&date=2025-05-26"  # 하나

# url_4 = "https://www.card-gorilla.com/chart/top100?term=weekly"
# url_5 = "https://www.card-gorilla.com/chart/check100?term=weekly"


def get_card_urls_selenium():
    """카드 고릴라에서 카드 URL 목록을 수집하는 함수"""
    driver = webdriver.Chrome()
    driver.get(url=url_1)  # 신용카드 TOP 100
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    anchors = soup.select(".num1_card .con_area a[href^='/card/detail/'], .inner .con_area a[href^='/card/detail/']")

    card_urls = {"https://www.card-gorilla.com" + a['href'] for a in anchors}
    driver.quit()
    return list(card_urls)


def parse_card_detail(url):
    """개별 카드 상세 정보를 파싱하는 함수"""
    options = Options()
    options.add_argument("--headless")

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(3)

    # 혜택 정보 펼치기 위해 dt 요소들을 클릭
    dt_elements = driver.find_elements(By.CSS_SELECTOR, ".lst.bene_area dl dt")
    for dt in dt_elements:
        try:
            driver.execute_script("arguments[0].scrollIntoView(true);", dt)
            driver.execute_script("arguments[0].click();", dt)
            time.sleep(0.2)
        except Exception as e:
            print(f"클릭 실패: {e}")

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    # 기본 정보 파싱
    name = soup.select_one(".data_area .tit .card").get_text(strip=True)
    brand = soup.select_one(".data_area .tit .brand").get_text(strip=True)
    c_brand = soup.select_one(".c_brand span").get_text(strip=True)
    
    # 연회비 정보 파싱
    fee_domestic, fee_global = "", ""
    for span in soup.select(".in_out span"):
        text = span.get_text()
        fee = span.select_one("b")
        if not fee:
            continue
        fee_value = fee.get_text(strip=True)
        if "국내" in text:
            fee_domestic = fee_value
        elif "해외" in text:
            fee_global = fee_value
    
    # 혜택 정보 파싱
    benefits = []
    for dl in soup.select(".lst.bene_area dl"):
        dt = dl.select_one("dt")
        dd = dl.select_one("dd")
        
        category_tag = dt.select_one("p") if dt else None
        short_desc_tag = dt.select_one("i") if dt else None
        category = category_tag.get_text(strip=True) if category_tag else "기타"
        
        # 유의사항 관련 카테고리는 제외
        if category.startswith("유의사항") or category.startswith("꼭 확인"):
            continue

        short_description = short_desc_tag.get_text(strip=True) if short_desc_tag else ""
        detail_description = dd.get_text(strip=True) if dd else ""

        benefits.append({
            "category": category,
            "short_description": short_description,
            "detail_description": detail_description
        })

    return {
        "name": name,                        # 카드명 (예: '쿠팡 와우카드')
        "brand": brand,                      # 카드사 이름 (예: '신한카드')
        "c_brand": c_brand,                  # 국제 브랜드 (예: 'VISA', 'MasterCard')
        "fee_domestic": fee_domestic,        # 국내 전용 연회비
        "fee_global": fee_global,            # 해외 겸용 연회비
        "benefits": benefits,                # 혜택 정보
        "url": url                           # 카드 상세 페이지 URL
    }


def main():
    """메인 함수 - 카드 정보 수집 및 저장"""
    print("카드 정보 수집을 시작합니다...")
    
    # 카드 URL 목록 수집
    card_urls = get_card_urls_selenium()
    print(f"총 {len(card_urls)}개의 카드 URL을 수집했습니다.")
    
    all_cards = []

    # 각 카드의 상세 정보 수집
    for i, url in enumerate(card_urls):
        print(f"Processing card {i + 1}/{len(card_urls)}: Fetching {url}")
        try:
            card = parse_card_detail(url)
            if card:
                all_cards.append(card)
                print(f"{card['name']} 정보 수집 완료")
        except Exception as e:
            print(f"카드 정보 수집 실패: {e}")
        
        time.sleep(1)  # 서버 부하 방지

    # JSON 파일로 저장
    output_filename = "신용카드.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(all_cards, f, ensure_ascii=False, indent=2)
    
    print(f"\n수집 완료! {len(all_cards)}개의 카드 정보를 '{output_filename}' 파일에 저장했습니다.")


if __name__ == "__main__":
    main()
