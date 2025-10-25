# {APPNAME}

## 概要
このプロジェクトの説明

## 必要環境
- Python 3.11

## セットアップ
\`\`\`bash
# 仮想環境作成
python3.11 -m venv venv

# 仮想環境有効化
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存パッケージインストール
pip install -r requirements.txt
\`\`\`

## 実行
\`\`\`bash
python main.py
\`\`\`

## ビルド
\`\`\`bash
pyinstaller --onefile --windowed --name "icon_generator" main.py
\`\`\`
