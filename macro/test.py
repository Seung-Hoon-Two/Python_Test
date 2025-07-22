from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import AskGpt
import subprocess

# === 사용자 설정 ===
business_number = "2158635051"
user_id = "76369"
password = "lsh97320@"


def run_edukisa_auto_learning():
    subprocess.Popen(['caffeinate','-dims'])
    # 크롬 드라이버 경로 설정
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--mute-audio")
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 20)

    try:
        # 사이트 접속 및 로그인
        driver.get("https://corp.edukisa.or.kr/")
        time.sleep(0.5)

        biznum1, biznum2, biznum3 = business_number[:3], business_number[3:5], business_number[5:]
        driver.find_element(By.ID, "rgst_num1").send_keys(biznum1)
        driver.find_element(By.ID, "rgst_num2").send_keys(biznum2)
        driver.find_element(By.ID, "rgst_num3").send_keys(biznum3 + Keys.RETURN)
        time.sleep(0.5)

        driver.find_element(By.ID, "user_id").send_keys(user_id)
        driver.find_element(By.ID, "user_pw").send_keys(password + Keys.RETURN)
        time.sleep(0.5)

        driver.find_element(By.CSS_SELECTOR, "a.btn-b-.btn-sz05").click()
        time.sleep(0.5)
        driver.find_element(By.CSS_SELECTOR, "button.btn-sz01.btn-nvi").click()
        print("✅ 강의실 입장 완료!")

        # 강의 목록 루프
        while True:
            rows = driver.find_elements(By.CSS_SELECTOR, "#trnAList tr.tbl-sec")
            for row in rows:
                try:
                    
                    tds = row.find_elements(By.TAG_NAME, "td")
                    
                    # 진도율은 항상 있는 열이라면 바로 추출
                    rate_text = tds[3].text if len(tds) >= 4 else "-"
                    # 시험 관련 텍스트는 td가 6개 이상일 때만 추출
                    test_text = tds[5].text if len(tds) >= 6 else ""

                    # 시험 실행 조건 확인
                    if "시험보기" in test_text or "재응시" in test_text:
                        test_btns = driver.find_elements(By.XPATH, "//button[contains(text(), '시험보기') or contains(text(), '재응시')]")
                        if test_btns:
                            handle_exam(driver, wait, test_btns[0])

                    # 진도율 확인 및 학습 시작
                    if rate_text != "-":
                        rate = int(rate_text.replace("진도율", "").replace("%", "").strip() or "0")
                        if rate < 100:
                            study_btns = row.find_elements(By.CSS_SELECTOR, "button.btn-sz01.btn-b-lgry:not(.disabled)")
                            if study_btns:
                                handle_lecture(driver, wait, row, study_btns[0])

                except Exception as e:
                    print(f"❌ 강의 탐색 오류: {e}")

    except Exception as main_error:
        print(f"❌ 전체 실행 중 오류 발생: {main_error}")

    finally:
        driver.quit()


def handle_exam(driver, wait, test_btn):
    try:
        time.sleep(0.5)
        test_btn.click()

        wait.until(EC.presence_of_element_located((By.ID, "attnCheck")))
        attn_checkbox = driver.find_element(By.ID, "attnCheck")
        if not attn_checkbox.is_selected():
            driver.execute_script("document.querySelector('.k-overlay')?.remove();")
            driver.execute_script("arguments[0].click();", attn_checkbox)
            print("✅ 유의사항 체크박스 선택 완료")

        confirm_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#myclass-edu-attn-window .popup-foot .btn-grp button.btn-"))
        )
        driver.execute_script("arguments[0].click();", confirm_btn)
        print("✅ 확인 버튼 클릭 완료")

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "myclass-edu-exam-window")))
        exam_items = driver.find_elements(By.CSS_SELECTOR, "#examList > li")

        for item in exam_items:
            qid_attr = item.get_attribute("id")
            if qid_attr.startswith("testExamNum_"):
                qid = qid_attr.replace("testExamNum_", "")
                question_text = item.text.strip()
                gpt_answer = AskGpt.ask_gpt_for_answer(question_text)

                if gpt_answer and gpt_answer.isdigit():
                    radio_id = f"examNum_{qid}_{gpt_answer}"
                    try:
                        answer_radio = driver.find_element(By.ID, radio_id)
                        driver.execute_script("arguments[0].click();", answer_radio)
                        print(f"✅ Q{qid} - {gpt_answer}번 선택 완료")
                    except Exception as e:
                        print(f"❌ Q{qid} 정답 클릭 실패: {e}")

        # 시험 제출
        submit_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#myclass-edu-exam-window .popup-foot .btn-grp button.btn-"))
        )
        driver.execute_script("arguments[0].click();", submit_btn)
        print("✅ 제출하기 버튼 클릭 완료")

        # 팝업 처리
        handle_alerts(driver)

    except Exception as e:
        print(f"❌ 시험 처리 오류: {e}")


def handle_alerts(driver):
    for i in range(2):
        try:
            alert = WebDriverWait(driver, 5).until(EC.alert_is_present())
            alert.accept()
            print(f"✅ {i+1}번째 확인 팝업 처리 완료")
        except:
            print(f"⚠️ {i+1}번째 확인 팝업 없음")


def handle_lecture(driver, wait, row, study_btn):
    lecture_name = row.find_elements(By.TAG_NAME, "td")[1].text
    study_btn.click()
    print(f"▶ 학습 시작: {lecture_name}")
    time.sleep(1)

    driver.execute_script("""
        var video = document.querySelector('.k-window video#video');
        if (video) {
            video.play();
            window._videoEnded = false;
        }
    """)
    print("▶ 동영상 자동 재생 및 종료 감지 등록")

    while True:
        if driver.execute_script("""
            const video = document.querySelector('video');
            return video ? video.ended : true;
        """):
            print("✅ 영상 종료 감지됨")
            try:
                close_btn = driver.find_element(By.CSS_SELECTOR, "div.k-window[aria-labelledby='myclass-edu-std-window_wnd_title'] button[aria-label='Close']")
                driver.execute_script("arguments[0].click();", close_btn)
                print("✅ 학습 팝업 닫기 버튼 클릭 완료")
            except Exception as e:
                print(f"❌ 닫기 버튼 클릭 실패: {e}")
            break


if __name__ == "__main__":
    run_edukisa_auto_learning()
