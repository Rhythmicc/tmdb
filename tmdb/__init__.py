# -*- coding: utf-8 -*-

name = "tmdb"

from .__config__ import *

config: tmdbConfig = None
if enable_config:
    config = tmdbConfig()

import sys
from QuickProject import user_pip, _ask, external_exec, QproDefaultStatus


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
            with QproDefaultStatus("Installing..." if user_lang != "zh" else "正在安装..."):
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

    if not imgs:
        QproDefaultConsole.print(error_string, "无样品图")
        return

    with QproDefaultStatus("拼接图片中") as st:
        heights_len = min(len(imgs), 3)

        one_width = int(
            QproDefaultConsole.width * terminal_font_size / heights_len / 2.125
        )

        heights = [0] * heights_len
        for i in imgs:
            one_height = int(one_width * i.size[1] / i.size[0])
            heights[heights.index(min(heights))] += one_height

        st.update("嗅探最佳拼接方式")
        max_height = QproDefaultConsole.height * terminal_font_size

        while max(heights) > max_height and heights_len < len(imgs):
            heights_len += 1
            heights = [0] * heights_len
            one_width = int(
                QproDefaultConsole.width / heights_len * terminal_font_size / 2.125
            )
            for i in imgs:
                one_height = int(one_width * i.size[1] / i.size[0])
                heights[heights.index(min(heights))] += one_height

        result = Image.new("RGBA", (one_width * heights_len, max(heights)))
        heights = [0] * heights_len

        imgs = [
            i.resize((one_width, int(one_width * i.size[1] / i.size[0]))) for i in imgs
        ]
        imgs = sorted(imgs, key=lambda i: -i.size[0] * i.size[1])

        for i in imgs:
            min_height_index = heights.index(min(heights))
            result.paste(i, (one_width * min_height_index, heights[min_height_index]))
            heights[min_height_index] += i.size[1]
    return result
