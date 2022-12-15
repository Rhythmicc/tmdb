# -*- coding: utf-8 -*-

name = "tmdb"

from .__config__ import *

config: tmdbConfig = None
if enable_config:
    config = tmdbConfig()

import sys
from QuickProject import user_pip, _ask, external_exec


info_string = "ℹ️ [bold cyan]提示[/]"
error_string = "❌ [bold red]错误[/]"
warning_string = "⚠️ [bold yellow]警告[/]"


def requirePackage(
    pname: str,
    module: str = "",
    real_name: str = "",
    not_exit: bool = True,
    not_ask: bool = False,
    set_pip: str = user_pip,
):
    """
    获取本机上的python第三方库，如没有则询问安装

    :param not_ask: 不询问，无依赖项则报错
    :param set_pip: 设置pip路径
    :param pname: 库名
    :param module: 待引入的模块名，可缺省
    :param real_name: 用于 pip3 install 的名字
    :param not_exit: 安装后不退出
    :return: 库或模块的地址
    """
    try:
        exec(f"from {pname} import {module}" if module else f"import {pname}")
    except (ModuleNotFoundError, ImportError):
        if not_ask:
            return None
        if _ask(
            {
                "type": "confirm",
                "name": "install",
                "message": f"""{name} require {pname + (' -> ' + module if module else '')}, confirm to install?
  {name} 依赖 {pname + (' -> ' + module if module else '')}, 是否确认安装?""",
                "default": True,
            }
        ):
            with QproDefaultConsole.status(
                "Installing..." if user_lang != "zh" else "正在安装..."
            ):
                external_exec(
                    f"{set_pip} install {pname if not real_name else real_name} -U",
                    True,
                )
            if not_exit:
                exec(f"from {pname} import {module}" if module else f"import {pname}")
            else:
                QproDefaultConsole.print(
                    QproInfoString,
                    f'just run again: "{" ".join(sys.argv)}"'
                    if user_lang != "zh"
                    else f'请重新运行: "{" ".join(sys.argv)}"',
                )
                exit(0)
        else:
            exit(-1)
    finally:
        return eval(f"{module if module else pname}")


def imgsConcat(imgs: list):
    """
    合并图片
    """

    def is_wide():
        width = QproDefaultConsole.width
        height = QproDefaultConsole.height
        rate = width / height
        return rate > 2

    from io import BytesIO

    terminal_font_size = int(
        requirePackage("QuickStart_Rhy", "qs_config").basicSelect("terminal_font_size")
    )

    Image = requirePackage("PIL", "Image", "Pillow")
    try:
        imgs = [Image.open(BytesIO(i)) for i in imgs if i]
    except:
        QproDefaultConsole.print(error_string, "样品图获取失败!")
        return

    wide = is_wide()
    heights_len = 4 if wide else 3
    with QproDefaultConsole.status("拼接图片中") as st:
        one_width = QproDefaultConsole.width // heights_len * terminal_font_size
        imgs = [
            i.resize((one_width, int(one_width * i.size[1] / i.size[0]))) for i in imgs
        ]
        imgs = sorted(imgs, key=lambda i: -i.size[0] * i.size[1])
        heights = [0] * heights_len
        for i in imgs:
            heights[heights.index(min(heights))] += i.size[1]
        if wide:
            st.update("嗅探最佳拼接方式")
            while max(heights) > one_width * heights_len:
                heights_len += 1
                heights = [0] * heights_len
                one_width = QproDefaultConsole.width // heights_len * terminal_font_size
                for i in imgs:
                    heights[heights.index(min(heights))] += i.size[1]
        result = Image.new("RGBA", (one_width * heights_len, max(heights)))
        heights = [0] * heights_len
        for i in imgs:
            min_height_index = heights.index(min(heights))
            result.paste(i, (one_width * min_height_index, heights[min_height_index]))
            heights[min_height_index] += i.size[1]
    return result
