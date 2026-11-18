
from pathlib import Path
import json

import networkx as nx
from pyvis.network import Network


BASE_DIR = Path(__file__).resolve().parent

CONCEPTS_PATH = BASE_DIR / "knowledge" / "concepts.json"
LINKS_PATH = BASE_DIR / "output" / "reviewed_links.json"
OUTPUT_PATH = BASE_DIR / "output" / "knowledge_graph.html"


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def build_graph(concepts, questions):
    graph = nx.DiGraph()

    for concept in concepts:
        concept_id = f"concept:{concept['id']}"

        graph.add_node(
            concept_id,
            label=concept["name"],
            node_type="concept",
            title=(
                f"知识点：{concept['name']}\n"
                f"分类：{concept['category']}"
            )
        )

    for question in questions:
        question_id = f"question:{question['question_id']}"

        graph.add_node(
            question_id,
            label=question["question_id"],
            node_type="question",
            title=(
                f"真题：{question['question']}\n"
                f"来源：{question['question_source']}\n"
                f"页码：{question['question_page']}"
            )
        )

        for concept in question["concepts"]:
            concept_id = f"concept:{concept['concept_id']}"
            status = concept["status"]

            # 已否定的关联不绘制为有效关系
            if status == "rejected":
                continue

            graph.add_edge(
                question_id,
                concept_id,
                status=status,
                label=(
                    "已确认"
                    if status == "confirmed"
                    else "待审核"
                )
            )

            for evidence in concept["evidence"]:
                source = evidence["source"]
                page = evidence["page"]

                source_id = f"source:{source}"
                page_id = f"page:{source}:{page}"

                graph.add_node(
                    source_id,
                    label=source,
                    node_type="source",
                    title=f"PDF：{source}"
                )

                graph.add_node(
                    page_id,
                    label=f"Page {page}",
                    node_type="page",
                    title=f"文件：{source}\n页码：{page}"
                )

                graph.add_edge(
                    concept_id,
                    page_id,
                    status="evidence",
                    label="候选证据"
                )

                graph.add_edge(
                    page_id,
                    source_id,
                    status="source",
                    label="来自"
                )

    return graph


def save_graph(graph):
    net = Network(
        height="800px",
        width="100%",
        bgcolor="#ffffff",
        font_color="#222222",
        directed=True,
        cdn_resources="in_line"
    )

    colors = {
        "question": "#F4A261",
        "concept": "#4A90E2",
        "source": "#2A9D8F",
        "page": "#A78BFA"
    }

    for node_id, data in graph.nodes(data=True):
        node_type = data["node_type"]

        net.add_node(
            node_id,
            label=data["label"],
            title=data["title"],
            color=colors.get(node_type, "#cccccc"),
            shape="dot",
            size=18
        )

    for source, target, data in graph.edges(data=True):
        status = data["status"]

        if status == "confirmed":
            color = "#2A9D8F"
            dashes = False
        elif status == "pending_review":
            color = "#E9C46A"
            dashes = True
        else:
            color = "#BBBBBB"
            dashes = True

        net.add_edge(
            source,
            target,
            title=data["label"],
            color=color,
            dashes=dashes
        )

    
    net.barnes_hut()
    html = net.generate_html()
    OUTPUT_PATH.write_text(html, encoding="utf-8")



def main():
    concepts = load_json(CONCEPTS_PATH)
    questions = load_json(LINKS_PATH)

    graph = build_graph(concepts, questions)

    save_graph(graph)

    print("知识图谱生成成功！")
    print(f"节点数量：{graph.number_of_nodes()}")
    print(f"连接数量：{graph.number_of_edges()}")
    print(f"文件位置：{OUTPUT_PATH}")


if __name__ == "__main__":
    main()
