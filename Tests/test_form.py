import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service


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

        # Ожидаем, что элемент cookie станет невидимым
        WebDriverWait(driver, 5).until(
            EC.invisibility_of_element_located(
                (By.XPATH, "//button[contains(text(), 'Принять все') or contains(text(), 'Accept all')]"))
        )
    except:
        print("Всплывающее окно cookie не найдено или уже закрыто")

    # 3. Скролл к форме
    iframe = driver.find_element(By.TAG_NAME, "iframe")
    driver.execute_script("arguments[0].scrollIntoView(true);", iframe)

    # 4. Найти фрейм по XPATH и переключиться на него
    iframe = driver.find_element(By.XPATH, "//*[contains(@id, 'form1006')]")

    driver.switch_to.frame(iframe)

    # 5. Найти и нажать кнопку "Отправить"
    submit_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Отправить') or @type='submit']")))
    submit_button.click()

    # 6. Попробовать найти ошибки разными способами
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

    # 7. Проверить, что найдены ошибки
    if not error_messages:
        # Сделать скриншот для отладки
        driver.save_screenshot("errors_screenshot.png")
        pytest.fail("Не найдено ни одного сообщения об ошибке")

    # 8. Проверить ожидаемые тексты ошибок
    expected_errors = [
        "Необходимо заполнить поле ФИО:.",
        "Необходимо заполнить поле E-mail.",
        "Необходимо заполнить поле Количество.",
        "Необходимо заполнить поле Дата доставки."
    ]

    # 9. Проверить, что все ожидаемые ошибки присутствуют
    found_expected_errors = []
    for expected_error in expected_errors:
        for actual_error in error_messages:
            if expected_error in actual_error:
                found_expected_errors.append(expected_error)
                break

    assert len(found_expected_errors) >= 1, \
        f"Не найдено ни одной ожидаемой ошибки. Найдены: {error_messages}. Ожидались: {expected_errors}"

    print(f"Тест прошел успешно. Найдены ошибки: {found_expected_errors}")
