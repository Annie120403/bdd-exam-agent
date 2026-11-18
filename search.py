
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
TXT_PATH = BASE_DIR / "output" / "C1-E_A.txt"


def main():
    keyword = input("请输入要搜索的关键词：")

    with open(TXT_PATH, "r", encoding="utf-8") as file:
        text = file.read()

    if keyword.lower() in text.lower():
        print("找到相关内容！")
    else:
        print("没有找到相关内容。")


if __name__ == "__main__":
    main()
