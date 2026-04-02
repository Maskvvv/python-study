import os
import shutil

print("=" * 50)
print("Python os 模块 - 文件和目录操作演示")
print("=" * 50)

# 1. 获取当前工作目录
print("\n【1. 获取当前工作目录】")
print(f"当前目录: {os.getcwd()}")

# 2. 列出目录内容
print("\n【2. 列出目录内容 - os.listdir()】")
files = os.listdir('.')
print(f"当前目录下的文件和文件夹: {files[:5]}...")  # 只显示前5个

# 3. 创建目录
print("\n【3. 创建目录】")
test_dir = 'test_os_demo'
if not os.path.exists(test_dir):
    os.mkdir(test_dir)
    print(f"✓ 创建目录: {test_dir}")
else:
    print(f"目录已存在: {test_dir}")

# 创建多级目录
nested_dir = 'test_os_demo/sub1/sub2'
os.makedirs(nested_dir, exist_ok=True)
print(f"✓ 创建多级目录: {nested_dir}")

# 4. 创建文件
print("\n【4. 创建文件】")
file_path = os.path.join(test_dir, 'demo.txt')
with open(file_path, 'w', encoding='utf-8') as f:
    f.write("这是一个演示文件\nHello OS Module!")
print(f"✓ 创建文件: {file_path}")

# 5. 检查路径是否存在
print("\n【5. 检查路径是否存在 - os.path.exists()】")
print(f"文件存在: {file_path} -> {os.path.exists(file_path)}")
print(f"目录存在: {test_dir} -> {os.path.exists(test_dir)}")
print(f"不存在的路径: 'xxx' -> {os.path.exists('xxx')}")

# 6. 判断是文件还是目录
print("\n【6. 判断文件/目录类型】")
print(f"是文件: {file_path} -> {os.path.isfile(file_path)}")
print(f"是目录: {test_dir} -> {os.path.isdir(test_dir)}")

# 7. 获取路径信息
print("\n【7. 获取路径信息 - os.path】")
abs_path = os.path.abspath(file_path)
print(f"绝对路径: {abs_path}")
print(f"文件名: {os.path.basename(file_path)}")
print(f"目录名: {os.path.dirname(file_path)}")
print(f"文件大小: {os.path.getsize(file_path)} 字节")

# 分割路径
print("\n【8. 分割路径】")
path_parts = os.path.split(file_path)
print(f"分割路径: {path_parts}")
ext_split = os.path.splitext('demo.txt')
print(f"分割扩展名: {ext_split}")

# 9. 重命名文件
print("\n【9. 重命名文件】")
new_file_path = os.path.join(test_dir, 'renamed.txt')
os.rename(file_path, new_file_path)
print(f"✓ 重命名: {file_path} -> {new_file_path}")

# 10. 遍历目录树
print("\n【10. 遍历目录树 - os.walk()】")
for root, dirs, files in os.walk(test_dir):
    print(f"根目录: {root}")
    print(f"  子目录: {dirs}")
    print(f"  文件: {files}")

# 11. 获取环境变量
print("\n【11. 获取环境变量】")
print(f"用户目录: {os.environ.get('USERPROFILE', '未找到')}")
print(f"系统路径: {os.environ.get('PATH', '')[:50]}...")

# 12. 路径拼接（推荐方式）
print("\n【12. 路径拼接 - os.path.join()】")
joined_path = os.path.join('folder', 'subfolder', 'file.txt')
print(f"拼接结果: {joined_path}")

# 13. 清理：删除文件和目录
print("\n【13. 删除文件和目录】")

# 删除文件
if os.path.exists(new_file_path):
    os.remove(new_file_path)
    print(f"✓ 删除文件: {new_file_path}")

# 删除空目录
empty_dir = os.path.join(test_dir, 'sub1', 'sub2')
if os.path.exists(empty_dir):
    os.rmdir(empty_dir)
    print(f"✓ 删除空目录: {empty_dir}")

# 删除整个目录树
print("\n【14. 删除整个目录树 - shutil.rmtree()】")
shutil.rmtree(test_dir)
print(f"✓ 删除目录树: {test_dir}")

print("\n" + "=" * 50)
print("演示完成！🎉")
print("=" * 50)
