from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import datetime
import json
import re
import os

def load_card_page(driver, card_id: int) -> bool:
    url = f"https://www.card-gorilla.com/card/detail/{card_id}"
    try:
        driver.get(url)
        time.sleep(2)
        return True
    except Exception as e:
        print(f"페이지 로딩 실패 (ID: {card_id}):", e)
        return False

def expand_dl_sections(driver):
    try:
        script = """
        const dls = document.querySelectorAll("div.lst.bene_area > dl");
        let count = 0;
        dls.forEach(dl => {
            if (!dl.classList.contains("on")) {
                dl.classList.add("on");

                // dt 클릭 이벤트 강제로 발생시켜 렌더링 유도
                const dt = dl.querySelector("dt");
                if (dt) {
                    dt.dispatchEvent(new MouseEvent('click', { bubbles: true }));
                }

                count += 1;
            }
        });
        return count;
        """
        expanded_count = driver.execute_script(script)
        print(f"{expanded_count}개의 dl 확장 완료 (JS class 추가 + click 이벤트)")
    except Exception as e:
        print("확장 실패:", e)
            
def extract_card_details(driver):
    benefits = []
    cautions = []

    try:
        # 혜택/유의사항이 확장된 dl 요소만 추출
        dl_elements = driver.find_elements(By.CSS_SELECTOR, 'div.lst.bene_area > dl.on')
    except Exception as e:
        print("혜택 영역 추출 실패:", e)
        return [], []

    for i, dl in enumerate(dl_elements):
        try:
            # dt 안의 혜택 유형과 요약 설명 추출
            dt = dl.find_element(By.TAG_NAME, "dt")
            benefit_type = dt.find_element(By.CSS_SELECTOR, "p.txt1").text.strip()

            # <i>는 innerText로 줄바꿈 포함한 텍스트 추출
            i_tag = dt.find_element(By.TAG_NAME, "i")
            summary = i_tag.get_attribute("innerText").strip().replace('\n', ' ')

            # 상세 내용: dd > div.in_box > p 태그들
            p_tags = dl.find_elements(By.CSS_SELECTOR, "dd > div.in_box > p")
            details = []
            is_caution = False

            for p in p_tags:
                text = p.text.strip()
                if not text or text == "<br>":
                    continue

                if "유의사항" in text or "유의사항" in benefit_type:
                    is_caution = True
                    # continue

                clean_text = text.lstrip("-").strip()

                if is_caution:
                    cautions.append(clean_text)
                else:
                    details.append(clean_text)

            # 유의사항 블록은 benefits에 포함하지 않음
            if "유의사항" not in benefit_type:
                benefits.append({
                    "type": benefit_type,
                    "summary": summary,
                    "details": details
                })

        except Exception as e:
            print(f"{i+1}번째 혜택 파싱 실패:", e)
            continue

    return benefits, cautions

def extract_card_info(driver, card_id: int) -> dict:
    data = {"card_id": card_id}

    # 카드 url 추가
    try:
        data["card_url"] = url = f"https://www.card-gorilla.com/card/detail/{card_id}"
    except:
        data["card_url"] = None

    # 카드명
    try:
        data["card_name"] = driver.find_element(By.CSS_SELECTOR, ".tit .card").text
    except:
        data["card_name"] = None

    # 카드사 (issuer)
    try:
        data["issuer"] = driver.find_element(By.CLASS_NAME, "brand").text
    except:
        data["issuer"] = None

    try:
        data["inactive"] = driver.find_element(By.CLASS_NAME, "inactive").text
    except:
        data["inactive"] = None

    # 연회비
    try:
        fees = driver.find_elements(By.CSS_SELECTOR, ".in_out span")
        data["annual_fee"] = {
            "domestic": fees[0].text.strip() if len(fees) > 0 else None,
            "international": fees[1].text.strip() if len(fees) > 1 else None
        }
    except:
        data["annual_fee"] = {"domestic": None, "international": None}

    # 전월 실적
    try:
        bnf2_section = driver.find_element(By.CLASS_NAME, "bnf2")
        dls = bnf2_section.find_elements(By.TAG_NAME, "dl")
        for dl in dls:
            try:
                dt = dl.find_element(By.TAG_NAME, "dt").text.strip()
                if "전월실적" in dt:
                    dd = dl.find_element(By.TAG_NAME, "dd")
                    raw_text = dd.text.strip().replace("\n", "")
                    data["required_spending"] = raw_text

                    # 숫자만 따로 추출 (예: 50)
                    match = re.search(r"(\d+)", raw_text)
                    if match:
                        data["required_spending_amount"] = int(match.group(1))
                    else:
                        data["required_spending_amount"] = None
                    break
            except:
                continue
        else:
            data["required_spending"] = None
            data["required_spending_amount"] = None
    except:
        data["required_spending"] = None
        data["required_spending_amount"] = None

    # 브랜드
    try:
        brand_spans = driver.find_elements(By.CSS_SELECTOR, ".c_brand span")
        data["brands"] = [span.text.strip() for span in brand_spans if span.text.strip()]
    except:
        data["brands"] = []

    # 혜택 및 유의사항
    try:
       benefits, cautions = extract_card_details(driver)
       data["benefits"] = benefits
       data["cautions"] = cautions
    except:
        data["benefits"] = []
        data["cautions"] = []

    return data

def save_card_json(data: dict, output_root="./cards"):
    issuer = data.get("issuer", "unknown").strip().replace(" ", "_")
    card_id = data.get("card_id", "unknown")

    # 디렉토리 경로: cards/현대카드/
    output_dir = os.path.join(output_root, issuer)
    os.makedirs(output_dir, exist_ok=True)

    filename = f"{issuer}_{card_id}.json"
    path = os.path.join(output_dir, filename)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"저장 완료: {path}")

def get_card_info(card_id: int, save=True) -> dict:
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    try:
        if not load_card_page(driver, card_id):
            return {}

        expand_dl_sections(driver)
        data = extract_card_info(driver, card_id)

        if save:
            save_card_json(data)

        return data
    finally:
        driver.quit()

def save_all_cards(start_id=1, end_id=2857, log_path="./card_crawl_log.txt"):
    with open(log_path, "w", encoding="utf-8") as log_file:
        for card_id in range(start_id, end_id + 1):
            print(f"\n[+] 카드 ID {card_id} 처리 중...")
            try:
                data = get_card_info(card_id, save=True)

                if not data or not data.get("card_name"):
                    print(f"[!] 카드 ID {card_id}: 정보 없음 (스킵)")
                    log_file.write(f"{card_id} FAIL\n")
                else:
                    log_file.write(f"{card_id} CLEAR\n")
            except Exception as e:
                print(f"[!] 카드 ID {card_id} 처리 실패: {e}")
                log_file.write(f"{card_id} FAIL\n")
                
            time.sleep(2)


if __name__ == "__main__":
    # start = time.time()
    # save_all_cards(1, 2857)
    # sec = time.time() - start
    # times = str(datetime.timedelta(seconds=sec)) # 걸린시간 보기좋게 바꾸기
    # short = times.split(".")[0] # 초 단위 까지만
    # print(f"{times} sec")
    # print(f"{short} sec")
    save_all_cards(1, 10)