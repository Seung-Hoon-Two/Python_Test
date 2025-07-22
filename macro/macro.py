from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time

# 설정: 본인 정보 입력
business_number = "2158635051"  # 10자리 사업자번호
user_id = "76369"
password = "lsh97320@"

# ChromeDriver 경로 설정
chrome_path = "C:\Program Files\chromedriver\chromedriver.exe"  # 또는 전체 경로 지정

# Selenium 드라이버 실행
service = Service(chrome_path)
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")  # 창 최대화
driver = webdriver.Chrome(service=service, options=options)

try:
    # 1. 사이트 접속
    driver.get("https://corp.edukisa.or.kr/home.do")
    time.sleep(1)

    # 2. 사업자번호 입력 (3칸 분할)
    # 사업자번호를 3-2-5로 분할
    biznum1 = business_number[:3]
    biznum2 = business_number[3:5]
    biznum3 = business_number[5:]

    input_biznum1 = driver.find_element(By.ID, "rgst_num1")
    input_biznum2 = driver.find_element(By.ID, "rgst_num2")
    input_biznum3 = driver.find_element(By.ID, "rgst_num3")

    input_biznum1.send_keys(biznum1)
    input_biznum2.send_keys(biznum2)
    input_biznum3.send_keys(biznum3)
    input_biznum3.send_keys(Keys.RETURN)
    time.sleep(1)

    # 3. 로그인 (ID/비밀번호)
    input_id = driver.find_element(By.ID, "user_id")  # 로그인 ID 필드
    input_pw = driver.find_element(By.ID, "user_pw")  # 비밀번호 필드

    input_id.send_keys(user_id)
    input_pw.send_keys(password)
    input_pw.send_keys(Keys.RETURN)
    time.sleep(1)

    # 4. 강의장 접속 (메뉴 클릭)
    enter_button = driver.find_element(By.CSS_SELECTOR, "a.btn-b-.btn-sz05")
    enter_button.click()
    time.sleep(1)

    # 5. 학습실 입장 버튼 클릭
    study_button = driver.find_element(By.CSS_SELECTOR, "button.btn-sz01.btn-nvi")
    study_button.click()
    time.sleep(1)

    print("✅ 강의실 입장 완료!")

    # 6. 진도율 100%가 아닌 강의의 '학습하기' 버튼 클릭
    rows = driver.find_elements(By.CSS_SELECTOR, "#trnAList tr.tbl-sec")
    for row in rows:
        try:
            # 진도율 셀 찾기
            rate_cell = row.find_elements(By.TAG_NAME, "td")[3]
            rate_text = rate_cell.text.replace("진도율", "").replace("%", "").strip()
            # 진도율이 100%가 아니고, 학습하기 버튼이 활성화되어 있으면 클릭
            if rate_text and rate_text != "-" and int(rate_text) < 100:
                study_btns = row.find_elements(By.CSS_SELECTOR, "button.btn-sz01.btn-b-lgry:not(.disabled)")
                if study_btns:
                    study_btns[0].click()
                    print(f"▶ 학습하기 클릭: {row.find_elements(By.TAG_NAME, 'td')[1].text}")
                    time.sleep(1)  # 강의 재생 대기
                    # 팝업 안의 video 태그 재생 (자바스크립트로 play)
                    try:
                        driver.execute_script("""
                            var video = document.querySelector('.k-window video#video');
                            if (video) {
                                video.play();
                                window._videoEnded = false;
                                video.onended = function() { window._videoEnded = true; };
                            }
                        """)
                        print("▶ 동영상 자동 재생 및 종료 감지 이벤트 등록")
                    except Exception as e:
                        print(f"❌ 동영상 재생 오류: {e}")

                    # 영상이 끝날 때까지 대기
                    for _ in range(600):  # 최대 600초(10분) 대기
                        ended = driver.execute_script("return window._videoEnded === true;")
                        if ended:
                            print("✅ 영상 종료 감지")
                            break
                        time.sleep(1)
                    else:
                        print("⚠️ 영상 종료 감지 실패, 최대 대기시간 초과")

                    # 팝업 닫기 버튼 클릭
                    try:
                        close_btn = driver.find_element(By.CSS_SELECTOR, ".k-window .k-window-titlebar-action")
                        close_btn.click()
                        print("✅ 팝업 닫기 완료")
                    except Exception as e:
                        print(f"❌ 팝업 닫기 오류: {e}")

                    break        
        except Exception as e:
            print(f"❌ 강의목차 처리 오류: {e}")

except Exception as e:
    print(f"❌ 오류 발생: {e}")

finally:
    # driver.quit()  # 테스트 후 자동 종료 원할 경우 사용
    pass
