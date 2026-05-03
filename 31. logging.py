# ============================================================
# Python logging 模块学习指南
# ============================================================

# ------------------------------------------------------------
# 1. 什么是 logging？
# ------------------------------------------------------------
# logging 是 Python 标准库中用于记录日志的模块。
# 相比直接 print()，logging 有以下优势：
#   - 支持不同级别（DEBUG / INFO / WARNING / ERROR / CRITICAL）
#   - 可以同时输出到多个目标（控制台、文件、网络等）
#   - 可以灵活控制输出格式
#   - 生产环境中 print 需要手动删除，而 logging 只需调整级别即可
#   - 线程安全，多线程环境下可以放心使用

print("=" * 50)
print("Python logging 模块演示")
print("=" * 50)

# ------------------------------------------------------------
# 2. 最简单的用法：basicConfig
# ------------------------------------------------------------
# logging.basicConfig() 是最快速的配置方式
# 默认级别是 WARNING，所以 DEBUG 和 INFO 不会显示

print("\n【2. basicConfig 基础配置】")

import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logging.debug("这是 DEBUG 级别 -- 调试信息，最详细")
logging.info("这是 INFO 级别 -- 一般信息")
logging.warning("这是 WARNING 级别 -- 警告信息")
logging.error("这是 ERROR 级别 -- 错误信息")
logging.critical("这是 CRITICAL 级别 -- 严重错误")

print("[OK] basicConfig 演示完成")

# ------------------------------------------------------------
# 3. 五个日志级别详解
# ------------------------------------------------------------
# 级别从低到高：DEBUG(10) < INFO(20) < WARNING(30) < ERROR(40) < CRITICAL(50)
# 设置某个级别后，只有 >= 该级别的日志才会被输出
# 开发环境通常用 DEBUG，生产环境通常用 INFO 或 WARNING

print("\n【3. 日志级别详解】")

print(f"  DEBUG    = {logging.DEBUG}   (详细调试信息)")
print(f"  INFO     = {logging.INFO}   (确认程序按预期运行)")
print(f"  WARNING  = {logging.WARNING}   (意外情况，但程序仍能运行)")
print(f"  ERROR    = {logging.ERROR}   (严重问题，部分功能无法执行)")
print(f"  CRITICAL = {logging.CRITICAL}   (程序可能无法继续运行)")

for level_name, level_num in [("DEBUG", 10), ("INFO", 20), ("WARNING", 30), ("ERROR", 40), ("CRITICAL", 50)]:
    print(f"  {level_name:10s} 数值 = {level_num}")

print("[OK] 日志级别详解完成")

# ------------------------------------------------------------
# 4. 输出到文件
# ------------------------------------------------------------
# 通过 filename 参数将日志写入文件，而不是控制台
# filemode='w' 表示每次覆盖，'a' 表示追加（默认）

print("\n【4. 输出到文件】")

import os

log_file = os.path.join(os.path.dirname(__file__), "_logging_test.log")

file_logger = logging.getLogger("file_demo")
file_logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))

file_logger.addHandler(file_handler)

file_logger.info("这条日志写入了文件")
file_logger.warning("警告信息也写入了文件")
file_logger.debug("调试信息同样写入了文件")

with open(log_file, "r", encoding="utf-8") as f:
    print("  文件中的日志内容：")
    for line in f:
        print(f"    {line.rstrip()}")

file_handler.close()
file_logger.removeHandler(file_handler)

if os.path.exists(log_file):
    os.remove(log_file)

print("[OK] 文件输出演示完成")

# ------------------------------------------------------------
# 5. 同时输出到控制台和文件
# ------------------------------------------------------------
# 一个 Logger 可以添加多个 Handler，实现多目标输出
# 常见做法：控制台输出 INFO 及以上，文件记录 DEBUG 及以上

print("\n【5. 同时输出到控制台和文件】")

dual_logger = logging.getLogger("dual_demo")
dual_logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))

log_file2 = os.path.join(os.path.dirname(__file__), "_logging_dual.log")
file_handler2 = logging.FileHandler(log_file2, mode="w", encoding="utf-8")
file_handler2.setLevel(logging.DEBUG)
file_handler2.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))

dual_logger.addHandler(console_handler)
dual_logger.addHandler(file_handler2)

dual_logger.debug("DEBUG 信息 -- 只写入文件，控制台不显示")
dual_logger.info("INFO 信息 -- 控制台和文件都有")
dual_logger.warning("WARNING 信息 -- 控制台和文件都有")

with open(log_file2, "r", encoding="utf-8") as f:
    print("  文件中记录的日志（包含 DEBUG）：")
    for line in f:
        print(f"    {line.rstrip()}")

file_handler2.close()
dual_logger.removeHandler(file_handler2)

if os.path.exists(log_file2):
    os.remove(log_file2)

print("[OK] 双输出演示完成")

# ------------------------------------------------------------
# 6. 格式化字符串（Formatter）
# ------------------------------------------------------------
# Formatter 支持丰富的占位符，常用的有：
#   %(asctime)s   -- 时间戳
#   %(name)s      -- Logger 名称
#   %(levelname)s -- 级别名称
#   %(message)s   -- 日志消息
#   %(filename)s  -- 文件名
#   %(lineno)d    -- 行号
#   %(funcName)s  -- 函数名
#   %(module)s    -- 模块名
#   %(process)d   -- 进程 ID
#   %(thread)d    -- 线程 ID

print("\n【6. 格式化字符串详解】")

format_logger = logging.getLogger("format_demo")
format_logger.setLevel(logging.DEBUG)

format_handler = logging.StreamHandler()
format_handler.setLevel(logging.DEBUG)
format_handler.setFormatter(
    logging.Formatter(
        "[%(asctime)s] %(name)s/%(levelname)s "
        "(%(filename)s:%(lineno)d %(funcName)s) - %(message)s"
    )
)
format_logger.handlers.clear()
format_logger.addHandler(format_handler)

def demo_function():
    format_logger.info("这条日志包含了文件名、行号和函数名")

demo_function()

print("[OK] 格式化字符串演示完成")

# ------------------------------------------------------------
# 7. 使用 Logger 对象（最佳实践）
# ------------------------------------------------------------
# 最佳实践：每个模块用自己的 logger = logging.getLogger(__name__)
# __name__ 会自动变成模块的完整路径，方便追踪日志来源
# 避免直接使用 logging.info() 这种根 logger 的方式

print("\n【7. Logger 对象最佳实践】")

logger1 = logging.getLogger("myapp.database")
logger2 = logging.getLogger("myapp.api")
logger3 = logging.getLogger("myapp.api.auth")

app_handler = logging.StreamHandler()
app_handler.setLevel(logging.DEBUG)
app_handler.setFormatter(logging.Formatter("%(name)s - %(levelname)s - %(message)s"))

root = logging.getLogger("myapp")
root.setLevel(logging.DEBUG)
root.handlers.clear()
root.addHandler(app_handler)

logger1.info("数据库连接成功")
logger2.info("API 请求处理中")
logger3.warning("认证令牌即将过期")

print("[OK] Logger 层级演示完成")

# ------------------------------------------------------------
# 8. Logger 的层级关系
# ------------------------------------------------------------
# Logger 是树形结构，子 Logger 的日志会向上传播给父 Logger
# 根 Logger 是 logging.root，名称为空字符串 ""
# "myapp" 是 "myapp.database" 的父 Logger
# 可以通过 propagate=False 阻止日志向上传播

print("\n【8. Logger 层级与传播】")

parent_logger = logging.getLogger("parent")
parent_logger.setLevel(logging.DEBUG)
parent_logger.handlers.clear()
parent_logger.addHandler(app_handler)

child_logger = logging.getLogger("parent.child")

child_logger.info("子 Logger 的日志 -- 会同时被父 Logger 的 Handler 处理")

print(f"  parent.child 的传播设置 propagate = {child_logger.propagate}")

child_logger.propagate = False
child_logger.handlers.clear()
child_logger.addHandler(logging.StreamHandler())
child_logger.handlers[0].setFormatter(logging.Formatter("[子Logger] %(message)s"))

child_logger.info("关闭传播后，只有子 Logger 自己的 Handler 处理")

child_logger.propagate = True

print("[OK] Logger 层级传播演示完成")

# ------------------------------------------------------------
# 9. RotatingFileHandler -- 日志轮转
# ------------------------------------------------------------
# 当日志文件太大时，自动分割成多个文件
# RotatingFileHandler：按文件大小轮转
#   maxBytes -- 单个文件最大字节数
#   backupCount -- 保留的备份文件数量

print("\n【9. RotatingFileHandler 日志轮转】")

from logging.handlers import RotatingFileHandler

rotating_file = os.path.join(os.path.dirname(__file__), "_logging_rotate.log")

rotating_logger = logging.getLogger("rotating_demo")
rotating_logger.setLevel(logging.DEBUG)
rotating_logger.handlers.clear()

rotating_handler = RotatingFileHandler(
    rotating_file,
    maxBytes=200,
    backupCount=3,
    encoding="utf-8",
)
rotating_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
rotating_logger.addHandler(rotating_handler)

for i in range(20):
    rotating_logger.info(f"这是第 {i+1} 条日志，用于测试日志轮转功能")

print(f"  日志文件已生成，超过 200 字节会自动轮转")
print(f"  备份文件: _logging_rotate.log.1, .2, .3")

rotating_handler.close()
rotating_logger.removeHandler(rotating_handler)

for suffix in ["", ".1", ".2", ".3"]:
    path = rotating_file + suffix if suffix else rotating_file
    if os.path.exists(path):
        size = os.path.getsize(path)
        print(f"    {os.path.basename(path)}: {size} 字节")
        os.remove(path)

print("[OK] RotatingFileHandler 演示完成")

# ------------------------------------------------------------
# 10. TimedRotatingFileHandler -- 按时间轮转
# ------------------------------------------------------------
# 按时间间隔自动分割日志文件
# when 参数：'S'秒 / 'M'分 / 'H'时 / 'D'天 / 'midnight'每天午夜

print("\n【10. TimedRotatingFileHandler 按时间轮转】")

from logging.handlers import TimedRotatingFileHandler

print("  TimedRotatingFileHandler 参数说明：")
print("    when='S'       -- 每秒轮转")
print("    when='M'       -- 每分钟轮转")
print("    when='H'       -- 每小时轮转")
print("    when='D'       -- 每天轮转")
print("    when='midnight'-- 每天午夜轮转")
print("    when='W0'-'W6' -- 每周一到周日轮转")
print()
print("  示例代码：")
print("    handler = TimedRotatingFileHandler(")
print("        'app.log', when='midnight', backupCount=7")
print("    )")
print("    # 每天午夜轮转，保留 7 天的日志")

print("[OK] TimedRotatingFileHandler 说明完成")

# ------------------------------------------------------------
# 11. 异常日志记录
# ------------------------------------------------------------
# logger.exception() 会自动附带完整的堆栈跟踪信息
# 等同于 logger.error(..., exc_info=True)
# 在 except 块中使用最方便

print("\n【11. 异常日志记录】")

exc_logger = logging.getLogger("exc_demo")
exc_logger.setLevel(logging.DEBUG)
exc_logger.handlers.clear()
exc_logger.addHandler(app_handler)

try:
    result = 1 / 0
except ZeroDivisionError:
    exc_logger.exception("捕获到除零异常")

print("[OK] 异常日志记录演示完成")

# ------------------------------------------------------------
# 12. 使用 dictConfig 进行高级配置
# ------------------------------------------------------------
# logging.config.dictConfig() 允许用字典/JSON/YAML 配置日志
# 这是大型项目推荐的方式，配置与代码分离

print("\n【12. dictConfig 高级配置】")

import logging.config

config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "%(levelname)s - %(message)s",
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "simple",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "myapp": {
            "level": "DEBUG",
            "handlers": ["console"],
            "propagate": False,
        },
    },
}

logging.config.dictConfig(config)

dict_logger = logging.getLogger("myapp")
dict_logger.info("通过 dictConfig 配置的 Logger")
dict_logger.debug("DEBUG 信息 -- 不会在控制台显示（Handler 级别为 INFO）")

print("[OK] dictConfig 演示完成")

# ------------------------------------------------------------
# 13. 自定义 Handler
# ------------------------------------------------------------
# 继承 logging.Handler，重写 emit() 方法即可

print("\n【13. 自定义 Handler】")


class ColorHandler(logging.Handler):
    """在控制台输出带颜色的日志"""

    COLORS = {
        logging.DEBUG: "\033[36m",
        logging.INFO: "\033[32m",
        logging.WARNING: "\033[33m",
        logging.ERROR: "\033[31m",
        logging.CRITICAL: "\033[35m",
    }
    RESET = "\033[0m"

    def emit(self, record):
        color = self.COLORS.get(record.levelno, self.RESET)
        msg = self.format(record)
        print(f"{color}{msg}{self.RESET}")


color_logger = logging.getLogger("color_demo")
color_logger.setLevel(logging.DEBUG)
color_logger.handlers.clear()

color_handler = ColorHandler()
color_handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
color_logger.addHandler(color_handler)

color_logger.debug("DEBUG -- 青色")
color_logger.info("INFO -- 绿色")
color_logger.warning("WARNING -- 黄色")
color_logger.error("ERROR -- 红色")
color_logger.critical("CRITICAL -- 紫色")

print("[OK] 自定义 Handler 演示完成")

# ------------------------------------------------------------
# 14. 自定义 Filter
# ------------------------------------------------------------
# Filter 可以更精细地控制哪些日志被输出
# 比如只输出特定模块的日志，或者根据消息内容过滤

print("\n【14. 自定义 Filter】")


class KeywordFilter(logging.Filter):
    """只允许包含指定关键词的日志通过"""

    def __init__(self, keyword):
        super().__init__()
        self.keyword = keyword

    def filter(self, record):
        return self.keyword in record.getMessage()


filter_logger = logging.getLogger("filter_demo")
filter_logger.setLevel(logging.DEBUG)
filter_logger.handlers.clear()

filter_handler = logging.StreamHandler()
filter_handler.setLevel(logging.DEBUG)
filter_handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
filter_handler.addFilter(KeywordFilter("重要"))

filter_logger.addHandler(filter_handler)

filter_logger.info("这是一条普通信息")
filter_logger.info("这是一条【重要】信息")
filter_logger.warning("重要警告！请注意！")
filter_logger.error("普通错误信息")

print("[OK] 自定义 Filter 演示完成")

# ------------------------------------------------------------
# 15. 日志性能优化：延迟格式化
# ------------------------------------------------------------
# 不要用 f-string 或 % 格式化再传给 logging
# 应该用 %s 占位符，让 logging 在需要时才格式化
# 这样当日志级别不满足时，就不会执行格式化操作

print("\n【15. 日志性能优化】")

perf_logger = logging.getLogger("perf_demo")
perf_logger.handlers.clear()
perf_logger.addHandler(app_handler)
perf_logger.setLevel(logging.WARNING)

expensive_data = {"key": "value", "list": list(range(1000))}

perf_logger.debug("不推荐: " + str(expensive_data))
perf_logger.debug("推荐: %s", expensive_data)

print("  当级别为 WARNING 时，DEBUG 不会输出")
print("  但第一种写法 str() 已经执行了，浪费性能")
print("  第二种写法 %s 只在实际输出时才格式化")

print("[OK] 性能优化说明完成")

# ------------------------------------------------------------
# 16. 实战：为项目配置完整的日志系统
# ------------------------------------------------------------

print("\n【16. 实战：完整日志系统配置】")


def setup_logging(log_dir=None, console_level=logging.INFO, file_level=logging.DEBUG):
    """为项目配置完整的日志系统"""
    if log_dir is None:
        log_dir = os.path.dirname(__file__)

    log_path = os.path.join(log_dir, "_logging_app.log")

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.handlers.clear()

    console = logging.StreamHandler()
    console.setLevel(console_level)
    console.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%H:%M:%S")
    )

    file_h = RotatingFileHandler(
        log_path, maxBytes=10_000, backupCount=5, encoding="utf-8"
    )
    file_h.setLevel(file_level)
    file_h.setFormatter(
        logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s"
        )
    )

    root_logger.addHandler(console)
    root_logger.addHandler(file_h)

    return root_logger


setup_logging()

app_logger = logging.getLogger("myapp")
db_logger = logging.getLogger("myapp.database")
api_logger = logging.getLogger("myapp.api")

app_logger.info("应用启动")
db_logger.info("数据库连接成功")
api_logger.info("API 服务就绪")
db_logger.warning("查询耗时较长: 2.5s")
api_logger.error("请求超时: /api/users")

log_path = os.path.join(os.path.dirname(__file__), "_logging_app.log")
root = logging.getLogger()
for h in root.handlers[:]:
    h.close()
    root.removeHandler(h)

if os.path.exists(log_path):
    with open(log_path, "r", encoding="utf-8") as f:
        print("\n  日志文件内容：")
        for line in f:
            print(f"    {line.rstrip()}")
    os.remove(log_path)

print("[OK] 完整日志系统演示完成")

# ------------------------------------------------------------
# 总结
# ------------------------------------------------------------
print("\n" + "=" * 50)
print("logging 模块总结")
print("=" * 50)
print("""
  1. 五个级别：DEBUG < INFO < WARNING < ERROR < CRITICAL
  2. 核心组件：
     - Logger     -> 记录器，发出日志消息
     - Handler    -> 处理器，决定日志输出到哪里
     - Formatter  -> 格式器，决定日志的样式
     - Filter     -> 过滤器，精细控制哪些日志通过
  3. 最佳实践：
     - 用 logger = logging.getLogger(__name__) 为每个模块创建 Logger
     - 避免直接用 logging.info()（会使用根 Logger）
     - 用 %s 占位符而非 f-string 传参，提升性能
     - 生产环境用 dictConfig 或 fileConfig 管理配置
     - 用 RotatingFileHandler / TimedRotatingFileHandler 防止日志文件过大
  4. 常用 Handler：
     - StreamHandler          -> 控制台输出
     - FileHandler            -> 文件输出
     - RotatingFileHandler    -> 按大小轮转
     - TimedRotatingFileHandler -> 按时间轮转
  5. 记住：logging 比 print 强大得多，养成用 logging 的好习惯！
""")
