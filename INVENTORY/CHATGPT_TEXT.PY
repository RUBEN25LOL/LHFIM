import flet as ft
import sqlite3
from typing import List, Dict, Any, Optional
import time
from flet import colors, icons

# ========== CONSTANTS ==========
CATEGORY_TABLE = "category"
DATA_TYPES = ["text", "numbers", "yes/no", "date", "percentage", "price"]

# ========== DATABASE LAYER ==========
class Database:
    def __init__(self, db_path: str = "inventory.db"):
        self.db_path = db_path
        self._initialize_db()

    def _initialize_db(self) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {CATEGORY_TABLE} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    datatype TEXT NOT NULL,
                    null_status INTEGER DEFAULT 0
                )
            """)
            conn.commit()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def insert_category(self, name: str, datatype: str, null_status: bool) -> bool:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    f"INSERT INTO {CATEGORY_TABLE} (name, datatype, null_status) VALUES (?, ?, ?)",
                    (name, datatype, int(null_status))
                )
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False  # Duplicate name
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False

    def get_all_categories(self) -> List[Dict[str, Any]]:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT name, datatype, null_status FROM {CATEGORY_TABLE} ORDER BY name")
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []

# ========== UI UTILITIES ==========
class UIUtils:
    @staticmethod
    def show_snackbar(
        page: ft.Page,
        message: str,
        color: str = colors.GREEN_400,
        duration: int = 3000
    ) -> None:
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=color,
            behavior=ft.SnackBarBehavior.FLOATING,
            duration=duration,
            show_close_icon=True
        )
        page.snack_bar.open = True
        page.update()

# ========== MAIN APPLICATION ==========
class InventoryApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.db = Database()
        self.ui = UIUtils()
        self._setup_page()

    def _setup_page(self) -> None:
        self.page.title = "Inventory Management"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.vertical_alignment = ft.MainAxisAlignment.START
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.padding = 20

    def main_scene(self, e=None) -> None:
        self.page.clean()
        self.page.add(
            ft.Column(
                [
                    ft.Text("Main Menu", size=30, weight=ft.FontWeight.BOLD),
                    ft.ElevatedButton("Inventory", icon=icons.INVENTORY_2, on_click=self.show_inventory_scene),
                    ft.ElevatedButton("Buyers", icon=icons.PEOPLE_OUTLINE, on_click=self.show_buyers_scene),
                    ft.ElevatedButton("Customers", icon=icons.SHOPPING_CART_OUTLINED, on_click=self.show_customers_scene),
                    ft.ElevatedButton("Reports", icon=icons.ANALYTICS_OUTLINED, on_click=self.show_reports_scene),
                    ft.ElevatedButton("Settings", icon=icons.SETTINGS_OUTLINED, on_click=self.show_settings_scene),
                    ft.ElevatedButton("Toggle Theme", icon=icons.DARK_MODE_OUTLINED, on_click=self.toggle_theme),
                ],
                spacing=15,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )
        self.page.update()

    def show_inventory_scene(self, e) -> None:
        self.page.clean()
        
        header = ft.Row(
            controls=[
                ft.IconButton(
                    icon=icons.ARROW_BACK_IOS_NEW_OUTLINED,
                    on_click=self.main_scene
                ),
                ft.Text("Inventory Management", size=25, expand=True),
            ],
            alignment=ft.MainAxisAlignment.START
        )

        actions = ft.ResponsiveRow(
            controls=[
                self._create_action_card("Add New Category", icons.ADD_CIRCLE_OUTLINED, self.add_category_scene),
                self._create_action_card("Add New Item", icons.ADD_BOX_OUTLINED, lambda e: print("Add item")),
                self._create_action_card("View Inventory", icons.LIST_OUTLINED, lambda e: print("View inventory")),
                self._create_action_card("Edit Categories", icons.EDIT_OUTLINED, lambda e: print("Edit categories")),
            ],
            spacing=20
        )

        self.page.add(ft.Column([header, actions], spacing=30))
        self.page.update()

    def _create_action_card(self, title: str, icon: str, on_click) -> ft.Container:
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(icon, size=40),
                    ft.Text(title)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            padding=20,
            on_click=on_click,
            ink=True,
            border_radius=10,
            bgcolor=colors.SURFACE_VARIANT,
            width=250,
            height=120,
            alignment=ft.alignment.center
        )

    def add_category_scene(self, e) -> None:
        self.page.clean()
        
        # Form elements
        name_field = ft.TextField(label="Category Name", autofocus=True)
        type_field = ft.TextField(label="Data Type", read_only=True)
        
        type_menu = ft.PopupMenuButton(
            items=[
                ft.PopupMenuItem(text=dt, on_click=lambda e, dt=dt: self._set_type(type_field, dt))
                for dt in DATA_TYPES
            ]
        )
        
        null_switch = ft.Switch(label="Allow empty values?", value=False)
        save_button = ft.ElevatedButton("Save", icon=icons.SAVE_OUTLINED, on_click=lambda e: self._save_category(
            name_field, type_field, null_switch, category_list
        ))
        
        # Category list
        category_list = ft.ListView(expand=True)
        self._load_categories(category_list)

        self.page.add(
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.IconButton(
                                icon=icons.ARROW_BACK_IOS_NEW_OUTLINED,
                                on_click=self.show_inventory_scene
                            ),
                            ft.Text("Add Category", size=25, expand=True),
                        ]
                    ),
                    ft.Row([name_field]),
                    ft.Row([type_field, type_menu]),
                    ft.Row([null_switch]),
                    ft.Row([save_button]),
                    ft.Divider(),
                    ft.Text("Existing Categories"),
                    ft.Container(
                        content=category_list,
                        border=ft.border.all(1, colors.OUTLINE),
                        border_radius=10,
                        padding=10,
                        height=200
                    )
                ],
                spacing=15
            )
        )
        self.page.update()

    def _set_type(self, field: ft.TextField, value: str) -> None:
        field.value = value
        self.page.update()

    def _load_categories(self, list_view: ft.ListView) -> None:
        categories = self.db.get_all_categories()
        list_view.controls = [
            ft.ListTile(
                title=ft.Text(cat["name"]),
                subtitle=ft.Text(f"Type: {cat['datatype']} | Nullable: {'Yes' if cat['null_status'] else 'No'}")
            ) for cat in categories
        ] or [ft.Text("No categories yet")]
        self.page.update()

    def _save_category(self, name_field: ft.TextField, type_field: ft.TextField, 
                      null_switch: ft.Switch, list_view: ft.ListView) -> None:
        if not name_field.value:
            self.ui.show_snackbar(self.page, "Name is required!", colors.RED_400)
            return
        if not type_field.value:
            self.ui.show_snackbar(self.page, "Select a data type", colors.RED_400)
            return

        if self.db.insert_category(name_field.value, type_field.value, null_switch.value):
            name_field.value = ""
            type_field.value = ""
            null_switch.value = False
            self._load_categories(list_view)
            self.ui.show_snackbar(self.page, "Category saved!")
        else:
            self.ui.show_snackbar(self.page, "Name already exists!", colors.RED_400)
        self.page.update()

    # Placeholder scenes
    def show_buyers_scene(self, e): self._placeholder_scene("Buyers")
    def show_customers_scene(self, e): self._placeholder_scene("Customers")
    def show_settings_scene(self, e): self._placeholder_scene("Settings")
    def show_reports_scene(self, e): self._placeholder_scene("Reports")
    
    def _placeholder_scene(self, title: str) -> None:
        self.page.clean()
        self.page.add(
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.IconButton(
                                icon=icons.ARROW_BACK_IOS_NEW_OUTLINED,
                                on_click=self.main_scene
                            ),
                            ft.Text(title, size=25, expand=True),
                        ]
                    ),
                    ft.Text(f"{title} management coming soon!"),
                    ft.ElevatedButton("Back", on_click=self.main_scene)
                ],
                spacing=20
            )
        )
        self.page.update()

    def toggle_theme(self, e) -> None:
        self.page.theme_mode = (
            ft.ThemeMode.LIGHT 
            if self.page.theme_mode == ft.ThemeMode.DARK 
            else ft.ThemeMode.DARK
        )
        self.page.update()

def main(page: ft.Page):
    app = InventoryApp(page)
    app.main_scene()

if __name__ == "__main__":
    ft.app(target=main)