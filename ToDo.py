import csv
from textual import on
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll, Horizontal
from textual.widgets import Static, Header, Footer, Checkbox, Input, Button

class ToDo(App):
    CSS_PATH = "light.tcss"
    watch_css = True
    csv_file = "todo_items.csv"

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
                checkbox = child.query(Checkbox).first()
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

    @on(Button.Pressed, "#item-button")
    def on_button_pressed(self) -> None:
        # Remove the Horizontal container containing the delete button
        todo_list = self.query_one("#todo-list", VerticalScroll)
        for child in todo_list.children:
            if isinstance(child, Horizontal):
                child.remove()
                output_widget = self.query_one("#output", Static)
                output_widget.update("Removed item")
                break

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