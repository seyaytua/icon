# v1.3.0 ビルド手順書

## 概要
Windows ZIP展開問題を修正したv1.3.0をビルドしてリリースする手順です。

## ステップ1: ワークフローファイルの修正

GitHubのWebインターフェースで`.github/workflows/build.yml`を直接編集してください。

### 修正方法

1. GitHubリポジトリページにアクセス: https://github.com/seyaytua/icon
2. `.github/workflows/build.yml`ファイルに移動
3. 右上の鉛筆アイコン（Edit this file）をクリック
4. 以下の修正を適用：

**35-37行目を削除:**
```yaml
      - name: Create ZIP archive
        run: |
          powershell Compress-Archive -Path release\* -DestinationPath IconGenerator-Windows.zip
```

**その場所に以下を追加:**
```yaml
      - name: Install 7zip
        run: |
          choco install 7zip -y
          
      - name: Create ZIP archive with 7zip
        run: |
          & "C:\Program Files\7-Zip\7z.exe" a -tzip IconGenerator-Windows.zip .\release\*
```

5. "Commit changes..."をクリック
6. コミットメッセージ: `fix(workflow): Use 7zip for better ZIP compatibility`
7. "Commit directly to the main branch"を選択
8. "Commit changes"をクリック

## ステップ2: タグの作成とプッシュ

ローカルまたはGitHub Webから以下を実行:

### オプションA: ローカルから（推奨）
```bash
cd /home/user/webapp
git pull origin main
git tag v1.3.0
git push origin v1.3.0
```

### オプションB: GitHub Webから
1. リポジトリページの右側「Releases」をクリック
2. "Draft a new release"をクリック
3. "Choose a tag" → "v1.3.0"を入力して"Create new tag: v1.3.0 on publish"
4. Release title: "v1.3.0 - Windows ZIP extraction fix"
5. 説明欄に以下を入力:
```
## v1.3.0 の変更点

### 🐛 バグ修正
- Windows でZIPファイルが正しく展開できない問題を修正
- PowerShell の Compress-Archive から 7zip に変更
- より互換性の高いZIPフォーマットを使用

### ✨ 改善点
- Windows 標準の解凍ツールとの完全互換を確保
- ファイル属性とタイムスタンプの正確な保持

### 📦 ダウンロード
`IconGenerator-Windows.zip` をダウンロードして解凍してください。

### ⚠️ 初回起動時の注意
Windows SmartScreen の警告が表示された場合:
1. "詳細情報" をクリック
2. "実行" をクリック

このアプリケーションは安全です。警告はコード署名がないためです。
```
6. "Publish release"をクリック（自動的にタグが作成され、ビルドが開始されます）

## ステップ3: ビルドの確認

1. "Actions"タブをクリック
2. "Build and Release" ワークフローの実行を確認
3. ビルドが完了するまで待機（通常5-10分）
4. 完了後、"Releases"ページに`IconGenerator-Windows.zip`がアップロードされていることを確認

## ステップ4: テスト

1. リリースページから`IconGenerator-Windows.zip`をダウンロード
2. Windows環境で右クリック → "すべて展開"
3. 正常に展開できることを確認
4. `IconGenerator.exe`を実行して動作確認

## 期待される結果

- ✅ ZIPファイルがWindows標準の解凍ツールで正常に展開できる
- ✅ 展開後のファイルが破損していない
- ✅ アプリケーションが正常に起動する
- ✅ バージョン情報が1.3.0と表示される

## トラブルシューティング

### ワークフロー編集時に権限エラーが出る
→ リポジトリの管理者権限が必要です。オーナーに依頼してください。

### ビルドが失敗する
→ Actionsタブでエラーログを確認し、必要に応じて修正してください。

### ZIPファイルがまだ展開できない
→ ワークフローファイルの修正が正しく適用されているか確認してください。

## 完了

以上の手順で、v1.3.0のビルドとリリースが完了します。
