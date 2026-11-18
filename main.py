
import batch_ocr
import search_knowledge
import precise_search
import link_questions
import review_links
import knowledge_graph
import difficulty_sort
import quiz_generator


def show_menu():
    print("\n" + "=" * 50)
    print("BDD EXAM ASSISTANT 1.0")
    print("=" * 50)

    print("1. 批量 PDF OCR")
    print("2. 跨 PDF 知识点搜索")
    print("3. 精准检索")
    print("4. 真题与知识点关联")
    print("5. 整理人工审核结果")
    print("6. 生成知识图谱")
    print("7. 知识点难度排序")
    print("8. 复习测试")
    print("0. 退出程序")


def main():
    actions = {
        "1": batch_ocr.main,
        "2": search_knowledge.main,
        "3": precise_search.main,
        "4": link_questions.main,
        "5": review_links.main,
        "6": knowledge_graph.main,
        "7": difficulty_sort.main,
        "8": quiz_generator.main
    }

    while True:
        show_menu()

        choice = input("\n请选择功能（0-8）：").strip()

        if choice == "0":
            print("感谢使用 BDD Exam Assistant！")
            break

        action = actions.get(choice)

        if action is None:
            print("无效选项，请重新选择。")
            continue

        try:
            print("\n正在执行所选功能...\n")
            action()
            print("\n操作结束，返回主菜单。")

        except (FileNotFoundError, ValueError) as error:
            print(f"\n操作失败：{error}")

        except KeyboardInterrupt:
            print("\n操作已取消，返回主菜单。")


if __name__ == "__main__":
    main()
