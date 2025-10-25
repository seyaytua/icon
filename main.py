from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QProgressBar, QTabWidget,
    QSlider, QColorDialog, QCheckBox, QComboBox, QGroupBox,
    QSpinBox, QMessageBox, QSplitter, QScrollArea, QFrame,
    QLineEdit, QListWidget, QDialog, QDialogButtonBox
)
from PySide6.QtCore import Qt, QThread, Signal, QSize, QTimer
from PySide6.QtGui import QPixmap, QImage, QColor, QPainter, QFont, QIcon, QPalette
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
import sys
import os
import platform
import json
from pathlib import Path
from datetime import datetime


class IconGeneratorThread(QThread):
    """バックグラウンドでアイコンを生成するスレッド"""
    progress = Signal(int)
    status = Signal(str)
    finished_signal = Signal(str)
    error = Signal(str)
    
    def __init__(self, source_image, output_path, options):
        super().__init__()
        self.source_image = source_image
        self.output_path = output_path
        self.options = options
    
    def run(self):
        try:
            self.status.emit("アイコン生成を開始しています...")
            self.progress.emit(10)
            
            # Windows ICO
            if self.options.get('windows'):
                self.status.emit("Windows用アイコンを生成中...")
                self.create_windows_icon()
                self.progress.emit(40)
            
            # macOS ICNS
            if self.options.get('macos'):
                self.status.emit("macOS用アイコンを生成中...")
                self.create_mac_icon()
                self.progress.emit(60)
            
            # PNG セット
            if self.options.get('png_set'):
                self.status.emit("PNGセットを生成中...")
                self.create_png_set()
                self.progress.emit(80)
            
            # Favicon
            if self.options.get('favicon'):
                self.status.emit("Faviconを生成中...")
                self.create_favicon()
                self.progress.emit(90)
            
            self.progress.emit(100)
            self.finished_signal.emit("アイコンの生成が完了しました！")
            
        except Exception as e:
            self.error.emit(f"エラーが発生しました: {str(e)}")
    
    def create_windows_icon(self):
        """Windows用アイコン生成"""
        sizes = [16, 24, 32, 48, 64, 128, 256]
        icon_sizes = [(size, size) for size in sizes]
        
        output_file = os.path.join(self.output_path, "app_icon.ico")
        self.source_image.save(output_file, format='ICO', sizes=icon_sizes)
    
    def create_mac_icon(self):
        """macOS用アイコン生成"""
        sizes = [16, 32, 64, 128, 256, 512, 1024]
        output_dir = os.path.join(self.output_path, "macos_icons")
        os.makedirs(output_dir, exist_ok=True)
        
        if platform.system() == 'Darwin':
            # macOSの場合、iconsetを作成
            iconset_path = os.path.join(self.output_path, "AppIcon.iconset")
            os.makedirs(iconset_path, exist_ok=True)
            
            for size in sizes:
                img = self.source_image.resize((size, size), Image.Resampling.LANCZOS)
                img.save(f"{iconset_path}/icon_{size}x{size}.png")
                
                if size <= 512:
                    retina_size = size * 2
                    img_2x = self.source_image.resize(
                        (retina_size, retina_size),
                        Image.Resampling.LANCZOS
                    )
                    img_2x.save(f"{iconset_path}/icon_{size}x{size}@2x.png")
            
            # iconutilで変換
            os.system(f"iconutil -c icns {iconset_path}")
            
            # 一時ディレクトリを削除
            import shutil
            shutil.rmtree(iconset_path)
        else:
            # macOS以外の場合、PNGセットとして保存
            for size in sizes:
                img = self.source_image.resize((size, size), Image.Resampling.LANCZOS)
                img.save(os.path.join(output_dir, f"icon_{size}x{size}.png"))
    
    def create_png_set(self):
        """PNGセット生成"""
        sizes = [16, 32, 48, 64, 128, 256, 512, 1024]
        output_dir = os.path.join(self.output_path, "png_icons")
        os.makedirs(output_dir, exist_ok=True)
        
        for size in sizes:
            img = self.source_image.resize((size, size), Image.Resampling.LANCZOS)
            img.save(os.path.join(output_dir, f"icon_{size}x{size}.png"))
    
    def create_favicon(self):
        """Favicon生成"""
        sizes = [(16, 16), (32, 32), (48, 48)]
        output_file = os.path.join(self.output_path, "favicon.ico")
        self.source_image.save(output_file, format='ICO', sizes=sizes)


class AdvancedImageProcessor:
    """高度な画像処理機能"""
    
    @staticmethod
    def add_drop_shadow(image, offset=(8, 8), blur_radius=15, color=(0, 0, 0, 180)):
        """ドロップシャドウを追加"""
        # 影用の新しい画像を作成
        shadow_size = (
            image.width + abs(offset[0]) * 3,
            image.height + abs(offset[1]) * 3
        )
        shadow = Image.new('RGBA', shadow_size, (0, 0, 0, 0))
        
        # 影を描画
        shadow_layer = Image.new('RGBA', image.size, color)
        shadow_offset = (abs(offset[0]) + offset[0], abs(offset[1]) + offset[1])
        shadow.paste(shadow_layer, shadow_offset, image)
        shadow = shadow.filter(ImageFilter.GaussianBlur(blur_radius))
        
        # 元の画像を上に配置
        final = Image.new('RGBA', shadow.size, (0, 0, 0, 0))
        final.paste(shadow, (0, 0))
        final.paste(image, (abs(offset[0]), abs(offset[1])), image)
        
        return final
    
    @staticmethod
    def create_rounded_corners(image, radius=30):
        """角を丸くする"""
        # マスクを作成
        mask = Image.new('L', image.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([(0, 0), image.size], radius, fill=255)
        
        # 結果画像を作成
        result = Image.new('RGBA', image.size, (0, 0, 0, 0))
        result.paste(image, (0, 0))
        result.putalpha(mask)
        
        return result
    
    @staticmethod
    def add_gradient_background(image, color1=(66, 133, 244), color2=(219, 68, 55), direction='vertical'):
        """グラデーション背景を追加"""
        gradient = Image.new('RGB', image.size, color1)
        draw = ImageDraw.Draw(gradient)
        
        if direction == 'vertical':
            for i in range(image.height):
                ratio = i / image.height
                r = int(color1[0] + (color2[0] - color1[0]) * ratio)
                g = int(color1[1] + (color2[1] - color1[1]) * ratio)
                b = int(color1[2] + (color2[2] - color1[2]) * ratio)
                draw.line([(0, i), (image.width, i)], fill=(r, g, b))
        else:  # horizontal
            for i in range(image.width):
                ratio = i / image.width
                r = int(color1[0] + (color2[0] - color1[0]) * ratio)
                g = int(color1[1] + (color2[1] - color1[1]) * ratio)
                b = int(color1[2] + (color2[2] - color1[2]) * ratio)
                draw.line([(i, 0), (i, image.height)], fill=(r, g, b))
        
        # RGBA変換
        gradient = gradient.convert('RGBA')
        result = Image.new('RGBA', image.size)
        result.paste(gradient, (0, 0))
        result.paste(image, (0, 0), image)
        
        return result
    
    @staticmethod
    def add_padding(image, padding=20, background_color=(255, 255, 255, 0)):
        """パディングを追加"""
        new_size = (image.width + padding * 2, image.height + padding * 2)
        result = Image.new('RGBA', new_size, background_color)
        result.paste(image, (padding, padding), image)
        return result
    
    @staticmethod
    def add_border(image, width=5, color=(0, 0, 0, 255)):
        """枠線を追加"""
        result = image.copy()
        draw = ImageDraw.Draw(result)
        draw.rectangle(
            [(0, 0), (image.width - 1, image.height - 1)],
            outline=color,
            width=width
        )
        return result
    
    @staticmethod
    def apply_glass_effect(image):
        """ガラス効果を適用"""
        # 明るさを上げる
        enhancer = ImageEnhance.Brightness(image)
        bright = enhancer.enhance(1.15)
        
        # ハイライトを追加
        highlight = Image.new('RGBA', image.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(highlight)
        
        # グラデーションハイライト
        for i in range(image.height // 3):
            alpha = int(80 * (1 - i / (image.height // 3)))
            draw.line([(0, i), (image.width, i)], fill=(255, 255, 255, alpha))
        
        result = Image.alpha_composite(bright, highlight)
        return result
    
    @staticmethod
    def create_circular_mask(image):
        """円形マスクを適用"""
        mask = Image.new('L', image.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse([(0, 0), image.size], fill=255)
        
        result = Image.new('RGBA', image.size, (0, 0, 0, 0))
        result.paste(image, (0, 0))
        result.putalpha(mask)
        
        return result
    
    @staticmethod
    def add_noise(image, amount=25):
        """ノイズを追加"""
        import random
        result = image.copy()
        pixels = result.load()
        
        for i in range(result.width):
            for j in range(result.height):
                if random.randint(0, 100) < amount:
                    r, g, b, a = pixels[i, j]
                    noise = random.randint(-30, 30)
                    r = max(0, min(255, r + noise))
                    g = max(0, min(255, g + noise))
                    b = max(0, min(255, b + noise))
                    pixels[i, j] = (r, g, b, a)
        
        return result


class PresetDialog(QDialog):
    """プリセット選択ダイアログ"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("プリセットを選択")
        self.setMinimumWidth(400)
        self.selected_preset = None
        
        layout = QVBoxLayout()
        
        # プリセットリスト
        self.preset_list = QListWidget()
        presets = [
            "モダンフラット - 明るく鮮やかなフラットデザイン",
            "グロッシー3D - 光沢のある立体的な外観",
            "ミニマル - シンプルで洗練されたデザイン",
            "ビビッド - 鮮やかで目を引く色合い",
            "ダーク - 暗めの落ち着いた雰囲気",
            "パステル - 柔らかく優しい色調",
            "ネオン - 明るく輝くネオン風",
            "レトロ - 懐かしいヴィンテージ風"
        ]
        self.preset_list.addItems(presets)
        self.preset_list.setCurrentRow(0)
        layout.addWidget(self.preset_list)
        
        # ボタン
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def get_selected_preset(self):
        """選択されたプリセット名を取得"""
        current_item = self.preset_list.currentItem()
        if current_item:
            return current_item.text().split(' - ')[0]
        return None


class PresetManager:
    """プリセット管理"""
    
    PRESETS = {
        'モダンフラット': {
            'brightness': 10,
            'contrast': 15,
            'saturation': 20,
            'rounded_corners': True,
            'corner_radius': 25,
            'shadow': True,
            'padding': 15
        },
        'グロッシー3D': {
            'brightness': 5,
            'contrast': 20,
            'saturation': 10,
            'glass_effect': True,
            'shadow': True,
            'shadow_blur': 15
        },
        'ミニマル': {
            'brightness': 0,
            'contrast': 0,
            'saturation': -20,
            'padding': 25,
            'border': True,
            'border_width': 2
        },
        'ビビッド': {
            'brightness': 15,
            'contrast': 30,
            'saturation': 50,
            'sharpen': 15
        },
        'ダーク': {
            'brightness': -20,
            'contrast': 25,
            'saturation': -10,
            'shadow': True
        },
        'パステル': {
            'brightness': 20,
            'contrast': -10,
            'saturation': -30,
            'rounded_corners': True
        },
        'ネオン': {
            'brightness': 25,
            'contrast': 40,
            'saturation': 60,
            'shadow': True,
            'shadow_blur': 20
        },
        'レトロ': {
            'brightness': -10,
            'contrast': 15,
            'saturation': -15,
            'noise': 10
        }
    }
    
    @classmethod
    def apply_preset(cls, image, preset_name):
        """プリセットを適用"""
        if preset_name not in cls.PRESETS:
            return image
        
        preset = cls.PRESETS[preset_name]
        result = image.copy()
        
        # 明るさ
        if 'brightness' in preset and preset['brightness'] != 0:
            enhancer = ImageEnhance.Brightness(result)
            result = enhancer.enhance(1 + preset['brightness'] / 100)
        
        # コントラスト
        if 'contrast' in preset and preset['contrast'] != 0:
            enhancer = ImageEnhance.Contrast(result)
            result = enhancer.enhance(1 + preset['contrast'] / 100)
        
        # 彩度
        if 'saturation' in preset and preset['saturation'] != 0:
            enhancer = ImageEnhance.Color(result)
            result = enhancer.enhance(1 + preset['saturation'] / 100)
        
        # シャープネス
        if preset.get('sharpen'):
            enhancer = ImageEnhance.Sharpness(result)
            result = enhancer.enhance(1 + preset['sharpen'] / 100)
        
        # 角丸
        if preset.get('rounded_corners'):
            radius = preset.get('corner_radius', 20)
            result = AdvancedImageProcessor.create_rounded_corners(result, radius)
        
        # パディング
        if preset.get('padding'):
            result = AdvancedImageProcessor.add_padding(result, preset['padding'])
        
        # 枠線
        if preset.get('border'):
            width = preset.get('border_width', 3)
            result = AdvancedImageProcessor.add_border(result, width)
        
        # ガラス効果
        if preset.get('glass_effect'):
            result = AdvancedImageProcessor.apply_glass_effect(result)
        
        # ノイズ
        if preset.get('noise'):
            result = AdvancedImageProcessor.add_noise(result, preset['noise'])
        
        # 影（最後に適用）
        if preset.get('shadow'):
            blur = preset.get('shadow_blur', 10)
            result = AdvancedImageProcessor.add_drop_shadow(
                result, blur_radius=blur
            )
        
        return result


class RichIconGenerator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.source_image = None
        self.edited_image = None
        self.current_preset = None
        self.history = []
        self.history_index = -1
        
        self.init_ui()
        self.apply_modern_style()
    
    def init_ui(self):
        """UIの初期化"""
        self.setWindowTitle('プロフェッショナルアイコンジェネレーター v2.0')
        self.setGeometry(100, 100, 1400, 900)
        
        # メインウィジェット
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)
        
        # スプリッターで左右を分割
        splitter = QSplitter(Qt.Horizontal)
        
        # 左側：プレビューエリア
        left_widget = self.create_preview_area()
        splitter.addWidget(left_widget)
        
        # 右側：コントロールパネル
        right_widget = self.create_control_panel()
        splitter.addWidget(right_widget)
        
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(splitter)
        
        # ステータスバー
        self.statusBar().showMessage('画像を選択してください')
    
    def create_preview_area(self):
        """プレビューエリアの作成"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # タイトル
        title = QLabel('プレビュー')
        title.setFont(QFont('Arial', 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # メインプレビュー
        preview_container = QFrame()
        preview_container.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        preview_layout = QVBoxLayout()
        preview_container.setLayout(preview_layout)
        
        self.preview_label = QLabel('画像をドラッグ&ドロップ\nまたは下のボタンから選択')
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(500, 500)
        self.preview_label.setStyleSheet("""
            QLabel {
                border: 3px dashed #999999;
                border-radius: 15px;
                background-color: #f8f9fa;
                color: #666666;
                font-size: 16px;
            }
        """)
        self.preview_label.setAcceptDrops(True)
        preview_layout.addWidget(self.preview_label)
        
        layout.addWidget(preview_container)
        
        # 画像選択ボタン
        button_layout = QHBoxLayout()
        
        select_btn = QPushButton('📁 画像を選択')
        select_btn.clicked.connect(self.select_image)
        select_btn.setMinimumHeight(50)
        select_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        button_layout.addWidget(select_btn)
        
        reset_btn = QPushButton('🔄 リセット')
        reset_btn.clicked.connect(self.reset_image)
        reset_btn.setMinimumHeight(50)
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #fb8c00;
            }
            QPushButton:pressed {
                background-color: #ef6c00;
            }
        """)
        button_layout.addWidget(reset_btn)
        
        layout.addLayout(button_layout)
        
        # マルチサイズプレビュー
        size_preview_label = QLabel('サイズ別プレビュー')
        size_preview_label.setFont(QFont('Arial', 12, QFont.Bold))
        size_preview_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(size_preview_label)
        
        size_preview_container = QFrame()
        size_preview_container.setFrameStyle(QFrame.StyledPanel)
        size_preview_layout = QHBoxLayout()
        size_preview_container.setLayout(size_preview_layout)
        
        self.size_previews = {}
        sizes = [16, 32, 64, 128, 256]
        for size in sizes:
            size_widget = QWidget()
            size_layout = QVBoxLayout()
            size_widget.setLayout(size_layout)
            
            label = QLabel()
            label.setFixedSize(size + 20, size + 20)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("""
                border: 2px solid #ddd;
                background: white;
                border-radius: 5px;
            """)
            self.size_previews[size] = label
            size_layout.addWidget(label)
            
            size_text = QLabel(f'{size}×{size}')
            size_text.setAlignment(Qt.AlignCenter)
            size_text.setStyleSheet("font-size: 10px; color: #666;")
            size_layout.addWidget(size_text)
            
            size_preview_layout.addWidget(size_widget)
        
        layout.addWidget(size_preview_container)
        
        # プログレスバー
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ddd;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # ステータスラベル
        self.status_label = QLabel('')
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(self.status_label)
        
        return widget
    
    def create_control_panel(self):
        """コントロールパネルの作成"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # タイトル
        title = QLabel('編集ツール')
        title.setFont(QFont('Arial', 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # スクロールエリア
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_content.setLayout(scroll_layout)
        
        # タブウィジェット
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            QTabBar::tab {
                background: #f0f0f0;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom: 2px solid #4CAF50;
            }
        """)
        
        # 各タブを作成
        self.tab_widget.addTab(self.create_quick_tab(), "⚡ クイック")
        self.tab_widget.addTab(self.create_adjust_tab(), "🎨 調整")
        self.tab_widget.addTab(self.create_effect_tab(), "✨ エフェクト")
        self.tab_widget.addTab(self.create_background_tab(), "🖼️ 背景")
        self.tab_widget.addTab(self.create_export_tab(), "💾 エクスポート")
        
        scroll_layout.addWidget(self.tab_widget)
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        return widget
    
    def create_quick_tab(self):
        """クイックタブの作成"""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # プリセット選択
        preset_group = QGroupBox("プリセット")
        preset_layout = QVBoxLayout()
        
        preset_btn = QPushButton('🎭 プリセットを選択')
        preset_btn.clicked.connect(self.show_preset_dialog)
        preset_btn.setMinimumHeight(40)
        preset_layout.addWidget(preset_btn)
        
        self.current_preset_label = QLabel('選択なし')
        self.current_preset_label.setAlignment(Qt.AlignCenter)
        self.current_preset_label.setStyleSheet("""
            padding: 10px;
            background: #f0f0f0;
            border-radius: 5px;
            font-weight: bold;
        """)
        preset_layout.addWidget(self.current_preset_label)
        
        preset_group.setLayout(preset_layout)
        layout.addWidget(preset_group)
        
        # クイックアクション
        action_group = QGroupBox("クイックアクション")
        action_layout = QVBoxLayout()
        
        actions = [
            ('🔄 左に90°回転', lambda: self.rotate_image(-90)),
            ('🔄 右に90°回転', lambda: self.rotate_image(90)),
            ('↔️ 水平反転', self.flip_horizontal),
            ('↕️ 垂直反転', self.flip_vertical),
            ('⭕ 円形マスク', self.apply_circular_mask),
            ('📐 正方形にトリミング', self.crop_to_square),
        ]
        
        for text, func in actions:
            btn = QPushButton(text)
            btn.clicked.connect(func)
            btn.setMinimumHeight(35)
            action_layout.addWidget(btn)
        
        action_group.setLayout(action_layout)
        layout.addWidget(action_group)
        
        layout.addStretch()
        return tab
    
    def create_adjust_tab(self):
        """調整タブの作成"""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # 明るさ
        brightness_group = self.create_slider_group(
            "明るさ", -100, 100, 0, self.apply_adjustments
        )
        self.brightness_slider = brightness_group['slider']
        self.brightness_value = brightness_group['value']
        layout.addWidget(brightness_group['widget'])
        
        # コントラスト
        contrast_group = self.create_slider_group(
            "コントラスト", -100, 100, 0, self.apply_adjustments
        )
        self.contrast_slider = contrast_group['slider']
        self.contrast_value = contrast_group['value']
        layout.addWidget(contrast_group['widget'])
        
        # 彩度
        saturation_group = self.create_slider_group(
            "彩度", -100, 100, 0, self.apply_adjustments
        )
        self.saturation_slider = saturation_group['slider']
        self.saturation_value = saturation_group['value']
        layout.addWidget(saturation_group['widget'])
        
        # シャープネス
        sharpness_group = self.create_slider_group(
            "シャープネス", -100, 100, 0, self.apply_adjustments
        )
        self.sharpness_slider = sharpness_group['slider']
        self.sharpness_value = sharpness_group['value']
        layout.addWidget(sharpness_group['widget'])
        
        # リセットボタン
        reset_btn = QPushButton('すべてリセット')
        reset_btn.clicked.connect(self.reset_adjustments)
        layout.addWidget(reset_btn)
        
        layout.addStretch()
        return tab
    
    def create_effect_tab(self):
        """エフェクトタブの作成"""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # ぼかし
        blur_group = self.create_slider_group(
            "ぼかし", 0, 30, 0, self.apply_effects
        )
        self.blur_slider = blur_group['slider']
        self.blur_value = blur_group['value']
        layout.addWidget(blur_group['widget'])
        
        # 角丸
        rounded_group = QGroupBox("角丸")
        rounded_layout = QVBoxLayout()
        
        self.rounded_check = QCheckBox("角を丸くする")
        self.rounded_check.stateChanged.connect(self.apply_effects)
        rounded_layout.addWidget(self.rounded_check)
        
        radius_group = self.create_slider_group(
            "半径", 0, 100, 30, self.apply_effects
        )
        self.corner_radius_slider = radius_group['slider']
        self.corner_radius_value = radius_group['value']
        rounded_layout.addWidget(radius_group['widget'])
        
        rounded_group.setLayout(rounded_layout)
        layout.addWidget(rounded_group)
        
        # 影
        shadow_group = QGroupBox("ドロップシャドウ")
        shadow_layout = QVBoxLayout()
        
        self.shadow_check = QCheckBox("影を追加")
        self.shadow_check.stateChanged.connect(self.apply_effects)
        shadow_layout.addWidget(self.shadow_check)
        
        shadow_blur_group = self.create_slider_group(
            "ぼかし", 0, 30, 15, self.apply_effects
        )
        self.shadow_blur_slider = shadow_blur_group['slider']
        self.shadow_blur_value = shadow_blur_group['value']
        shadow_layout.addWidget(shadow_blur_group['widget'])
        
        shadow_group.setLayout(shadow_layout)
        layout.addWidget(shadow_group)
        
        # 枠線
        border_group = QGroupBox("枠線")
        border_layout = QVBoxLayout()
        
        self.border_check = QCheckBox("枠線を追加")
        self.border_check.stateChanged.connect(self.apply_effects)
        border_layout.addWidget(self.border_check)
        
        border_width_group = self.create_slider_group(
            "太さ", 1, 20, 5, self.apply_effects
        )
        self.border_width_slider = border_width_group['slider']
        self.border_width_value = border_width_group['value']
        border_layout.addWidget(border_width_group['widget'])
        
        border_group.setLayout(border_layout)
        layout.addWidget(border_group)
        
        # その他のエフェクト
        other_group = QGroupBox("その他")
        other_layout = QVBoxLayout()
        
        self.glass_check = QCheckBox("ガラス効果")
        self.glass_check.stateChanged.connect(self.apply_effects)
        other_layout.addWidget(self.glass_check)
        
        other_group.setLayout(other_layout)
        layout.addWidget(other_group)
        
        layout.addStretch()
        return tab
    
    def create_background_tab(self):
        """背景タブの作成"""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # パディング
        padding_group = self.create_slider_group(
            "パディング", 0, 100, 0, self.apply_background
        )
        self.padding_slider = padding_group['slider']
        self.padding_value = padding_group['value']
        layout.addWidget(padding_group['widget'])
        
        # 背景色
        bg_color_group = QGroupBox("背景色")
        bg_color_layout = QVBoxLayout()
        
        self.bg_color_check = QCheckBox("背景色を追加")
        self.bg_color_check.stateChanged.connect(self.apply_background)
        bg_color_layout.addWidget(self.bg_color_check)
        
        color_btn_layout = QHBoxLayout()
        self.bg_color_btn = QPushButton('色を選択')
        self.bg_color_btn.clicked.connect(self.select_background_color)
        color_btn_layout.addWidget(self.bg_color_btn)
        
        self.bg_color_display = QLabel()
        self.bg_color_display.setFixedSize(50, 30)
        self.bg_color_display.setStyleSheet("""
            background-color: white;
            border: 2px solid #ddd;
            border-radius: 5px;
        """)
        color_btn_layout.addWidget(self.bg_color_display)
        
        bg_color_layout.addLayout(color_btn_layout)
        bg_color_group.setLayout(bg_color_layout)
        layout.addWidget(bg_color_group)
        
        self.bg_color = (255, 255, 255, 255)
        
        # グラデーション
        gradient_group = QGroupBox("グラデーション")
        gradient_layout = QVBoxLayout()
        
        self.gradient_check = QCheckBox("グラデーション背景")
        self.gradient_check.stateChanged.connect(self.apply_background)
        gradient_layout.addWidget(self.gradient_check)
        
        # グラデーション色1
        grad_color1_layout = QHBoxLayout()
        grad_color1_label = QLabel("色1:")
        grad_color1_layout.addWidget(grad_color1_label)
        
        self.grad_color1_btn = QPushButton('選択')
        self.grad_color1_btn.clicked.connect(lambda: self.select_gradient_color(1))
        grad_color1_layout.addWidget(self.grad_color1_btn)
        
        self.grad_color1_display = QLabel()
        self.grad_color1_display.setFixedSize(50, 30)
        self.grad_color1_display.setStyleSheet("""
            background-color: rgb(66, 133, 244);
            border: 2px solid #ddd;
            border-radius: 5px;
        """)
        grad_color1_layout.addWidget(self.grad_color1_display)
        gradient_layout.addLayout(grad_color1_layout)
        
        # グラデーション色2
        grad_color2_layout = QHBoxLayout()
        grad_color2_label = QLabel("色2:")
        grad_color2_layout.addWidget(grad_color2_label)
        
        self.grad_color2_btn = QPushButton('選択')
        self.grad_color2_btn.clicked.connect(lambda: self.select_gradient_color(2))
        grad_color2_layout.addWidget(self.grad_color2_btn)
        
        self.grad_color2_display = QLabel()
        self.grad_color2_display.setFixedSize(50, 30)
        self.grad_color2_display.setStyleSheet("""
            background-color: rgb(219, 68, 55);
            border: 2px solid #ddd;
            border-radius: 5px;
        """)
        grad_color2_layout.addWidget(self.grad_color2_display)
        gradient_layout.addLayout(grad_color2_layout)
        
        # グラデーション方向
        direction_layout = QHBoxLayout()
        direction_label = QLabel("方向:")
        direction_layout.addWidget(direction_label)
        
        self.gradient_direction = QComboBox()
        self.gradient_direction.addItems(["垂直", "水平"])
        self.gradient_direction.currentIndexChanged.connect(self.apply_background)
        direction_layout.addWidget(self.gradient_direction)
        gradient_layout.addLayout(direction_layout)
        
        gradient_group.setLayout(gradient_layout)
        layout.addWidget(gradient_group)
        
        self.grad_color1 = (66, 133, 244)
        self.grad_color2 = (219, 68, 55)
        
        layout.addStretch()
        return tab
    
    def create_export_tab(self):
        """エクスポートタブの作成"""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # プラットフォーム選択
        platform_group = QGroupBox("プラットフォーム")
        platform_layout = QVBoxLayout()
        
        self.windows_check = QCheckBox("Windows (.ico)")
        self.windows_check.setChecked(True)
        platform_layout.addWidget(self.windows_check)
        
        self.mac_check = QCheckBox("macOS (.icns / PNG)")
        self.mac_check.setChecked(True)
        platform_layout.addWidget(self.mac_check)
        
        self.png_check = QCheckBox("PNGセット")
        self.png_check.setChecked(True)
        platform_layout.addWidget(self.png_check)
        
        self.favicon_check = QCheckBox("Favicon")
        platform_layout.addWidget(self.favicon_check)
        
        platform_group.setLayout(platform_layout)
        layout.addWidget(platform_group)
        
        # 出力先
        output_group = QGroupBox("出力先")
        output_layout = QVBoxLayout()
        
        output_path_layout = QHBoxLayout()
        self.output_path_edit = QLineEdit()
        self.output_path_edit.setPlaceholderText("出力フォルダを選択...")
        self.output_path_edit.setReadOnly(True)
        output_path_layout.addWidget(self.output_path_edit)
        
        browse_btn = QPushButton('📁 参照')
        browse_btn.clicked.connect(self.select_output_folder)
        output_path_layout.addWidget(browse_btn)
        
        output_layout.addLayout(output_path_layout)
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
        
        # エクスポートボタン
        export_btn = QPushButton('💾 エクスポート開始')
        export_btn.clicked.connect(self.export_icons)
        export_btn.setMinimumHeight(60)
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
            QPushButton:pressed {
                background-color: #0a6bc5;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        layout.addWidget(export_btn)
        
        # 情報表示
        info_label = QLabel(
            "💡 ヒント:\n"
            "• 最高品質のアイコンには1024x1024以上の画像を推奨\n"
            "• 透明背景のPNG形式が最適\n"
            "• macOS用.icnsはmacでのみ生成可能"
        )
        info_label.setStyleSheet("""
            padding: 15px;
            background: #e3f2fd;
            border-radius: 5px;
            color: #1976d2;
            font-size: 11px;
        """)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        layout.addStretch()
        return tab
    
    def create_slider_group(self, title, min_val, max_val, default, callback):
        """スライダーグループを作成"""
        group = QGroupBox(title)
        layout = QVBoxLayout()
        
        slider_layout = QHBoxLayout()
        
        slider = QSlider(Qt.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(default)
        slider.valueChanged.connect(callback)
        slider_layout.addWidget(slider)
        
        value_label = QLabel(str(default))
        value_label.setFixedWidth(40)
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setStyleSheet("""
            background: #f0f0f0;
            border-radius: 3px;
            padding: 5px;
            font-weight: bold;
        """)
        slider_layout.addWidget(value_label)
        
        slider.valueChanged.connect(lambda v: value_label.setText(str(v)))
        
        layout.addLayout(slider_layout)
        group.setLayout(layout)
        
        return {
            'widget': group,
            'slider': slider,
            'value': value_label
        }
    
    def apply_modern_style(self):
        """モダンなスタイルを適用"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 8px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
            QSlider::groove:horizontal {
                border: 1px solid #bbb;
                background: white;
                height: 8px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #4CAF50;
                border: 1px solid #4CAF50;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QCheckBox {
                spacing: 8px;
                font-size: 13px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QComboBox {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 5px;
                background: white;
            }
        """)
    
    def select_image(self):
        """画像を選択"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "画像を選択",
            "",
            "画像ファイル (*.png *.jpg *.jpeg *.bmp *.gif *.webp)"
        )
        if file_path:
            self.load_image(file_path)
    
    def load_image(self, file_path):
        """画像を読み込み"""
        try:
            self.source_image = Image.open(file_path)
            if self.source_image.mode != 'RGBA':
                self.source_image = self.source_image.convert('RGBA')
            
            self.edited_image = self.source_image.copy()
            self.history = [self.source_image.copy()]
            self.history_index = 0
            
            self.update_preview()
            self.statusBar().showMessage(f'画像を読み込みました: {os.path.basename(file_path)}')
            
            # 画像情報を表示
            width, height = self.source_image.size
            self.status_label.setText(
                f'サイズ: {width}×{height}px | '
                f'モード: {self.source_image.mode}'
            )
            
        except Exception as e:
            QMessageBox.critical(self, 'エラー', f'画像の読み込みに失敗しました:\n{str(e)}')
    
    def update_preview(self):
        """プレビューを更新"""
        if not self.edited_image:
            return
        
        try:
            # メインプレビュー
            display_size = 500
            preview = self.edited_image.copy()
            
            # アスペクト比を保持してリサイズ
            preview.thumbnail((display_size, display_size), Image.Resampling.LANCZOS)
            
            # PIL ImageをQPixmapに変換
            preview_bytes = preview.tobytes("raw", "RGBA")
            qimage = QImage(
                preview_bytes,
                preview.width,
                preview.height,
                preview.width * 4,
                QImage.Format_RGBA8888
            )
            pixmap = QPixmap.fromImage(qimage)
            self.preview_label.setPixmap(pixmap)
            
            # サイズ別プレビュー
            for size, label in self.size_previews.items():
                size_preview = self.edited_image.copy()
                size_preview.thumbnail((size, size), Image.Resampling.LANCZOS)
                
                # 中央配置用の背景を作成
                bg = Image.new('RGBA', (size, size), (255, 255, 255, 0))
                offset = ((size - size_preview.width) // 2,
                         (size - size_preview.height) // 2)
                bg.paste(size_preview, offset, size_preview)
                
                size_bytes = bg.tobytes("raw", "RGBA")
                size_qimage = QImage(
                    size_bytes,
                    size,
                    size,
                    size * 4,
                    QImage.Format_RGBA8888
                )
                size_pixmap = QPixmap.fromImage(size_qimage)
                label.setPixmap(size_pixmap)
                
        except Exception as e:
            print(f"Preview update error: {e}")
    
    def show_preset_dialog(self):
        """プリセット選択ダイアログを表示"""
        if not self.source_image:
            QMessageBox.warning(self, '警告', '先に画像を選択してください')
            return
        
        dialog = PresetDialog(self)
        if dialog.exec():
            preset_name = dialog.get_selected_preset()
            if preset_name:
                self.apply_preset(preset_name)
    
    def apply_preset(self, preset_name):
        """プリセットを適用"""
        if not self.source_image:
            return
        
        try:
            self.edited_image = PresetManager.apply_preset(
                self.source_image.copy(),
                preset_name
            )
            self.current_preset = preset_name
            self.current_preset_label.setText(preset_name)
            self.update_preview()
            self.statusBar().showMessage(f'プリセット「{preset_name}」を適用しました')
            
        except Exception as e:
            QMessageBox.critical(self, 'エラー', f'プリセットの適用に失敗しました:\n{str(e)}')
    
    def apply_adjustments(self):
        """調整を適用"""
        if not self.source_image:
            return
        
        try:
            self.edited_image = self.source_image.copy()
            
            # 明るさ
            brightness_value = self.brightness_slider.value() / 100.0
            if brightness_value != 0:
                enhancer = ImageEnhance.Brightness(self.edited_image)
                self.edited_image = enhancer.enhance(1 + brightness_value)
            
            # コントラスト
            contrast_value = self.contrast_slider.value() / 100.0
            if contrast_value != 0:
                enhancer = ImageEnhance.Contrast(self.edited_image)
                self.edited_image = enhancer.enhance(1 + contrast_value)
            
            # 彩度
            saturation_value = self.saturation_slider.value() / 100.0
            if saturation_value != 0:
                enhancer = ImageEnhance.Color(self.edited_image)
                self.edited_image = enhancer.enhance(1 + saturation_value)
            
            # シャープネス
            sharpness_value = self.sharpness_slider.value() / 100.0
            if sharpness_value != 0:
                enhancer = ImageEnhance.Sharpness(self.edited_image)
                self.edited_image = enhancer.enhance(1 + sharpness_value)
            
            self.update_preview()
            
        except Exception as e:
            print(f"Adjustment error: {e}")
    
    def apply_effects(self):
        """エフェクトを適用"""
        if not self.edited_image:
            return
        
        try:
            # 現在の調整を保持
            temp_image = self.edited_image.copy()
            
            # ぼかし
            blur_value = self.blur_slider.value()
            if blur_value > 0:
                temp_image = temp_image.filter(
                    ImageFilter.GaussianBlur(blur_value / 2)
                )
            
            # 角丸
            if self.rounded_check.isChecked():
                radius = self.corner_radius_slider.value()
                temp_image = AdvancedImageProcessor.create_rounded_corners(
                    temp_image, radius
                )
            
            # 枠線
            if self.border_check.isChecked():
                width = self.border_width_slider.value()
                temp_image = AdvancedImageProcessor.add_border(temp_image, width)
            
            # ガラス効果
            if self.glass_check.isChecked():
                temp_image = AdvancedImageProcessor.apply_glass_effect(temp_image)
            
            # 影（最後に適用）
            if self.shadow_check.isChecked():
                blur = self.shadow_blur_slider.value()
                temp_image = AdvancedImageProcessor.add_drop_shadow(
                    temp_image, blur_radius=blur
                )
            
            self.edited_image = temp_image
            self.update_preview()
            
        except Exception as e:
            print(f"Effect error: {e}")
    
    def apply_background(self):
        """背景を適用"""
        if not self.source_image:
            return
        
        try:
            # 現在の編集を取得
            temp_image = self.edited_image.copy()
            
            # パディング
            padding = self.padding_slider.value()
            if padding > 0:
                temp_image = AdvancedImageProcessor.add_padding(
                    temp_image, padding
                )
            
            # 背景色
            if self.bg_color_check.isChecked():
                bg = Image.new('RGBA', temp_image.size, self.bg_color)
                result = Image.new('RGBA', temp_image.size)
                result.paste(bg, (0, 0))
                result.paste(temp_image, (0, 0), temp_image)
                temp_image = result
            
            # グラデーション
            if self.gradient_check.isChecked():
                direction = 'vertical' if self.gradient_direction.currentIndex() == 0 else 'horizontal'
                temp_image = AdvancedImageProcessor.add_gradient_background(
                    temp_image,
                    self.grad_color1,
                    self.grad_color2,
                    direction
                )
            
            self.edited_image = temp_image
            self.update_preview()
            
        except Exception as e:
            print(f"Background error: {e}")
    
    def reset_adjustments(self):
        """調整をリセット"""
        self.brightness_slider.setValue(0)
        self.contrast_slider.setValue(0)
        self.saturation_slider.setValue(0)
        self.sharpness_slider.setValue(0)
    
    def rotate_image(self, angle):
        """画像を回転"""
        if not self.edited_image:
            return
        
        self.edited_image = self.edited_image.rotate(angle, expand=True)
        self.update_preview()
        self.statusBar().showMessage(f'{angle}度回転しました')
    
    def flip_horizontal(self):
        """水平反転"""
        if not self.edited_image:
            return
        
        self.edited_image = self.edited_image.transpose(Image.FLIP_LEFT_RIGHT)
        self.update_preview()
        self.statusBar().showMessage('水平反転しました')
    
    def flip_vertical(self):
        """垂直反転"""
        if not self.edited_image:
            return
        
        self.edited_image = self.edited_image.transpose(Image.FLIP_TOP_BOTTOM)
        self.update_preview()
        self.statusBar().showMessage('垂直反転しました')
    
    def apply_circular_mask(self):
        """円形マスクを適用"""
        if not self.edited_image:
            return
        
        self.edited_image = AdvancedImageProcessor.create_circular_mask(
            self.edited_image
        )
        self.update_preview()
        self.statusBar().showMessage('円形マスクを適用しました')
    
    def crop_to_square(self):
        """正方形にトリミング"""
        if not self.edited_image:
            return
        
        width, height = self.edited_image.size
        size = min(width, height)
        
        left = (width - size) // 2
        top = (height - size) // 2
        right = left + size
        bottom = top + size
        
        self.edited_image = self.edited_image.crop((left, top, right, bottom))
        self.update_preview()
        self.statusBar().showMessage('正方形にトリミングしました')
    
    def select_background_color(self):
        """背景色を選択"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.bg_color = (color.red(), color.green(), color.blue(), 255)
            self.bg_color_display.setStyleSheet(
                f"background-color: rgb({color.red()}, {color.green()}, {color.blue()}); "
                f"border: 2px solid #ddd; border-radius: 5px;"
            )
            if self.bg_color_check.isChecked():
                self.apply_background()
    
    def select_gradient_color(self, color_num):
        """グラデーション色を選択"""
        color = QColorDialog.getColor()
        if color.isValid():
            rgb = (color.red(), color.green(), color.blue())
            
            if color_num == 1:
                self.grad_color1 = rgb
                self.grad_color1_display.setStyleSheet(
                    f"background-color: rgb({color.red()}, {color.green()}, {color.blue()}); "
                    f"border: 2px solid #ddd; border-radius: 5px;"
                )
            else:
                self.grad_color2 = rgb
                self.grad_color2_display.setStyleSheet(
                    f"background-color: rgb({color.red()}, {color.green()}, {color.blue()}); "
                    f"border: 2px solid #ddd; border-radius: 5px;"
                )
            
            if self.gradient_check.isChecked():
                self.apply_background()
    
    def select_output_folder(self):
        """出力フォルダを選択"""
        folder = QFileDialog.getExistingDirectory(self, "出力フォルダを選択")
        if folder:
            self.output_path_edit.setText(folder)
    
    def reset_image(self):
        """画像をリセット"""
        if self.source_image:
            self.edited_image = self.source_image.copy()
            
            # すべてのスライダーをリセット
            self.reset_adjustments()
            self.blur_slider.setValue(0)
            self.corner_radius_slider.setValue(30)
            self.shadow_blur_slider.setValue(15)
            self.border_width_slider.setValue(5)
            self.padding_slider.setValue(0)
            
            # チェックボックスをリセット
            self.rounded_check.setChecked(False)
            self.shadow_check.setChecked(False)
            self.border_check.setChecked(False)
            self.glass_check.setChecked(False)
            self.bg_color_check.setChecked(False)
            self.gradient_check.setChecked(False)
            
            self.current_preset = None
            self.current_preset_label.setText('選択なし')
            
            self.update_preview()
            self.statusBar().showMessage('画像をリセットしました')
    
    def export_icons(self):
        """アイコンをエクスポート"""
        if not self.edited_image:
            QMessageBox.warning(self, '警告', '先に画像を選択してください')
            return
        
        output_path = self.output_path_edit.text()
        if not output_path:
            QMessageBox.warning(self, '警告', '出力フォルダを選択してください')
            return
        
        # オプションを収集
        options = {
            'windows': self.windows_check.isChecked(),
            'macos': self.mac_check.isChecked(),
            'png_set': self.png_check.isChecked(),
            'favicon': self.favicon_check.isChecked()
        }
        
        if not any(options.values()):
            QMessageBox.warning(self, '警告', '少なくとも1つのプラットフォームを選択してください')
            return
        
        # タイムスタンプ付きフォルダを作成
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_folder = os.path.join(output_path, f"icons_{timestamp}")
        os.makedirs(output_folder, exist_ok=True)
        
        # プログレスバーを表示
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # バックグラウンドスレッドで生成
        self.generator_thread = IconGeneratorThread(
            self.edited_image,
            output_folder,
            options
        )
        
        self.generator_thread.progress.connect(self.progress_bar.setValue)
        self.generator_thread.status.connect(self.status_label.setText)
        self.generator_thread.finished_signal.connect(self.on_export_finished)
        self.generator_thread.error.connect(self.on_export_error)
        
        self.generator_thread.start()
        self.statusBar().showMessage('アイコンを生成中...')
    
    def on_export_finished(self, message):
        """エクスポート完了時の処理"""
        self.progress_bar.setVisible(False)
        self.statusBar().showMessage(message)
        
        QMessageBox.information(
            self,
            '完了',
            f'{message}\n\n出力先:\n{self.output_path_edit.text()}'
        )
        
        # 出力フォルダを開く
        output_path = self.output_path_edit.text()
        if platform.system() == 'Darwin':
            os.system(f'open "{output_path}"')
        elif platform.system() == 'Windows':
            os.system(f'explorer "{output_path}"')
        else:
            os.system(f'xdg-open "{output_path}"')
    
    def on_export_error(self, error_message):
        """エクスポートエラー時の処理"""
        self.progress_bar.setVisible(False)
        self.statusBar().showMessage('エラーが発生しました')
        QMessageBox.critical(self, 'エラー', error_message)


def main():
    app = QApplication(sys.argv)
    
    # アプリケーション情報
    app.setApplicationName("Professional Icon Generator")
    app.setOrganizationName("IconTools")
    
    # モダンなスタイルを適用
    app.setStyle('Fusion')
    
    # カラーパレット
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(255, 255, 255))
    palette.setColor(QPalette.WindowText, QColor(0, 0, 0))
    palette.setColor(QPalette.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.AlternateBase, QColor(245, 245, 245))
    palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ToolTipText, QColor(0, 0, 0))
    palette.setColor(QPalette.Text, QColor(0, 0, 0))
    palette.setColor(QPalette.Button, QColor(240, 240, 240))
    palette.setColor(QPalette.ButtonText, QColor(0, 0, 0))
    palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.Highlight, QColor(76, 175, 80))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)
    
    window = RichIconGenerator()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

