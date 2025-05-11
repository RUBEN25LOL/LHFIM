import flet as ft
import pyrebase
import json
from datetime import datetime
import uuid
from typing import Dict, List, Optional

# Firebase Configuration
with open("firebase_config.json") as f:
    firebase_config = json.load(f)

firebase = pyrebase.initialize_app(firebase_config)
db = firebase.database()
auth = firebase.auth()
storage = firebase.storage()
db.persistence = True

class InventoryItem:
    def __init__(self, name: str, group: str, characteristics: Dict, photo_url: Optional[str] = None):
        self.name = name
        self.group = group
        self.characteristics = characteristics
        self.photo_url = photo_url
        self.created_at = datetime.now().isoformat()
        self.last_updated = datetime.now().isoformat()

class InventoryGroup:
    def __init__(self, name: str, characteristics: Dict[str, Dict]):
        self.name = name
        self.characteristics = characteristics

class InventoryPro:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Inventory Pro"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.theme = ft.Theme(
            color_scheme=ft.ColorScheme(
                primary=ft.colors.PURPLE_ACCENT,
                secondary=ft.colors.CYAN_ACCENT,
                surface=ft.colors.SURFACE,
                background=ft.colors.BLACK,
            ),
            text_theme=ft.TextTheme(
                body_medium=ft.TextStyle(color=ft.colors.WHITE)
            )
        )
        self.current_user = None
        self.groups: Dict[str, InventoryGroup] = {}
        self.items: Dict[str, InventoryItem] = {}
        self.global_characteristics: Dict[str, Dict] = {}
        
        self.file_picker = ft.FilePicker()
        self.page.overlay.append(self.file_picker)
        
        self.setup_ui()
        self.check_auth()
        self.load_inventory_data()

    def setup_ui(self):
        self.page.bgcolor = ft.colors.BLACK
        self.page.padding = 0

        # Navigation Rail - Updated with proper icons
        self.nav_rail = ft.NavigationRail(
            selected_index=1,
            destinations=[
                ft.NavigationRailDestination(icon_content=ft.Icon(ft.icons.HOME_OUTLINED), 
                ft.NavigationRailDestination(icon_content=ft.Icon(ft.icons.INVENTORY_2_OUTLINED)),
                ft.NavigationRailDestination(icon_content=ft.Icon(ft.icons.PEOPLE_OUTLINE)),
                ft.NavigationRailDestination(icon_content=ft.Icon(ft.icons.ACCOUNT_BALANCE_WALLET_OUTLINED)),
                ft.NavigationRailDestination(icon_content=ft.Icon(ft.icons.SETTINGS_OUTLINED)),
            ],
            on_change=self.nav_change,
            min_width=80,
            extended=True,
            bgcolor=ft.colors.SURFACE,
            indicator_color=ft.colors.PURPLE_ACCENT,
            label_type=ft.NavigationRailLabelType.ALL
        )

        # Inventory View Controls
        self.view_mode = ft.Dropdown(
            options=[
                ft.dropdown.Option("icons"),
                ft.dropdown.Option("list"),
                ft.dropdown.Option("table"),
            ],
            value="icons",
            on_change=self.change_view_mode
        )
        
        self.group_filter = ft.Dropdown(
            hint_text="Filter by group",
            on_change=self.filter_items
        )
        
        self.inventory_content = ft.Column([
            ft.Row([
                ft.ElevatedButton("Add Group", on_click=self.show_add_group_dialog),
                ft.ElevatedButton("Add Item", on_click=self.show_add_item_dialog),
                self.view_mode,
                self.group_filter
            ]),
            ft.Column()  # Items will be displayed here
        ], expand=True)
        
        # Placeholder contents for other sections
        self.home_content = ft.Column([ft.Text("Home Dashboard")])
        self.customers_content = ft.Column([ft.Text("Customers Management")])
        self.purchasers_content = ft.Column([ft.Text("Purchasers Management")])
        self.settings_content = ft.Column([ft.Text("App Settings")])

        # Main Content Container
        self.main_content = ft.Container(
            content=self.inventory_content,
            padding=20,
            border_radius=10,
            bgcolor=ft.colors.with_opacity(0.2, ft.colors.SURFACE),
            expand=True
        )

        # App Layout
        self.page.add(
            ft.Row(
                [
                    self.nav_rail, 
                    ft.VerticalDivider(width=1), 
                    ft.Column([
                        self.build_appbar(),
                        ft.Divider(height=1),
                        self.main_content
                    ], expand=True)
                ],
                expand=True,
                spacing=0
            )
        )

    def build_appbar(self):
        return ft.AppBar(
            title=ft.Text("Inventory Pro", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
            center_title=False,
            bgcolor=ft.colors.SURFACE,
            actions=[
                ft.IconButton(icon=ft.icons.DARK_MODE, on_click=self.toggle_theme),
                ft.IconButton(icon=ft.icons.SYNC, on_click=self.sync_data),
                ft.PopupMenuButton(
                    icon=ft.icons.MORE_VERT,
                    items=[ft.PopupMenuItem(text="Logout", on_click=self.logout)]
                )
            ]
        )

    def nav_change(self, e):
        index = e.control.selected_index
        if index == 0:
            self.show_home()
        elif index == 1:
            self.show_inventory()
        elif index == 2:
            self.show_customers()
        elif index == 3:
            self.show_purchasers()
        elif index == 4:
            self.show_settings()

    def show_home(self):
        self.main_content.content = self.home_content
        self.page.update()

    def show_inventory(self):
        self.main_content.content = self.inventory_content
        self.display_items()
        self.page.update()

    def show_customers(self):
        self.main_content.content = self.customers_content
        self.page.update()

    def show_purchasers(self):
        self.main_content.content = self.purchasers_content
        self.page.update()

    def show_settings(self):
        self.main_content.content = self.settings_content
        self.page.update()

    # ===== INVENTORY MANAGEMENT METHODS =====
    def load_inventory_data(self):
        # Load groups from Firebase
        groups_data = db.child("inventory_groups").get().val() or {}
        for group_name, group_data in groups_data.items():
            self.groups[group_name] = InventoryGroup(
                name=group_name,
                characteristics=group_data.get("characteristics", {})
            )
        
        # Load global characteristics
        self.global_characteristics = db.child("global_characteristics").get().val() or {}
        
        # Load items
        items_data = db.child("inventory_items").get().val() or {}
        for item_id, item_data in items_data.items():
            self.items[item_id] = InventoryItem(
                name=item_data["name"],
                group=item_data["group"],
                characteristics=item_data["characteristics"],
                photo_url=item_data.get("photo_url")
            )
        
        self.update_group_filter()

    def update_group_filter(self):
        self.group_filter.options = [
            ft.dropdown.Option("All Groups")
        ] + [
            ft.dropdown.Option(group) for group in self.groups.keys()
        ]
        self.group_filter.update()

    def display_items(self, filter_group: Optional[str] = None):
        if len(self.inventory_content.controls) > 1:
            self.inventory_content.controls.pop()
        
        items_view = ft.Column()
        
        if self.view_mode.value == "icons":
            self.display_icon_view(items_view, filter_group)
        elif self.view_mode.value == "list":
            self.display_list_view(items_view, filter_group)
        else:
            self.display_table_view(items_view, filter_group)
        
        self.inventory_content.controls.append(items_view)
        self.page.update()

    def display_icon_view(self, container: ft.Column, filter_group: Optional[str] = None):
        grid = ft.GridView(
            expand=True,
            runs_count=5,
            max_extent=200,
            child_aspect_ratio=1,
            spacing=10,
            run_spacing=10,
        )
        
        for item_id, item in self.items.items():
            if filter_group and item.group != filter_group:
                continue
                
            card = ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Image(src=item.photo_url, width=150, height=100, fit=ft.ImageFit.CONTAIN) if item.photo_url else ft.Icon(ft.icons.IMAGE, size=50),
                        ft.Text(item.name, weight=ft.FontWeight.BOLD),
                        ft.Text(f"Group: {item.group}"),
                        ft.FilledButton("Details", on_click=lambda e, i=item_id: self.show_item_details(i))
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    padding=10,
                    on_click=lambda e, i=item_id: self.show_item_details(i)
                )
            )
            grid.controls.append(card)
        
        container.controls.append(grid)

    def show_add_group_dialog(self, e):
        group_name = ft.TextField(label="Group Name")
        characteristics_list = ft.Column()
        
        for char_name, char_data in self.global_characteristics.items():
            self.add_characteristic_ui(characteristics_list, char_name, char_data)
        
        new_char_name = ft.TextField(label="New Characteristic Name")
        char_type = ft.Dropdown(
            label="Type",
            options=[
                ft.dropdown.Option("text"),
                ft.dropdown.Option("number"),
                ft.dropdown.Option("dropdown"),
            ]
        )
        char_options = ft.TextField(label="Options (comma separated)", visible=False)
        char_min = ft.TextField(label="Min value", visible=False)
        char_max = ft.TextField(label="Max value", visible=False)
        
        def update_char_ui(e):
            char_options.visible = char_type.value == "dropdown"
            char_min.visible = char_type.value == "number"
            char_max.visible = char_type.value == "number"
            char_options.update()
            char_min.update()
            char_max.update()
        
        char_type.on_change = update_char_ui
        
        def add_characteristic(e):
            if not new_char_name.value:
                return
                
            char_data = {"type": char_type.value}
            
            if char_type.value == "dropdown":
                char_data["options"] = [opt.strip() for opt in char_options.value.split(",") if opt.strip()]
            elif char_type.value == "number":
                char_data["min"] = float(char_min.value) if char_min.value else None
                char_data["max"] = float(char_max.value) if char_max.value else None
            
            self.global_characteristics[new_char_name.value] = char_data
            self.add_characteristic_ui(characteristics_list, new_char_name.value, char_data)
            
            # Clear fields
            new_char_name.value = ""
            char_type.value = None
            char_options.value = ""
            char_min.value = ""
            char_max.value = ""
            
            new_char_name.update()
            char_type.update()
            char_options.update()
            char_min.update()
            char_max.update()
        
        def save_group(e):
            if not group_name.value:
                return
                
            group_chars = {}
            for control in characteristics_list.controls:
                if isinstance(control, ft.Row) and len(control.controls) > 1:
                    char_name = control.controls[0].content.value
                    include = control.controls[1].value
                    
                    if include and char_name in self.global_characteristics:
                        group_chars[char_name] = self.global_characteristics[char_name]
            
            # Save to Firebase
            db.child("inventory_groups").child(group_name.value).set({
                "name": group_name.value,
                "characteristics": group_chars
            })
            
            # Save global characteristics
            db.child("global_characteristics").set(self.global_characteristics)
            
            self.groups[group_name.value] = InventoryGroup(
                name=group_name.value,
                characteristics=group_chars
            )
            self.update_group_filter()
            self.page.dialog.open = False
            self.page.update()
        
        content = ft.Column([
            group_name,
            ft.Divider(),
            ft.Text("Select Characteristics:", weight=ft.FontWeight.BOLD),
            characteristics_list,
            ft.Divider(),
            ft.Text("Add New Characteristic:", weight=ft.FontWeight.BOLD),
            ft.Row([new_char_name, char_type]),
            char_options,
            ft.Row([char_min, char_max]),
            ft.ElevatedButton("Add Characteristic", on_click=add_characteristic)
        ], scroll=ft.ScrollMode.ALWAYS)
        
        self.page.dialog = ft.AlertDialog(
            title=ft.Text("Create New Group"),
            content=content,
            actions=[
                ft.TextButton("Save", on_click=save_group),
                ft.TextButton("Cancel", on_click=lambda e: self.close_dialog())
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            open=True
        )
        self.page.update()

    def show_add_item_dialog(self, e):
        if not self.groups:
            self.show_snackbar("Create at least one group first!", ft.colors.RED)
            return
        
        item_name = ft.TextField(label="Item Name")
        group_dropdown = ft.Dropdown(
            label="Group",
            options=[ft.dropdown.Option(group) for group in self.groups.keys()]
        )
        
        photo_display = ft.Image(width=100, height=100, visible=False)
        char_inputs = ft.Column()
        
        def select_photo(e):
            self.file_picker.pick_files(
                allowed_extensions=["jpg", "jpeg", "png"],
                on_result=lambda e: self.handle_photo_selection(e, photo_display)
            )
        
        def group_changed(e):
            char_inputs.controls.clear()
            if not group_dropdown.value:
                return
                
            group = self.groups[group_dropdown.value]
            for char_name, char_data in group.characteristics.items():
                if char_data["type"] == "text":
                    field = ft.TextField(label=char_name)
                elif char_data["type"] == "number":
                    field = ft.TextField(
                        label=char_name,
                        keyboard_type=ft.KeyboardType.NUMBER,
                        min_lines=1,
                        max_lines=1
                    )
                elif char_data["type"] == "dropdown":
                    field = ft.Dropdown(
                        label=char_name,
                        options=[ft.dropdown.Option(opt) for opt in char_data["options"]]
                    )
                char_inputs.controls.append(field)
            char_inputs.update()
        
        group_dropdown.on_change = group_changed
        
        def save_item(e):
            if not item_name.value or not group_dropdown.value:
                self.show_snackbar("Name and group are required!", ft.colors.RED)
                return
                
            characteristics = {}
            group = self.groups[group_dropdown.value]
            
            for i, (char_name, char_data) in enumerate(group.characteristics.items()):
                field = char_inputs.controls[i]
                value = field.value
                
                if char_data["type"] == "number":
                    try:
                        value = float(value)
                        if "min" in char_data and value < char_data["min"]:
                            raise ValueError(f"Must be ≥ {char_data['min']}")
                        if "max" in char_data and value > char_data["max"]:
                            raise ValueError(f"Must be ≤ {char_data['max']}")
                    except ValueError as ex:
                        self.show_snackbar(str(ex), ft.colors.RED)
                        return
                
                characteristics[char_name] = value
            
            # Upload photo if selected
            photo_url = None
            if photo_display.src and photo_display.visible:
                try:
                    storage_path = f"inventory_photos/{uuid.uuid4()}.{photo_display.src.split('.')[-1]}"
                    storage.child(storage_path).put(photo_display.src)
                    photo_url = storage.child(storage_path).get_url(None)
                except Exception as ex:
                    print(f"Photo upload error: {ex}")
            
            # Create and save item
            item_id = uuid.uuid4().hex
            new_item = InventoryItem(
                name=item_name.value,
                group=group_dropdown.value,
                characteristics=characteristics,
                photo_url=photo_url
            )
            
            db.child("inventory_items").child(item_id).set({
                "name": new_item.name,
                "group": new_item.group,
                "characteristics": new_item.characteristics,
                "photo_url": new_item.photo_url,
                "created_at": new_item.created_at,
                "last_updated": new_item.last_updated
            })
            
            self.items[item_id] = new_item
            self.display_items()
            self.close_dialog()
            self.show_snackbar("Item added!", ft.colors.GREEN)
        
        content = ft.Column([
            ft.Row([item_name, group_dropdown]),
            ft.ElevatedButton("Select Photo", on_click=select_photo),
            photo_display,
            ft.Divider(),
            char_inputs
        ], scroll=ft.ScrollMode.ALWAYS)
        
        self.page.dialog = ft.AlertDialog(
            title=ft.Text("Add New Item"),
            content=content,
            actions=[
                ft.TextButton("Save", on_click=save_item),
                ft.TextButton("Cancel", on_click=lambda e: self.close_dialog())
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            open=True
        )
        self.page.update()

    def show_item_details(self, item_id: str):
        item = self.items[item_id]
        group = self.groups.get(item.group)
        
        details = ft.Column([
            ft.Text(item.name, style=ft.TextThemeStyle.HEADLINE_MEDIUM),
            ft.Text(f"Group: {item.group}"),
            ft.Divider()
        ])
        
        if item.photo_url:
            details.controls.append(ft.Image(src=item.photo_url, width=300, height=300, fit=ft.ImageFit.CONTAIN))
            details.controls.append(ft.Divider())
        
        for char_name, value in item.characteristics.items():
            if group and char_name in group.characteristics:
                char_type = group.characteristics[char_name]["type"]
                if char_type == "dropdown":
                    options = group.characteristics[char_name]["options"]
                    details.controls.append(ft.Text(f"{char_name}: {value} (Options: {', '.join(options)})"))
                elif char_type == "number":
                    min_val = group.characteristics[char_name].get("min")
                    max_val = group.characteristics[char_name].get("max")
                    range_str = f" (Range: {min_val}-{max_val})" if min_val is not None or max_val is not None else ""
                    details.controls.append(ft.Text(f"{char_name}: {value}{range_str}"))
                else:
                    details.controls.append(ft.Text(f"{char_name}: {value}"))
            else:
                details.controls.append(ft.Text(f"{char_name}: {value}"))
        
        details.controls.extend([
            ft.Divider(),
            ft.Text(f"Created: {item.created_at}"),
            ft.Text(f"Updated: {item.last_updated}"),
            ft.Row([
                ft.FilledButton("Edit", on_click=lambda e: self.edit_item(item_id)),
                ft.FilledButton("Delete", on_click=lambda e: self.delete_item(item_id)),
            ], alignment=ft.MainAxisAlignment.END)
        ])
        
        self.page.dialog = ft.AlertDialog(
            content=details,
            actions=[ft.TextButton("Close", on_click=lambda e: self.close_dialog())],
            open=True
        )
        self.page.update()

    def edit_item(self, item_id: str):
        item = self.items[item_id]
        group = self.groups[item.group]
        
        item_name = ft.TextField(label="Item Name", value=item.name)
        photo_display = ft.Image(width=100, height=100, visible=bool(item.photo_url))
        if item.photo_url:
            photo_display.src = item.photo_url
        
        char_inputs = ft.Column()
        
        for char_name, char_data in group.characteristics.items():
            value = item.characteristics.get(char_name, "")
            
            if char_data["type"] == "text":
                field = ft.TextField(label=char_name, value=str(value))
            elif char_data["type"] == "number":
                field = ft.TextField(
                    label=char_name,
                    value=str(value),
                    keyboard_type=ft.KeyboardType.NUMBER
                )
            elif char_data["type"] == "dropdown":
                field = ft.Dropdown(
                    label=char_name,
                    options=[ft.dropdown.Option(opt) for opt in char_data["options"]],
                    value=str(value)
                )
            char_inputs.controls.append(field)
        
        def select_photo(e):
            self.file_picker.pick_files(
                allowed_extensions=["jpg", "jpeg", "png"],
                on_result=lambda e: self.handle_photo_selection(e, photo_display)
            )
        
        def save_changes(e):
            characteristics = {}
            
            for i, (char_name, char_data) in enumerate(group.characteristics.items()):
                field = char_inputs.controls[i]
                value = field.value
                
                if char_data["type"] == "number":
                    try:
                        value = float(value)
                        if "min" in char_data and value < char_data["min"]:
                            raise ValueError(f"Must be ≥ {char_data['min']}")
                        if "max" in char_data and value > char_data["max"]:
                            raise ValueError(f"Must be ≤ {char_data['max']}")
                    except ValueError as ex:
                        self.show_snackbar(str(ex), ft.colors.RED)
                        return
                
                characteristics[char_name] = value
            
            # Handle photo update
            photo_url = item.photo_url
            if photo_display.src and photo_display.src != item.photo_url:
                try:
                    storage_path = f"inventory_photos/{uuid.uuid4()}.{photo_display.src.split('.')[-1]}"
                    storage.child(storage_path).put(photo_display.src)
                    photo_url = storage.child(storage_path).get_url(None)
                except Exception as ex:
                    print(f"Photo upload error: {ex}")
            
            # Update item
            updated_item = InventoryItem(
                name=item_name.value,
                group=item.group,
                characteristics=characteristics,
                photo_url=photo_url
            )
            
            db.child("inventory_items").child(item_id).update({
                "name": updated_item.name,
                "characteristics": updated_item.characteristics,
                "photo_url": updated_item.photo_url,
                "last_updated": updated_item.last_updated
            })
            
            self.items[item_id] = updated_item
            self.display_items()
            self.close_dialog()
            self.show_snackbar("Item updated!", ft.colors.GREEN)
        
        content = ft.Column([
            item_name,
            ft.ElevatedButton("Change Photo", on_click=select_photo),
            photo_display,
            ft.Divider(),
            char_inputs
        ], scroll=ft.ScrollMode.ALWAYS)
        
        self.page.dialog = ft.AlertDialog(
            title=ft.Text("Edit Item"),
            content=content,
            actions=[
                ft.TextButton("Save", on_click=save_changes),
                ft.TextButton("Cancel", on_click=lambda e: self.close_dialog())
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            open=True
        )
        self.page.update()

    def delete_item(self, item_id: str):
        def confirm_delete(e):
            db.child("inventory_items").child(item_id).remove()
            del self.items[item_id]
            self.display_items()
            self.close_dialog()
            self.show_snackbar("Item deleted", ft.colors.RED)
        
        self.page.dialog = ft.AlertDialog(
            title=ft.Text("Confirm Delete"),
            content=ft.Text("Are you sure you want to delete this item?"),
            actions=[
                ft.TextButton("Delete", on_click=confirm_delete),
                ft.TextButton("Cancel", on_click=lambda e: self.close_dialog())
            ],
            open=True
        )
        self.page.update()

    def handle_photo_selection(self, e: ft.FilePickerResultEvent, photo_display: ft.Image):
        if e.files:
            photo_path = e.files[0].path
            photo_display.src = photo_path
            photo_display.visible = True
        else:
            photo_display.visible = False
        photo_display.update()

    def change_view_mode(self, e):
        self.display_items(self.group_filter.value if self.group_filter.value != "All Groups" else None)

    def filter_items(self, e):
        filter_group = e.control.value if e.control.value != "All Groups" else None
        self.display_items(filter_group)

    def toggle_theme(self, e):
        self.page.theme_mode = ft.ThemeMode.LIGHT if self.page.theme_mode == ft.ThemeMode.DARK else ft.ThemeMode.DARK
        self.page.update()

    def sync_data(self, e):
        self.load_inventory_data()
        self.show_snackbar("Data synced!", ft.colors.GREEN)

    def check_auth(self):
        try:
            self.current_user = auth.current_user
            if not self.current_user:
                self.show_login()
        except:
            self.show_login()

    def show_login(self):
        email_field = ft.TextField(label="Email")
        password_field = ft.TextField(label="Password", password=True)
        
        def auth_action(e):
            try:
                if e.control.text == "Login":
                    auth.sign_in_with_email_and_password(email_field.value, password_field.value)
                else:
                    auth.create_user_with_email_and_password(email_field.value, password_field.value)
                self.current_user = auth.current_user
                self.close_dialog()
                self.show_snackbar("Welcome!", ft.colors.GREEN)
            except Exception as e:
                self.show_snackbar(f"Error: {str(e)}", ft.colors.RED)
        
        self.show_dialog(
            "Login",
            ft.Column([email_field, password_field]),
            [
                ft.TextButton("Login", on_click=auth_action),
                ft.TextButton("Register", on_click=auth_action)
            ]
        )

    def logout(self, e):
        auth.sign_out()
        self.current_user = None
        self.show_login()

    def show_dialog(self, title, content, actions):
        self.page.dialog = ft.AlertDialog(
            title=ft.Text(title),
            content=content,
            actions=actions,
            bgcolor=ft.colors.SURFACE,
            open=True
        )
        self.page.update()

    def close_dialog(self, e=None):
        self.page.dialog.open = False
        self.page.update()

    def show_snackbar(self, message, color):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=color,
            duration=2000
        )
        self.page.snack_bar.open = True
        self.page.update()

if __name__ == "__main__":
    ft.app(target=InventoryPro)