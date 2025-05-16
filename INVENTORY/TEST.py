import flet as ft
import sqlite3


def table_creater(name,listofcolumns):
    cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS {name} (
        name TEXT NOT NULL)''')
    connection.commit()
    for i in range(len(listofcolumns)):
        cursor.execute(f''' 
        ALTER TABLE {name} ADD COLUMN {listofcolumns[i]} TEXT''')


def table_reader(name, listofcolumns):
   
    try:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        
        if len(listofcolumns) == 0:
            cursor.execute(f"SELECT * FROM {name}")
        else:
            # Escape column names to prevent SQL injection and join them
            columns = ", ".join(f"[{col}]" for col in listofcolumns)
            cursor.execute(f"SELECT {columns} FROM {name}")
        
        rows = cursor.fetchall()
        return rows
    except sqlite3.Error as e:
        print(f"Error reading table {name}: {e}")
        return []


def table_writer(name, dictionary_of_values):
    try:
        # Extract columns and rows
        columns = list(dictionary_of_values.keys())
        num_rows = len(dictionary_of_values[columns[0]])
        
        # Ensure all columns have the same number of rows
        for col in columns:
            if len(dictionary_of_values[col]) != num_rows:
                raise ValueError(f"Column '{col}' has inconsistent row count.")

        # Insert row by row
        for i in range(num_rows):
            values = [dictionary_of_values[col][i] for col in columns]
            placeholders = ", ".join(["?"] * len(columns))
            column_names = ", ".join(f"[{col}]" for col in columns)  # Escape names with brackets
            cursor.execute(
                f"INSERT INTO {name} ({column_names}) VALUES ({placeholders})",
                values
            )
        
        connection.commit()
        print("Rows inserted successfully.")
        
    except sqlite3.Error as e:
        print(f"Error writing to table {name}: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


class Parent:
    def __init__(self, page: ft.Page):
        self.page = page
        
        
    def main_scene(self):
        self.page.controls.clear()  # Clear existing controls
        self.inventory_button = ft.ElevatedButton(
            text="Go to Inventory", 
            icon_color="gray", 
            on_click=self.show_inventory_scene
        )
        self.buyers_button = ft.ElevatedButton(
            text="Go to Buyers", 
            icon_color="gray", 
            on_click=self.show_buyers_scene
        )
        self.customers_button = ft.ElevatedButton(
            text="Go to Customers", 
            icon_color="gray", 
            on_click=self.show_customers_scene
        )
        self.settings_button = ft.ElevatedButton(
            text="Go to Settings", 
            icon_color="gray", 
            on_click=self.show_settings_scene
        )
        self.reports_button = ft.ElevatedButton(
            text="Go to Reports", 
            icon_color="gray", 
            on_click=self.show_reports_scene
        )
        self.toggle_button = ft.ElevatedButton(
            text="toggle theme", 
            icon_color="gray", 
            on_click=self.toggle_theme
        )
        self.main_column = ft.Column(controls=[
            ft.Text("Main Menu", size=20, weight=ft.FontWeight.BOLD),
            self.inventory_button,
            self.buyers_button,
            self.customers_button,
            self.settings_button,
            self.reports_button,
            self.toggle_button
        ])
        self.page.add(ft.Container(content=self.main_column, alignment=ft.alignment.top_left))
        self.page.update()

    def show_inventory_scene(self, e):
        self.page.controls.clear()
        main_text = ft.Text("INVENTORY", size=25, weight=ft.FontWeight.BOLD)
        exit_button = ft.IconButton(ft.Icons.EXIT_TO_APP_ROUNDED, on_click=self.back_to_main)
        temp2 = ft.Row(
         controls=[
            ft.Container(content=exit_button, alignment=ft.alignment.top_left),
            ft.Container(content=main_text, alignment=ft.alignment.center, expand=True)
        ]
    )
        group_creation = ft.Icon(ft.Icons.ADD_BOX_ROUNDED)
        group_text = ft.Text("ADD A NEW CATEGORY", text_align=ft.TextAlign.CENTER)
        inventory_icon=ft.Icon(ft.Icons.WAREHOUSE,tooltip="INVENTORY")
        edit_icon=ft.Icon(ft.Icons.EDIT)
    
    # Place icon and text in a Row to align them horizontally, centered
        add_group_row = ft.Column(
        controls=[
            group_creation,
            group_text
        ],
        alignment=ft.MainAxisAlignment.CENTER,  # Center horizontally
        horizontal_alignment=ft.CrossAxisAlignment.CENTER  # Center vertically
    )
    
        temp1 = ft.Container(
        content=ft.Column(controls=[add_group_row], alignment=ft.MainAxisAlignment.CENTER),
        alignment=ft.alignment.center,
        padding=15,
        on_click=self.add_category_scene,
        ink=True,
        ink_color=ft.Colors.AMBER_100
    )

        text3=ft.Text("ADD A NEW ITEM",text_align=ft.TextAlign.CENTER)
        add_group_row2= ft.Column(
        controls=[
            group_creation,
            text3
        ],
        alignment=ft.MainAxisAlignment.CENTER,  # Center horizontally
        horizontal_alignment=ft.CrossAxisAlignment.CENTER  # Center vertically
    )
        temp3= ft.Container(
        content=ft.Column(controls=[add_group_row2], alignment=ft.MainAxisAlignment.CENTER),
        alignment=ft.alignment.center,
        padding=15,
        on_click=lambda e: print(" new item button clicked"),
        ink=True,
        ink_color=ft.colors.AMBER_100)

        text4=ft.Text("VIEW INVENTORY ",text_align=ft.TextAlign.CENTER)
        add_group_row3= ft.Column(
        controls=[
            inventory_icon,
            text4
        ],
        alignment=ft.MainAxisAlignment.CENTER,  # Center horizontally
        horizontal_alignment=ft.CrossAxisAlignment.CENTER  # Center vertically
    )
        temp4= ft.Container(
        content=ft.Column(controls=[add_group_row3], alignment=ft.MainAxisAlignment.CENTER),
        alignment=ft.alignment.center,
        padding=15,
        on_click=lambda e: print(" INVENTORY button clicked"),
        ink=True,
        ink_color=ft.colors.AMBER_100)





        text5=ft.Text("EDIT CATEGORY ",text_align=ft.TextAlign.CENTER)
        add_group_row4= ft.Column(
        controls=[
            edit_icon,
            text5
        ],
        alignment=ft.MainAxisAlignment.CENTER,  # Center horizontally
        horizontal_alignment=ft.CrossAxisAlignment.CENTER  # Center vertically
    )
        temp5= ft.Container(
        content=ft.Column(controls=[add_group_row4], alignment=ft.MainAxisAlignment.CENTER),
        alignment=ft.alignment.center,
        padding=15,
        on_click=lambda e: print(" edit category button clicked"),
        ink=True,
        ink_color=ft.Colors.AMBER_100)



        text6=ft.Text("EDIT ITEM ",text_align=ft.TextAlign.CENTER)
        add_group_row5= ft.Column(
        controls=[
            edit_icon,
            text6
        ],
        alignment=ft.MainAxisAlignment.CENTER,  # Center horizontally
        horizontal_alignment=ft.CrossAxisAlignment.CENTER  # Center vertically
    )
        temp6= ft.Container(
        content=ft.Column(controls=[add_group_row5], alignment=ft.MainAxisAlignment.CENTER),
        alignment=ft.alignment.center,
        padding=15,
        on_click=lambda e: print(" edit item button clicked"),
        ink=True,
        ink_color=ft.colors.AMBER_100)
        







        self.page.add(ft.Column(controls=[temp2, temp1,temp3,temp4,temp5,temp6]))
        self.page.update()
    
    def show_buyers_scene(self, e):
        self.page.controls.clear()
        self.page.add(
            ft.Container(
                content=ft.Column([
                    ft.Text("Buyers Scene", size=20, weight=ft.FontWeight.BOLD),
                    ft.Text("View buyer information here."),
                    ft.ElevatedButton("Back to Main Menu", on_click=self.back_to_main)
                ]),
                alignment=ft.alignment.center
            )
        )
        self.page.update()

    def show_customers_scene(self, e):
        self.page.controls.clear()
        self.page.add(
            ft.Container(
                content=ft.Column([
                    ft.Text("Customers Scene", size=20, weight=ft.FontWeight.BOLD),
                    ft.Text("Manage customer data here."),
                    ft.ElevatedButton("Back to Main Menu", on_click=self.back_to_main)
                ]),
                alignment=ft.alignment.center
            )
        )
        self.page.update()

    def show_settings_scene(self, e):
        self.page.controls.clear()
        self.page.add(
            ft.Container(
                content=ft.Column([
                    ft.Text("Settings Scene", size=20, weight=ft.FontWeight.BOLD),
                    ft.Text("Adjust app settings here."),
                    ft.ElevatedButton("Back to Main Menu", on_click=self.back_to_main)
                ]),
                alignment=ft.alignment.center
            )
        )
        self.page.update()

    def show_reports_scene(self, e):
        self.page.controls.clear()
        self.page.add(
            ft.Container(
                content=ft.Column([
                    ft.Text("Reports Scene", size=20, weight=ft.FontWeight.BOLD),
                    ft.Text("View reports here."),
                    ft.ElevatedButton("Back to Main Menu", on_click=self.back_to_main)
                ]),
                alignment=ft.alignment.center
            )
        )
        self.page.update()
    
    def back_to_main(self, e):
        self.main_scene()

    def toggle_theme(self,e):
        page = self.page
        page.theme_mode = ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        page.update()
    
    def add_category_scene(self,e):
        categ_list=["a","v","s","e","s","i","t","s","s","i","t"]
        self.page.controls.clear()
        main_text = ft.Text("ADD A NEW CATEGORY", size=25, weight=ft.FontWeight.BOLD)
        exit_button = ft.IconButton(ft.Icons.EXIT_TO_APP_ROUNDED, on_click=self.show_inventory_scene)
        temp = ft.Row(
         controls=[
            ft.Container(content=exit_button, alignment=ft.alignment.top_left),
            ft.Container(content=main_text, alignment=ft.alignment.center, expand=True)])
        
        text1 = ft.Text("ENTER THE NAME :", size=25, weight=ft.FontWeight.BOLD)
        textfield1=ft.TextField(hint_text="ENTER THE NAME : ")
        text2=ft.Text("SELECT THE TYPE OF CATEGORY : ",size=25, weight=ft.FontWeight.BOLD)
        text21=ft.TextField(hint_text="PLEASE SELECT ")
        options_menu=ft.PopupMenuButton(
            items= [
                     ft.PopupMenuItem(text="text",),
                     ft.PopupMenuItem(text="numbers",on_click=lambda e :(setattr(text21,"value","numbers"),self.page.update())),
                     ft.PopupMenuItem(text="yes/no",on_click=lambda e :(setattr(text21,"value","yes/no"),self.page.update())),
                     ft.PopupMenuItem(text="date",on_click=lambda e :(setattr(text21,"value","yes/no"),self.page.update())),
                     ft.PopupMenuItem(text="percentage",on_click=lambda e :(setattr(text21,"value","percentage"),self.page.update())),
                     ft.PopupMenuItem(text="price",on_click=lambda e :(setattr(text21,"value","price"),self.page.update()))],
                      )
        text3=ft.Text("CAN BE EMPTY OR NOT ?  NO  ",size=25, weight=ft.FontWeight.BOLD)
        text31=ft.Text("  YES",size=25, weight=ft.FontWeight.BOLD)
        switch=ft.Switch(
            value=False,
            active_color=ft.Colors.LIGHT_BLUE_ACCENT,
            inactive_track_color=ft.Colors.RED_ACCENT,
            thumb_color=ft.Colors.WHITE24)
        
        
        text4=ft.Text(" SAVE ",size=25, weight=ft.FontWeight.BOLD)
        icon=ft.Icon(ft.Icons.WAREHOUSE_SHARP)
        save_button=ft.Container(
            content=ft.Column(controls=[text4,icon],
            alignment=ft.MainAxisAlignment.CENTER,  
            horizontal_alignment=ft.CrossAxisAlignment.CENTER ),
            on_click=lambda e:(self.add_category_scene(None),),
            ink=True,
            alignment=ft.alignment.center,
            ink_color=ft.colors.AMBER_100)
       
       
        text5=ft.Text("    CANCEL ",size=25, weight=ft.FontWeight.BOLD)
        icon1=ft.Icon(ft.Icons.CANCEL)
     # Create individual Text widgets for each category
        category_widgets = [
            ft.Text(category, size=20, weight=ft.FontWeight.BOLD,text_align=ft.TextAlign.CENTER)
            for category in categ_list
            ]

        scrollable_content = ft.ListView(
        controls=[
        ft.Text("PREVIOUS CATEGORIES ADDED", size=20, weight=ft.FontWeight.BOLD,text_align=ft.TextAlign.CENTER),
            *category_widgets  # Unpack all category widgets
              ],
            spacing=10,  # Space between items
            height=200,  # Fixed height
            auto_scroll=False  # Set to True if you want auto-scroll to bottom
            )

        temp6 = ft.Container(
            content=scrollable_content,
            alignment=ft.alignment.top_center,
            border=ft.border.all(1),
            border_radius=10
            )

        cancel_button=ft.Container(
            content=ft.Column(controls=[text5,icon1],
            alignment=ft.MainAxisAlignment.CENTER,  
            horizontal_alignment=ft.CrossAxisAlignment.CENTER ),
            on_click=lambda e:(self.add_category_scene(None),),
            ink=True,
            alignment=ft.alignment.center,
            ink_color=ft.colors.AMBER_100)
        
        buttonrow=ft.Row(controls=[save_button,cancel_button],alignment=ft.MainAxisAlignment.CENTER)
        
        
        
        temp1=ft.Row(controls=[
            ft.Container(content=text1),
            ft.Container(content=textfield1)],
            alignment=ft.alignment.center)

        temp2=ft.Row(controls=[
            ft.Container(content=text2),
            ft.Container(content=text21),
            ft.Container(content=options_menu)],
            alignment=ft.alignment.center)

        temp3=ft.Row(controls=[
            ft.Container(content=text3),
            ft.Container(content=switch),
             ft.Container(content=text31)],
            alignment=ft.CrossAxisAlignment.CENTER
            )
        
        
        
        self.page.add(ft.Column(controls=[temp,temp1,temp2,temp3,buttonrow,temp6],alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.MainAxisAlignment.CENTER))
        self.page.add()
        self.page.update()











    def run_app(self):
        def main(page: ft.Page):
            self.page = page
            theme = ft.Theme(
            primary_color=ft.colors.BLUE
            
            )
            
            self.page.theme_mode=ft.ThemeMode.DARK
            self.main_scene()  # Start with the main scene
        ft.app(target=main)

# Create an instance of Parent and run the app
connection=sqlite3.connect("mydb.db")
cursor=connection.cursor()

parent = Parent(None)  # Temporarily pass None for page; it will be set in run_app
parent.run_app()