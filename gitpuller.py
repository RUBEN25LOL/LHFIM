import flet as ft
import os

def main(page: ft.Page):
    page.title = "puller"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    
    # UI Components
    text = ft.Text(
        "GET THE LATEST UPDATES FROM SERVER",
        size=15,
        weight=ft.FontWeight.BOLD
    )
    button = ft.IconButton(
        icon=ft.icons.CHECK_CIRCLE,
        icon_size=40,
        on_click=git_caller,
        tooltip="Commit changes"
    )
    
    # Layout
    page.add(
        ft.Column(
            [
                text,
                
                ft.Row([button], alignment=ft.MainAxisAlignment.CENTER)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )

def git_caller(prompt):
    # Change to your project directory if needed
    # os.chdir("/path/to/your/project")
    os.chdir("E:\github_lhfim")
    
    os.system("git pull origin main")
    

ft.app(target=main)