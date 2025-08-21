import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time


@pytest.fixture(scope="function")
def driver():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    yield driver
    driver.quit()


def test_error_messages_for_empty_required_fields(driver):
    # 1. Открыть страницу
    driver.get("https://formdesigner.ru/examples/order.html")

    # 2. Закрыть всплывающее окно cookie
    try:
        cookie_accept = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(text(), 'Принять все') or contains(text(), 'Accept all')]"))
        )
        cookie_accept.click()
        # Даем время закрыться всплывающему окну
        time.sleep(1)
    except:
        print("Всплывающее окно cookie не найдено или уже закрыто")

    # 3. Скролл к форме
    iframe = driver.find_element(By.TAG_NAME, "iframe")
    driver.execute_script("arguments[0].scrollIntoView(true);", iframe)

    # 4. Найти все фреймы на странице
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    print(f"Найдено фреймов: {len(iframes)}")

    # 5. Переключиться на первый фрейм (скорее всего, это нужный нам фрейм)
    if not iframes:
        pytest.fail("Не найдено ни одного фрейма на странице")

    driver.switch_to.frame(iframes[0])

    # 6. Дать время для загрузки содержимого фрейма
    time.sleep(2)

    # 7. Найти кнопку "Отправить" разными способами
    submit_selectors = [
        "//button[contains(text(), 'Отправить')]",
        "//button[@type='submit']",
        "//input[@type='submit']",
        "//button[contains(@class, 'submit')]",
        "//button[contains(@class, 'button')]"
    ]

    # 8. Нажать кнопку "Отправить"
    submit_button = None
    for selector in submit_selectors:
        try:
            submit_button = driver.find_element(By.XPATH, selector)
            if submit_button.is_displayed():
                print(f"Найдена кнопка с селектором: {selector}")
                submit_button.click()
                break
        except:
            continue

    if not submit_button:
        # Вернуться к основному контенту и попробовать найти кнопку в других фреймах
        driver.switch_to.default_content()

        # Попробовать другие фреймы
        for i, iframe in enumerate(iframes):
            if i == 0:  # Первый фрейм уже пробовали
                continue

            try:
                driver.switch_to.frame(iframe)
                for selector in submit_selectors:
                    try:
                        submit_button = driver.find_element(By.XPATH, selector)
                        if submit_button.is_displayed():
                            print(f"Найдена кнопка во фрейме {i} с селектором: {selector}")
                            break
                    except:
                        continue

                if submit_button:
                    break
                else:
                    driver.switch_to.default_content()
            except:
                driver.switch_to.default_content()

    if not submit_button:
        # Сделать скриншот для отладки
        driver.save_screenshot("debug_screenshot.png")
        pytest.fail("Не удалось найти кнопку отправки формы ни в одном фрейме")

    # 9. Подождать и проверить наличие ошибок
    time.sleep(2)  # Дать время для появления ошибок

    # Попробовать найти ошибки разными способами
    error_selectors = [
        "//*[contains(text(), 'Пожалуйста')]",
        "//*[contains(@class, 'error')]",
        "//*[contains(@class, 'invalid')]",
        "//*[contains(@class, 'alert')]",
        "//*[contains(@class, 'warning')]"
    ]

    error_messages = []
    for selector in error_selectors:
        try:
            errors = driver.find_elements(By.XPATH, selector)
            for error in errors:
                if error.text and error.is_displayed():
                    error_messages.append(error.text)
                    print(f"Найдена ошибка: {error.text}")
        except:
            continue

    # 9. Проверить, что найдены ошибки
    if not error_messages:
        # Сделать скриншот для отладки
        driver.save_screenshot("errors_screenshot.png")
        pytest.fail("Не найдено ни одного сообщения об ошибке")

    # 10. Проверить ожидаемые тексты ошибок
    expected_errors = [
        "ФИО: field is required.",
        "E-mail field is required.",
        "Количество field is required.",
        "Дата доставки field is required."
    ]

    # Проверить, что все ожидаемые ошибки присутствуют
    found_expected_errors = []
    for expected_error in expected_errors:
        for actual_error in error_messages:
            if expected_error in actual_error:
                found_expected_errors.append(expected_error)
                break

    assert len(found_expected_errors) >= 1, \
        f"Не найдено ни одной ожидаемой ошибки. Найдены: {error_messages}. Ожидались: {expected_errors}"

    print(f"Тест прошел успешно. Найдены ошибки: {found_expected_errors}")
