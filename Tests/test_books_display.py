import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


@pytest.fixture(scope="function")
def driver():
    with webdriver.Chrome(service=ChromeService(ChromeDriverManager().install())) as chrome_driver:
        chrome_driver.implicitly_wait(5)
        chrome_driver.maximize_window()
        yield chrome_driver


def test_items_per_page(driver):
    # 1) Открыть раздел "Books"
    driver.get("https://demowebshop.tricentis.com/books")

    # Проверить, что мы на странице Books
    assert "Books" in driver.title

    # Локаторы
    display_per_page_dropdown = (By.ID, "products-pagesize")
    product_items_locator = (By.CSS_SELECTOR, ".product-item")

    # 2) Проверить отображение 8 товаров
    display_dropdown = Select(driver.find_element(*display_per_page_dropdown))
    display_dropdown.select_by_visible_text("8")

    # Ждем обновления списка товаров
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(product_items_locator)
    )

    # Проверяем количество товаров
    items = driver.find_elements(*product_items_locator)
    assert len(items) <= 8, f"Ожидалось не более 8 товаров, но найдено {len(items)}"

    # 3) Выбрать 4 товара на странице
    display_dropdown = Select(driver.find_element(*display_per_page_dropdown))
    display_dropdown.select_by_visible_text("4")

    # Ждем обновления списка товаров
    WebDriverWait(driver, 10).until(
        EC.invisibility_of_element_located((By.CSS_SELECTOR, ".product-item[style*='display: none']"))
    )

    # 4) Проверить отображение 4 товаров
    items = driver.find_elements(*product_items_locator)
    assert len(items) <= 4, f"Ожидалось не более 4 товаров, но найдено {len(items)}"

    # Проверить, что товары видны на странице
    visible_items = [item for item in items if item.is_displayed()]
    assert len(visible_items) == len(items), "Не все товары отображаются"
