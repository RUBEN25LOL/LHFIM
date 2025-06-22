import flet as ft
import os
import subprocess

def main(page: ft.Page):
    page.title = "Commiter"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    
    # UI Components
    text1 = ft.Text("UNSAVED PLEASE SAVE", 
                   weight=ft.FontWeight.BOLD,
                   text_align=ft.TextAlign.CENTER)
    
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
    
    output_text = ft.Text()  # To display git command output
    
    def commit_changes(e):
        if textfield.value:  # Only commit if there's a message
            text1.value = "SAVING PLEASE WAIT..."
            page.update()
            
            output = git_caller(textfield.value)
            output_text.value = "\n".join(output)
            
            page.snack_bar = ft.SnackBar(ft.Text("Changes committed successfully!"))
            text1.value = "SAVED SUCCESSFULLY"
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Please enter a commit message!"))
        
        textfield.value = ""
        page.snack_bar.open = True
        page.update()
    
    button = ft.IconButton(
        icon=ft.Icons.CHECK_CIRCLE,
        icon_size=40,
        on_click=commit_changes,
        tooltip="Commit changes"
    )
    
    # Layout
    page.add(
        ft.Column(
            [
                text,
                ft.Row([textfield], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([button], alignment=ft.MainAxisAlignment.CENTER),
                text1,
                ft.Container(
                    content=output_text,
                    alignment=ft.alignment.top_center,
                    border=ft.border.all(1),
                    border_radius=10,
                    padding=10,
                    width=500
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )

def git_caller(prompt):
    output = []
    try:
        # Change to your project directory
        
        
        # Run git commands and capture output
        result = subprocess.run(["git", "add", "."], 
                              capture_output=True, 
                              text=True)
        output.append(result.stdout)
        
        result = subprocess.run(["git", "commit", "-m", prompt],
                              capture_output=True,
                              text=True)
        output.append(result.stdout)
        
        result = subprocess.run(["git", "push", "origin", "main"],
                              capture_output=True,
                              text=True)
        output.append(result.stdout)
        
    except Exception as e:
        output.append(f"Error: {str(e)}")
    
    return output

ft.app(target=main)