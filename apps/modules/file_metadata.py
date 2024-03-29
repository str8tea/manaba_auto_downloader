from __future__ import annotations
from dataclasses import dataclass, asdict
import json
from pathlib import Path
import re
from shutil import move
from time import sleep
import traceback

from bs4 import BeautifulSoup
from selenium.webdriver.chrome.webdriver import WebDriver

from settings import MANABA_CLIENT_URL, SAVE_DIR


@dataclass(slots=True)
class FileMetadata:
    """ファイルのメタデータを扱うデータクラス

    ファイルのダウンロード、ファイルのメタデータをJSONファイルに書き込む処理を行う

    Note:
        manabaのコンテンツページの添付ファイルソースから作成されることを想定
    """

    name: str
    link: str
    upload_date: str  # ex) 2000-01-01 00:00:00
    course_name: str  # 不明の場合はUnknown
    content_name: str  # 不明の場合はUnknown
    page_title: str
    description: str  # ファイルの説明がない場合はNothing
    path: str = "Not downloaded"
    can_download: bool = False  # ダウンロードに成功した場合はTrue、それ以外の場合はFalse

    @classmethod
    def from_soup(cls, file_soup: BeautifulSoup, course_name: str = "Unknown", content_name: str = "Unknown", page_title: str = "Unknown") -> FileMetadata:
        """引数のソースから自身のインスタンスを生成する

        Args:
            file_soup (BeautifulSoup): manabaのコンテンツページの添付ファイルソース（BeautifulSoupで解析済みのもの）
            course_name (str, optional): 講義の名前（デフォルト値はUnknown）
            content_name (str, optional): コンテンツの名前（デフォルト値はUnknown）
            page_title (str, optional): ファイルがあるコンテンツページのタイトル（デフォルト値はUnknown）

        Returns:
            FileMetadata: ファイルのメタデータを引数とした自身のインスタンス
        """

        detail = file_soup.find("div", class_="inlineaf-description").find("a")
        file_link = detail["href"]
        file_full_link = MANABA_CLIENT_URL + file_link
        detail_text = detail.get_text("<br>")  # <br>タグが消えないようにする

        # ファイルの説明がある（2行ある）場合は、1行目が説明、2行目がファイルのヘッダー
        if "<br>" in detail_text:
            description, file_header = detail_text.split("<br>")
        else:
            description = "Nothing"
            file_header = detail_text

        # headerの形式は「ファイル名」または「ファイル名 - アップロード日時」なので、アップロード日時の有無を正規表現で確かめる
        header_regex = re.compile(
            r'(.+\.[a-z]+) - (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})')
        m = re.match(header_regex, file_header)
        if m:
            file_name, file_upload_date = m.groups()
        else:
            file_name = file_header
            file_upload_date = "Unknown"

        return cls(file_name, file_full_link, file_upload_date, course_name, content_name, page_title, description)

    def download_by(self, driver: WebDriver) -> None:
        """引数のdriverを用いて、このファイルのリンクからダウンロードを行う

        SAVE_DIR直下に講義名のディレクトリを作成し、そこにダウンロードしたファイルを保存する

        Args:
            driver (WebDriver): ブラウザを操作するドライバー（Selenium）

        Note:
            ファイルのダウンロードに20秒以上かかる場合は、SAVE_DIRに保存されます
        """

        # 講義名のディレクトリを作成する
        course_dir = SAVE_DIR / self.course_name
        course_dir.mkdir(exist_ok=True)

        # ファイルをダウンロードする
        driver.get(self.link)

        # ダウンロードしたファイルを講義名のディレクトリに移動させる
        for _ in range(10):
            # ダウンロードが完了していない可能性があるので、2秒間隔で10回ダウンロードしたファイルの移動を試みる
            sleep(2)

            # ダウンロードする予定のファイルの拡張子をスクレイピングで取得できなかった場合、ファイル名（拡張子なし）で探す
            if len(Path(self.name).suffix) == 0:
                for path in SAVE_DIR.iterdir():
                    if path.is_file and path.stem == self.name:
                        self.name = path.name  # 見つかった場合は、ファイル名を更新する

            src_path = SAVE_DIR / self.name  # ダウンロードしたファイルのパス
            dest_path = course_dir / self.name  # ダウンロードしたファイルの移動先のパス

            # ダウンロードに成功した場合
            if src_path.is_file():
                print(
                    f"Succeeded to download '{self.name}' in {self.page_title} of {self.course_name}")
                self.can_download = True

                # dest_pathへファイルを移動する
                try:
                    move(src_path, dest_path)
                except:
                    print(
                        f"Failed to move '{self.name}' in {self.page_title} of {self.course_name}")
                    print(traceback.format_exc())
                    dest_path = src_path
                else:
                    print(
                        f"Succeeded to move '{self.name}' in {self.page_title} of {self.course_name}")
                finally:
                    break
        # ダウンロードしたはずのファイルが見つからなかった場合
        else:
            print(
                f"Failed to download '{self.name}' in {self.page_title} of {self.course_name}")
            dest_path = "Unknown"

        self.path = str(dest_path)  # パスを更新する

    def to_json(self, json_path: Path) -> None:
        """ファイルのメタデータをJSONファイルに書き込む（追記）

        Args:
            json_path (Path): 書き込み先のJSONファイルパス
        """

        # 辞書型に変換する
        file_dict = asdict(self)

        with open(json_path, "a", encoding="utf-8") as f:
            # JSON形式でファイルに追記する
            json.dump(file_dict, f, ensure_ascii=False)
