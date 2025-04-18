# MCP-Undetected-Chromedriver

基于undetected-chromedriver构建的MCP服务，提供一套完整的接口用于自动化控制Chrome浏览器，绕过反爬虫检测。

## 安装

使用 [Smithery](https://smithery.ai/server/@dragons96/mcp-undetected-chromedriver) 为claude安装mcp-undetected-chromedriver服务:

```bash
npx -y @smithery/cli install @dragons96/mcp-undetected-chromedriver --client claude
```

## 配置使用Undetected Chromedriver服务

calude配置实例:

```json
{
  "mcpServers": {
    "mcp-undetected-chromedriver": {
      "command": "npx",
      "args": [
        "-y",
        "@smithery/cli@latest",
        "run",
        "@dragons96/mcp-undetected-chromedriver",
        "--config",
        "{}"
      ]
    }
  }
}
```


### 环境要求

- Python >= 3.11
- Chrome浏览器

### 使用uv安装

```bash
# 创建虚拟环境
uv venv

# 激活虚拟环境
# Windows
.venv\Scripts\activate
# Linux/MacOS
source .venv/bin/activate

# 安装依赖
uv pip install -e .
```


## 项目介绍

MCP-Undetected-Chromedriver 是一个MCP (Multi Channel Protocol) 服务，它将undetected-chromedriver库的功能封装为一系列易于使用的API。该项目适合需要在自动化测试、数据抓取或网页自动化脚本中绕过现代网站反爬虫检测机制的场景。

### 主要特性

- 基于undetected-chromedriver，有效绕过网站的反爬虫检测
- 提供丰富的浏览器操作API接口
- 支持屏幕截图、PDF导出等功能
- 支持复杂的页面交互操作，如点击、填写表单、拖拽等
- 可在MCP生态系统中与其他工具无缝集成

## 待办事项

- [ ] 优化浏览器驱动管理，驱动的异常中断处理
- [ ] 扩展API调用
- [ ] 添加更全面的错误处理和日志记录
- [ ] 完善文档，增加更多使用示例
- [ ] 添加对浏览器配置文件和扩展的支持

## Claude / Cursor 等工具安装

1. 下载源码

```shell
git clone git@github.com:dragons96/mcp-undetected-chromedriver.git
```

2. 配置 `mcpServers`：
   ```json
   {
     "mcpServers": {
       "undetected-chromedriver-mcp-server": {
         "command": "uv",
         "args": [
           "--directory",
           "path/to/mcp-undetected-chromedriver",
           "run",
           "mcp-server-undetected-chromedriver"
         ]
       }
     }
   }
   ```

## 使用方法

### 启动服务

```bash
mcp-server-undetected-chromedriver
```

### 可用API

服务提供以下主要API接口：

- `browser_navigate`: 导航到指定URL
- `browser_screenshot`: 截取当前页面截图
- `browser_click`: 点击页面元素
- `browser_iframe_click`: 点击iframe内的元素
- `browser_fill`: 在输入框中填写内容
- `browser_select`: 在下拉选择框中选择选项
- `browser_hover`: 鼠标悬停在元素上
- `browser_evalute`: 执行JavaScript代码
- `browser_close`: 关闭浏览器
- `browser_get_visible_text`: 获取页面可见文本
- `browser_get_visible_html`: 获取页面可见HTML
- `browser_go_back`: 浏览器后退
- `browser_go_forward`: 浏览器前进
- `browser_drag`: 拖拽元素
- `browser_press_key`: 模拟按键
- `browser_save_as_pdf`: 将页面保存为PDF

### 代码示例

```python
from mcp.client import Client

# 创建MCP客户端
client = Client()
client.start("undetected-chromedriver-mcp-server")

# 导航到网站
response = client.call("browser_navigate", {"url": "https://example.com"})
print(response)

# 截取屏幕截图
response = client.call("browser_screenshot", {"name": "example"})
print(response)

# 获取页面文本
response = client.call("browser_get_visible_text")
print(response.content[0].text)

# 关闭浏览器
client.call("browser_close")
```

## 工作原理

本服务使用undetected-chromedriver库创建一个特殊的Chrome浏览器实例，该实例能有效规避常见的反爬虫检测机制。服务通过MCP协议包装这些功能，提供了一套易于使用的API接口，使自动化测试和网页爬取变得更加便捷。

## 许可证

本项目采用MIT许可证 - 查看[LICENSE](LICENSE)文件了解详情。

## 贡献指南

欢迎提交问题报告和功能请求到GitHub Issues页面。如果您想贡献代码，请先创建issue讨论您的想法。

## 常见问题

**Q: 为什么选择undetected-chromedriver而不是标准的selenium webdriver?**

A: undetected-chromedriver专门设计用于绕过现代网站的反爬虫检测机制，如Cloudflare、Distil Networks等，使其在数据抓取和自动化测试场景中更加可靠。

**Q: 服务如何处理浏览器实例?**

A: 服务维护一个全局的浏览器实例，当首次调用需要浏览器的API时会自动创建。使用 `browser_close`可以显式关闭浏览器。

**Q: 如何处理iframe中的元素?**

A: 使用 `browser_iframe_click`API可以直接操作iframe内的元素，无需手动切换frame上下文。
