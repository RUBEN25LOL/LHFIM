import flet as ft
import os

def main(page: ft.Page):
    page.title = "Commiter"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    
    # UI Components
    text1=ft.Text("UNSAVED PLEASE SAVE",weight=ft.FontWeight.BOLD,text_align=ft.TextAlign.CENTER)
    text = ft.Text(
        "CLICK TO SAVE ALL THE CHANGES MADE IN THE FILE TO ALL THE SYSTEM:",
        size=15,
        weight=ft.FontWeight.BOLD
    )
    
    textfield = ft.TextField(
        hint_text="ENTER THE NAME OF THE SAVE",
        width=300,
        text_align=ft.TextAlign.CENTER
    )
    
    def commit_changes(e):
        if textfield.value:  # Only commit if there's a message
            text1.value="SAVING PLEASE WAIT"
            git_caller(textfield.value)
            page.snack_bar = ft.SnackBar(ft.Text("Changes committed successfully!"))
            page.snack_bar.open = True
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Please enter a commit message!"))
            page.snack_bar.open = True
        textfield.value=""
        text1.value="SAVED SUCCESSFULLY"
        page.update()
    
    


    button1= ft.IconButton(
        icon=ft.icons.CHECK_CIRCLE,
        icon_size=40,
        on_click=lambda e :(setattr(text1,"value","SAVING PLEASE WAIT"),commit_changes(None)),
        tooltip="Commit changes"
    )
    
    # Layout
    page.add(
        ft.Column(
            [
                text,
                ft.Row([textfield], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([button1], alignment=ft.MainAxisAlignment.CENTER),
                text1
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )

def git_caller(prompt):
    # Change to your project directory if needed
    # os.chdir("/path/to/your/project")
    os.chdir("E:\github_lhfim")
    
    os.system("git add .")
    os.system(f'git commit -m "{prompt}"')
    os.system("git push origin main")

ft.app(target=main)