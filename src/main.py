import flet as ft
import flet_audio as fa


url = "https://github.com/mdn/webaudio-examples/blob/main/audio-basics/outfoxing.mp3?raw=true"


def main(page: ft.Page):
    def change_play_pause_button(e):
        # print(e.data)
        # print(e.data == ft.AudioState.PLAYING.value)
        if e.data == ft.AudioState.PAUSED.value:
            play_pause_button.icon = ft.Icons.PLAY_ARROW
            play_pause_button.on_click = lambda e: audio1.resume()
        elif e.data == ft.AudioState.PLAYING.value:
            play_pause_button.icon = ft.Icons.PAUSE
            play_pause_button.on_click = lambda e: audio1.pause()
        play_pause_button.update()

    play_pause_button = ft.IconButton(
        icon=ft.Icons.PLAY_ARROW,
        icon_color="black",
        bgcolor="green",
        on_click=lambda _: audio1.play()
        )

    audio1 = fa.Audio(
        src=url,
        autoplay=False,
        volume=1,
        balance=0,
        on_loaded=lambda _: print("Loaded"),
        on_duration_changed=lambda e: print("Duration changed:", e.data),
        on_position_changed=lambda e: print("Position changed:", e.data),
        on_state_changed=change_play_pause_button,
        on_seek_complete=lambda _: print("Seek complete"),
    )

    page.overlay.append(audio1)
    page.add(
        ft.BottomAppBar(
            padding=3,
            content=ft.Column(
                spacing=3,
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
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.IconButton(icon=ft.Icons.SKIP_PREVIOUS, icon_color="white"),
                            play_pause_button,
                            ft.IconButton(icon=ft.Icons.SKIP_NEXT, icon_color="white")
                        ],
                    ),
                ],
            )
        )
    )


ft.app(main)
