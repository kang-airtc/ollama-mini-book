import chromadb

# 创建客户端
client = chromadb.Client()

# 创建集合（类似数据库表）
collection = client.create_collection(name="test_docs")

# 添加数据
collection.add(
    documents=[
        "苹果是一种水果，富含维生素C",
        "香蕉是黄色的水果，长在树上",
        "Python是一种编程语言，易于学习",
        "Golang是Google开发的编程语言",
    ],
    ids=["doc1", "doc2", "doc3", "doc4"],
    metadatas=[
        {"category": "水果"},
        {"category": "水果"},
        {"category": "编程"},
        {"category": "编程"},
    ],
)

print("✅ 数据添加成功！")

# 查询相似内容
results = collection.query(query_texts=["Python编程"], n_results=2)

print("\n🔍 查询 'Python编程' 的结果：")
for i, doc in enumerate(results["documents"][0]):
    print(f"  {i + 1}. {doc} 距离: {results['distances'][0][i]:.4f})")

# 另一个查询
results2 = collection.query(query_texts=["水果"], n_results=2)

print("\n🔍 查询 '水果' 的结果：")
for i, doc in enumerate(results2["documents"][0]):
    print(f"  {i + 1}. {doc} (距离: {results2['distances'][0][i]:.4f})")

print("\n✅ 测试完成！")
