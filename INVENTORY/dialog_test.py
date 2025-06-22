import flet as ft

def main(page: ft.Page):

    def close_modal(e=None):
        modal.visible = False
        page.update()

    def show_modal(e):
        modal.visible = True
        page.update()

    # Fake dialog using container
    modal = ft.Container(
        visible=False,
        bgcolor=ft.Colors.WHITE,
        width=300,
        padding=20,
        border_radius=10,
        content=ft.Column([
            ft.Text("This is a custom dialog box"),
            ft.ElevatedButton("Close", on_click=close_modal)
        ]),
        alignment=ft.alignment.center,
    )

    # Add modal and button
    page.add(
        ft.ElevatedButton("Open Dialog", on_click=show_modal),
        modal
    )

    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.bgcolor = ft.Colors.BLACK26

ft.app(target=main)
