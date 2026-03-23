from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import re


def clean_value(text):
    """숫자, 마침표(.), 마이너스(-)만 남기고 나머지(원, 배, %, 콤마 등) 제거"""
    if not text or text == "N/A":
        return "N/A"
    # 숫자와 관련 기호만 추출
    cleaned = re.sub(r'[^0-9.\-]', '', text)
    return cleaned


def get_stock_details_clean(name, stock_code, is_domestic=True):
    path = "domestic" if is_domestic else "worldstock"
    url = f"https://m.stock.naver.com/{path}/stock/{stock_code}/total"

    options = Options()
    options.add_argument("--headless")
    options.add_argument(
        "user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/04.1")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    result = {
        "종목명": name,
        "종목코드": stock_code,
        "PER": "N/A",
        "PBR": "N/A",
        "배당수익률": "N/A",
        "주당배당금": "N/A"
    }

    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'StockInfo_key__naiA4')))

        keys = driver.find_elements(By.CLASS_NAME, 'StockInfo_key__naiA4')
        values = driver.find_elements(By.CLASS_NAME, 'StockInfo_value__WAuXk')

        for key, value in zip(keys, values):
            # 자바스크립트로 자식 span 태그 제외 순수 텍스트 추출
            k_text = driver.execute_script("""
                var parent = arguments[0];
                var child = parent.firstChild;
                var ret = "";
                while(child) {
                    if (child.nodeType === Node.TEXT_NODE) ret += child.textContent;
                    child = child.nextSibling;
                }
                return ret;
            """, key).strip()

            # 숨겨진 값 포함 텍스트 추출 후 숫자만 정제
            raw_v_text = value.get_attribute('textContent').strip()
            v_text = clean_value(raw_v_text)

            if k_text == 'PER':
                result['PER'] = v_text
            elif k_text == 'PBR':
                result['PBR'] = v_text
            elif '배당' in k_text and '수익률' in k_text:
                result['배당수익률'] = v_text
            elif '주당배당금' in k_text:
                result['주당배당금'] = v_text

        return result

    except Exception:
        return result
    finally:
        driver.quit()


# --- 종목 리스트 ---
domestic_list = [
    ["하나금융지주", "086790"],
    ["현대차(2우B)", "005387"],
    ["우리금융지주", "316140"],
    ["삼성화재(우)", "000815"],
    ["기아", "000270"],
    ["DB손해보험", "005830"],
]

world_list = [
    ["ExxonMobil", "XOM"],
    ["AT&T", "T"],
    ["CITI Group", "C"],
]

if __name__ == "__main__":
    final_data = []
    print("데이터를 수집 및 정제 중입니다...\n")

    for name, code in domestic_list:
        final_data.append(get_stock_details_clean(name, code, True))
    for name, code in world_list:
        final_data.append(get_stock_details_clean(name, code, False))

    # --- TSV 형식 출력 (숫자만 포함) ---
    header = ["종목명", "종목코드", "PER", "PBR", "배당수익률(%)", "주당배당금(원)"]

    print("-" * 30 + " 복사하여 엑셀에 붙여넣으세요 " + "-" * 30)
    print("\t".join(header))

    for row in final_data:
        line = [
            row["종목명"],
            row["종목코드"],
            row["PER"],
            row["PBR"],
            row["배당수익률"],
            row["주당배당금"]
        ]
        print("\t".join(line))
    print("-" * 95)