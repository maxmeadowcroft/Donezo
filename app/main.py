import csv
import sys
from textual import on
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll, Horizontal
from textual.widgets import Static, Header, Footer, Checkbox, Input, Button

def resource_path(relative_path):
    """ Get the absolute path to the resource for PyInstaller. """
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

class ToDo(App):
    CSS_PATH = "styles/light.tcss"
    watch_css = True
    csv_file = "../data/todo_items.csv"

    def compose(self) -> ComposeResult:
        # Import the header and footer
        yield Header()
        yield Footer()
        yield Button("Quit", id="quit", variant="error")
        # Widget to get user input
        yield Horizontal(
            Input(placeholder="Please enter an item", type="text", id="input"),
            Button("add item", id="add")
        )
        # Output for notes back to the user
        yield Static(id="output")
        # Vertical scroll for the ToDo Items
        yield VerticalScroll(id="todo-list")

    def save_to_csv(self):
        todo_list = self.query_one("#todo-list", VerticalScroll)
        rows = []
        for child in todo_list.children:
            if isinstance(child, Horizontal):
                # Find the Checkbox directly
                checkbox = next((widget for widget in child.children if isinstance(widget, Checkbox)), None)
                if checkbox:
                    rows.append([checkbox.label, checkbox.value])
        with open(self.csv_file, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Item", "Completed"])
            writer.writerows(rows)

    def load_from_csv(self):
        try:
            with open(self.csv_file, mode="r") as file:
                reader = csv.DictReader(file)
                todo_list = self.query_one("#todo-list", VerticalScroll)
                for row in reader:
                    checkbox = Checkbox(row["Item"], value=row["Completed"] == "True")
                    if row["Completed"] == "True":
                        checkbox.styles.background = "green 10%"
                    else:
                        checkbox.styles.background = "red 10%"
                    todo_list.mount(
                        Horizontal(
                            checkbox,
                            Button("Delete", variant="error", id="item-button")
                        )
                    )
        except FileNotFoundError:
            pass  # File does not exist yet, no items to load

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        # Update the item's appearance when the checkbox state changes
        checkbox = event.checkbox
        if checkbox.value:
            checkbox.styles.background = "green 10%"
        else:
            checkbox.styles.background = "red 10%"
        self.save_to_csv()

    def add_item(self, input_name: str) -> None:
        todo_list = self.query_one("#todo-list", VerticalScroll)
        todo_list.mount(
            Horizontal(
                Checkbox(input_name),
                Button("Delete", variant="error", id="item-button")
            )
        )
        output_widget = self.query_one("#output", Static)
        output_widget.update(f"Added {input_name}")

    @on(Button.Pressed, "#add")
    @on(Input.Submitted)
    def on_input_submitted(self) -> None:
        input = self.query_one(Input)
        self.add_item(input.value)
        input.value = ""
        self.save_to_csv()

    @on(Button.Pressed, "#item-button")
    def on_button_pressed(self, event: Button.Pressed) -> None:
        # Find the parent Horizontal container of the button that was pressed
        button = event.button
        parent = button.parent
        if parent:
            parent.remove()  # Remove the Horizontal container
            output_widget = self.query_one("#output", Static)
            output_widget.update("Removed item")
        self.save_to_csv()

    def on_mount(self) -> None:
        self.title = "ToDo"
        self.sub_title = "A Maximus Meadowcroft Production"
        self.load_from_csv()

    @on(Button.Pressed, '#quit')
    def quit(self):
        self.save_to_csv()
        self.exit()

if __name__ == "__main__":
    app = ToDo()
    app.run()