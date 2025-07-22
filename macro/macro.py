from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import JavascriptException
import time
import AskGpt


# === [사용자 설정] ===
business_number = "2158635051"     # 10자리 사업자번호
user_id = "76369"                  # 사용자 ID
password = "lsh97320@"             # 사용자 비밀번호
chrome_path = r"C:\Program Files\chromedriver\chromedriver.exe"  # chromedriver 경로


def run_edukisa_auto_learning():
    # 드라이버 설정
    # service = Service(chrome_path)
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--mute-audio")   # 오디오 음소거
    options.add_argument("--start-maximized")
    # driver = webdriver.Chrome(service=servic, options=options)
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 20)


    try:
        # === 1. 사이트 접속 ===
        driver.get("https://corp.edukisa.or.kr/")
        time.sleep(0.5)

        # === 2. 사업자 번호 입력 ===
        biznum1, biznum2, biznum3 = business_number[:3], business_number[3:5], business_number[5:]
        driver.find_element(By.ID, "rgst_num1").send_keys(biznum1)
        driver.find_element(By.ID, "rgst_num2").send_keys(biznum2)
        driver.find_element(By.ID, "rgst_num3").send_keys(biznum3 + Keys.RETURN)
        time.sleep(0.5)

        # === 3. 로그인 ===
        driver.find_element(By.ID, "user_id").send_keys(user_id)
        driver.find_element(By.ID, "user_pw").send_keys(password + Keys.RETURN)
        time.sleep(0.5)

        # === 4. 강의장 접속 ===
        driver.find_element(By.CSS_SELECTOR, "a.btn-b-.btn-sz05").click()
        time.sleep(0.5)

        # === 5. 학습실 입장 ===
        driver.find_element(By.CSS_SELECTOR, "button.btn-sz01.btn-nvi").click()
        time.sleep(1)
        print("✅ 강의실 입장 완료!")

        # === 6. 학습 가능한 강의 자동 실행 ===
        while True:
            rows = driver.find_elements(By.CSS_SELECTOR, "#trnAList tr.tbl-sec")
            for row in rows:
                try:
                    rate_text = row.find_elements(By.TAG_NAME, "td")[3].text
                    try:
                        test_text = row.find_elements(By.TAG_NAME, "td")[5].text
                        if "시험보기" in test_text or "재응시" in test_text:
                            test_btns = driver.find_elements(By.XPATH, "//button[contains(text(), '시험보기') or contains(text(), '재응시')]")
                            
                            if test_btns:
                                try:
                                    test_btn = test_btns[0]
                                    # driver.execute_script("arguments[0].scrollIntoView(true);", test_btn)
                                    time.sleep(0.5)
                                    test_btn.click()
                                    
                                    # 팝업 내 체크박스 등장 대기
                                    wait.until(EC.presence_of_element_located((By.ID, "attnCheck")))

                                    # 체크박스 클릭 (이미 체크되어 있지 않으면)
                                    attn_checkbox = driver.find_element(By.ID, "attnCheck")
                                    if not attn_checkbox.is_selected():
                                        driver.execute_script("document.querySelector('.k-overlay')?.remove();")
                                        driver.execute_script("arguments[0].click();", attn_checkbox)
                                        print("✅ 유의사항 체크박스 선택 완료")
                                    else:
                                        print("⚠️ 체크박스는 이미 선택되어 있음")

                                    # "확인" 버튼 클릭
                                    confirm_btn = WebDriverWait(driver, 10).until(
                                        EC.element_to_be_clickable((By.CSS_SELECTOR, "#myclass-edu-attn-window .popup-foot .btn-grp button.btn-"))
                                    )
                                    driver.execute_script("arguments[0].click();", confirm_btn)
                                    print("✅ 확인 버튼 클릭 완료")
                                    time.sleep(1)
                                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "myclass-edu-exam-window")))
                                    exam_items = driver.find_elements(By.CSS_SELECTOR, "#examList > li")

                                    # 문제 번호(ID에서 숫자 부분) 추출
                                    question_ids = {}
                                    for item in exam_items:
                                        qid_attr = item.get_attribute("id")  # 예: "testExamNum_517"
                                        if qid_attr and qid_attr.startswith("testExamNum_"):
                                            qid = qid_attr.replace("testExamNum_", "")  # 숫자만 추출
                                            question_text = item.text.strip()
                                            gpt_answer = AskGpt.ask_gpt_for_answer(question_text)
                                            
                                            
                                            if gpt_answer and gpt_answer.isdigit():
                                                question_ids[qid] = (gpt_answer, question_text)
                                                radio_id = f"examNum_{qid}_{gpt_answer}"
                                                try:
                                                    answer_radio = driver.find_element(By.ID, radio_id)
                                                    driver.execute_script("arguments[0].click();", answer_radio)
                                                    print(f"✅ Q{qid} - {gpt_answer}번 선택 완료")
                                                except Exception as e:
                                                    print(f"❌ Q{qid} 정답 클릭 실패: {e}")
                                            else:
                                                print(f"❌ Q{qid} GPT 정답 실패: {gpt_answer}")
                                    # 제출 버튼 클릭
                                    submit_btn = WebDriverWait(driver, 10).until(
                                        EC.element_to_be_clickable((By.CSS_SELECTOR, "#myclass-edu-exam-window .popup-foot .btn-grp button.btn-"))
                                    )
                                    driver.execute_script("arguments[0].click();", submit_btn)
                                    
                                    print("✅ 제출하기 버튼 클릭 완료")

                                    # 첫 번째 확인 팝업 처리
                                    try:
                                        alert1 = WebDriverWait(driver, 5).until(EC.alert_is_present())
                                        alert1.accept()
                                        print("✅ 첫 번째 확인 팝업 처리 완료")
                                    except:
                                        print("⚠️ 첫 번째 확인 팝업 없음")

                                    # 두 번째 확인 팝업 처리
                                    try:
                                        alert2 = WebDriverWait(driver, 5).until(EC.alert_is_present())
                                        alert2.accept()
                                        print("✅ 두 번째 확인 팝업 처리 완료")
                                    except:
                                        print("⚠️ 두 번째 확인 팝업 없음")
                                    
                                    time.sleep(1)

                                except Exception as e:
                                    print(f"❌ 시험 버튼 클릭 실패: {e}")
                    except:
                        # print("시험보기 버튼이 없습니다.")
                        pass

                    if rate_text=="-":
                        continue
                    else:
                        rate = int(rate_text.replace("진도율", "").replace("%", "").strip() or "0")

                    if rate < 100:
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
                                }
                            """)
                            print("▶ 동영상 자동 재생 및 종료 감지 등록")

                            # 영상 종료 대기 (무제한)
                            while True:
                                if driver.execute_script("""
                                        const video = document.querySelector('video');
                                        return video ? video.ended : true;
                                    """):
                                    print("✅ 영상 종료 감지됨")

                                    # 닫기 버튼 클릭
                                    try:
                                        close_btn = driver.find_element(By.CSS_SELECTOR, "div.k-window[aria-labelledby='myclass-edu-std-window_wnd_title'] button[aria-label='Close']")
                                        driver.execute_script("arguments[0].click();", close_btn)
                                        print("✅ 학습 팝업 닫기 버튼 클릭 완료")
                                        # [시험보기] 버튼이 있으면 클릭
                                        test_btns = driver.find_elements(By.XPATH, "//button[contains(text(), '시험보기')]") or driver.find_elements(By.XPATH, "//button[contains(text(), '재응시')]")
                                        if test_btns:
                                            try:
                                                test_btn = test_btns[0]
                                                # driver.execute_script("arguments[0].scrollIntoView(true);", test_btn)
                                                time.sleep(0.5)
                                                test_btn.click()
                                                
                                                # 팝업 내 체크박스 등장 대기
                                                wait.until(EC.presence_of_element_located((By.ID, "attnCheck")))

                                                # 체크박스 클릭 (이미 체크되어 있지 않으면)
                                                attn_checkbox = driver.find_element(By.ID, "attnCheck")
                                                if not attn_checkbox.is_selected():
                                                    driver.execute_script("document.querySelector('.k-overlay')?.remove();")
                                                    driver.execute_script("arguments[0].click();", attn_checkbox)
                                                    print("✅ 유의사항 체크박스 선택 완료")
                                                else:
                                                    print("⚠️ 체크박스는 이미 선택되어 있음")

                                                # "확인" 버튼 클릭
                                                confirm_btn = WebDriverWait(driver, 10).until(
                                                    EC.element_to_be_clickable((By.CSS_SELECTOR, "#myclass-edu-attn-window .popup-foot .btn-grp button.btn-"))
                                                )
                                                driver.execute_script("arguments[0].click();", confirm_btn)
                                                print("✅ 확인 버튼 클릭 완료")
                                            except Exception as e:
                                                print(f"❌ 시험 버튼 클릭 실패: {e}")

                                        break  # 다음 강의로 이동
                                    
                                    except Exception as e:
                                        print(f"❌ 닫기 버튼 클릭 실패: {e}")    
                except Exception as e:
                    print(f"❌ 강의 탐색 오류: {e}")
                

    except Exception as main_error:
        print(f"❌ 전체 실행 중 오류 발생: {main_error}")

    finally:
        driver.quit()  # 필요 시 드라이버 종료
        pass


if __name__ == "__main__":    # 스크립트 실행
    run_edukisa_auto_learning()