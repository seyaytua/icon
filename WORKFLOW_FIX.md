# Windows ZIP展開問題の修正方法

## 問題
GitHubからダウンロードしたZIPファイルがWindowsで正しく解凍できない問題が発生していました。

## 原因
PowerShellの`Compress-Archive`コマンドで作成されたZIPファイルに互換性の問題がありました。

## 解決方法

### .github/workflows/build.yml の修正

以下の変更を手動で適用してください：

**修正前（35-37行目）:**
```yaml
      - name: Create ZIP archive
        run: |
          powershell Compress-Archive -Path release\* -DestinationPath IconGenerator-Windows.zip
```

**修正後:**
```yaml
      - name: Install 7zip
        run: |
          choco install 7zip -y
          
      - name: Create ZIP archive with 7zip
        run: |
          & "C:\Program Files\7-Zip\7z.exe" a -tzip IconGenerator-Windows.zip .\release\*
```

### 変更内容の説明

1. **7-Zipのインストール**: Chocolateyを使用してWindowsランナーに7-Zipをインストール
2. **ZIP作成方法の変更**: PowerShellの`Compress-Archive`から7-Zipの`7z.exe`に変更
3. **互換性の向上**: 7-Zipは標準的なZIPフォーマットを使用し、Windows標準の解凍ツールと完全互換

### この修正により

- ✅ Windows標準の「右クリック→解凍」が正常に動作
- ✅ Windows Explorerでの解凍が正常に動作
- ✅ サードパーティの解凍ソフト（WinRAR、7-Zip等）での解凍が正常に動作
- ✅ ファイル属性・タイムスタンプが正しく保持される

## 修正適用後の手順

1. 上記の変更を`.github/workflows/build.yml`に適用
2. 変更をコミットしてプッシュ
3. 新しいタグ `v1.3.0` を作成してプッシュ:
   ```bash
   git tag v1.3.0
   git push origin v1.3.0
   ```
4. GitHub Actionsが自動的にビルドを実行
5. リリースページで`IconGenerator-Windows.zip`をダウンロードしてテスト

## 注意事項

- この修正はGitHub Appの権限制限により、自動的に適用できません
- 手動でファイルを編集するか、リポジトリの設定でGitHub Appに`workflows`権限を付与する必要があります
