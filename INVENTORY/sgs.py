import flet as ft
from flet import colors, icons

def main(page: ft.Page):
    # 1. Configure page first
    page.title = "Snackbar Test"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    # 2. Create a snackbar and add to page (important!)
    page.snack_bar = ft.SnackBar(
        content=ft.Text(""),  # Empty text by default
        show_close_icon=True,
        bgcolor=colors.GREEN_400,
        duration=3000  # 3 seconds
    )
    
    # 3. Button click handler
    def show_snackbar(e):
        # Update snackbar content
        page.snack_bar.content = ft.Text("Hello! This snackbar works!")
        page.snack_bar.bgcolor = colors.BLUE_800
        
        # Open and update
        page.snack_bar.open = True
        page.update()  # THIS LINE IS CRUCIAL
    
    # 4. Add a button to trigger it
    page.add(
        ft.ElevatedButton(
            "Click to show Snackbar",
            icon=icons.CHECK_CIRCLE,
            on_click=show_snackbar
        )
    )

ft.app(target=main)