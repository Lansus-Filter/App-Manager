#----------------------------------------------------------------------

    # Libraries
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from sys import exit
from math import *
import os, json
from datetime import datetime, timedelta
from data.lib import *
#----------------------------------------------------------------------

    # Class
class Application(QBaseApplication):
    BUILD = '07e6d408'
    VERSION = 'Experimental'

    COLOR_LINK = QUtilsColor()

    TIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
    MESSAGE_DURATION = 5000

    ALERT_RAISE_DURATION = 350
    ALERT_PAUSE_DURATION = 2300
    ALERT_FADE_DURATION = 350

    def __init__(self):
        super().__init__()

        self.save_data = SaveData(save_path = os.path.abspath('./data/save.dat').replace('\\', '/'))
        self.must_exit_after_download = False
        self.must_update = False

        InstallButton.platform = PlatformType.Windows
        InstallButton.token = self.save_data.token
        RequestWorker.token = self.save_data.token

        InstalledButton.settings_icon = self.save_data.getIcon('pushbutton/settings.png')
        InstalledButton.remove_from_list_icon = self.save_data.getIcon('popup/removeFromList.png')
        InstalledButton.edit_icon = self.save_data.getIcon('popup/edit.png')
        InstalledButton.show_in_explorer_icon = self.save_data.getIcon('popup/showInExplorer.png')
        InstalledButton.uninstall_icon = self.save_data.getIcon('popup/uninstall.png')

        EditAppDialog.general_tab_icon = self.save_data.getIcon('sidepanel/general.png', False)
        EditAppDialog.advanced_tab_icon = self.save_data.getIcon('sidepanel/advanced.png', False)
        EditAppDialog.updates_tab_icon = self.save_data.getIcon('sidepanel/updates.png', False)
        EditAppDialog.icon_tab_icon = self.save_data.getIcon('sidepanel/icon.png', False)
        EditAppDialog.icon_file_button_icon = self.save_data.getIcon('filebutton/image.png', False)
        EditAppDialog.icon_file_button_icon = self.save_data.getIcon('filebutton/folder.png', False)
        EditAppDialog.icon_path = './data/icons/sample'

        SettingsListNamedItem.remove_icon = self.save_data.getIcon('pushbutton/delete.png')

        self.downloads = {}
        self.uninstalls = {}
        self.updates = {}
        self.is_updating = []

        self.install_page_worker = None
        self.install_page_buttons = [[], []]
        self.app_buttons = {}

        self.save_data.setStyleSheet(self)
        self.window.setProperty('color', 'cyan')

        self.setWindowIcon(QIcon('./data/icons/AppManager.svg'))

        self.create_widgets()
        self.load_colors()
        self.update_title()

        self.check_updates()
        self.refresh_apps()

        self.create_about_menu()
        self.create_tray_icon()

        if self.save_data.check_for_apps_updates == 4: self.install_app_page_refresh_template(True)
        elif self.save_data.check_for_apps_updates > 0 and self.save_data.check_for_apps_updates < 4:
            deltatime = datetime.now() - self.save_data.last_check_for_apps_updates

            match self.save_data.check_for_apps_updates:
                case 1:
                    if deltatime > timedelta(days = 1): self.install_app_page_refresh_template(True)
                case 2:
                    if deltatime > timedelta(weeks = 1): self.install_app_page_refresh_template(True)
                case 3:
                    if deltatime > timedelta(weeks = 4): self.install_app_page_refresh_template(True)

        if self.save_data.check_for_updates == 4: self.check_updates()
        elif self.save_data.check_for_updates > 0 and self.save_data.check_for_updates < 4:
            deltatime = datetime.now() - self.save_data.last_check_for_updates

            match self.save_data.check_for_updates:
                case 1:
                    if deltatime > timedelta(days = 1): self.check_updates()
                case 2:
                    if deltatime > timedelta(weeks = 1): self.check_updates()
                case 3:
                    if deltatime > timedelta(weeks = 4): self.check_updates()

        self.window.setMinimumSize(int(self.primaryScreen().size().width() * (8 / 15)), int(self.primaryScreen().size().height() * (14 / 27))) # 128x71 -> 1022x568



    def update_title(self):
        self.window.setWindowTitle(self.save_data.language_data['QMainWindow']['title'] + f' | Version: {self.VERSION} | Build: {self.BUILD}')

    def load_colors(self):
        qss = QssParser(
            self.save_data.getStyleSheet(app = self, mode = QSaveData.StyleSheetMode.Local) + '\n' +
            self.save_data.getStyleSheet(app = self, mode = QSaveData.StyleSheetMode.Global)
        )

        self.COLOR_LINK = QUtilsColor(
            qss.search(
                QssSelector(widget = 'QLabel', attributes = {'color': self.window.property('color')}, items = ['link'])
            )['color']
        )
        SaveData.COLOR_LINK = self.COLOR_LINK

        QNamedLineEdit.normal_color = qss.search(
            QssSelector(widget = 'QWidget', attributes = {'QNamedLineEdit': True}),
            QssSelector(widget = 'QLabel')
        )['color']
        QNamedLineEdit.hover_color = qss.search(
            QssSelector(widget = 'QWidget', attributes = {'QNamedLineEdit': True}),
            QssSelector(widget = 'QLabel', attributes = {'hover': True})
        )['color']
        QNamedLineEdit.focus_color = qss.search(
            QssSelector(widget = 'QWidget', attributes = {'color': self.window.property('color')}),
            QssSelector(widget = 'QWidget', attributes = {'QNamedLineEdit': True, 'color': 'main'}),
            QssSelector(widget = 'QLabel', attributes = {'focus': True})
        )['color']

        QNamedTextEdit.normal_color = qss.search(
            QssSelector(widget = 'QWidget', attributes = {'QNamedTextEdit': True}),
            QssSelector(widget = 'QLabel')
        )['color']
        QNamedTextEdit.hover_color = qss.search(
            QssSelector(widget = 'QWidget', attributes = {'QNamedTextEdit': True}),
            QssSelector(widget = 'QLabel', attributes = {'hover': True})
        )['color']
        QNamedTextEdit.focus_color = qss.search(
            QssSelector(widget = 'QWidget', attributes = {'color': self.window.property('color')}),
            QssSelector(widget = 'QWidget', attributes = {'QNamedTextEdit': True, 'color': 'main'}),
            QssSelector(widget = 'QLabel', attributes = {'focus': True})
        )['color']

        QNamedComboBox.normal_color = qss.search(
            QssSelector(widget = 'QWidget', attributes = {'QNamedComboBox': True}),
            QssSelector(widget = 'QLabel')
        )['color']
        QNamedComboBox.hover_color = qss.search(
            QssSelector(widget = 'QWidget', attributes = {'QNamedComboBox': True}),
            QssSelector(widget = 'QLabel', attributes = {'hover': True})
        )['color']
        QNamedComboBox.focus_color = qss.search(
            QssSelector(widget = 'QWidget', attributes = {'color': self.window.property('color')}),
            QssSelector(widget = 'QWidget', attributes = {'QNamedComboBox': True, 'color': 'main'}),
            QssSelector(widget = 'QLabel', attributes = {'focus': True})
        )['color']

        QNamedSpinBox.normal_color = qss.search(
            QssSelector(widget = 'QWidget', attributes = {'QNamedSpinBox': True}),
            QssSelector(widget = 'QLabel')
        )['color']
        QNamedSpinBox.hover_color = qss.search(
            QssSelector(widget = 'QWidget', attributes = {'QNamedSpinBox': True}),
            QssSelector(widget = 'QLabel', attributes = {'hover': True})
        )['color']
        QNamedSpinBox.focus_color = qss.search(
            QssSelector(widget = 'QWidget', attributes = {'color': self.window.property('color')}),
            QssSelector(widget = 'QWidget', attributes = {'QNamedSpinBox': True, 'color': 'main'}),
            QssSelector(widget = 'QLabel', attributes = {'focus': True})
        )['color']

        QNamedDoubleSpinBox.normal_color = qss.search(
            QssSelector(widget = 'QWidget', attributes = {'QNamedDoubleSpinBox': True}),
            QssSelector(widget = 'QLabel')
        )['color']
        QNamedDoubleSpinBox.hover_color = qss.search(
            QssSelector(widget = 'QWidget', attributes = {'QNamedDoubleSpinBox': True}),
            QssSelector(widget = 'QLabel', attributes = {'hover': True})
        )['color']
        QNamedDoubleSpinBox.focus_color = qss.search(
            QssSelector(widget = 'QWidget', attributes = {'color': self.window.property('color')}),
            QssSelector(widget = 'QWidget', attributes = {'QNamedDoubleSpinBox': True, 'color': 'main'}),
            QssSelector(widget = 'QLabel', attributes = {'focus': True})
        )['color']

        QFileButton.normal_color = qss.search(
            QssSelector(widget = 'QWidget', attributes = {'QFileButton': True}),
            QssSelector(widget = 'QLabel')
        )['color']
        QFileButton.hover_color = qss.search(
            QssSelector(widget = 'QWidget', attributes = {'QFileButton': True}),
            QssSelector(widget = 'QLabel', attributes = {'hover': True})
        )['color']

        QToggleButton.normal_color = qss.search(
            QssSelector(widget = 'QWidget', attributes = {'QToggleButton': True}),
            QssSelector(widget = 'QCheckBox')
        )['color']
        QToggleButton.normal_color_handle = qss.search(
            QssSelector(widget = 'QWidget', attributes = {'QToggleButton': True}),
            QssSelector(widget = 'QCheckBox', items = ['handle'])
        )['color']
        QToggleButton.checked_color = qss.search(
            QssSelector(widget = 'QWidget', attributes = {'color': self.window.property('color')}),
            QssSelector(widget = 'QWidget', attributes = {'QToggleButton': True}),
            QssSelector(widget = 'QCheckBox', states = ['checked'])
        )['color']
        QToggleButton.checked_color_handle = qss.search(
            QssSelector(widget = 'QWidget', attributes = {'QToggleButton': True}),
            QssSelector(widget = 'QCheckBox', states = ['checked'], items = ['handle'])
        )['color']



    def settings_menu(self):
        self.save_data.settings_menu(self)
        self.load_colors()
        self.refresh_apps()



    def not_implemented(self, text = ''):
        if text:
            w = QDropDownWidget(text = lang['details'], widget = QLabel(text))
        else: w = None

        lang = self.save_data.language_data['QMessageBox']['critical']['notImplemented']

        QMessageBoxWithWidget(
            app = self,
            title = lang['title'],
            text = lang['text'],
            icon = QMessageBoxWithWidget.Icon.Critical,
            widget = w
        ).exec()

    def create_widgets(self):
        self.root = QGridWidget()
        self.root.grid_layout.setSpacing(0)
        self.root.grid_layout.setContentsMargins(0, 0, 0, 0)

        self.window.setCentralWidget(self.root)

        self.create_main_page()
        self.create_install_app_page()



    def create_main_page(self):
        self.main_page = QGridWidget()
        self.root.grid_layout.addWidget(self.main_page, 0, 0)

        self.main_page.left = QGridWidget()
        self.main_page.left.grid_layout.setSpacing(0)
        self.main_page.left.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.main_page.grid_layout.addWidget(self.main_page.left, 0, 0)
        self.main_page.grid_layout.setSpacing(0)
        self.main_page.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.main_page.grid_layout.setAlignment(self.main_page.left, Qt.AlignmentFlag.AlignLeft)

        self.main_page.right = QGridWidget()
        self.main_page.grid_layout.addWidget(self.main_page.right, 0, 1)
        self.main_page.right.grid_layout.setRowStretch(0, 1)
        self.main_page.right.grid_layout.setColumnStretch(0, 1)

        self.create_apps_widget()
        self.create_downloads_widget()

        left_top = QFrame()
        left_top.grid_layout = QGridLayout()
        left_top.setLayout(left_top.grid_layout)
        left_top.setProperty('border-top', True)
        left_top.setProperty('border-left', True)
        left_top.setProperty('border-right', True)
        left_top.setProperty('background', 'light')
        self.main_page.left.grid_layout.addWidget(left_top, 0, 0)

        button = QPushButton()
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setIcon(self.save_data.getIcon('/pushbutton/note.png'))
        button.clicked.connect(self.about_menu_clicked)
        left_top.grid_layout.addWidget(button, 0, 0)
        left_top.grid_layout.setAlignment(button, Qt.AlignmentFlag.AlignLeft)

        button = QPushButton()
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setIcon(self.save_data.getIcon('/pushbutton/settings.png'))
        button.clicked.connect(self.settings_menu)
        left_top.grid_layout.addWidget(button, 0, 1)
        left_top.grid_layout.setAlignment(button, Qt.AlignmentFlag.AlignRight)

        self.main_page.side_panel = QSidePanel(None, 240)
        self.main_page.side_panel.setProperty('border-right', True)
        self.main_page.left.grid_layout.addWidget(self.main_page.side_panel, 1, 0)
        self.main_page.side_panel.add_items([
            QSidePanelItem(self.save_data.language_data['QMainWindow']['mainPage']['QSidePanel']['apps']['title'], f'{self.save_data.getIconsDir()}/sidepanel/apps.png', self.panel_select_apps),
            QSidePanelItem(self.save_data.language_data['QMainWindow']['mainPage']['QSidePanel']['downloads']['title'], f'{self.save_data.getIconsDir()}/sidepanel/downloads.png', self.panel_select_downloads),
        ])
        self.panel_select_apps()


    def create_apps_widget(self):
        self.main_page.apps_widget = QGridWidget()

        self.main_page.apps_widget.top = QGridWidget()
        self.main_page.apps_widget.grid_layout.addWidget(self.main_page.apps_widget.top, 0, 0)
        self.main_page.apps_widget.grid_layout.setAlignment(self.main_page.apps_widget.top, Qt.AlignmentFlag.AlignTop)

        label = QLabel(self.save_data.language_data['QMainWindow']['mainPage']['QSidePanel']['apps']['title'])
        label.setProperty('h', '1')
        self.main_page.apps_widget.top.grid_layout.addWidget(label, 0, 0)
        self.main_page.apps_widget.top.grid_layout.setAlignment(label, Qt.AlignmentFlag.AlignLeft)

        right_buttons = QGridWidget()
        self.main_page.apps_widget.top.grid_layout.addWidget(right_buttons, 0, 1, 2, 1)
        self.main_page.apps_widget.top.grid_layout.setAlignment(right_buttons, Qt.AlignmentFlag.AlignRight)

        button = QPushButton(self.save_data.language_data['QMainWindow']['mainPage']['QSidePanel']['apps']['QPushButton']['locate'])
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.clicked.connect(self.locate_app_click)
        button.setProperty('color', 'gray')
        right_buttons.grid_layout.addWidget(button, 0, 1)

        button = QPushButton(self.save_data.language_data['QMainWindow']['mainPage']['QSidePanel']['apps']['QPushButton']['installApp'])
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.clicked.connect(self.install_app_click)
        button.setProperty('color', 'main')
        right_buttons.grid_layout.addWidget(button, 0, 2)

        right_buttons.grid_layout.setRowStretch(2, 1)
        right_buttons.grid_layout.setColumnStretch(2, 1)

        self.main_page.apps_widget.searchbar = QIconLineEdit(icon = f'{self.save_data.getIconsDir()}lineedit/search.png')
        self.main_page.apps_widget.searchbar.setPlaceholderText(self.save_data.language_data['QMainWindow']['mainPage']['QSidePanel']['apps']['QLineEdit']['search'])
        self.main_page.apps_widget.searchbar.textChanged.connect(self.refresh_apps_list)
        right_buttons.grid_layout.addWidget(self.main_page.apps_widget.searchbar, 1, 1, 1, 2)
        right_buttons.grid_layout.setAlignment(self.main_page.apps_widget.searchbar, Qt.AlignmentFlag.AlignTop)

        self.main_page.apps_widget.notebook = QTabWidget()
        self.main_page.apps_widget.notebook.tabBar().setProperty('color', 'main')
        self.main_page.apps_widget.notebook.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.main_page.apps_widget.notebook.tabBar().setCursor(Qt.CursorShape.PointingHandCursor)
        self.main_page.apps_widget.grid_layout.addWidget(self.main_page.apps_widget.notebook, 2, 0)

        self.main_page.apps_widget.notebook_tabs = QScrollableGridWidget()
        self.main_page.apps_widget.grid_layout.addWidget(self.main_page.apps_widget.notebook_tabs, 3, 0)
        self.main_page.apps_widget.notebook_tabs.scroll_layout.setAlignment(self.main_page.apps_widget.notebook_tabs, Qt.AlignmentFlag.AlignTop)
        self.main_page.apps_widget.notebook_tabs.scroll_layout.setSpacing(1)

        widget = QWidget()
        widget.setFixedHeight(1)
        self.main_page.apps_widget.notebook.addTab(widget, self.save_data.language_data['QMainWindow']['mainPage']['QSidePanel']['apps']['QTabWidget']['all'])

        widget = QWidget()
        widget.setFixedHeight(1)
        self.main_page.apps_widget.notebook.addTab(widget, self.save_data.language_data['QMainWindow']['mainPage']['QSidePanel']['apps']['QTabWidget']['official'])

        widget = QWidget()
        widget.setFixedHeight(1)
        self.main_page.apps_widget.notebook.addTab(widget, self.save_data.language_data['QMainWindow']['mainPage']['QSidePanel']['apps']['QTabWidget']['pre'])

        widget = QWidget()
        widget.setFixedHeight(1)
        self.main_page.apps_widget.notebook.addTab(widget, self.save_data.language_data['QMainWindow']['mainPage']['QSidePanel']['apps']['QTabWidget']['custom'])

        self.main_page.apps_widget.notebook.currentChanged.connect(self.refresh_apps_list)

        self.main_page.right.grid_layout.addWidget(self.main_page.apps_widget, 0, 0)
        self.main_page.apps_widget.setVisible(False)


    def create_downloads_widget(self):
        self.main_page.downloads_widget = QGridWidget()

        self.main_page.downloads_widget.top = QGridWidget()
        self.main_page.downloads_widget.grid_layout.addWidget(self.main_page.downloads_widget.top, 0, 0)
        self.main_page.downloads_widget.grid_layout.setAlignment(self.main_page.downloads_widget.top, Qt.AlignmentFlag.AlignTop)

        label = QLabel(self.save_data.language_data['QMainWindow']['mainPage']['QSidePanel']['downloads']['title'])
        label.setProperty('h', '1')
        self.main_page.downloads_widget.top.grid_layout.addWidget(label, 0, 0)
        self.main_page.downloads_widget.top.grid_layout.setAlignment(label, Qt.AlignmentFlag.AlignLeft)

        self.main_page.downloads_widget.list = QScrollableGridWidget()
        self.main_page.downloads_widget.grid_layout.addWidget(self.main_page.downloads_widget.list, 1, 0, 1, 2)
        self.main_page.downloads_widget.list.setVisible(False)


        self.main_page.downloads_widget.no_download = QGridWidget()

        label = QLabel()
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setProperty('normal', True)
        label.setPixmap(QPixmap(f'{self.save_data.getIconsDir()}/download/dl.png'))
        label.setPixmap(label.pixmap().scaledToHeight(64, Qt.TransformationMode.SmoothTransformation))
        self.main_page.downloads_widget.no_download.grid_layout.addWidget(label, 0, 0)
        self.main_page.downloads_widget.no_download.grid_layout.setAlignment(label, Qt.AlignmentFlag.AlignCenter)

        label = QLabel(self.save_data.language_data['QMainWindow']['mainPage']['QSidePanel']['downloads']['QLabel']['noDownload']['title'])
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setProperty('title', True)
        self.main_page.downloads_widget.no_download.grid_layout.addWidget(label, 1, 0)
        self.main_page.downloads_widget.no_download.grid_layout.setAlignment(label, Qt.AlignmentFlag.AlignCenter)

        label = QLabel(self.save_data.language_data['QMainWindow']['mainPage']['QSidePanel']['downloads']['QLabel']['noDownload']['text'])
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setProperty('normal', True)
        self.main_page.downloads_widget.no_download.grid_layout.addWidget(label, 2, 0)
        self.main_page.downloads_widget.no_download.grid_layout.setAlignment(label, Qt.AlignmentFlag.AlignCenter)

        self.main_page.downloads_widget.grid_layout.addWidget(self.main_page.downloads_widget.no_download, 1, 0, 1, 2)
        self.main_page.downloads_widget.no_download.grid_layout.setSpacing(3)
        self.main_page.downloads_widget.no_download.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.main_page.downloads_widget.no_download.grid_layout.setRowStretch(3, 1)

        self.main_page.right.grid_layout.addWidget(self.main_page.downloads_widget, 0, 0)
        self.main_page.downloads_widget.setVisible(False)


    def create_install_app_page(self):
        self.install_app_page = QGridWidget()
        self.root.grid_layout.addWidget(self.install_app_page, 0, 0)
        self.install_app_page.grid_layout.setSpacing(0)
        self.install_app_page.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.install_app_page.setVisible(False)

        self.install_app_page.top = QGridFrame()
        self.install_app_page.grid_layout.addWidget(self.install_app_page.top, 0, 0)
        self.install_app_page.top.setProperty('border-top', True)
        self.install_app_page.top.setProperty('border-left', True)
        self.install_app_page.top.setProperty('border-right', True)
        self.install_app_page.top.grid_layout.setSpacing(0)
        self.install_app_page.top.grid_layout.setContentsMargins(16, 16, 16, 0)

        label = QLabel(self.save_data.language_data['QMainWindow']['installAppPage']['QLabel']['installApp'])
        label.setProperty('h', '4')
        label.setProperty('bigbrighttitle', True)
        self.install_app_page.top.grid_layout.addWidget(label, 0, 0)
        self.install_app_page.top.grid_layout.setAlignment(label, Qt.AlignmentFlag.AlignTop)

        frame = QGridFrame()
        frame.grid_layout.setSpacing(20)
        frame.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.install_app_page.top.grid_layout.addWidget(frame, 1, 1)
        self.install_app_page.top.grid_layout.setAlignment(frame, Qt.AlignmentFlag.AlignRight)

        button = QPushButton()
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setIcon(self.save_data.getIcon('pushbutton/refresh.png'))
        button.setProperty('color', 'main')
        button.clicked.connect(lambda: self.install_app_page_refresh_template(True))
        frame.grid_layout.addWidget(button, 0, 0)

        self.install_app_page.top.searchbar = QIconLineEdit(icon = f'{self.save_data.getIconsDir()}lineedit/search.png')
        self.install_app_page.top.searchbar.setPlaceholderText(self.save_data.language_data['QMainWindow']['installAppPage']['QLineEdit']['search'])
        self.install_app_page.top.searchbar.textChanged.connect(self.refresh_install_apps_list)
        frame.grid_layout.addWidget(self.install_app_page.top.searchbar, 0, 1)


        self.install_app_page.middle = QGridFrame()
        self.install_app_page.grid_layout.addWidget(self.install_app_page.middle, 1, 0)
        self.install_app_page.middle.setProperty('border-bottom', True)
        self.install_app_page.middle.setProperty('border-left', True)
        self.install_app_page.middle.setProperty('border-right', True)

        self.install_app_page.tab_widget = QTabWidget()
        self.install_app_page.tab_widget.tabBar().setProperty('color', 'main')
        self.install_app_page.tab_widget.tabBar().setCursor(Qt.CursorShape.PointingHandCursor)
        self.install_app_page.middle.grid_layout.addWidget(self.install_app_page.tab_widget, 0, 0)
        self.install_app_page.middle.grid_layout.setSpacing(0)
        self.install_app_page.middle.grid_layout.setContentsMargins(0, 0, 0, 0)


        self.install_app_page.tab_widget.official = QGridFrame()
        self.install_app_page.tab_widget.official.setProperty('border-top', True)
        self.install_app_page.tab_widget.official.grid_layout.setSpacing(0)
        self.install_app_page.tab_widget.official.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.install_app_page.tab_widget.official.inside = QScrollableGridWidget()
        self.install_app_page.tab_widget.official.grid_layout.addWidget(self.install_app_page.tab_widget.official.inside, 0, 0)
        self.install_app_page.tab_widget.official.inside.scroll_layout.setSpacing(1)
        self.install_app_page.tab_widget.official.inside.scroll_layout.setContentsMargins(16, 16, 16, 16)

        self.install_app_page.tab_widget.pre = QGridFrame()
        self.install_app_page.tab_widget.pre.setProperty('border-top', True)
        self.install_app_page.tab_widget.pre.grid_layout.setSpacing(0)
        self.install_app_page.tab_widget.pre.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.install_app_page.tab_widget.pre.inside = QScrollableGridWidget()
        self.install_app_page.tab_widget.pre.grid_layout.addWidget(self.install_app_page.tab_widget.pre.inside, 0, 0)
        self.install_app_page.tab_widget.pre.inside.scroll_layout.setSpacing(1)
        self.install_app_page.tab_widget.pre.inside.scroll_layout.setContentsMargins(16, 16, 16, 16)

        self.install_app_page.tab_widget.addTab(self.install_app_page.tab_widget.official, self.save_data.language_data['QMainWindow']['installAppPage']['QTabWidget']['officialReleases']['title'])
        self.install_app_page.tab_widget.addTab(self.install_app_page.tab_widget.pre, self.save_data.language_data['QMainWindow']['installAppPage']['QTabWidget']['preReleases']['title'])



        self.install_app_page.bottom = QGridFrame()
        self.install_app_page.grid_layout.addWidget(self.install_app_page.bottom, 2, 0)
        self.install_app_page.bottom.setProperty('border-bottom', True)
        self.install_app_page.bottom.setProperty('border-left', True)
        self.install_app_page.bottom.setProperty('border-right', True)
        
        self.install_app_page.bottom.grid_layout.setSpacing(0)
        self.install_app_page.bottom.grid_layout.setContentsMargins(0, 0, 0, 0)

        right_buttons = QGridWidget()
        self.install_app_page.bottom.grid_layout.addWidget(right_buttons, 0, 0)

        button = QPushButton(self.save_data.language_data['QMainWindow']['installAppPage']['QPushButton']['goToDownloadPage'])
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.clicked.connect(self.panel_select_downloads)
        button.setProperty('color', 'main')
        button.setProperty('transparent', True)
        right_buttons.grid_layout.addWidget(button, 0, 0)
        right_buttons.grid_layout.setAlignment(button, Qt.AlignmentFlag.AlignLeft)

        button = QPushButton(self.save_data.language_data['QMainWindow']['installAppPage']['QPushButton']['back'])
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.clicked.connect(self.main_page_click)
        button.setProperty('color', 'white')
        button.setProperty('transparent', True)
        right_buttons.grid_layout.addWidget(button, 0, 1)
        right_buttons.grid_layout.setAlignment(button, Qt.AlignmentFlag.AlignRight)


    def install_app_page_refresh_template(self, force: bool = False) -> None:
        if not self.install_page_worker: force = True
        if not force:
            if datetime.now() < self.install_page_worker.time + timedelta(hours = 1): return # Happened in the last hour

        if self.install_page_worker:
            if self.install_page_worker.isRunning():
                self.install_page_worker.terminate()

        self.install_page_buttons = [[], []]
        self.clear_layout(self.install_app_page.tab_widget.official.inside.scroll_layout)
        self.clear_layout(self.install_app_page.tab_widget.pre.inside.scroll_layout)

        followed_apps_to_update = []
        followed_apps_not_installed = []

        for fapp in self.save_data.followed_apps:
            name = fapp.split('/')[-1].replace('-', ' ')
            app_is_installed = False

            for app in self.save_data.apps['official'] + self.save_data.apps['pre']:
                if app.split('/')[-1] == name:
                    app_is_installed = True

                    with open(f'{app}/manifest.json', 'r') as infile:
                        manifest = json.load(infile)

                    if manifest['checkForUpdates'] == 4: followed_apps_to_update.append(fapp)
                    elif manifest['checkForUpdates'] > 0 and manifest['checkForUpdates'] < 4:
                        deltatime = datetime.now() - manifest['lastCheckForUpdates']

                        match manifest['checkForUpdates']:
                            case 1:
                                if deltatime > timedelta(days = 1): followed_apps_to_update.append(fapp)
                            case 2:
                                if deltatime > timedelta(weeks = 1): followed_apps_to_update.append(fapp)
                            case 3:
                                if deltatime > timedelta(weeks = 4): followed_apps_to_update.append(fapp)

                    break
            if not app_is_installed: followed_apps_not_installed.append(fapp)

        self.install_page_worker = RequestWorker(followed_apps_not_installed + followed_apps_to_update, self.save_data.apps_folder)
        self.install_page_worker.signals.received.connect(self.release_received)
        self.install_page_worker.signals.failed.connect(self.release_failed)
        self.install_page_worker.start()

        self.save_data.last_check_for_apps_updates = datetime.now()

    def get_installed_releases(self) -> list[str]:
        return [folder.split('/')[-1] for k in ['official', 'pre'] for folder in self.save_data.apps[k]]

    def install_app_page_refresh_buttons(self) -> None:
        installed_releases = self.get_installed_releases()
        for button in self.install_page_buttons[0] + self.install_page_buttons[1]:
            button.set_disabled(button.name in installed_releases)

    def release_received(self, rel: dict) -> None:
        installed_releases = self.get_installed_releases()
        icon = './data/icons/questionMark.svg'
        button = InstallButton(rel, self.save_data.language_data['QMainWindow']['installAppPage']['QPushButton']['install'], rel['name'], rel['tag_name'], icon, f'{rel["name"]}' in installed_releases or f'{rel["name"]}' in list(self.downloads.keys()) + [j.split('/')[-1] for j in list(self.uninstalls.keys())])
        button.download.connect(self.add_to_download_list)
        if rel['prerelease']: self.install_app_page.tab_widget.pre.inside.scroll_layout.addWidget(button, self.install_app_page.tab_widget.pre.inside.scroll_layout.count(), 0)
        else: self.install_app_page.tab_widget.official.inside.scroll_layout.addWidget(button, self.install_app_page.tab_widget.official.inside.scroll_layout.count(), 0)
        self.install_page_buttons[int(rel['prerelease'])].append(button)

        if not (rel['name'] in installed_releases and os.path.exists(os.path.join(self.save_data.apps_folder, rel['name'], 'manifest.json'))): return
        with open(os.path.join(self.save_data.apps_folder, rel['name'], 'manifest.json'), 'r', encoding = 'utf-8') as f:
            manifest = json.load(f)

        if datetime.strptime(manifest['created_at'], self.TIME_FORMAT) >= datetime.strptime(rel['created_at'], self.TIME_FORMAT): return
        match manifest['release']:
            case 'official':
                if rel['prerelease']: return

            case 'pre': pass

            case _: return

        self.updates[rel['name']] = InstallButton.get_release(InstallButton.platform, rel, self.save_data.token)
        self.refresh_apps()

    def release_failed(self, error: str) -> None:
        if self.save_data.request_worker_failed_notif: self.sys_tray.showMessage(
            self.save_data.language_data['QSystemTrayIcon']['showMessage']['requestWorkerFailed']['title'],
            self.save_data.language_data['QSystemTrayIcon']['showMessage']['requestWorkerFailed']['message'].replace('%s', error),
            QSystemTrayIcon.MessageIcon.Critical,
            self.MESSAGE_DURATION
        )
        self.show_alert(
            message = self.save_data.language_data['QSystemTrayIcon']['showMessage']['requestWorkerFailed']['message'].replace('%s', error),
            raise_duration = self.ALERT_RAISE_DURATION,
            pause_duration = self.ALERT_PAUSE_DURATION,
            fade_duration = self.ALERT_FADE_DURATION,
            color = 'main'
        )


    def add_to_download_list(self, data: InstallButton.download_data):
        if len(list(self.downloads.keys())) == 0:
            self.main_page.downloads_widget.no_download.setVisible(False)
            self.main_page.downloads_widget.list.setVisible(True)

        iw = Installer(None, self.save_data.language_data['QMainWindow']['mainPage']['QSidePanel']['downloads'], data, self.save_data.downloads_folder, self.save_data.apps_folder)
        self.main_page.downloads_widget.list.scroll_layout.addWidget(iw, len(list(self.downloads.keys())), 0)
        self.main_page.downloads_widget.list.scroll_layout.setAlignment(iw, Qt.AlignmentFlag.AlignTop)
        iw.done.connect(self.remove_from_download_list)
        iw.failed.connect(self.remove_from_download_list)
        self.downloads[f'{data.name}'] = iw

        iw.start()

    def remove_from_download_list(self, name: str, error: str = None) -> None:
        self.main_page.downloads_widget.list.scroll_layout.removeWidget(self.downloads[name])
        self.save_data.apps['pre' if self.downloads[name].data.prerelease else 'official'].append(f'{self.save_data.apps_folder}/{name}')
        del self.downloads[name]

        self.refresh_apps()
        self.save_data.save()

        if error:
            if self.save_data.app_install_failed_notif: self.sys_tray.showMessage(
                self.save_data.language_data['QSystemTrayIcon']['showMessage']['appInstallFailed']['title'],
                self.save_data.language_data['QSystemTrayIcon']['showMessage']['appInstallFailed']['message'].replace('%s', name, 1).replace('%s', error),
                QSystemTrayIcon.MessageIcon.Critical,
                self.MESSAGE_DURATION
            )
            self.show_alert(
                message = self.save_data.language_data['QSystemTrayIcon']['showMessage']['appInstallFailed']['message'].replace('%s', name, 1).replace('%s', error),
                raise_duration = self.ALERT_RAISE_DURATION,
                pause_duration = self.ALERT_PAUSE_DURATION,
                fade_duration = self.ALERT_FADE_DURATION,
                color = 'main'
            )
        else:
            if self.save_data.app_install_done_notif: self.sys_tray.showMessage(
                self.save_data.language_data['QSystemTrayIcon']['showMessage']['appInstallDone']['title'],
                self.save_data.language_data['QSystemTrayIcon']['showMessage']['appInstallDone']['message'].replace('%s', name),
                QSystemTrayIcon.MessageIcon.Information,
                self.MESSAGE_DURATION
            )
            self.show_alert(
                self.save_data.language_data['QSystemTrayIcon']['showMessage']['appInstallDone']['message'].replace('%s', name),
                raise_duration = self.ALERT_RAISE_DURATION,
                pause_duration = self.ALERT_PAUSE_DURATION,
                fade_duration = self.ALERT_FADE_DURATION,
                color = 'main'
            )

        if len(list(self.downloads.keys())) == 0:
            self.main_page.downloads_widget.list.setVisible(False)
            self.main_page.downloads_widget.no_download.setVisible(True)

            try: os.rmdir(self.save_data.downloads_folder)
            except: pass

            if self.must_exit_after_download:
                if self.window.isVisible(): self.must_exit_after_download = False
                else: self.exit()

    def remove_from_install_list(self, path: str):
        for i in ['official', 'pre', 'custom']:
            if path in self.save_data.apps[i]: self.save_data.apps[i].remove(path)
        self.refresh_apps()
        self.save_data.save()

    def add_to_uninstall_list(self, path: str):
        self.remove_from_install_list(path)
        self.uninstalls[path] = UninstallWorker(path)
        self.uninstalls[path].signals.done.connect(self.remove_from_uninstall_list)
        self.uninstalls[path].signals.failed.connect(self.remove_from_uninstall_list)
        self.uninstalls[path].start()

    def remove_from_uninstall_list(self, path: str, error: str = None):
        self.uninstalls[path].exit()
        del self.uninstalls[path]
        self.refresh_apps()
        self.install_app_page_refresh_buttons()

        name = path.split('/')[-1]

        if error:
            if self.save_data.app_uninstall_failed_notif: self.sys_tray.showMessage(
                self.save_data.language_data['QSystemTrayIcon']['showMessage']['appUninstallFailed']['title'],
                self.save_data.language_data['QSystemTrayIcon']['showMessage']['appUninstallFailed']['message'].replace('%s', name, 1).replace('%s', error),
                QSystemTrayIcon.MessageIcon.Critical,
                self.MESSAGE_DURATION
            )
            self.show_alert(
                self.save_data.language_data['QSystemTrayIcon']['showMessage']['appUninstallFailed']['message'].replace('%s', name, 1).replace('%s', error),
                raise_duration = self.ALERT_RAISE_DURATION,
                pause_duration = self.ALERT_PAUSE_DURATION,
                fade_duration = self.ALERT_FADE_DURATION,
                color = 'main'
            )
        else:
            if self.save_data.app_uninstall_done_notif: self.sys_tray.showMessage(
                self.save_data.language_data['QSystemTrayIcon']['showMessage']['appUninstallDone']['title'],
                self.save_data.language_data['QSystemTrayIcon']['showMessage']['appUninstallDone']['message'].replace('%s', name),
                QSystemTrayIcon.MessageIcon.Information,
                self.MESSAGE_DURATION
            )
            self.show_alert(
                self.save_data.language_data['QSystemTrayIcon']['showMessage']['appUninstallDone']['message'].replace('%s', name),
                raise_duration = self.ALERT_RAISE_DURATION,
                pause_duration = self.ALERT_PAUSE_DURATION,
                fade_duration = self.ALERT_FADE_DURATION,
                color = 'main'
            )



    def panel_select_apps(self):
        self.main_page.side_panel.set_current_index(0)
        self.main_page.downloads_widget.setVisible(False)
        self.main_page.apps_widget.setVisible(True)

    def panel_select_downloads(self):
        if not self.main_page.isVisible(): self.main_page_click()
        self.main_page.side_panel.set_current_index(1)
        self.main_page.apps_widget.setVisible(False)
        self.main_page.downloads_widget.setVisible(True)


    def main_page_click(self):
        self.install_app_page.setVisible(False)
        self.main_page.setVisible(True)

    def locate_app_click(self):
        path = QFileDialog.getOpenFileName(
            parent = self.window,
            directory = self.save_data.apps_folder,
            caption = self.save_data.language_data['QFileDialog']['locateApp'],
            filter = 'All supported files (*.exe *.bat *.cmd manifest.json);;Manifest (manifest.json);;Application (*.exe);;Command Line (*.bat *.cmd)'
        )[0]
        if not path: return
        if path.endswith('.exe'): self.create_app(path)
        else: self.locate_app(path)

    def create_app(self, path: str) -> None:
        filename = os.path.basename(path)
        path = os.path.dirname(path).replace('\\', '/')
        if os.path.exists(f'{path}/manifest.json'): return self.locate_app(f'{path}/manifest.json')

        with open(f'{path}/manifest.json', 'w', encoding = 'utf-8') as f:
            json.dump(obj = {
                'release': 'custom',
                'tag_name': None,
                'command': f'{path}/{filename}',
                'url': None,
                'created_at': None
            }, fp = f, ensure_ascii = False)

        self.save_data.apps['custom'].append(path)
        self.refresh_apps()
        self.save_data.save()

    def locate_app(self, path: str) -> None:
        with open(path, 'r', encoding = 'utf-8') as f:
            data = json.load(f)

        if data['release'] in list(self.save_data.apps.keys()):
            app = '/'.join(path.split('/')[:-1])
            if app not in self.save_data.apps[data['release']]:
                self.save_data.apps[data['release']].append(app)
                self.refresh_apps()
                self.save_data.save()

    def install_app_click(self):
        self.main_page.setVisible(False)
        self.install_app_page.setVisible(True)
        self.install_app_page_refresh_template()



    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()



    def refresh_install_apps_list(self):
        for i in self.install_page_buttons[0] + self.install_page_buttons[1]:
            i.setVisible(self.install_app_page.top.searchbar.text().lower() in i.name.lower())



    def check_updates(self):
        pass
    #     self.update_worker = UpdateWorker()
    #     self.update_worker.signals.done.connect(self.update_done)
    #     self.update_worker.start()

    # def update_done(self):
    #     self.update_worker.exit()
    #     self.refresh_apps()
    #     self.save_data.save()



    def add_to_update_list(self, path: str) -> None:
        self.app_buttons[path].init_update(self.save_data.downloads_folder)
        self.is_updating.append(path)

    def remove_from_update_list(self, path: str, success: bool) -> None:
        if success:
            del self.updates[path.split('/')[-1]]
            self.is_updating.remove(path)



    def refresh_apps(self):
        for k in self.save_data.apps:
            for app in self.save_data.apps[k].copy():
                if not os.path.exists(f'{app}/manifest.json'):
                    self.save_data.apps[k].remove(app)
                    if app in self.app_buttons:
                        self.app_buttons[app].setParent(None)
                        del self.app_buttons[app]
                    continue

        self.refresh_apps_list()

    def refresh_apps_list(self, event: str|int = None):
        match self.main_page.apps_widget.notebook.currentIndex():
            case 0: k = 'all'
            case 1: k = 'official'
            case 2: k = 'pre'
            case 3: k = 'custom'

        app_keys = list(self.app_buttons.keys())

        for button in self.app_buttons.values():
            button.setParent(None)

        for i, app in enumerate(self.save_data.apps[k] if k != 'all' else [*self.save_data.apps['official'], *self.save_data.apps['pre'], *self.save_data.apps['custom']]):
            name = app.split('/')[-1]
            has_update = name in list(self.updates.keys())
            compact_mode = (self.devicePixelRatio() > 1) if self.save_data.compact_paths == 0 else (self.save_data.compact_paths == 1)

            if self.main_page.apps_widget.searchbar.text().lower() in name.lower():
                if app in app_keys:
                    b: InstalledButton = self.app_buttons[app]
                    if b.compact_mode != compact_mode: b.set_compact_mode(compact_mode)
                    if b.has_update != has_update: b.set_update(has_update, self.updates[name] if has_update else None)

                else:
                    b = InstalledButton(
                        name,
                        app,
                        self.save_data.language_data['QMainWindow']['mainPage']['QSidePanel']['apps']['InstalledButton'],
                        './data/icons/questionMark.svg',
                        False,
                        InstallButton.get_release(InstallButton.platform, self.updates[name], self.save_data.token) if has_update else None,
                        compact_mode
                    )
                    b.remove_from_list.connect(self.remove_from_install_list)
                    b.uninstall.connect(self.add_to_uninstall_list)
                    b.update_app.connect(self.add_to_update_list)
                    b.update_app_done.connect(self.remove_from_update_list)
                    self.app_buttons[app] = b
                self.main_page.apps_widget.notebook_tabs.scroll_layout.addWidget(b, i, 0)


    def create_about_menu(self) -> None:
        self.about_menu = QMenu(self.window)
        self.about_menu.setCursor(Qt.CursorShape.PointingHandCursor)

        act = self.about_menu.addAction(self.save_data.getIcon('menubar/qt.png', mode = QSaveData.IconMode.Global), self.save_data.language_data['QMenu']['about']['Qt'])
        act.triggered.connect(self.aboutQt)

        act = self.about_menu.addAction(QIcon('./data/icons/AppManager.svg'), self.save_data.language_data['QMenu']['about']['AppManager'])
        act.triggered.connect(self.about_clicked)

    def about_menu_clicked(self) -> None:
        self.about_menu.popup(QCursor.pos())

    def about_clicked(self) -> None:
        lang = self.save_data.language_data['QAbout']['AppManager']
        supports = '\n'.join(f'&nbsp;&nbsp;&nbsp;• <a href=\"{link}\" style=\"color: {self.COLOR_LINK.hex}; text-decoration: none;\">{name}</a>' for name, link in [
            ('GitHub', 'https://github.com')
        ])
        QAboutBox(
            app = self,
            title = lang['title'],
            logo = './data/icons/AppManager.svg',
            texts = [
                lang['texts'][0],
                lang['texts'][1].replace('%s', f'<a href=\"https://github.com/Synell\" style=\"color: {self.COLOR_LINK.hex}; text-decoration: none;\">Synel</a>'),
                lang['texts'][2].replace('%s', supports),
                lang['texts'][3].replace('%s', f'<a href=\"https://github.com/App-Manager\" style=\"color: {self.COLOR_LINK.hex}; text-decoration: none;\">App Manager Github</a>')
            ]
        ).exec()


    def create_tray_icon(self) -> None:
        self.window.closeEvent = self.close_event

        self.sys_tray = QSystemTrayIcon(self)
        self.sys_tray.setToolTip('App Manager')
        self.sys_tray.setIcon(QIcon('./data/icons/AppManager.svg'))
        self.sys_tray.setVisible(True)
        self.sys_tray.activated.connect(self.on_sys_tray_activated)

        self.sys_tray_menu = QMenu(self.window)
        self.sys_tray_menu.setCursor(Qt.CursorShape.PointingHandCursor)
        self.sys_tray_menu.setProperty('QSystemTrayIcon', True)
        act = self.sys_tray_menu.addAction(self.save_data.getIcon('popup/exit.png'), self.save_data.language_data['QSystemTrayIcon']['QMenu']['exit'])
        act.triggered.connect(self.exit)


    def on_sys_tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        match reason:
            case QSystemTrayIcon.ActivationReason.Trigger:
                self.window.show()
                self.window.raise_()
                self.window.setWindowState(Qt.WindowState.WindowActive)
            case QSystemTrayIcon.ActivationReason.Context:
                self.sys_tray_menu.popup(QCursor.pos())


    def close_event(self, event: QCloseEvent) -> None:
        event.ignore()
        self.window.hide()

        if self.save_data.minimize_to_tray:
            if self.save_data.goes_to_tray_notif: self.sys_tray.showMessage(
                self.save_data.language_data['QSystemTrayIcon']['showMessage']['goesToTray']['title'],
                self.save_data.language_data['QSystemTrayIcon']['showMessage']['goesToTray']['message'],
                QSystemTrayIcon.MessageIcon.Information,
                self.MESSAGE_DURATION
            )
            self.show_alert(
                self.save_data.language_data['QSystemTrayIcon']['showMessage']['goesToTray']['message'],
                raise_duration = self.ALERT_RAISE_DURATION,
                pause_duration = self.ALERT_PAUSE_DURATION,
                fade_duration = self.ALERT_FADE_DURATION,
                color = 'main'
            )
        else:
            self.exit()

    def exit(self) -> None:
        if self.downloads or self.uninstalls or self.is_updating:
            if self.save_data.exit_during_work_notif: self.sys_tray.showMessage(
                self.save_data.language_data['QSystemTrayIcon']['showMessage']['exitDuringWork']['title'],
                self.save_data.language_data['QSystemTrayIcon']['showMessage']['exitDuringWork']['message'],
                QSystemTrayIcon.MessageIcon.Information,
                self.MESSAGE_DURATION
            )
            self.must_exit_after_download = True
            return
        super().exit()
#----------------------------------------------------------------------

    # Main
if __name__ == '__main__':
    app = Application()
    app.window.showNormal()
    exit(app.exec())
#----------------------------------------------------------------------