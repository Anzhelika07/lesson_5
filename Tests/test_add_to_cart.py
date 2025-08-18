import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


@pytest.fixture(scope="function")
def driver():
    # Используем контекстный менеджер для управления драйвером
    with webdriver.Chrome(service=ChromeService(ChromeDriverManager().install())) as chrome_driver:
        chrome_driver.implicitly_wait(5)
        chrome_driver.maximize_window()
        yield chrome_driver


@pytest.mark.parametrize("search_query", ["Laptop", "Smartphone", "Fiction"])
def test_add_to_cart(driver, search_query):
    try:
        # 1) Открыть главную страницу
        driver.get("https://demowebshop.tricentis.com/")

        # 2) Выполнить поиск
        search_input = driver.find_element(By.ID, "small-searchterms")
        search_input.clear()
        search_input.send_keys(search_query)
        driver.find_element(By.CSS_SELECTOR, "input[value='Search']").click()

        # Ожидание результатов поиска
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".product-item"))
        )

        # 3) Добавить первый товар в корзину
        products = driver.find_elements(By.CSS_SELECTOR, ".product-item")
        assert len(products) > 0, f"Товары по запросу '{search_query}' не найдены"

        first_product = products[0]
        product_title = first_product.find_element(By.CSS_SELECTOR, ".product-title a").text.strip()

        # Проверяем наличие кнопки добавления
        add_button = first_product.find_element(By.CSS_SELECTOR, ".button-2.product-box-add-to-cart-button")
        add_button.click()

        # Ожидание сообщения о добавлении
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//p[contains(., 'added to your')]"))
        )

        # 4) Перейти в корзину
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Shopping cart']"))
        ).click()

        # 5) Проверить наличие товара в корзине
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".product-name"))
        )

        cart_items = driver.find_elements(By.CSS_SELECTOR, ".product-name")
        item_titles = [item.text.strip() for item in cart_items]

        assert product_title in item_titles, (
            f"Ожидался товар: '{product_title}'\n"
            f"Фактические товары в корзине: {item_titles}"
        )

    except Exception as e:
        # Делаем скриншот при ошибке
        driver.save_screenshot(f"error_{search_query}.png")
        pytest.fail(f"Тест упал с ошибкой: {str(e)}")
