from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import JavascriptException
import time

# === [사용자 설정] ===
business_number = "2158635051"     # 10자리 사업자번호
user_id = "76369"                  # 사용자 ID
password = "lsh97320@"             # 사용자 비밀번호
chrome_path = r"C:\Program Files\chromedriver\chromedriver.exe"  # chromedriver 경로


def run_edukisa_auto_learning():
    """에듀키사 자동 로그인 및 수강 스크립트 실행 함수"""
    # 드라이버 설정
    service = Service(chrome_path)
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # === 1. 사이트 접속 ===
        driver.get("https://corp.edukisa.or.kr/home.do")
        time.sleep(1)

        # === 2. 사업자 번호 입력 ===
        biznum1, biznum2, biznum3 = business_number[:3], business_number[3:5], business_number[5:]
        driver.find_element(By.ID, "rgst_num1").send_keys(biznum1)
        driver.find_element(By.ID, "rgst_num2").send_keys(biznum2)
        driver.find_element(By.ID, "rgst_num3").send_keys(biznum3 + Keys.RETURN)
        time.sleep(1)

        # === 3. 로그인 ===
        driver.find_element(By.ID, "user_id").send_keys(user_id)
        driver.find_element(By.ID, "user_pw").send_keys(password + Keys.RETURN)
        time.sleep(2)

        # === 4. 강의장 접속 ===
        driver.find_element(By.CSS_SELECTOR, "a.btn-b-.btn-sz05").click()
        time.sleep(2)

        # === 5. 학습실 입장 ===
        driver.find_element(By.CSS_SELECTOR, "button.btn-sz01.btn-nvi").click()
        time.sleep(2)
        print("✅ 강의실 입장 완료!")

        # === 6. 학습 가능한 강의 자동 실행 ===
        rows = driver.find_elements(By.CSS_SELECTOR, "#trnAList tr.tbl-sec")
        rows = rows[4:]
        for row in rows:
            try:
                rate_text = row.find_elements(By.TAG_NAME, "td")[3].text
                rate = int(rate_text.replace("진도율", "").replace("%", "").strip() or "0")

                if rate < 101:
                    study_btns = row.find_elements(By.CSS_SELECTOR, "button.btn-sz01.btn-b-lgry:not(.disabled)")
                    if study_btns:
                        study_btns[0].click()
                        lecture_name = row.find_elements(By.TAG_NAME, "td")[1].text
                        print(f"▶ 학습 시작: {lecture_name}")
                        time.sleep(1)

                        # 영상 재생 스크립트 실행
                        driver.execute_script("""
                            var video = document.querySelector('.k-window video#video');
                            if (video) {
                                video.play();
                                window._videoEnded = false;
                                video.onended = function() { window._videoEnded = true; };
                            }
                        """)
                        print("▶ 동영상 자동 재생 및 종료 감지 등록")

                        # 영상 종료 대기 (무제한)
                        while True:
                            if driver.execute_script("return window._videoEnded === true;"):
                                print("✅ 영상 종료 감지됨")

                                # 팝업 닫기 (버튼이 보일 때까지 최대 10초 반복 대기)
                                try:
                                    for _ in range(20):  # 0.5초 * 20 = 10초
                                        close_btn = driver.find_element(By.CSS_SELECTOR, "button.k-window-titlebar-action[aria-label='Close']")
                                        visible = driver.execute_script("return arguments[0].offsetParent !== null;", close_btn)
                                        if visible:
                                            break
                                        time.sleep(0.5)
                                    print("is_displayed:", close_btn.is_displayed())
                                    print("offsetParent visible:", visible)
                                    driver.execute_script("arguments[0].click();", close_btn)
                                    print("✅ 닫기 버튼 클릭 완료 (JS 강제 실행)")
                                except Exception as e:
                                    print(f"❌ 닫기 버튼 처리 실패: {e}")
                                    driver.execute_script("window._videoEnded = false;")
                                # break는 제거 (실행 계속)

            except Exception as e:
                print(f"❌ 강의 탐색 오류: {e}")

    except Exception as main_error:
        print(f"❌ 전체 실행 중 오류 발생: {main_error}")

    finally:
        driver.quit()  # 필요 시 드라이버 종료
        pass


if __name__ == "__main__":    # 스크립트 실행
    run_edukisa_auto_learning()
