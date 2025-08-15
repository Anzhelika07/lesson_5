import pytest
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

# Получаем путь к текущему файлу теста
current_dir = os.path.dirname(os.path.abspath(__file__))
# Формируем полный путь к файлу изображения
PICTURE_PATH = os.path.join(current_dir, "i.jpg")

# Данные для заполнения формы
TEST_DATA = {
    "first_name": "Angelika",
    "last_name": "Volf",
    "email": "anjela_karlova@mail.ru",
    "gender": "Female",
    "mobile": "9930160544",
    "date_of_birth": "07 November,1989",
    "subjects": "Maths",
    "hobbies": ["Sports", "Reading"],
    "current_address": "street Academic House 27 apartment 32",
    "state": "NCR",
    "city": "Delhi",
    "picture": "i.jpg"
}


# Фикстура для инициализации и завершения работы драйвера
@pytest.fixture(params=["chrome", "firefox", "edge"])
def driver(request):
    browser = request.param
    driver = None

    if browser == "chrome":
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    elif browser == "firefox":
        driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
    elif browser == "edge":
        driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()))

    driver.maximize_window()
    driver.get("https://demoqa.com/automation-practice-form")

    yield driver
    driver.quit()


# Основной тест
def test_fill_form(driver):
    wait = WebDriverWait(driver, 10)

    # Заполнение основных полей
    driver.find_element(By.ID, "firstName").send_keys(TEST_DATA["first_name"])
    driver.find_element(By.ID, "lastName").send_keys(TEST_DATA["last_name"])
    driver.find_element(By.ID, "userEmail").send_keys(TEST_DATA["email"])

    # Выбор пола
    driver.find_element(By.XPATH, f"//label[text()='{TEST_DATA['gender']}']").click()

    # Ввод номера телефона
    driver.find_element(By.ID, "userNumber").send_keys(TEST_DATA["mobile"])

    # Выбор даты рождения
    datepicker = driver.find_element(By.ID, "dateOfBirthInput")
    datepicker.click()
    driver.execute_script("arguments[0].value = '';", datepicker)
    datepicker.send_keys(TEST_DATA["date_of_birth"])
    driver.find_element(By.CLASS_NAME, "react-datepicker__year-select").click()

    # Выбор предмета
    subjects_input = driver.find_element(By.ID, "subjectsInput")
    subjects_input.send_keys("mat")
    wait.until(EC.visibility_of_element_located(
        (By.XPATH, "//div[contains(@class, 'subjects-auto-complete__option') and text()='Maths']")
    )).click()

    # Выбор хобби
    for hobby in TEST_DATA["hobbies"]:
        driver.find_element(By.XPATH, f"//label[text()='{hobby}']").click()

    # Загрузка файла
    driver.find_element(By.ID, "uploadPicture").send_keys(PICTURE_PATH)

    # Ввод адреса
    driver.find_element(By.ID, "currentAddress").send_keys(TEST_DATA["current_address"])

    # Выбор штата и города
    driver.find_element(By.ID, "state").click()
    driver.find_element(By.XPATH, f"//div[text()='{TEST_DATA['state']}']").click()
    driver.find_element(By.ID, "city").click()
    driver.find_element(By.XPATH, f"//div[text()='{TEST_DATA['city']}']").click()

    # Отправка формы
    driver.find_element(By.ID, "submit").click()

    # Ожидание появления модального окна
    modal = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "modal-content")))

    # Проверка данных в модальном окне
    rows = modal.find_elements(By.CSS_SELECTOR, "table tbody tr")
    results = {}

    for row in rows:
        key = row.find_element(By.TAG_NAME, "td").text
        value = row.find_elements(By.TAG_NAME, "td")[1].text
        results[key] = value

    assert results["Student Name"] == f"{TEST_DATA['first_name']} {TEST_DATA['last_name']}"
    assert results["Student Email"] == TEST_DATA["email"]
    assert results["Gender"] == TEST_DATA["gender"]
    assert results["Mobile"] == TEST_DATA["mobile"]
    assert results["Date of Birth"] == TEST_DATA["date_of_birth"]
    assert results["Subjects"] == TEST_DATA["subjects"]
    assert results["Hobbies"] == ", ".join(TEST_DATA["hobbies"])
    assert results["Address"] == TEST_DATA["current_address"]
    assert results["State and City"] == f"{TEST_DATA['state']} {TEST_DATA['city']}"
    assert results["Picture"] == TEST_DATA["picture"]
