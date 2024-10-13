import cv2
import numpy as np
import pyautogui
import pytesseract
import keyboard
import sys
import time
import uuid
from paddlex import create_pipeline

paddlex_pipeline = create_pipeline(pipeline='ocr', device='cpu')
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe' # 设置 Tesseract-OCR 的路径

# 跟踪状态的变量
not_found_count = 0
last_not_found_time = 0
last_numbers = None  # 存储上次识别的数字
skip_count = 0  # 跳过次数计数器

def capture_area():
    region = (200, 220, 300, 140)  # (x, y, width, height) 详情如何配置可以看 (https://github.com/ChaosJulien/XiaoYuanKouSuan_Auto/blob/main/image/example1.png)
    screenshot = pyautogui.screenshot(region=region)
    file_name = str(uuid.uuid4()) + ".png"  # Generate a random UUID and use it as the file name
    # screenshot.save(f"../img/{file_name}")
    return np.array(screenshot)

def recognize_numbers(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    text = pytesseract.image_to_string(thresh, config='--psm 6')
    number = [int(s) for s in text.split() if s.isdigit()]
    print(number)
    return number

def recognize_numbers_paddlex(image):
    output = paddlex_pipeline.predict([image])
    for res in output:
        ret = res.json['rec_text']
        print(ret)
        if len(ret) == 3 and (ret[1] == '？' or ret[1] == '?'):
            return [ret[0], ret[2]]
        return ret    

def handle_insufficient_numbers():
    global not_found_count, last_not_found_time

    current_time = time.time()
    not_found_count = not_found_count + 1 if current_time - last_not_found_time <= 1 else 1
    last_not_found_time = current_time

    print("未找到足够的数字进行比较")

def click_buttons():
    pyautogui.click(280, 840)  # 点击“开心收下”按钮
    time.sleep(0.3)
    pyautogui.click(410, 990)  # 点击“继续”按钮
    time.sleep(0.3)
    pyautogui.click(280, 910)  # 点击“继续PK”按钮

def draw_comparison(numbers):
    global not_found_count, last_numbers, skip_count

    if len(numbers) != 2 or not numbers[0].isdigit() or not numbers[1].isdigit():
        handle_insufficient_numbers()
        return

    # 如果当前数字与上一个数字相同，则增加跳过计数
    # if last_numbers is not None and last_numbers == numbers:
    #     skip_count += 1
    #     print(f"当前结果与上次相同，跳过此次执行 (次数: {skip_count})")
    #     if skip_count > 5:  # 如果跳过次数超过5，则强制执行一次
    #         skip_count = 0
    #         execute_drawing_logic(numbers)
    #     return

    execute_drawing_logic(numbers)  # 执行当前数字的绘制逻辑

    not_found_count = 0  # 重置未找到计数
    last_numbers = numbers  # 更新上次识别的数字
    skip_count = 0  # 重置跳过次数

def execute_drawing_logic(numbers):
    first, second = int(numbers[0]), int(numbers[1])  # 获取前两个数字
    print(f"识别的数字: {first}, {second}")

    if first > second:
        print(f"{first} > {second}")
        draw_greater_than()
    elif first < second:
        print(f"{first} < {second}")
        draw_less_than()

def draw_greater_than():
    print("press .")
    pyautogui.press(".")  # BlueStacks中的大于号快捷键

def draw_less_than():
    print("press ,")
    pyautogui.press(",")  # BlueStacks中的小于号快捷键

def main():
    keyboard.add_hotkey('=', lambda: sys.exit("进程已结束"))  # 默认的退出快捷键

    try:
        while True:
            image = capture_area()  # 截取屏幕区域
            numbers = recognize_numbers_paddlex(image)  # 从截取的图像中识别数字
            draw_comparison(numbers)  # 比较并绘制结果
            time.sleep(0.1)
    except SystemExit as e:
        print(e)

if __name__ == "__main__":
    main()  # 启动主程序