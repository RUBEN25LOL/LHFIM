import flet as ft

def main(page: ft.Page):
    page.title = "Flet GridView Example"
    page.padding = 20  # Adds padding around the GridView
    
    # Define a GridView with 3 columns and max item width of 150
    grid = ft.GridView(
        runs_count=3,          # Number of columns (items per row)
        max_extent=150,        # Maximum width of each item
        spacing=10,            # Horizontal spacing between items
        run_spacing=10,        # Vertical spacing between rows
        controls=[
            ft.Container(
                content=ft.Text(f"Item {i + 1}", color="white", size=20),
                alignment=ft.alignment.center,
                bgcolor=ft.colors.BLUE_500,
                border_radius=ft.border_radius.all(10),
                height=100,     # Fixed height for all items
            )
            for i in range(10)  # Creates 10 containers
        ],
    )
    
    page.add(grid)  # Add the GridView to the page

ft.app(target=main)