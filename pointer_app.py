import sys
import os
import json
from PyQt5 import QtWidgets, QtGui, QtCore, QtMultimedia

ASSETS_PATH = os.path.join(os.path.dirname(__file__), 'src', 'assets')
CURSORS = [
    ('default', 'default.png'),
    ('default_reverse', 'default_reverse.png'),
]
SOUND_CLICK = os.path.join(ASSETS_PATH, 'knock.wav')
SOUND_LOOP = os.path.join(ASSETS_PATH, 'hold.wav')
SETTINGS_FILE = os.path.join(os.path.dirname(__file__), 'settings.json')

CURSOR_SCALE = 0.4

def load_settings():
    default_settings = {'volume': 100, 'selected_screen': 0}
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                saved_settings = json.load(f)
                for key, value in default_settings.items():
                    if key not in saved_settings:
                        saved_settings[key] = value
                return saved_settings
        except Exception:
            pass
    return default_settings

def save_settings(settings):
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)

class CursorOverlay(QtWidgets.QWidget):
    def __init__(self, cursor_img_path, sound_click_path, sound_loop_path, settings, on_close_callback=None, on_cursor_change=None, screen=None):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground, True)
        self.setAttribute(QtCore.Qt.WA_ShowWithoutActivating)
        self.setCursor(QtCore.Qt.BlankCursor)

        if os.path.exists('icon.ico'):
            self.setWindowIcon(QtGui.QIcon('icon.ico'))

        self.cursor_img_path = cursor_img_path
        self.update_cursor_image()

        self.cursor_pos = QtGui.QCursor.pos()
        self.rotation = 0
        
        self.screen = screen
        self.setup_screen(screen)
        
        self.mouse_down = False
        self.settings = settings
        self.on_close_callback = on_close_callback
        self.on_cursor_change = on_cursor_change

        self.active_click_players = []
        self.sound_click_path = sound_click_path
        self.player_loop = QtMultimedia.QMediaPlayer()
        self.player_loop.setMedia(QtMultimedia.QMediaContent(QtCore.QUrl.fromLocalFile(sound_loop_path)))
        self.player_loop.setVolume(self.settings['volume'])
        self.player_loop.mediaStatusChanged.connect(self.loop_sound_if_needed)
        self._closed = False

        self.poll_timer = QtCore.QTimer(self)
        self.poll_timer.timeout.connect(self.poll_mouse)
        self.poll_timer.start(10)
        self._last_mouse_down = False

    def setup_screen(self, screen=None):
        if screen:
            self.setGeometry(screen.geometry())
        else:
            primary_screen = QtWidgets.QApplication.primaryScreen()
            self.setGeometry(primary_screen.geometry())
        
        self.showFullScreen()

    def update_cursor_image(self):
        orig_pixmap = QtGui.QPixmap(self.cursor_img_path)
        w = int(orig_pixmap.width() * CURSOR_SCALE)
        h = int(orig_pixmap.height() * CURSOR_SCALE)
        scaled_pixmap = orig_pixmap.scaled(w, h, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        scaled_pixmap = scaled_pixmap.transformed(QtGui.QTransform().scale(-1, 1))
        self.cursor_img = scaled_pixmap

    def change_cursor(self, cursor_img_path):
        self.cursor_img_path = cursor_img_path
        self.update_cursor_image()
        self.update()

    def set_volume(self, volume):
        for player in self.active_click_players:
            player.setVolume(volume)
        self.player_loop.setVolume(volume)

    def get_relative_cursor_pos(self):
        global_pos = QtGui.QCursor.pos()
        if self.screen:
            screen_geometry = self.screen.geometry()
            relative_x = global_pos.x() - screen_geometry.x()
            relative_y = global_pos.y() - screen_geometry.y()
            return QtCore.QPoint(relative_x, relative_y)
        else:
            return global_pos

    def poll_mouse(self):
        if self._closed or not self.isVisible():
            return
        pos = self.get_relative_cursor_pos()
        if pos != self.cursor_pos:
            self.cursor_pos = pos
            self.update()
        buttons = QtWidgets.QApplication.mouseButtons()
        left_down = bool(buttons & QtCore.Qt.LeftButton)
        if left_down and not self._last_mouse_down:
            self.handle_mouse_press()
        elif not left_down and self._last_mouse_down:
            self.handle_mouse_release()
        self._last_mouse_down = left_down

    def handle_mouse_press(self):
        player = QtMultimedia.QMediaPlayer()
        player.setMedia(QtMultimedia.QMediaContent(QtCore.QUrl.fromLocalFile(self.sound_click_path)))
        player.setVolume(self.settings['volume'])
        player.mediaStatusChanged.connect(lambda status, p=player: self.cleanup_click_player(status, p))
        self.active_click_players.append(player)
        player.play()
        self.rotation = -15
        self.update()
        self.mouse_down = True
        self.player_loop.stop()
        self.player_loop.play()

    def cleanup_click_player(self, status, player):
        if status == QtMultimedia.QMediaPlayer.EndOfMedia:
            if player in self.active_click_players:
                self.active_click_players.remove(player)
                player.deleteLater()

    def handle_mouse_release(self):
        self.mouse_down = False
        self.player_loop.stop()
        self.rotation = 0
        self.update()

    def loop_sound_if_needed(self, status):
        if status == QtMultimedia.QMediaPlayer.EndOfMedia and self.mouse_down:
            self.player_loop.stop()
            self.player_loop.play()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.translate(self.cursor_pos.x(), self.cursor_pos.y())
        painter.rotate(self.rotation)
        painter.drawPixmap(-self.cursor_img.width() // 2, -self.cursor_img.height() // 2, self.cursor_img)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close_overlay()

    def close_overlay(self):
        if self._closed:
            return
        self._closed = True
        self.player_loop.stop()
        self.poll_timer.stop()
        for player in self.active_click_players:
            player.stop()
            player.deleteLater()
        self.active_click_players.clear()
        if self.on_close_callback:
            self.on_close_callback()
        self.close()

class PointerApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Pointer')
        
        if os.path.exists('icon.ico'):
            self.setWindowIcon(QtGui.QIcon('icon.ico'))
        
        self.settings = load_settings()
        self.selected_cursor_index = 0
        self.overlay = None
        self.init_ui()
        self.apply_dark_theme()
        self.resize(550, 600)

    def init_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        title = QtWidgets.QLabel('<h1 style="color: #2a82da; margin: 0;">👆 Pointer</h1>')
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet('font-size: 24px; font-weight: bold; margin-bottom: 10px;')
        main_layout.addWidget(title)

        cursor_group = QtWidgets.QGroupBox("Выбор указки")
        cursor_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #f0f0f0;
                border: 2px solid #2a82da;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        cursor_layout = QtWidgets.QHBoxLayout(cursor_group)
        cursor_layout.setSpacing(15)
        
        self.cursor_buttons = []
        for i, (name, filename) in enumerate(CURSORS):
            btn = QtWidgets.QPushButton()
            btn.setCheckable(True)
            btn.setAutoExclusive(True)
            pix = QtGui.QPixmap(os.path.join(ASSETS_PATH, filename)).scaled(80, 80, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            pix = pix.transformed(QtGui.QTransform().scale(-1, 1))
            btn.setIcon(QtGui.QIcon(pix))
            btn.setIconSize(QtCore.QSize(80, 80))
            btn.setFixedSize(100, 100)
            btn.setToolTip(name)
            btn.setStyleSheet("""
                QPushButton {
                    background: #31363b;
                    border: 3px solid #2a82da;
                    border-radius: 8px;
                    padding: 5px;
                }
                QPushButton:checked {
                    border-color: #4a9eea;
                    background: #2a82da;
                }
                QPushButton:hover {
                    border-color: #4a9eea;
                    background: #3a3f44;
                }
            """)
            if i == self.selected_cursor_index:
                btn.setChecked(True)
            btn.clicked.connect(lambda checked, idx=i: self.select_cursor(idx))
            self.cursor_buttons.append(btn)
            cursor_layout.addWidget(btn)
        
        main_layout.addWidget(cursor_group)

        self.start_btn = QtWidgets.QPushButton('🚀 Включить указку')
        self.start_btn.setFixedHeight(50)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background: linear-gradient(135deg, #2a82da, #1e6bb8);
                color: white;
                border: 3px solid #4a9eea;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background: linear-gradient(135deg, #1e6bb8, #2a82da);
                border-color: #5ab0fa;
            }
            QPushButton:pressed {
                background: linear-gradient(135deg, #1a5a9e, #1e6bb8);
            }
        """)
        self.start_btn.clicked.connect(self.start_pointer)
        main_layout.addWidget(self.start_btn)

        settings_group = QtWidgets.QGroupBox("Настройки")
        settings_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #f0f0f0;
                border: 2px solid #2a82da;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        settings_layout = QtWidgets.QVBoxLayout(settings_group)
        settings_layout.setSpacing(15)
        
        volume_layout = QtWidgets.QHBoxLayout()
        volume_label = QtWidgets.QLabel("🔊 Громкость:")
        volume_label.setFixedWidth(100)
        volume_label.setStyleSheet("color: #f0f0f0; font-weight: bold;")
        
        self.volume_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(self.settings['volume'])
        self.volume_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #444;
                height: 10px;
                background: #31363b;
                margin: 2px 0;
                border-radius: 5px;
            }
            QSlider::handle:horizontal {
                background: #2a82da;
                border: 2px solid #4a9eea;
                width: 20px;
                margin: -5px 0;
                border-radius: 10px;
            }
            QSlider::sub-page:horizontal {
                background: #2a82da;
                border-radius: 5px;
            }
        """)
        self.volume_slider.valueChanged.connect(self.on_volume_changed)
        
        self.volume_value = QtWidgets.QLabel(f"{self.settings['volume']}%")
        self.volume_value.setFixedWidth(50)
        self.volume_value.setStyleSheet("color: #f0f0f0; font-weight: bold;")
        
        volume_layout.addWidget(volume_label)
        volume_layout.addWidget(self.volume_slider)
        volume_layout.addWidget(self.volume_value)
        settings_layout.addLayout(volume_layout)
        
        screen_layout = QtWidgets.QHBoxLayout()
        screen_label = QtWidgets.QLabel("🖥️ Монитор:")
        screen_label.setFixedWidth(100)
        screen_label.setStyleSheet("color: #f0f0f0; font-weight: bold;")
        
        self.screen_combo = QtWidgets.QComboBox()
        screens = QtWidgets.QApplication.screens()
        for i, screen in enumerate(screens):
            screen_name = f"Монитор {i+1}"
            if screen == QtWidgets.QApplication.primaryScreen():
                screen_name += " (основной)"
            self.screen_combo.addItem(screen_name)
        
        selected_screen = min(self.settings['selected_screen'], len(screens) - 1)
        self.screen_combo.setCurrentIndex(selected_screen)
        self.screen_combo.currentIndexChanged.connect(self.on_screen_changed)
        self.screen_combo.setStyleSheet("""
            QComboBox {
                background: #31363b;
                color: #f0f0f0;
                border: 2px solid #2a82da;
                border-radius: 6px;
                padding: 5px;
                font-weight: bold;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #2a82da;
            }
            QComboBox QAbstractItemView {
                background: #31363b;
                color: #f0f0f0;
                border: 2px solid #2a82da;
                selection-background-color: #2a82da;
            }
        """)
        
        screen_layout.addWidget(screen_label)
        screen_layout.addWidget(self.screen_combo)
        screen_layout.addStretch()
        settings_layout.addLayout(screen_layout)
        main_layout.addWidget(settings_group)

        info_layout = QtWidgets.QVBoxLayout()
        
        tips_label = QtWidgets.QLabel("💡 Подсказки:")
        tips_label.setStyleSheet("color: #2a82da; font-weight: bold; font-size: 14px;")
        info_layout.addWidget(tips_label)
        
        tips_text = QtWidgets.QLabel("• ESC - выключить указку")
        tips_text.setStyleSheet("color: #888; font-size: 12px; margin-left: 10px;")
        info_layout.addWidget(tips_text)
        
        main_layout.addLayout(info_layout)

        github_btn = QtWidgets.QPushButton("GitHub")
        github_btn.setFixedSize(80, 35)
        github_btn.setToolTip("GitHub")
        github_btn.clicked.connect(lambda: QtGui.QDesktopServices.openUrl(QtCore.QUrl("https://github.com/dreamtydev")))
        github_btn.setStyleSheet("""
            QPushButton {
                background: #31363b;
                color: #f0f0f0;
                border: 2px solid #2a82da;
                border-radius: 6px;
                padding: 8px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                border-color: #4a9eea;
                background: #3a3f44;
            }
            QPushButton:pressed {
                background: #2a82da;
                color: #fff;
            }
        """)
        
        github_layout = QtWidgets.QHBoxLayout()
        github_layout.addWidget(github_btn)
        github_layout.addStretch()
        main_layout.addLayout(github_layout)
        
        self.setLayout(main_layout)

    def select_cursor(self, idx):
        self.selected_cursor_index = idx
        for i, btn in enumerate(self.cursor_buttons):
            btn.setChecked(i == idx)
        if self.overlay and self.overlay.isVisible():
            name, filename = CURSORS[idx]
            img_path = os.path.join(ASSETS_PATH, filename)
            self.overlay.change_cursor(img_path)

    def start_pointer(self):
        if self.overlay:
            self.overlay.close_overlay()
            self.overlay = None
        name, filename = CURSORS[self.selected_cursor_index]
        img_path = os.path.join(ASSETS_PATH, filename)
        
        screens = QtWidgets.QApplication.screens()
        selected_screen_index = min(self.settings['selected_screen'], len(screens) - 1)
        selected_screen = screens[selected_screen_index]
        
        self.overlay = CursorOverlay(
            img_path, SOUND_CLICK, SOUND_LOOP, self.settings, 
            self.on_overlay_close, self.on_cursor_change, selected_screen
        )
        self.overlay.show()

    def toggle_pointer(self):
        if self.overlay:
            self.overlay.close_overlay()
            self.overlay = None
        else:
            self.start_pointer()

    def on_overlay_close(self):
        if self.overlay:
            self.overlay.close()
        self.overlay = None

    def on_cursor_change(self, cursor_index):
        self.selected_cursor_index = cursor_index
        for i, btn in enumerate(self.cursor_buttons):
            btn.setChecked(i == cursor_index)

    def on_volume_changed(self, value):
        self.settings['volume'] = value
        self.volume_value.setText(f"{value}%")
        save_settings(self.settings)
        if self.overlay:
            self.overlay.set_volume(value)

    def on_screen_changed(self, index):
        self.settings['selected_screen'] = index
        save_settings(self.settings)
        if self.overlay:
            self.overlay.close_overlay()
            self.overlay = None
            self.start_pointer()

    def apply_dark_theme(self):
        dark_qss = """
        QWidget { 
            background: #232629; 
            color: #f0f0f0; 
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        QMainWindow, QDialog { 
            background: #232629; 
        }
        QGroupBox {
            color: #f0f0f0;
            background: #2a2e32;
            border: 2px solid #2a82da;
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
            color: #f0f0f0;
        }
        QLabel {
            color: #f0f0f0;
        }
        QMenuBar {
            background: #232629;
            color: #f0f0f0;
            border: none;
        }
        QMenuBar::item {
            background: transparent;
            color: #f0f0f0;
            padding: 4px 8px;
        }
        QMenuBar::item:selected {
            background: #2a82da;
            color: #ffffff;
        }
        QMenu {
            background: #31363b;
            color: #f0f0f0;
            border: 1px solid #444;
        }
        QMenu::item {
            padding: 4px 20px;
        }
        QMenu::item:selected {
            background: #2a82da;
            color: #ffffff;
        }
        QTitleBar {
            background: #232629;
            color: #f0f0f0;
        }
        """
        self.setStyleSheet(dark_qss)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    
    if os.path.exists('icon.ico'):
        app.setWindowIcon(QtGui.QIcon('icon.ico'))
    
    window = PointerApp()
    window.show()
    sys.exit(app.exec_()) 