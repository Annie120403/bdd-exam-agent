
from pathlib import Path
import json
import shutil
import subprocess

import pymupdf


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"

JSON_PATH = OUTPUT_DIR / "knowledge_base.json"

TESSERACT = shutil.which("tesseract") or (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


def extract_text(pdf_path):
    pages = []

    with pymupdf.open(pdf_path) as doc:

        for i, page in enumerate(doc):

            # 优先读取 PDF 自带文字
            text = page.get_text().strip()

            # 如果没有可提取文字，则使用 OCR
            if not text:
                image = page.get_pixmap(dpi=300).tobytes("png")

                result = subprocess.run(
                    [TESSERACT, "stdin", "stdout", "-l", "fra"],
                    input=image,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True
                )

                text = result.stdout.decode("utf-8").strip()

            pages.append({
                "source": pdf_path.name,
                "page": i + 1,
                "text": text
            })

            print(
                f"{pdf_path.name}: "
                f"{i + 1}/{doc.page_count} 页完成"
            )

    return pages


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    pdf_files = sorted(DATA_DIR.glob("*.pdf"))

    if not pdf_files:
        print("data 文件夹中没有 PDF 文件")
        return

    knowledge_base = []

    for pdf_path in pdf_files:
        print(f"\n开始处理：{pdf_path.name}")

        pages = extract_text(pdf_path)
        knowledge_base.extend(pages)

    with open(JSON_PATH, "w", encoding="utf-8") as file:
        json.dump(
            knowledge_base,
            file,
            ensure_ascii=False,
            indent=4
        )

    print("\n全部 PDF 处理完成！")
    print(f"PDF 文件数量：{len(pdf_files)}")
    print(f"总页数：{len(knowledge_base)}")
    print(f"知识库位置：{JSON_PATH}")


if __name__ == "__main__":
    main()
