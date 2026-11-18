
from pathlib import Path  # 管理文件路径
import subprocess  # 调用外部 OCR 引擎
import pymupdf  # 读取 PDF

BASE_DIR = Path(__file__).resolve().parent  # 项目根目录
PDF_PATH = BASE_DIR / "data" / "C1-E_A.pdf"  # PDF 路径
OUTPUT_PATH = BASE_DIR / "output" / "C1-E_A.txt"  # TXT 保存路径

TESSERACT = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def main():
    OUTPUT_PATH.parent.mkdir(exist_ok=True)  # 确保 output 文件夹存在

    with pymupdf.open(PDF_PATH) as doc:  # 打开 PDF
        with open(OUTPUT_PATH, "w", encoding="utf-8") as file:  # 打开 TXT 文件

            for i, page in enumerate(doc):  # 遍历全部 26 页
                image = page.get_pixmap(dpi=300).tobytes("png")  # 页面转图片

                result = subprocess.run(
                    [TESSERACT, "stdin", "stdout", "-l", "fra"],
                    input=image,  # 将图片交给 OCR
                    stdout=subprocess.PIPE,  # 接收识别结果
                    check=True  # OCR 失败时报告错误
                )

                text = result.stdout.decode("utf-8")  # 转换成字符串

                file.write(f"\n===== Page {i + 1} =====\n")  # 写入页码
                file.write(text + "\n")  # 写入识别文字

                print(f"第 {i + 1}/{doc.page_count} 页识别完成")  # 显示进度

    print("全部 OCR 识别完成！")  # 循环结束后输出


if __name__ == "__main__":
    main()  # 启动主程序
