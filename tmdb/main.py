from QuickProject.Commander import Commander
from . import *

app = Commander(name)


api_url = "https://api.themoviedb.org/3"
img_url = "https://image.tmdb.org/t/p/original"

# 影片类型对应icon

class_to_icon = {
    "爱情": "❤️",
    "动作": "🔫",
    "喜剧": "😂",
    "科幻": "👽",
    "动画": "🐱",
    "剧情": "🎭",
    "惊悚": "👻",
    "恐怖": "👹",
    "犯罪": "👮",
    "悬疑": "🕵️",
    "冒险": "🏃",
    "战争": "⚔️",
    "奇幻": "🧙",
    "家庭": "👨‍👩‍👧‍👦",
    "歌舞": "🎤",
    "传记": "📖",
    "历史": "📜",
    "运动": "🏀",
    "西部": "🤠",
    "古装": "👳",
    "武侠": "👊",
    "黑色电影": "🖤",
    "短片": "🎞️",
    "纪录片": "📽️",
    "其他": "🔖",
    "动作冒险": "🔫🏃",
    "Sci-Fi & Fantasy": "👽🧙",
}


@app.custom_complete("type")
def top():
    return [
        {"name": "all", "description": "所有类型", "icon": "🗂"},
        {"name": "movie", "description": "电影", "icon": "🎬"},
        {"name": "tv", "description": "剧集", "icon": "📺"},
        {"name": "person", "description": "人物", "icon": "👤"},
    ]


@app.custom_complete("time")
def top():
    return [
        {"name": "day", "description": "今天", "icon": "📅"},
        {"name": "week", "description": "本周", "icon": "📆"},
    ]


@app.command()
def top(type: str = "all", time: str = "day"):
    """
    获取热门电影

    :param type: 类型
    :param time: 时间
    """
    import requests

    with QproDefaultConsole.status("正在获取数据"):
        res = requests.get(
            f"{api_url}/trending/{type}/{time}",
            params={"api_key": config.select("token"), "language": user_lang},
        )
    if res.status_code != 200:
        QproDefaultConsole.print(error_string, "获取数据失败")
        return
    import json

    res = json.loads(res.text)

    from QuickStart_Rhy.TuiTools.Table import qs_default_table

    table = qs_default_table(
        ["序号", "名称", "类型", "流行指标", "平均评分", "发布日期"],
        "[bold]🔥 TMDB 热门[/]\n",
    )

    for _id, i in enumerate(res["results"]):
        i = {j: str(i[j]) for j in i}
        table.add_row(
            *[
                f"[bold cyan]{_id + 1}[/]",
                i["title"] if i["media_type"] == "movie" else i["name"],
                "电影" if i["media_type"] == "movie" else "剧集",
                "[bold magenta]" + i["popularity"] + "[/]",
                "[bold cyan]" + i["vote_average"] + "[/]",
                "[bold yellow]"
                + (
                    i["release_date"]
                    if i["media_type"] == "movie"
                    else i["first_air_date"]
                )
                + "[/]",
            ]
        )

    from . import _ask

    while True:
        QproDefaultConsole.print(table, justify="center")

        _id = _ask(
            {
                "type": "input",
                "message": "输入序号查看详情 (q 退出):",
                "validate": lambda x: x == "q"
                or (x.isdigit() and 0 < int(x) <= len(res["results"])),
            }
        )

        if _id == "q":
            break
        _id = int(_id) - 1

        QproDefaultConsole.clear()

        app.real_call(
            "info",
            res["results"][_id]["media_type"],
            res["results"][_id]["id"],
        )

        QproDefaultConsole.clear()


@app.custom_complete("type")
def info():
    return [
        {"name": "movie", "description": "电影", "icon": "🎬"},
        {"name": "tv", "description": "剧集", "icon": "📺"},
    ]


@app.command()
def info(type: str = "movie", id: int = 0):
    """
    获取电影信息

    :param type: 类型
    :param id: ID
    """
    import requests

    with QproDefaultConsole.status("正在获取数据"):
        res = requests.get(
            f"{api_url}/{type}/{id}",
            params={"api_key": config.select("token"), "language": user_lang},
        )
    if res.status_code != 200:
        QproDefaultConsole.print(error_string, "获取数据失败")
        return
    import json

    res = json.loads(res.text)

    from QuickStart_Rhy.ImageTools.ImagePreview import image_preview
    from QuickStart_Rhy.TuiTools.Table import qs_default_table
    from QuickStart_Rhy import table_cell

    with QproDefaultConsole.status("正在获取并展示图片") as st:
        image_preview(f"{img_url}{res['backdrop_path']}", qs_console_status=st)

    table = qs_default_table(
        ["字段", {"header": "值", "justify": "left"}],
        without_headers=True,
    )

    QproDefaultConsole.print(
        f"[bold]📽 {res['title'] if type == 'movie' else res['name']}[/]",
        justify="center",
    )

    if res["tagline"]:
        QproDefaultConsole.print(
            f"[underline dim]{res['tagline']}[/]", justify="center"
        )

    QproDefaultConsole.print()

    table.add_row(
        "🏠 影片简介",
        table_cell(res["overview"], QproDefaultConsole.width - 20),
    )

    if type == "movie":
        table.add_row(
            "🏷 ️ 影片类型",
            ", ".join(
                [
                    "[underline]"
                    + (
                        class_to_icon[i["name"]] + " "
                        if i["name"] in class_to_icon
                        else ""
                    )
                    + i["name"]
                    + "[/]"
                    for i in res["genres"]
                ]
            ),
        )
        table.add_row("🔥 ️流行指标", f"[bold magenta]{res['popularity']}[/]")
        table.add_row(
            "👍 ️平均评分",
            f"[bold cyan]{res['vote_average']}[/] | [bold cyan]{res['vote_count']}[/] 人评分",
        )
        table.add_row("📅 上映日期", f"[bold yellow]{res['release_date']}[/]")
        table.add_row(
            "🎬 影片时长",
            f"[bold cyan]{res['runtime'] // 60}[/] 小时 [bold cyan]{res['runtime'] % 60}[/] 分钟",
        )
    else:
        table.add_row(
            "🏷 ️ 剧集类型",
            ", ".join(
                [
                    "[underline]"
                    + (
                        class_to_icon[i["name"]] + " "
                        if i["name"] in class_to_icon
                        else ""
                    )
                    + i["name"]
                    + "[/]"
                    for i in res["genres"]
                ]
            ),
        )
        table.add_row("🔥 ️流行指标", f"[bold magenta]{res['popularity']}[/]")
        table.add_row(
            "👍 ️平均评分",
            f"[bold cyan]{res['vote_average']}[/] | [bold cyan]{res['vote_count']}[/] 人评分",
        )
        table.add_row("📅 上映日期", f"[bold yellow]{res['first_air_date']}[/]")
        if res["seasons"]:
            table.add_row(
                "🗒️  剧集季数",
                "\n".join(
                    [
                        f"【{i['air_date']}】{i['name']}: {i['overview']}"
                        for i in res["seasons"]
                    ]
                ),
            )
    QproDefaultConsole.print(table, justify="center")

    from . import _ask

    # 查看剧照

    if _ask(
        {
            "type": "confirm",
            "message": "查看剧照?",
            "default": True,
        }
    ):
        with QproDefaultConsole.status("正在获取数据"):
            res = requests.get(
                f"{api_url}/{type}/{id}/images",
                params={"api_key": config.select("token")},
            )
        if res.status_code != 200:
            QproDefaultConsole.print(error_string, "获取数据失败")
            return
        import json

        res = json.loads(res.text)

        from QuickStart_Rhy.NetTools.MultiSingleDL import multi_single_dl_content_ls

        image_preview(
            imgsConcat(
                multi_single_dl_content_ls(
                    [f"{img_url}{i['file_path']}" for i in res["backdrops"][:12]]
                )
            )
        )

    # 前往官网查看

    if _ask(
        {
            "type": "confirm",
            "message": "前往官网查看?",
            "default": False,
        }
    ):
        from QuickStart_Rhy import open_url

        open_url([f"https://www.themoviedb.org/{type}/{id}"])


@app.command()
def search():
    """
    搜索电影或剧集
    """
    from . import _ask

    keywords = _ask(
        {
            "type": "input",
            "message": "请输入关键词",
        }
    )

    if not keywords:
        return

    import requests

    with QproDefaultConsole.status("正在获取数据"):
        res = requests.get(
            f"{api_url}/search/multi",
            params={
                "api_key": config.select("token"),
                "query": keywords,
                "language": user_lang,
            },
        )

    if res.status_code != 200:
        QproDefaultConsole.print(error_string, "获取数据失败")
        return

    import json

    res = json.loads(res.text)

    if not res["results"]:
        QproDefaultConsole.print(warning_string, "未找到相关内容")
        return

    from QuickStart_Rhy.TuiTools.Table import qs_default_table
    from QuickStart_Rhy.ImageTools.ImagePreview import image_preview

    table = qs_default_table(
        ["序号", "类型", "标题", "评分", "日期"],
        "🔍 搜索结果\n",
    )

    actors = []
    items = []
    index = 1

    # QproDefaultConsole.print(res["results"])

    for item in res["results"]:
        item = {
            i: item[i]
            if isinstance(item[i], list) or isinstance(item[i], dict)
            else str(item[i])
            for i in item
            if item[i]
        }
        if item["media_type"] in ["movie", "tv"]:
            table.add_row(
                f"[bold cyan]{index}[/]",
                "电影" if item["media_type"] == "movie" else "剧集",
                item["title"] if item["media_type"] == "movie" else item["name"],
                f"[bold cyan]{item['vote_average']}[/] | [bold cyan]{item['vote_count']}[/]"
                if "vote_average" in item
                else "",
                "[bold yellow]"
                + (
                    item["release_date"]
                    if item["media_type"] == "movie" and "release_date" in item
                    else item["first_air_date"]
                    if "first_air_date" in item
                    else ""
                )
                + "[/]",
            )
            items.append(item)
            if "poster_path" in item:
                actors.append(f"{img_url}{item['poster_path']}")
            index += 1
        else:  # 人物
            actors.append(f"{img_url}{item['profile_path']}")
            for _item in item["known_for"]:
                _item = {
                    i: _item[i]
                    if isinstance(_item[i], list) or isinstance(_item[i], dict)
                    else str(_item[i])
                    for i in _item
                    if _item[i]
                }
                table.add_row(
                    f"[bold cyan]{index}[/]",
                    "电影" if _item["media_type"] == "movie" else "剧集",
                    _item["title"] if _item["media_type"] == "movie" else _item["name"],
                    f"[bold cyan]{_item['vote_average']}[/] | [bold cyan]{_item['vote_count']}[/]"
                    if "vote_average" in _item
                    else "",
                    "[bold yellow]"
                    + (
                        _item["release_date"]
                        if _item["media_type"] == "movie" and "release_date" in _item
                        else _item["first_air_date"]
                        if "first_air_date" in _item
                        else ""
                    )
                    + "[/]",
                )
                items.append(_item)
                if "poster_path" in _item:
                    actors.append(f"{img_url}{_item['poster_path']}")
                index += 1

    if actors:
        from QuickStart_Rhy.NetTools.MultiSingleDL import multi_single_dl_content_ls

        img = imgsConcat(multi_single_dl_content_ls(actors))

    while True:
        if actors:
            image_preview(img)
        QproDefaultConsole.print(table, justify="center")

        _id = _ask(
            {
                "type": "input",
                "message": "请输入ID (q退出)",
                "validate": lambda val: val.isdigit()
                and 0 < int(val) < index
                or val == "q",
            }
        )

        if _id == "q":
            break

        _id = int(_id) - 1

        QproDefaultConsole.clear()
        app.real_call(
            "info", res["results"][_id]["media_type"], res["results"][_id]["id"]
        )
        QproDefaultConsole.clear()


def main():
    """
    注册为全局命令时, 默认采用main函数作为命令入口, 请勿将此函数用作它途.
    When registering as a global command, default to main function as the command entry, do not use it as another way.
    """
    app()


if __name__ == "__main__":
    main()
