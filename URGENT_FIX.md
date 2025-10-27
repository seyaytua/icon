# 🚨 緊急修正: PyInstaller v6 エラーの解決

## 問題
GitHubActionsで以下のエラーが発生しています：

```
ERROR: Support for collecting and processing WinSxS assemblies was removed in PyInstaller v6.0. 
Please remove your --win-private-assemblies argument.
```

## 原因
PyInstaller v6.0で以下のオプションが廃止されました：
- `--win-private-assemblies`
- `--win-no-prefer-redirects`

## 緊急修正手順（所要時間: 2分）

### GitHubで直接編集

1. **ワークフローファイルを開く**
   - https://github.com/seyaytua/icon/blob/main/.github/workflows/build.yml にアクセス
   - 右上の鉛筆アイコン（Edit this file）をクリック

2. **26行目を修正**
   
   **修正前（26行目）:**
   ```yaml
   pyinstaller --onefile --windowed --name "IconGenerator" --version-file=version_info.txt --win-private-assemblies --win-no-prefer-redirects main.py
   ```
   
   **修正後:**
   ```yaml
   pyinstaller --onefile --windowed --name "IconGenerator" --version-file=version_info.txt main.py
   ```
   
   つまり、行末の `--win-private-assemblies --win-no-prefer-redirects` を削除します。

3. **コミット**
   - コミットメッセージ: `fix: Remove deprecated PyInstaller v6 flags`
   - "Commit directly to the main branch" を選択
   - "Commit changes" をクリック

## 修正後の確認

この修正により、以下が解決されます：
- ✅ PyInstaller v6のビルドエラー
- ✅ v1.3.0タグのビルドが成功

## 次のステップ

修正完了後、v1.3.0のビルドを実行：

```bash
git pull origin main
git tag v1.3.0
git push origin v1.3.0
```

または、GitHubのReleasesページから直接v1.3.0リリースを作成してください。

## 補足: 7zipの設定について

7zipによるZIP作成の修正は既に適用済みです（コミット cd2e62d）。
この修正でPyInstallerの問題のみが解決されます。

## タイムライン

1. ✅ v1.3.0バージョン更新（PR #1）
2. ✅ 7zip統合（コミット cd2e62d）
3. 🔄 PyInstallerオプション削除（この修正）← **今ここ**
4. ⏳ v1.3.0タグ作成とビルド

---

この修正を行えば、すぐにv1.3.0のビルドが成功します！
