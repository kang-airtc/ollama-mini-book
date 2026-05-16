def split_text_by_paragraphs(text, separator="\n\n"):
    """
    按段落分割文本

    Args:
        text: 原始文本内容
        separator: 分隔符，默认是双换行符（空行分隔）

    Returns:
        分割后的文本块列表
    """
    chunks = []

    # 按分隔符分割
    raw_chunks = text.split(separator)

    # 清理每个块
    for chunk in raw_chunks:
        # 去除首尾空白字符
        cleaned = chunk.strip()
        # 只保留非空的块
        if cleaned:
            chunks.append(cleaned)

    return chunks


def split_text_with_overlap(text, separator="\n\n", overlap=50):
    """
    按段落分割，并添加重叠内容（更适合向量化）

    Args:
        text: 原始文本内容
        separator: 分隔符
        overlap: 重叠字符数

    Returns:
        带有重叠的文本块列表
    """
    chunks = split_text_by_paragraphs(text, separator)

    if len(chunks) <= 1:
        return chunks

    # 添加重叠
    overlapped_chunks = []
    for i, chunk in enumerate(chunks):
        if i > 0 and overlap > 0:
            # 从前一个块取末尾的overlap个字符
            prev_end = chunks[i - 1][-overlap:]
            chunk = prev_end + chunk

        overlapped_chunks.append(chunk)

    return overlapped_chunks


def load_and_split_text(filepath, separator="\n\n", with_overlap=False, overlap=50):
    """
    从文件加载文本并进行分割

    Args:
        filepath: 文本文件路径
        separator: 分隔符
        with_overlap: 是否添加重叠
        overlap: 重叠字符数

    Returns:
        文本块列表
    """
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    if with_overlap:
        return split_text_with_overlap(text, separator, overlap)
    else:
        return split_text_by_paragraphs(text, separator)


if __name__ == "__main__":
    # 读取文本文件
    filepath = "text.txt"

    print("=" * 60)
    print("文本分割演示")
    print("=" * 60)

    # 方式1：简单分割
    print("\n【方式1：按段落简单分割】\n")
    chunks = load_and_split_text(filepath, separator="\n\n")

    print(f"共分割成 {len(chunks)} 个文本块：\n")

    for i, chunk in enumerate(chunks, 1):
        # 显示前100字符
        preview = chunk[:100].replace("\n", " ")
        if len(chunk) > 100:
            preview += "..."
        print(f"块 {i}: {preview}")
        print(f"  长度: {len(chunk)} 字符\n")

    # 方式2：带重叠的分割
    print("\n" + "=" * 60)
    print("\n【方式2：带重叠的分割（overlap=30）】\n")
    chunks_with_overlap = load_and_split_text(
        filepath, separator="\n\n", with_overlap=True, overlap=30
    )

    print(f"共分割成 {len(chunks_with_overlap)} 个文本块：\n")

    for i, chunk in enumerate(chunks_with_overlap[:3], 1):  # 只显示前3个
        preview = chunk[:100].replace("\n", " ")
        if len(chunk) > 100:
            preview += "..."
        print(f"块 {i}: {preview}")
        print(f"  长度: {len(chunk)} 字符")
        if i > 0:
            print(f"  包含前一块的末尾30个字符作为上下文\n")

    # 展示完整块内容示例
    print("\n" + "=" * 60)
    print("\n【完整块内容示例 - 第2块】\n")
    print(chunks[1])
    print(f"\n（共 {len(chunks[1])} 字符）")

    print("\n" + "=" * 60)
    print("\n✅ 文本分割完成！这些文本块可以直接用于：")
    print("   - 生成向量嵌入 (Embedding)")
    print("   - 存储到向量数据库")
    print("   - 构建检索增强生成 (RAG) 系统")
    print("=" * 60)
