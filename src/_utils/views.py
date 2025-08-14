import flet as ft


class ViewStore:
    def __init__(self, app_state, control_store):
        self.app_state = app_state
        self.control_store = control_store

        self.main_view = ft.View(
                        "/",
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    self.control_store.login_button,
                                    self.control_store.logged_user
                                ],
                            ),
                            ft.Row(
                                controls=[
                                    ft.Column(
                                        controls=[
                                            self.control_store.playlists_view,
                                        ],
                                        scroll=ft.ScrollMode.AUTO,
                                        expand=True,
                                        horizontal_alignment=ft.CrossAxisAlignment.STRETCH
                                    ),
                                    ft.Column(
                                        controls=[
                                            self.control_store.tracks_view
                                        ],
                                        scroll=ft.ScrollMode.AUTO,
                                        expand=True,
                                        horizontal_alignment=ft.CrossAxisAlignment.STRETCH
                                    ),
                                ],
                                expand=True,
                            ),
                        ],
                        bottom_appbar=self.control_store.bottom_app_bar,
                        appbar=self.control_store.app_bar,
                    )

        self.client_id_form = ft.View(
                    '/client_id_form',
                    controls=[
                        ft.Row(
                            controls=[
                                self.control_store.client_id_input_field,
                                self.control_store.client_id_submit_button,
                            ]
                        )
                    ]
                )

        self.settings = ft.View(
                    '/settings',
                    controls=[
                        ft.Column(
                            controls=[
                                self.control_store.client_id_input_field,
                                self.control_store.client_id_submit_button,
                                self.control_store.clear_client_id_button
                            ]
                        )
                    ],
                    appbar=self.control_store.app_bar
                )
