import os
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QTabWidget, QTextEdit, QToolBar, QPushButton
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QEvent
import shutil


class Terminal(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the main window
        self.setWindowTitle("AI Terminal")
        self.resize(900, 600)

        # Current working directory (default to D:\)
        self.current_dir = "D:\\"  # Ensure this is your desired path

        # Tabbed terminal layout
        self.tab_widget = QTabWidget(self)
        self.setCentralWidget(self.tab_widget)

        # Create the first terminal tab
        self.add_terminal_tab("Terminal 1")

        # Add a toolbar for additional functionality
        self.add_toolbar()

    def add_toolbar(self):
        """
        Adds a toolbar with buttons for additional features.
        """
        toolbar = QToolBar("Toolbar", self)
        self.addToolBar(toolbar)

        clear_btn = QPushButton("Clear Screen")
        new_tab_btn = QPushButton("New Tab")

        toolbar.addWidget(clear_btn)
        toolbar.addWidget(new_tab_btn)

        # Connect buttons to actions
        clear_btn.clicked.connect(self.clear_screen)
        new_tab_btn.clicked.connect(self.create_new_tab)

    def add_terminal_tab(self, tab_name):
        """
        Adds a new terminal tab with its own text area.
        """
        terminal_widget = QWidget()
        layout = QVBoxLayout()

        # Terminal text area
        terminal_text_area = QTextEdit(self)
        terminal_text_area.setReadOnly(False)
        terminal_text_area.setFont(QFont("Consolas", 12))
        terminal_text_area.setStyleSheet("background-color: black; color: white; border: none;")
        terminal_text_area.installEventFilter(self)
        terminal_text_area.append(f"{self.current_dir}> ")  # Default prompt

        layout.addWidget(terminal_text_area)
        terminal_widget.setLayout(layout)

        # Add the tab
        self.tab_widget.addTab(terminal_widget, tab_name)

    def eventFilter(self, source, event):
        """
        Handle key events in the text area.
        """
        current_tab = self.tab_widget.currentWidget()
        if not current_tab:
            return super().eventFilter(source, event)

        text_area = current_tab.layout().itemAt(0).widget()
        if event.type() == QEvent.Type.KeyPress and source is text_area:
            if event.key() == Qt.Key.Key_Return:  # If Enter key is pressed
                full_text = text_area.toPlainText()
                last_line = full_text.split("\n")[-1]
                command = last_line[len(f"{self.current_dir}> "):].strip()  # Extract user command

                if command:  # If there is a command, process it
                    self.run_command(command, text_area)

                text_area.append(f"{self.current_dir}> ")  # Add a new prompt
                return True

        return super().eventFilter(source, event)

    def run_command(self, command, text_area):
        """
        Run the user's command and display the output in the current tab.
        """
        try:
            if command.startswith("cd "):  # Change directory command
                # Extract the directory path after 'cd'
                parts = command.split(" ", 1)
                if len(parts) > 1:
                    new_dir = parts[1].strip()
                    # Construct the full directory path
                    target_dir = os.path.join(self.current_dir, new_dir)
                    if os.path.isdir(target_dir):  # Check if it's a valid directory
                        self.current_dir = target_dir  # Update current directory
                        output = f"Changed directory to {self.current_dir}.\n"
                    else:
                        output = f"Error: Directory '{new_dir}' not found.\n"
                else:
                    output = "Error: No directory specified.\n"
                    
            elif command.startswith("mkdir "):  # Make directory command
                dir_name = command.split(" ", 1)[1]
                target_dir = os.path.join(self.current_dir, dir_name)
    
                try:
                   os.mkdir(target_dir)  # Create the directory
        
        # After directory is created, create a .txt file inside it
                   txt_file_path = os.path.join(target_dir, "new_file.txt")  # Name of the new file
                   with open(txt_file_path, "w") as txt_file:
                       txt_file.write("This is a new text file.")  # You can modify this text
        
                   output = f"Directory '{dir_name}' created successfully, and 'new_file.txt' was created inside it.\n"
        
                except FileExistsError:
                     output = f"Error: Directory '{dir_name}' already exists.\n"
                except Exception as e:
                     output = f"Error creating directory: {str(e)}\n"




            elif command.startswith("write "):  # Write to file command
                parts = command.split(" ", 2)
                if len(parts) < 3:
                    output = "Usage: write <filename> <content>\n"
                else:
                    file_name = parts[1]
                    content = parts[2]
                    file_path = os.path.join(self.current_dir, file_name)

                    # Check if file is writable
                    try:
                        # Try writing content to the file
                        with open(file_path, "a") as f:
                            f.write(content + "\n")
                        output = f"Content written to '{file_name}'.\n"
                    except PermissionError:
                        output = f"Error: Permission denied to write to '{file_name}'.\n"
                    except Exception as e:
                        output = f"Error: {str(e)}\n"

            elif command.startswith("read "):  # Read file command
                file_name = command.split(" ", 1)[1]
                try:
                    with open(os.path.join(self.current_dir, file_name), "r") as f:
                        output = f.read()
                except FileNotFoundError:
                    output = f"Error: File '{file_name}' not found.\n"
                except Exception as e:
                    output = f"Error reading file: {str(e)}\n"
                    
            elif command == "exit":  # Exit command
                output = "Exiting the terminal...\n"
                text_area.append(output)
                QApplication.quit()  # Close the application


            elif command.startswith("delete "):  # Delete file command
                file_name = command.split(" ", 1)[1]
                try:
                    os.remove(os.path.join(self.current_dir, file_name))
                    output = f"File '{file_name}' deleted successfully.\n"
                except FileNotFoundError:
                    output = f"Error: File '{file_name}' not found.\n"
                except Exception as e:
                    output = f"Error deleting file: {str(e)}\n"

            elif command == "dir":  # List directory contents
                try:
                    files = os.listdir(self.current_dir)
                    output = "\n".join(files) + "\n"
                except Exception as e:
                    output = f"Error listing directory: {str(e)}\n"

            else:
                output = f"Unknown command: {command}\n"

        except Exception as e:
            output = f"Error: {str(e)}\n"

        # Display the command output
        text_area.append(output)

    def clear_screen(self):
        """
        Clears the text in the current tab.
        """
        current_tab = self.tab_widget.currentWidget()
        if current_tab:
            text_area = current_tab.layout().itemAt(0).widget()
            text_area.setPlainText(f"{self.current_dir}> ")

    def create_new_tab(self):
        """
        Creates a new terminal tab.
        """
        tab_count = self.tab_widget.count()
        self.add_terminal_tab(f"Terminal {tab_count + 1}")


# Run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    terminal = Terminal()
    terminal.show()
    sys.exit(app.exec())
