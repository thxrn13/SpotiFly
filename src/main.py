import flet as ft
import configparser
from state import AppState

config = configparser.ConfigParser()
config.read('.config')
PORT = config.getint('General', 'PORT')


def main(page: ft.Page):
    # Create helper instance
    app_state = AppState(page)
    logged_user = app_state.logged_user
    page.on_login = app_state.on_login
    page.on_logout = app_state.on_logout
    page.appbar = ft.AppBar(
        leading=ft.IconButton(
            icon=ft.Icons.MENU,
            icon_color="white",
            on_click=lambda _: page.go("/"),
        ),
        title=ft.Text("SpotiFly"),
        center_title=True,
        bgcolor="black",
        actions=[
            app_state.logout_button,
            ft.IconButton(
                icon=ft.Icons.SETTINGS,
                icon_color="white",
                on_click=lambda _: page.go("/settings"),
            ),
        ]
    )

    # Create route for the main view
    def route_change(route):
        page.views.clear()
        page.views.append(
            ft.View(
                "/",
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            app_state.login_button,
                            logged_user,
                        ],
                    ),
                    ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.START,
                        expand=True,
                        controls=[
                            app_state.playlists_view,
                        ],
                        scroll=ft.ScrollMode.AUTO,
                    ),
                ],
                bottom_appbar=ft.BottomAppBar(
                                padding=5,
                                content=ft.Column(
                                    spacing=5,
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    controls=[
                                        ft.Row(
                                            alignment=ft.MainAxisAlignment.CENTER,
                                            controls=[
                                                ft.Text("LOREM IPSUM")
                                            ]
                                        ),
                                        ft.Row(
                                            alignment=ft.MainAxisAlignment.CENTER,
                                            vertical_alignment=ft.CrossAxisAlignment
                                            .CENTER,
                                            controls=[
                                                ft.IconButton(
                                                    icon=ft.Icons.SKIP_PREVIOUS,
                                                    icon_color="white"
                                                ),
                                                app_state.play_pause_button,
                                                ft.IconButton(
                                                    icon=ft.Icons.SKIP_NEXT,
                                                    icon_color="white"
                                                )
                                            ],
                                        ),
                                    ],
                                )
                            ),
                appbar=page.appbar,
            ),
        )
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)


ft.app(main, port=PORT, view=ft.WEB_BROWSER)  # type: ignore
