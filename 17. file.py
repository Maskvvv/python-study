print("=" * 50)
print("Python 文件读写演示")
print("=" * 50)

test_file = 'test_file.txt'

# 1. 写入文件 ('w' 模式 - 覆盖写入)
print("\n【1. 写入文件 - 'w' 模式】")
with open(test_file, 'w', encoding='utf-8') as f:
    f.write("第一行：Hello, Python!\n")
    f.write("第二行：文件操作很简单\n")
    f.write("第三行：继续学习吧\n")
print("✓ 文件写入完成")

# 2. 追加文件 ('a' 模式 - 在文件末尾追加)
print("\n【2. 追加文件 - 'a' 模式】")
with open(test_file, 'a', encoding='utf-8') as f:
    f.write("第四行：这是追加的内容\n")
    f.write("第五行：追加更多内容\n")
print("✓ 内容追加完成")

# 3. 读取文件 - read() 方法（一次性读取全部）
print("\n【3. 读取文件 - read() 方法】")
with open(test_file, 'r', encoding='utf-8') as f:
    content = f.read()
    print(content)

# 4. 读取文件 - readline() 方法（逐行读取）
print("\n【4. 读取文件 - readline() 方法】")
with open(test_file, 'r', encoding='utf-8') as f:
    line1 = f.readline()
    line2 = f.readline()
    print(f"第一行: {line1.strip()}")
    print(f"第二行: {line2.strip()}")

# 5. 读取文件 - readlines() 方法（返回列表）
print("\n【5. 读取文件 - readlines() 方法】")
with open(test_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    print(f"共有 {len(lines)} 行")
    for i, line in enumerate(lines, 1):
        print(f"  行{i}: {line.strip()}")

# 6. 逐行迭代（内存高效）
print("\n【6. 逐行迭代 - 推荐方式】")
with open(test_file, 'r', encoding='utf-8') as f:
    for line in f:
        print(f"  → {line.strip()}")

# 7. 读写模式 ('r+' 模式)
print("\n【7. 读写模式 - 'r+' 模式】")
with open(test_file, 'r+', encoding='utf-8') as f:
    content = f.read()
    print(f"当前内容:\n{content}")
    f.write("第六行：使用 r+ 模式添加\n")
print("✓ r+ 模式操作完成")

# 8. 文件指针操作
print("\n【8. 文件指针操作 - seek() 和 tell()】")
with open(test_file, 'r', encoding='utf-8') as f:
    print(f"初始位置: {f.tell()}")
    f.seek(0)
    first_char = f.read(1)
    print(f"第一个字符: '{first_char}'")
    print(f"当前位置: {f.tell()}")
    f.seek(10)
    print(f"跳转到位置10后读取: '{f.read(5)}'")

# 9. 写入多行
print("\n【9. 写入多行 - writelines()】")
lines_to_write = [
    "第七行：writelines方法\n",
    "第八行：批量写入\n",
    "第九行：最后一行\n"
]
with open(test_file, 'a', encoding='utf-8') as f:
    f.writelines(lines_to_write)
print("✓ 多行写入完成")

# 10. 最终读取展示
print("\n【10. 最终文件内容】")
with open(test_file, 'r', encoding='utf-8') as f:
    print(f.read())

print("=" * 50)
print("演示完成！🎉")
print("=" * 50)
