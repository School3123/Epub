import streamlit as st
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import os

# ページ設定
st.set_page_config(layout="wide", page_title="Simple EPUB Reader")

def chapter_to_str(chapter):
    """HTMLコンテンツからテキストを抽出して整形する"""
    soup = BeautifulSoup(chapter.get_body_content(), 'html.parser')
    text = [para.get_text() for para in soup.find_all('p')]
    return '\n\n'.join(text)

def get_chapters(book):
    """EPUBからドキュメント（章）のみを抽出する"""
    chapters = []
    # get_items()で本の中身を走査
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            chapters.append(item)
    return chapters

st.title("📖 Python EPUB Reader")

# ファイルアップロード
uploaded_file = st.file_uploader("EPUBファイルをアップロードしてください", type=["epub"])

if uploaded_file is not None:
    # EbookLibはファイルパスを要求するため、一時ファイルとして保存
    with open("temp.epub", "wb") as f:
        f.write(uploaded_file.getbuffer())

    try:
        # 本を読み込む
        book = epub.read_epub("temp.epub")
        
        # タイトルの表示
        title = book.get_metadata('DC', 'title')[0][0]
        st.sidebar.header(f"Title: {title}")

        # 章の抽出
        chapters = get_chapters(book)
        
        # サイドバーに章リストを表示（便宜上、ファイル名やIDを使用）
        # ※実際のEPUBは目次構造(toc)が複雑なため、ここでは単純化して全ドキュメントをリスト化します
        chapter_names = [f"Chapter {i+1} (ID: {ch.get_id()})" for i, ch in enumerate(chapters)]
        selected_chapter_name = st.sidebar.radio("目次", chapter_names)

        # 選択された章のインデックスを取得
        selected_index = chapter_names.index(selected_chapter_name)
        selected_chapter = chapters[selected_index]

        # 本文の表示
        st.divider()
        st.subheader("本文")
        
        # HTMLをそのまま表示したい場合は unsafe_allow_html=True を使いますが、
        # セキュリティと読みやすさのためテキスト抽出版を表示します。
        content = chapter_to_str(selected_chapter)
        
        # コンテンツが空の場合の対策
        if not content.strip():
            # テキスト抽出に失敗した場合（pタグがない場合など）、Raw HTMLを表示するオプション
            st.warning("テキスト抽出がうまくいきませんでした。HTMLとして表示を試みます。")
            st.markdown(selected_chapter.get_body_content().decode('utf-8'), unsafe_allow_html=True)
        else:
            st.markdown(content)

    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
        
    finally:
        # 後始末：一時ファイルの削除
        if os.path.exists("temp.epub"):
            os.remove("temp.epub")

else:
    st.info("左上の 'Browse files' から .epub ファイルをアップロードしてください。")
