import functools
import socket
import threading

def exception_handler(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (TypeError, ValueError, ZeroDivisionError) as e:
            print(f"类型或值错误: {e} (Func: {func.__name__})")
        except (FileNotFoundError, PermissionError) as e:
            print(f"文件操作错误: {e} (Func: {func.__name__})")
        except socket.error as e:
            print(f"套接字错误: {e} (Func: {func.__name__})")
        except (IndexError, KeyError) as e:
            print(f"数据访问错误: {e} (Func: {func.__name__})")
        except (ImportError, AttributeError) as e:
            print(f"模块或属性错误: {e} (Func: {func.__name__})")
        except MemoryError as e:
            print(f"内存错误: {e} (Func: {func.__name__})")
        except NameError as e:
            print(f"名称错误: {e} (Func: {func.__name__})")
        except RuntimeError as e:
            print(f"运行时错误: {e} (Func: {func.__name__})")
        except (SyntaxError, IndentationError) as e:
            print(f"语法或缩进错误: {e} (Func: {func.__name__})")
        except StopIteration as e:
            print(f"迭代停止错误: {e} (Func: {func.__name__})")
        except SystemExit as e:
            print(f"系统退出: {e} (Func: {func.__name__})")
        except threading.ThreadError as e:
            print(f"多线程错误: {e} (Func: {func.__name__})")
        except TimeoutError as e:
            print(f"超时错误: {e} (Func: {func.__name__})")
        except Exception as e:
            print(f"未知错误: {e} (Func: {func.__name__})")

    return wrapper
