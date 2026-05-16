import requests
import json


def get_embedding(text, model="nomic-embed-text:latest"):
    """
    使用 Ollama 的 nomic-embed-text 模型获取文本的向量嵌入

    Args:
        text: 要嵌入的文本
        model: 使用的模型名称

    Returns:
        向量列表
    """
    url = "http://localhost:11434/api/embeddings"

    payload = {"model": model, "prompt": text}

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        return result.get("embedding", [])
    except Exception as e:
        print(f"❌ 获取嵌入失败: {e}")
        return []


def split_text_by_paragraphs(text, separator="\n\n"):
    """按段落分割文本"""
    chunks = []
    raw_chunks = text.split(separator)

    for chunk in raw_chunks:
        cleaned = chunk.strip()
        if cleaned:
            chunks.append(cleaned)

    return chunks


def load_text(filepath):
    """加载文本文件"""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


if __name__ == "__main__":
    print("=" * 70)
    print("Ollama 向量化嵌入演示 - 使用 nomic-embed-text:latest")
    print("=" * 70)

    # 1. 加载并分割文本
    print("\n📄 正在加载文本文件...")
    text = load_text("text.txt")
    chunks = split_text_by_paragraphs(text, separator="\n\n")
    print(f"✅ 文本分割完成，共 {len(chunks)} 个文本块\n")

    # 2. 对每个文本块进行向量化
    print("🔮 正在使用 Ollama (nomic-embed-text:latest) 生成向量嵌入...\n")

    embeddings = []
    for i, chunk in enumerate(chunks, 1):
        print(f"处理第 {i}/{len(chunks)} 个文本块...", end=" ")

        # 获取向量
        embedding = get_embedding(chunk)

        if embedding:
            embeddings.append(
                {
                    "id": f"chunk_{i}",
                    "text": chunk,
                    "embedding": embedding,
                    "vector_dim": len(embedding),
                }
            )
            print(f"✅ 成功 (维度: {len(embedding)})")
        else:
            print("❌ 失败")

    # 3. 展示结果
    print("\n" + "=" * 70)
    print("📊 向量化结果概览")
    print("=" * 70)

    print(f"\n成功生成 {len(embeddings)} 个向量嵌入")

    if embeddings:
        print(f"向量维度: {embeddings[0]['vector_dim']}")
        print(f"\n各文本块预览：\n")

        for item in embeddings:
            preview = item["text"][:80].replace("\n", " ")
            if len(item["text"]) > 80:
                preview += "..."
            print(f"  {item['id']}: {preview}")
            print(
                f"       向量维度: {item['vector_dim']} | 向量前5个值: {item['embedding'][:5]}"
            )
            print()

        # 4. 示例：计算两个文本块的相似度
        print("=" * 70)
        print("🔍 相似度计算示例")
        print("=" * 70)

        if len(embeddings) >= 2:
            import numpy as np

            # 计算余弦相似度
            def cosine_similarity(vec1, vec2):
                vec1 = np.array(vec1)
                vec2 = np.array(vec2)
                return np.dot(vec1, vec2) / (
                    np.linalg.norm(vec1) * np.linalg.norm(vec2)
                )

            # 比较第1个和第2个文本块
            sim_1_2 = cosine_similarity(
                embeddings[0]["embedding"], embeddings[1]["embedding"]
            )
            print(f"\n块1 vs 块2 相似度: {sim_1_2:.4f}")

            # 比较第1个和第3个文本块（不同章节，应该不太相似）
            if len(embeddings) >= 3:
                sim_1_3 = cosine_similarity(
                    embeddings[0]["embedding"], embeddings[2]["embedding"]
                )
                print(f"块1 vs 块3 相似度: {sim_1_3:.4f}")

        # 5. 保存结果到文件（可选）
        print("\n" + "=" * 70)
        print("💾 保存结果")
        print("=" * 70)

        # 保存向量到JSON文件（用于检查）
        output_data = []
        for item in embeddings:
            output_data.append(
                {
                    "id": item["id"],
                    "text_preview": item["text"][:100] + "..."
                    if len(item["text"]) > 100
                    else item["text"],
                    "vector_dim": item["vector_dim"],
                    "vector_sample": item["embedding"][:10],  # 只保存前10个值作为示例
                }
            )

        with open("embeddings_result.json", "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"✅ 结果已保存到 embeddings_result.json")
        print(f"   包含文本预览和前10个向量值")

    print("\n" + "=" * 70)
    print("🎉 向量化完成！")
    print("\n下一步：可以将这些向量存储到 ChromaDB 或进行相似度搜索")
    print("=" * 70)
