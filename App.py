import streamlit as st
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import os

# ページ設定
st.set_page_config(page_title="簡易Epubリーダー", layout="wide")

def get_chapter_content(item):
    """チャプターのHTMLコンテンツを抽出して整形する"""
    soup = BeautifulSoup(item.get_content(), 'html.parser')
    return str(soup)

def main():
    st.title("📖 Python Epub Reader")
    st.markdown("GitHub Codespaces上で動作する簡易リーダーです。")

    # サイドバー: ファイルアップロード
    st.sidebar.header("メニュー")
    uploaded_file = st.sidebar.file_uploader("Epubファイルをアップロード", type=["epub"])

    if uploaded_file is not None:
        # Streamlitはメモリアップロードなので、一時ファイルとして保存する必要がある
        with open("temp.epub", "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        try:
            # Epubファイルの読み込み
            book = epub.read_epub("temp.epub")
            
            # 本のタイトル取得
            title = book.get_metadata('DC', 'title')[0][0]
            st.sidebar.success(f"読み込み完了: {title}")

            # 目次（ドキュメントアイテム）の抽出
            # 画像やCSSを除き、文章が入っているHTMLファイルだけを集めます
            items = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
            
            # 章の選択肢を作成
            # 名前が取れない場合もあるため、ファイル名(id)などをラベルにします
            chapter_map = {f"Chapter {i+1} ({item.get_name()})": item for i, item in enumerate(items)}
            
            # サイドバーで章を選択
            selected_chapter_name = st.sidebar.selectbox(
                "章を選択してください",
                options=list(chapter_map.keys())
            )

            # 選択された章の表示
            if selected_chapter_name:
                selected_item = chapter_map[selected_chapter_name]
                content = get_chapter_content(selected_item)
                
                # コンテンツ表示エリア
                st.markdown("---")
                # HTMLをそのままレンダリング許可設定で表示
                st.markdown(content, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"読み込みエラー: {e}")
            st.info("DRM（著作権保護）がかかっているファイルは開けません。")
            
    else:
        st.info("👈 左側のサイドバーから `.epub` ファイルをアップロードしてください。")

if __name__ == "__main__":
    main()
