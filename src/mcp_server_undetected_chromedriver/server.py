import base64
import datetime
import os
import asyncio
from dataclasses import dataclass
from mcp.server.fastmcp import FastMCP
from mcp import types
from mcp.types import TextContent
from webdriver_manager.core import constants
from typing import Callable, Coroutine, Any


constants.DEFAULT_USER_HOME_CACHE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "chromedriver")

from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.print_page_options import PrintOptions


class Global:
    webdriver = None


async def reset_browser_state():
    if Global.webdriver:
        Global.webdriver.quit()
        Global.webdriver = None


async def ensure_browser(config: dict | None = None):
    if not Global.webdriver:
        Global.webdriver = uc.Chrome(
            driver_executable_path=ChromeDriverManager().install()
        )
    return Global.webdriver


async def create_success_response(message: str | list[str]) -> types.CallToolResult:
    if isinstance(message, str):
        message = [message]
    return types.CallToolResult(
        content=[TextContent(type="text", text=msg) for msg in message],
        isError=False,
    )


async def create_error_response(message: str) -> types.CallToolResult:
    return types.CallToolResult(
        content=[TextContent(type="text", text=message)],
        isError=True,
    )


@dataclass
class ToolContext:
    webdriver: uc.Chrome | None = None


class Tool:

    async def safe_execute(
            self,
            context: ToolContext,
            handler: Callable[[uc.Chrome], Coroutine[Any, Any, types.CallToolResult]],
    ) -> types.CallToolResult:
        try:
            return await handler(context.webdriver)
        except AssertionError as error:
            return await create_error_response(f"Params error: {str(error)}")
        except Exception as error:
            return await create_error_response(f"Operation failed: {str(error)}")


tool = Tool()


mcp = FastMCP(
    "undetected-chromedriver-mcp-server",
)


@mcp.tool()
async def browser_navigate(url: str, timeout: int = 30000):
    """Navigate to a URL

    Args:
        url: The URL to navigate to - required
        timeout: The timeout for the navigation - optional, default is 30000
    """

    assert url, "URL is required"

    async def navigate_handler(driver: uc.Chrome):
        print(f"Navigating to {url}")
        driver.set_page_load_timeout(timeout)
        driver.get(url)
        return await create_success_response(f"Navigated to {url}")

    return await tool.safe_execute(
        ToolContext(webdriver=await ensure_browser()), navigate_handler
    )


DEFAULT_DOWNLOAD_PATH = os.path.join(os.path.expanduser("~"), "Downloads")
SCREENSHOTS = {}


@mcp.tool()
async def browser_screenshot(
        name: str,
        storeBase64: bool = True,
        downloadsDir: str = None,
):
    """Take a screenshot of the current page or a specific element

    Args:
        name: The name of the screenshot - required, default is "screenshot"
        storeBase64: Whether to store the screenshot as a base64 string - optional, default is True
        downloadsDir: The directory to save the screenshot to - optional, default is the user's Downloads directory
    """
    name = name or "screenshot"

    async def screenshot_handler(driver: uc.Chrome):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        filename = f"{name}-{timestamp}.png"
        download_dir = downloadsDir or DEFAULT_DOWNLOAD_PATH

        os.makedirs(download_dir, exist_ok=True)

        output_path = os.path.join(download_dir, filename)
        driver.save_screenshot(output_path)

        messages = [f"Screenshot saved to: {os.path.relpath(output_path, os.getcwd())}"]

        if storeBase64:
            base64 = driver.get_screenshot_as_base64()
            SCREENSHOTS[name] = base64
            # todo: notifications/resources/list_changed
            messages.append(f"Screenshot also stored in memory with name: {name}")

        return await create_success_response(messages)

    return await tool.safe_execute(
        ToolContext(webdriver=await ensure_browser()), screenshot_handler
    )


@mcp.tool()
async def browser_click(
        selector: str,
):
    """Click an element on the page

    Args:
        selector: The selector of the element to click - required
    """
    assert selector, "Selector is required"

    async def click_handler(driver: uc.Chrome):
        driver.find_element(By.CSS_SELECTOR, selector).click()
        return await create_success_response(f"Clicked element: {selector}")

    return await tool.safe_execute(
        ToolContext(webdriver=await ensure_browser()), click_handler
    )


@mcp.tool()
async def browser_iframe_click(
        iframeSelector: str,
        selector: str,
):
    """Click an element inside an iframe on the page

    Args:
        iframeSelector: The selector of the iframe - required
        selector: The selector of the element to click - required
    """
    assert iframeSelector, "Iframe selector is required"
    assert selector, "Selector is required"

    async def iframe_click_handler(driver: uc.Chrome):
        iframe = driver.find_element(By.CSS_SELECTOR, iframeSelector)
        driver.switch_to.frame(iframe)
        driver.find_element(By.CSS_SELECTOR, selector).click()
        driver.switch_to.default_content()
        return await create_success_response(
            f"Clicked element {selector} inside iframe {iframeSelector}"
        )

    return await tool.safe_execute(
        ToolContext(webdriver=await ensure_browser()), iframe_click_handler
    )


@mcp.tool()
async def browser_fill(
        selector: str,
        value: str,
):
    """fill out an input field

    Args:
        selector: CSS selector for input field - required
        value: The value to fill - required
    """
    assert selector, "Selector is required"
    assert value, "Value is required"

    async def fill_handler(driver: uc.Chrome):
        driver.find_element(By.CSS_SELECTOR, selector).send_keys(value)
        return await create_success_response(f"Filled {selector} with: {value}")

    return await tool.safe_execute(
        ToolContext(webdriver=await ensure_browser()), fill_handler
    )


@mcp.tool()
async def browser_select(
        selector: str,
        value: str,
):
    """Select an element on the page with Select tag

    Args:
        selector: CSS selector for element to select - required
        value: The value to select - required
    """
    assert selector, "Selector is required"
    assert value, "Value is required"

    async def select_handler(driver: uc.Chrome):
        select = Select(driver.find_element(By.CSS_SELECTOR, selector))
        select.select_by_value(value)
        return await create_success_response(f"Selected {selector} with: {value}")

    return await tool.safe_execute(
        ToolContext(webdriver=await ensure_browser()), select_handler
    )


@mcp.tool()
async def browser_hover(
        selector: str,
):
    """Hover over an element on the page

    Args:
        selector: CSS selector for element to hover over - required
    """
    assert selector, "Selector is required"

    async def hover_handler(driver: uc.Chrome):
        element = driver.find_element(By.CSS_SELECTOR, selector)
        ActionChains(driver).move_to_element(element).perform()
        return await create_success_response(f"Hovered over {selector}")

    return await tool.safe_execute(
        ToolContext(webdriver=await ensure_browser()), hover_handler
    )


@mcp.tool()
async def browser_evalute(
        script: str,
):
    """Evaluate a JavaScript expression in the browser console

    Args:
        script: The JavaScript expression to evaluate - required
    """
    assert script, "Script is required"

    async def evaluate_handler(driver: uc.Chrome):
        return await create_success_response(
            [
                "Executed script:",
                f"{script}",
                "Result:",
                f"{driver.execute_script(script)}",
            ]
        )

    return await tool.safe_execute(
        ToolContext(webdriver=await ensure_browser()), evaluate_handler
    )


@mcp.tool()
async def browser_close():
    """Close the browser and release all resources"""
    await reset_browser_state()
    return await create_success_response("Browser closed successfully")


@mcp.tool()
async def browser_get_visible_text():
    """Get the visible text of the current page"""

    async def get_visible_text_handler(driver: uc.Chrome):
        # 使用JavaScript获取页面中所有可见文本内容
        script = """
        return Array.from(document.body.querySelectorAll('*'))
            .filter(el => {
                const style = window.getComputedStyle(el);
                return !!(el.textContent.trim()) && 
                       style.display !== 'none' && 
                       style.visibility !== 'hidden' &&
                       style.opacity !== '0';
            })
            .map(el => el.textContent.trim())
            .filter(text => text)
            .join('\\n');
        """
        visible_text = driver.execute_script(script)
        return await create_success_response(visible_text)

    return await tool.safe_execute(
        ToolContext(webdriver=await ensure_browser()), get_visible_text_handler
    )


@mcp.tool()
async def browser_get_visible_html():
    """Get the HTML of the current page"""

    async def get_visible_html_handler(driver: uc.Chrome):
        return await create_success_response(driver.page_source)

    return await tool.safe_execute(
        ToolContext(webdriver=await ensure_browser()), get_visible_html_handler
    )


@mcp.tool()
async def browser_go_back():
    """Navigate back in browser history"""

    async def go_back_handler(driver: uc.Chrome):
        driver.back()
        return await create_success_response("Navigated back in browser history")

    return await tool.safe_execute(
        ToolContext(webdriver=await ensure_browser()), go_back_handler
    )


@mcp.tool()
async def browser_go_forward():
    """Navigate forward in browser history"""

    async def go_forward_handler(driver: uc.Chrome):
        driver.forward()
        return await create_success_response("Navigated forward in browser history")

    return await tool.safe_execute(
        ToolContext(webdriver=await ensure_browser()), go_forward_handler
    )


@mcp.tool()
async def browser_drag(
        sourceSelector: str,
        targetSelector: str,
):
    """Drag an element to another element

    Args:
        sourceSelector: The selector for the element to drag - required
        targetSelector: The selector for the target location - required
    """
    assert sourceSelector, "Source selector is required"
    assert targetSelector, "Target selector is required"

    async def drag_handler(driver: uc.Chrome):
        source = driver.find_element(By.CSS_SELECTOR, sourceSelector)
        target = driver.find_element(By.CSS_SELECTOR, targetSelector)
        ActionChains(driver).drag_and_drop(source, target).perform()
        return await create_success_response(
            f"Dragged {sourceSelector} to {targetSelector}"
        )

    return await tool.safe_execute(
        ToolContext(webdriver=await ensure_browser()), drag_handler
    )


@mcp.tool()
async def browser_press_key(
        key: str,
        selector: str = None,
):
    """Press a key on the keyboard

    Args:
        key: The key to press - required, (e.g. 'Enter', 'ArrowDown', 'a')
        selector: Optional CSS selector to focus on before pressing the key - optional
    """
    assert key, "Key is required"

    async def press_key_handler(driver: uc.Chrome):
        # 如果提供了选择器，先找到元素并聚焦
        if selector:
            element = driver.find_element(By.CSS_SELECTOR, selector)
            element.click()  # 点击元素以确保聚焦

        # 处理特殊键
        special_keys = {
            'Enter': '\ue007',
            'Tab': '\ue004',
            'Escape': '\ue00c',
            'Space': '\ue00d',
            'Backspace': '\ue003',
            'Delete': '\ue017',
            'ArrowUp': '\ue013',
            'ArrowDown': '\ue015',
            'ArrowLeft': '\ue012',
            'ArrowRight': '\ue014',
            'PageUp': '\ue00e',
            'PageDown': '\ue00f',
            'Home': '\ue011',
            'End': '\ue010',
            'F1': '\ue031',
            'F2': '\ue032',
            'F3': '\ue033',
            'F4': '\ue034',
            'F5': '\ue035',
            'F6': '\ue036',
            'F7': '\ue037',
            'F8': '\ue038',
            'F9': '\ue039',
            'F10': '\ue03a',
            'F11': '\ue03b',
            'F12': '\ue03c',
        }

        # 映射按键
        key_to_send = special_keys.get(key, key)

        # 创建ActionChains对象
        actions = ActionChains(driver)

        # 发送按键
        if selector:
            element = driver.find_element(By.CSS_SELECTOR, selector)
            actions.send_keys_to_element(element, key_to_send)
        else:
            actions.send_keys(key_to_send)

        # 执行操作
        actions.perform()

        if selector:
            return await create_success_response(f"Pressed key '{key}' on element '{selector}'")
        else:
            return await create_success_response(f"Pressed key '{key}'")

    return await tool.safe_execute(
        ToolContext(webdriver=await ensure_browser()), press_key_handler
    )


@mcp.tool()
async def browser_save_as_pdf(
        outputPath: str,
        filename: str = "page.pdf",
        format: str = 'A4',
        printBackground: bool = True,
        margin: dict = None,
):
    """Save the current page as a PDF

    Args:
        outputPath: The path to save the PDF to - required
        filename: The name of the PDF file - optional, default is "page.pdf"
        format: The format of the PDF - optional, default is "A4" (e.g. "A4", "LETTER", "LEGAL", "TABLOID")
        printBackground: Whether to print the background - optional, default is True
        margin: The margin of the PDF - optional, default is None (e.g. {"top": "1cm", "right": "1cm", "bottom": "1cm", "left": "1cm"})
    """
    assert outputPath, "Output path is required"

    margin = margin or {"top": 0, "right": 0, "bottom": 0, "left": 0}

    async def save_as_pdf_handler(driver: uc.Chrome):
        # 确保输出路径存在
        os.makedirs(outputPath, exist_ok=True)

        # 构建完整文件路径
        full_path = os.path.join(outputPath, filename)

        # 设置打印选项
        print_options = PrintOptions()
        print_options.orientation  = 'portrait'
        print_options.scale = 1.0
        print_options.background = printBackground
        print_options.margin_left = margin.get('left', 0)
        print_options.margin_right = margin.get('right', 0)
        print_options.margin_top = margin.get('top', 0)
        print_options.margin_bottom = margin.get('bottom', 0)

        # 保存PDF文件
        data = driver.print_page(print_options)
        with open(full_path, 'wb') as f:
            f.write(base64.b64decode(data))

        return await create_success_response(f"Saved page as PDF to {full_path}")

    return await tool.safe_execute(
        ToolContext(webdriver=await ensure_browser()), save_as_pdf_handler
    )


if __name__ == "__main__":
    asyncio.run(mcp.run_stdio_async())
