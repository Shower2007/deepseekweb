from playwright.sync_api import sync_playwright
import time
import re

# 模块级全局，导入时【不】启动浏览器（避免 with 块退出时把 page 关掉）
_p = None
_browser = None
_page = None
answer = ""
content = []
deepthink = 0
online = 0


def start():
    print('打开页面')
    """启动浏览器并完成登录。重复调用安全（只启动一次）。"""
    global _p, _browser, _page, deepthink, online
    if _page is not None:
        return
    _p = sync_playwright().start()
    _browser = _p.chromium.launch(channel="msedge", headless=False)
    _page = _browser.new_page()

    _page.goto("https://chat.deepseek.com/")
    _page.wait_for_timeout(3000)
    #_page.wait_for_load_state("networkidle")
    print('加载完成')
    # 登陆环节
    _page.get_by_role("button", name="密码登录").click()
    _page.get_by_role("textbox", name="请输入手机号/邮箱地址").click()
    _page.get_by_role("textbox", name="请输入手机号/邮箱地址").fill(open("deepseek_account.txt", encoding='utf-8').readlines()[0].rstrip('\n'))
    _page.get_by_role("textbox", name="请输入密码").click()
    _page.get_by_role("textbox", name="请输入密码").fill(open("deepseek_account.txt", encoding='utf-8').readlines()[1].rstrip('\n'))
    _page.get_by_role("textbox", name="请输入密码").press("Enter")
    #_page.wait_for_load_state("networkidle")
    _page.wait_for_timeout(3000)
    # 登陆环节
    print('登录完成')
    _page.locator("div").filter(has_text=re.compile(r"^智能搜索$")).click()
    deepthink = 0
    online = 0


def _ensure_started():
    """任何对外函数调用前，确保浏览器已启动。"""
    if _page is None:
        start()


def setdeepthink(a):
    if a == 1:
        print('打开深度思考')
    else:
        print('关闭深度思考')
    global deepthink
    _ensure_started()
    if not (a == deepthink):
        _page.locator("div").filter(has_text=re.compile(r"^深度思考$")).click()
        deepthink = a


def setonline(a):
    if a == 1:
        print('打开联网搜索')
    else:
        print('关闭联网搜索')
    global online
    _ensure_started()
    if not (a == online):
        _page.locator("div").filter(has_text=re.compile(r"^智能搜索$")).click()
        online = a


def send(text, title=''):
    print('发送消息')
    global answer
    _ensure_started()
    _page.get_by_role("textbox", name="给 DeepSeek 发送消息").fill(text)
    _page.locator(".ds-button.ds-button--primary").click()
    sendclass = '.ds-button.ds-button--primary.ds-button--filled.ds-button--circle.ds-button--m.ds-button--icon-relative-m._52c986b.bd74640a'
    time.sleep(1)
    while _page.locator(sendclass).count() == 0:
        time.sleep(1)
    # 定位最新（最底下）的回复容器
    latest_reply = _page.locator('.ds-markdown.ds-assistant-message-main-content').last
    # 在该容器内查找所有段落元素
    paragraphs = latest_reply.locator('.ds-markdown-paragraph')
    # 获取所有段落的文本列表（同步方法，不加 await）
    texts = paragraphs.all_inner_texts()
    # 用换行符合并
    answer = '\n'.join(texts).strip()
    print('生成完毕')
    if not (title == ''):
        nameclass = '.afa34042.e0a1edb7.e37a04e4._5a50d80'
        name(_page.locator(nameclass).inner_text(), title)

def new():
    print('打开新对话')
    _ensure_started()
    _page.keyboard.press("ControlOrMeta+j")


def go(title):
    _ensure_started()
    _page.get_by_role("link", name=title, exact=True).first.click()
    print('前往对话-' + title)

def name(old, new):
    print('命名-'+old+'-'+new)
    _ensure_started()
    go(old)
    _page.get_by_role("link", name=old, exact=True).first.hover()
    _page.get_by_role("link", name=old, exact=True).get_by_role("button").click()
    _page.get_by_role("link", name=old, exact=True).get_by_role("button").press("ArrowUp")
    _page.get_by_role("link", name=old, exact=True).get_by_role("button").press("Enter")
    _page.keyboard.press("Control+A")
    _page.keyboard.press("Backspace")
    _page.keyboard.type(new)
    _page.keyboard.press("Enter")


def delete(title):
    _ensure_started()
    go(title)
    _page.get_by_role("link", name=title, exact=True).first.hover()
    _page.get_by_role("link", name=title, exact=True).get_by_role("button").click()
    _page.keyboard.press("ArrowUp")
    _page.keyboard.press("ArrowUp")
    _page.keyboard.press("Enter")
    _page.keyboard.press("Tab")
    _page.keyboard.press("Enter")
    print('删除对话-' + title)

def getcontent():
    print('加载所有标题')
    global content
    _ensure_started()
    content0 = [1]
    content = [0]
    while not (content == content0):
        content0 = _page.locator('div.c08e6e93').all_inner_texts()
        if not (content == []):
            content = content0
            go(content0[-1])
            time.sleep(1)
            content0 = _page.locator('div.c08e6e93').all_inner_texts()


if __name__ == '__main__':
    start()
    content = []
    getcontent()
    if input(content) == 'del':
        for i in content:
            print('delete' + str(i))
            delete(i)
