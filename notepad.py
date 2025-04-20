import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QAction, QFileDialog,
    QTabWidget, QFontDialog, QColorDialog, QMessageBox, QToolBar,
    QLabel, QStatusBar, QShortcut, QInputDialog
)
from PyQt5.QtCore import Qt, QTimer


class NotePad(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        # Set dark mode as default
        self.dark_mode_action.setChecked(True)
        self.toggle_dark_mode()
        
        self.document_modified = False
        
        # auto save every 60 seconds
        self.auto_save_timer = QTimer(self)
        self.auto_save_timer.timeout.connect(self.auto_save)
        self.auto_save_timer.start(60000)  # 60 seconds

    def initUI(self):
        self.setWindowTitle("Enhanced Notepad")
        self.resize(900, 700)

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tab_widget)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.line_col_label = QLabel("Line: 1, Column: 1")
        self.status_bar.addPermanentWidget(self.line_col_label)
        self.char_count_label = QLabel("Characters: 0")
        self.status_bar.addPermanentWidget(self.char_count_label)

        self.create_toolbar()

        # the first tab        
        self.add_new_tab()
        self.create_menu_bar()
        self.show()

    def create_toolbar(self):
        toolbar = QToolBar("Toolbar")
        self.addToolBar(toolbar)

        new_action = QAction("New", self)
        new_action.triggered.connect(lambda: self.add_new_tab())
        toolbar.addAction(new_action)

        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)

        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_file)
        toolbar.addAction(save_action)

        toolbar.addSeparator()

        cut_action = QAction("Cut", self)
        cut_action.triggered.connect(self.cut)
        toolbar.addAction(cut_action)

        copy_action = QAction("Copy", self)
        copy_action.triggered.connect(self.copy)
        toolbar.addAction(copy_action)

        paste_action = QAction("Paste", self)
        paste_action.triggered.connect(self.paste)
        toolbar.addAction(paste_action)

    def add_new_tab(self, title="Untitled", content=""):
        text_edit = QTextEdit()
        text_edit.setText(content)
        text_edit.setProperty("file_path", None)  # make sure to store the file path property
        
        # this will connect signals for the position of the cursor and the text changed
        text_edit.cursorPositionChanged.connect(lambda: self.update_status_bar(text_edit))
        text_edit.textChanged.connect(lambda: self.on_text_changed(text_edit))

        index = self.tab_widget.addTab(text_edit, title)
        self.tab_widget.setCurrentIndex(index)
        text_edit.setFocus()

        return text_edit
    
    def on_text_changed(self, text_edit):
        self.document_modified = True
        char_count = len(text_edit.toPlainText())
        self.char_count_label.setText(f"Characters: {char_count}")
        
        current_index = self.tab_widget.currentIndex()
        current_tab_text = self.tab_widget.tabText(current_index)
        if not current_tab_text.endswith("*") and text_edit.property("file_path"):
            self.tab_widget.setTabText(current_index, current_tab_text + "*")

    def update_status_bar(self, text_edit):
        cursor = text_edit.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        self.line_col_label.setText(f"Line: {line}, Column: {col}")

    def close_tab(self, index):
        text_edit = self.tab_widget.widget(index)
        if isinstance(text_edit, QTextEdit) and self.document_modified:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Question)
            msg_box.setText("The document has been modified.")
            msg_box.setInformativeText("Do you want to save your changes?")
            msg_box.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            msg_box.setDefaultButton(QMessageBox.Save)
            ret = msg_box.exec_()
            
            if ret == QMessageBox.Save:
                self.tab_widget.setCurrentIndex(index)
                self.save_file()
            elif ret == QMessageBox.Cancel:
                return
        
        self.tab_widget.removeTab(index)
        if self.tab_widget.count() == 0:
            self.add_new_tab()

    def get_current_text_edit(self):
        widget = self.tab_widget.currentWidget()
        if isinstance(widget, QTextEdit):
            return widget
        return None

    def create_menu_bar(self):
        menu_bar = self.menuBar()
        menu_bar.addSeparator()
        
        file_menu = menu_bar.addMenu("File")

        new_file_action = QAction("New Window", self)
        new_file_action.setShortcut("Ctrl+N")
        new_file_action.triggered.connect(self.new_file)
        file_menu.addAction(new_file_action)

        new_tab_action = QAction("New Tab", self)
        new_tab_action.setShortcut("Ctrl+T")
        new_tab_action.triggered.connect(lambda: self.add_new_tab())
        file_menu.addAction(new_tab_action)

        open_file_action = QAction("Open...", self)
        open_file_action.setShortcut("Ctrl+O")
        open_file_action.triggered.connect(self.open_file)
        file_menu.addAction(open_file_action)

        save_file_action = QAction("Save", self)
        save_file_action.setShortcut("Ctrl+S")
        save_file_action.triggered.connect(self.save_file)
        file_menu.addAction(save_file_action)

        save_as_file_action = QAction("Save As...", self)
        save_as_file_action.setShortcut("Ctrl+Shift+S")
        save_as_file_action.triggered.connect(self.save_as_file)
        file_menu.addAction(save_as_file_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Alt+F4")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit Menu
        edit_menu = menu_bar.addMenu("Edit")

        undo_action = QAction("Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction("Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(self.redo)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        cut_action = QAction("Cut", self)
        cut_action.setShortcut("Ctrl+X")
        cut_action.triggered.connect(self.cut)
        edit_menu.addAction(cut_action)

        copy_action = QAction("Copy", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(self.copy)
        edit_menu.addAction(copy_action)

        paste_action = QAction("Paste", self)
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(self.paste)
        edit_menu.addAction(paste_action)

        delete_action = QAction("Delete", self)
        delete_action.setShortcut("Del")
        delete_action.triggered.connect(self.delete_text)
        edit_menu.addAction(delete_action)

        edit_menu.addSeparator()

        find_action = QAction("Find...", self)
        find_action.setShortcut("Ctrl+F")
        find_action.triggered.connect(self.find_text)
        edit_menu.addAction(find_action)
        
        find_next_action = QAction("Find Next", self)
        find_next_action.setShortcut("F3")
        find_next_action.triggered.connect(self.find_next)
        edit_menu.addAction(find_next_action)
        
        replace_action = QAction("Replace...", self)
        replace_action.setShortcut("Ctrl+H")
        replace_action.triggered.connect(self.replace_text)
        edit_menu.addAction(replace_action)
        
        edit_menu.addSeparator()

        select_all_action = QAction("Select All", self)
        select_all_action.setShortcut("Ctrl+A")
        select_all_action.triggered.connect(self.select_all)
        edit_menu.addAction(select_all_action)
        
        # Format Menu
        format_menu = menu_bar.addMenu("Format")
        
        word_wrap_action = QAction("Word Wrap", self, checkable=True)
        word_wrap_action.setChecked(True)
        word_wrap_action.triggered.connect(self.toggle_word_wrap)
        format_menu.addAction(word_wrap_action)
        
        font_action = QAction("Font...", self)
        font_action.triggered.connect(self.choose_font)
        format_menu.addAction(font_action)
        
        text_color_action = QAction("Text Color...", self)
        text_color_action.triggered.connect(self.choose_text_color)
        format_menu.addAction(text_color_action)
        
        bg_color_action = QAction("Background Color...", self)
        bg_color_action.triggered.connect(self.choose_bg_color)
        format_menu.addAction(bg_color_action)

        # View Menu
        view_menu = menu_bar.addMenu("View")

        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.setShortcut("Ctrl+=")
        zoom_in_action.triggered.connect(self.zoom_in)
        view_menu.addAction(zoom_in_action)

        zoom_out_action = QAction("Zoom Out", self)
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.triggered.connect(self.zoom_out)
        view_menu.addAction(zoom_out_action)

        restore_zoom_action = QAction("Restore Default Zoom", self)
        restore_zoom_action.setShortcut("Ctrl+0")
        restore_zoom_action.triggered.connect(self.restore_zoom)
        view_menu.addAction(restore_zoom_action)
        
        view_menu.addSeparator()
        
        show_status_bar_action = QAction("Status Bar", self, checkable=True)
        show_status_bar_action.setChecked(True)
        show_status_bar_action.triggered.connect(self.toggle_status_bar)
        view_menu.addAction(show_status_bar_action)

        self.dark_mode_action = QAction("Dark Mode", self, checkable=True)
        self.dark_mode_action.triggered.connect(self.toggle_dark_mode)
        view_menu.addAction(self.dark_mode_action)
        
    def toggle_dark_mode(self):
        if self.dark_mode_action.isChecked():
            dark_stylesheet = """
                QWidget {
                    background-color: #1e1e1e;
                    color: #f0f0f0;
                }

                QTextEdit {
                    background-color: #252525;
                    color: #f0f0f0;
                    border: none;
                    selection-background-color: #264f78;
                    selection-color: #ffffff;
                }

                QMenuBar {
                    background-color: #333333;
                    color: #f0f0f0;
                }

                QMenuBar::item {
                    background-color: #333333;
                    color: #f0f0f0;
                    padding: 4px 8px;
                }

                QMenuBar::item:selected {
                    background-color: #505050;
                }

                QMenu {
                    background-color: #2d2d2d;
                    color: #f0f0f0;
                    border: 1px solid #505050;
                }

                QMenu::item:selected {
                    background-color: #404040;
                }

                QTabWidget::pane {
                    border: none;
                }

                QTabBar::tab {
                    background: #333333;
                    color: #f0f0f0;
                    padding: 8px 12px;
                    margin-right: 2px;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                }

                QTabBar::tab:selected {
                    background: #0078d7;
                }
                
                QToolBar {
                    background-color: #333333;
                    border: none;
                    spacing: 3px;
                }
                
                QToolBar QToolButton {
                    background-color: #333333;
                    color: #f0f0f0;
                    border: 1px solid #505050;
                    border-radius: 4px;
                    padding: 4px;
                }
                
                QToolBar QToolButton:hover {
                    background-color: #404040;
                }
                
                QStatusBar {
                    background-color: #333333;
                    color: #f0f0f0;
                }
                
                QDialog {
                    background-color: #2d2d2d;
                    color: #f0f0f0;
                }
                
                QPushButton {
                    background-color: #0078d7;
                    color: #ffffff;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 4px;
                }
                
                QPushButton:hover {
                    background-color: #1084e0;
                }
                
                QLineEdit, QSpinBox {
                    background-color: #252525;
                    color: #f0f0f0;
                    border: 1px solid #505050;
                    padding: 4px;
                    border-radius: 4px;
                }
                
                QMessageBox {
                    background-color: #2d2d2d;
                    color: #f0f0f0;
                }
            """
            self.setStyleSheet(dark_stylesheet)
        else:
            self.setStyleSheet("")
    
    def toggle_status_bar(self):
        if self.statusBar().isVisible():
            self.statusBar().hide()
        else:
            self.statusBar().show()
    
    def toggle_word_wrap(self):
        text_edit = self.get_current_text_edit()
        if text_edit:
            if text_edit.lineWrapMode() == QTextEdit.NoWrap:
                text_edit.setLineWrapMode(QTextEdit.WidgetWidth)
            else:
                text_edit.setLineWrapMode(QTextEdit.NoWrap)
    
    def choose_font(self):
        text_edit = self.get_current_text_edit()
        if text_edit:
            current_font = text_edit.currentFont()
            font, ok = QFontDialog.getFont(current_font, self)
            if ok:
                text_edit.setFont(font)
    
    def choose_text_color(self):
        text_edit = self.get_current_text_edit()
        if text_edit:
            color = QColorDialog.getColor()
            if color.isValid():
                text_edit.setTextColor(color)
    
    def choose_bg_color(self):
        text_edit = self.get_current_text_edit()
        if text_edit:
            color = QColorDialog.getColor()
            if color.isValid():
                text_edit.setStyleSheet(f"background-color: {color.name()};")
    
    def delete_text(self):
        text_edit = self.get_current_text_edit()
        if text_edit:
            cursor = text_edit.textCursor()
            cursor.removeSelectedText()
    
    def find_text(self):
        text_edit = self.get_current_text_edit()
        if text_edit:
            search_term, ok = QInputDialog.getText(self, "Find", "Search for:")
            if ok and search_term:
                self.last_search = search_term
                self.find_next()
    
    def find_next(self):
        text_edit = self.get_current_text_edit()
        if text_edit and hasattr(self, 'last_search'):
            # store the cursor position 
            cursor = text_edit.textCursor()
            current_pos = cursor.position()
            
            if not text_edit.find(self.last_search):
                # If not found try from the beginning
                cursor.setPosition(0)
                text_edit.setTextCursor(cursor)
                if not text_edit.find(self.last_search):
                    QMessageBox.information(self, "Find", f"Cannot find '{self.last_search}'")
                    # Return to original position
                    cursor.setPosition(current_pos)
                    text_edit.setTextCursor(cursor)
    
    def replace_text(self):
        text_edit = self.get_current_text_edit()
        if text_edit:
            search_term, ok = QInputDialog.getText(self, "Replace", "Search for:")
            if ok and search_term:
                replace_with, ok = QInputDialog.getText(self, "Replace", "Replace with:")
                if ok:
                    self.last_search = search_term
                    cursor = text_edit.textCursor()
                    
                    if cursor.hasSelection() and cursor.selectedText() == search_term:
                        cursor.insertText(replace_with)
                    self.find_next()
        
    def auto_save(self):
        text_edit = self.get_current_text_edit()
        if text_edit and text_edit.property("file_path") and self.document_modified:
            self.save_file()
            self.status_bar.showMessage("Auto-saved", 2000)

    def undo(self):
        text_edit = self.get_current_text_edit()
        if text_edit:
            text_edit.undo()

    def redo(self):
        text_edit = self.get_current_text_edit()
        if text_edit:
            text_edit.redo()

    def cut(self):
        text_edit = self.get_current_text_edit()
        if text_edit:
            text_edit.cut()

    def copy(self):
        text_edit = self.get_current_text_edit()
        if text_edit:
            text_edit.copy()

    def paste(self):
        text_edit = self.get_current_text_edit()
        if text_edit:
            text_edit.paste()

    def select_all(self):
        text_edit = self.get_current_text_edit()
        if text_edit:
            text_edit.selectAll()

    def new_file(self):
        new_window = NotePad()
        new_window.show()

    def open_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", "Text Files (*.txt);;All Files (*)", options=options
        )
        if file_name:
            with open(file_name, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()

            from os.path import basename
            tab_title = basename(file_name)

            text_edit = self.add_new_tab(tab_title, content)
            text_edit.setProperty("file_path", file_name)
            self.document_modified = False

    def save_file(self):
        text_edit = self.get_current_text_edit()
        if text_edit:
            file_path = text_edit.property("file_path")

            if file_path:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(text_edit.toPlainText())

                current_index = self.tab_widget.currentIndex()
                current_tab_text = self.tab_widget.tabText(current_index)
                if current_tab_text.endswith("*"):
                    self.tab_widget.setTabText(current_index, current_tab_text[:-1])
                
                self.document_modified = False
                self.status_bar.showMessage(f"Saved to {file_path}", 2000)
            else:
                self.save_as_file()

    def save_as_file(self):
        text_edit = self.get_current_text_edit()
        if text_edit:
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(
                self, "Save As", "", "Text Files (*.txt);;All Files (*)", options=options
            )
            if file_name:
                with open(file_name, 'w', encoding='utf-8') as file:
                    file.write(text_edit.toPlainText())

                from os.path import basename
                tab_title = basename(file_name)
                self.tab_widget.setTabText(self.tab_widget.currentIndex(), tab_title)
                text_edit.setProperty("file_path", file_name)
                self.document_modified = False
                self.status_bar.showMessage(f"Saved to {file_name}", 2000)

    def zoom_in(self):
        text_edit = self.get_current_text_edit()
        if text_edit:
            current_font = text_edit.font()
            size = current_font.pointSize()
            current_font.setPointSize(size + 1)
            text_edit.setFont(current_font)

    def zoom_out(self):
        text_edit = self.get_current_text_edit()
        if text_edit:
            current_font = text_edit.font()
            size = current_font.pointSize()
            if size > 1:
                current_font.setPointSize(size - 1)
                text_edit.setFont(current_font)

    def restore_zoom(self):
        text_edit = self.get_current_text_edit()
        if text_edit:
            current_font = text_edit.font()
            current_font.setPointSize(10)
            text_edit.setFont(current_font)
    
    def closeEvent(self, event):
        # Check for unsaved changes before closing
        for i in range(self.tab_widget.count()):
            text_edit = self.tab_widget.widget(i)
            if isinstance(text_edit, QTextEdit) and self.document_modified:
                self.tab_widget.setCurrentIndex(i)
                
                msg_box = QMessageBox()
                msg_box.setIcon(QMessageBox.Question)
                msg_box.setText(f"The document '{self.tab_widget.tabText(i)}' has been modified.")
                msg_box.setInformativeText("Do you want to save your changes?")
                msg_box.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
                msg_box.setDefaultButton(QMessageBox.Save)
                ret = msg_box.exec_()
                
                if ret == QMessageBox.Save:
                    self.save_file()
                elif ret == QMessageBox.Cancel:
                    event.ignore()
                    return

        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  
    notepad = NotePad()
    notepad.show()
    sys.exit(app.exec_())