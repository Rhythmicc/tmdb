from QuickProject.Commander import Commander
from . import *

app = Commander(name)


api_url = "https://api.themoviedb.org/3"
img_url = "https://image.tmdb.org/t/p/original"


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
    """
    import requests

    res = requests.get(
        f"{api_url}/trending/{type}/{time}",
        params={"api_key": config.select("token"), "language": user_lang},
    )
    if res.status_code != 200:
        raise Exception("Error")
    import json

    res = json.loads(res.text)

    from QuickStart_Rhy.TuiTools.Table import qs_default_table
    from QuickStart_Rhy import table_cell

    table = qs_default_table(
        ["序号", "名称", "类型", "流行指标", "平均评分", "发布日期", {"header": "简介", "justify": "left"}],
        "[bold]🔥 TMDB 热门[/]\n",
    )

    for _id, i in enumerate(res["results"]):
        i = {j: str(i[j]) for j in i}
        table.add_row(
            *[
                str(_id + 1),
                i["title"] if i["media_type"] == "movie" else i["name"],
                "电影" if i["media_type"] == "movie" else "剧集",
                "[bold cyan]" + i["popularity"] + "[/]",
                "[bold cyan]" + i["vote_average"] + "[/]",
                "[bold yellow]"
                + (
                    i["release_date"]
                    if i["media_type"] == "movie"
                    else i["first_air_date"]
                )
                + "[/]",
                table_cell(i["overview"], QproDefaultConsole.width // 2),
            ]
        )

    from . import _ask

    while True:
        QproDefaultConsole.print(table, justify="center")

        _id = int(
            _ask(
                {
                    "type": "input",
                    "message": "输入序号查看详情 (输入 0 退出):",
                    "validate": lambda x: x.isdigit()
                    and 0 <= int(x) <= len(res["results"]),
                }
            )
        )

        if _id == 0:
            break

        app.real_call(
            "info",
            res["results"][_id - 1]["media_type"],
            res["results"][_id - 1]["id"],
        )


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
    """
    import requests

    res = requests.get(
        f"{api_url}/{type}/{id}",
        params={"api_key": config.select("token"), "language": user_lang},
    )
    if res.status_code != 200:
        raise Exception("Error")
    import json

    res = json.loads(res.text)

    from QuickStart_Rhy.ImageTools.ImagePreview import image_preview
    from QuickStart_Rhy.TuiTools.Table import qs_default_table

    image_preview(f"{img_url}{res['backdrop_path']}")

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

    QproDefaultConsole.print("\n" + res["overview"], end="\n\n")

    if type == "movie":
        table.add_row(
            "🏷 ️ 影片类型",
            ", ".join(["[underline]" + i["name"] + "[/]" for i in res["genres"]]),
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
            ", ".join(["[underline]" + i["name"] + "[/]" for i in res["genres"]]),
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


def main():
    """
    注册为全局命令时, 默认采用main函数作为命令入口, 请勿将此函数用作它途.
    When registering as a global command, default to main function as the command entry, do not use it as another way.
    """
    app()


if __name__ == "__main__":
    main()
