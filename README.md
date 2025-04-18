# MCP-Undetected-Chromedriver

An MCP service built on undetected-chromedriver, providing a comprehensive interface for automating Chrome browser control while bypassing anti-bot detection.

[中文文档](README_ZH.md)

## Project Introduction

MCP-Undetected-Chromedriver is an MCP (Multi Channel Protocol) service that wraps the functionality of the undetected-chromedriver library into a series of easy-to-use APIs. This project is particularly suitable for scenarios that require bypassing modern website anti-bot detection mechanisms in automated testing, data scraping, or web automation scripts.

### Key Features

- Based on undetected-chromedriver, effectively bypassing website anti-bot detection
- Provides rich browser operation API interfaces
- Supports screenshots, PDF export, and other functionalities
- Supports complex page interaction operations such as clicking, form filling, dragging, etc.
- Seamlessly integrates with other tools in the MCP ecosystem

## Todo List

- [ ] Optimize browser driver management and handle driver interruptions
- [ ] Extend API capabilities
- [ ] Add more comprehensive error handling and logging
- [ ] Improve documentation with more usage examples
- [ ] Add support for browser profiles and extensions

## Installation

### Requirements

- Python >= 3.11
- Chrome browser

### Installation with uv

```bash
# Create virtual environment
uv venv

# Activate virtual environment
# Windows
.venv\Scripts\activate
# Linux/MacOS
source .venv/bin/activate

# Install dependencies
uv pip install -e .
```

## Usage

### Starting the Service

```bash
mcp-server-undetected-chromedriver
```

### Available APIs

The service provides the following main API interfaces:

- `webdriver_navigate`: Navigate to a specified URL
- `webdriver_screenshot`: Take a screenshot of the current page
- `webdriver_click`: Click on page elements
- `webdriver_iframe_click`: Click on elements within an iframe
- `webdriver_fill`: Fill content in input fields
- `webdriver_select`: Select options in dropdown selection boxes
- `webdriver_hover`: Hover the mouse over elements
- `webdriver_evalute`: Execute JavaScript code
- `webdriver_close`: Close the browser
- `webdriver_get_visible_text`: Get visible text on the page
- `webdriver_get_visible_html`: Get visible HTML on the page
- `webdriver_go_back`: Navigate backward in browser history
- `webdriver_go_forward`: Navigate forward in browser history
- `webdriver_drag`: Drag elements
- `webdriver_press_key`: Simulate key presses
- `webdriver_save_as_pdf`: Save the page as a PDF

### Code Example

```python
from mcp.client import Client

# Create MCP client
client = Client()
client.start("undetected-chromedriver-mcp-server")

# Navigate to website
response = client.call("webdriver_navigate", {"url": "https://example.com"})
print(response)

# Take a screenshot
response = client.call("webdriver_screenshot", {"name": "example"})
print(response)

# Get page text
response = client.call("webdriver_get_visible_text")
print(response.content[0].text)

# Close the browser
client.call("webdriver_close")
```

## How It Works

This service uses the undetected-chromedriver library to create a specialized Chrome browser instance that effectively evades common anti-bot detection mechanisms. The service wraps these features through the MCP protocol, providing an easy-to-use API interface that makes automated testing and web scraping more convenient.

## License

[License Information]

## Contribution Guidelines

Bug reports and feature requests are welcome on the GitHub Issues page. If you want to contribute code, please create an issue to discuss your ideas first.

## FAQ

**Q: Why choose undetected-chromedriver instead of the standard selenium webdriver?**

A: undetected-chromedriver is specifically designed to bypass anti-bot detection mechanisms of modern websites, such as Cloudflare, Distil Networks, etc., making it more reliable for data scraping and automated testing scenarios.

**Q: How does the service handle browser instances?**

A: The service maintains a global browser instance, which is automatically created when an API requiring a browser is first called. The browser can be explicitly closed using the `webdriver_close` API.

**Q: How to handle elements within iframes?**

A: The `webdriver_iframe_click` API can directly operate on elements within iframes, without the need to manually switch frame contexts.
