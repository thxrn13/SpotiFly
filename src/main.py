import flet as ft
import configparser
from _utils.state import AppState

config = configparser.ConfigParser()
config.read('.config')
PORT = config.getint('General', 'PORT')


def main(page: ft.Page):
    app_state = AppState(page)

    # Create route for the main view
    def route_change(route):
        page.views.clear()
        page.views.append(
            app_state.view_store.main_view
        )
        if page.route == '/client_id_form':
            page.views.append(
                app_state.view_store.client_id_form
            )

        if page.route == '/settings':
            page.views.append(
                app_state.view_store.settings
            )
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.appbar = app_state.control_store.app_bar
    app_state.check_logged_in()

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)


ft.app(main, port=PORT, view=ft.WEB_BROWSER)  # type: ignore
