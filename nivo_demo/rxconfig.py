import reflex as rx

config = rx.Config(
    app_name="nivo_demo",
    # Dedicated ports: a browser tab still open from another Reflex app on the
    # default 3000/8000 would reconnect its socket to this backend and fail with
    # "no dispatch function for substate(s)" (its frontend has other states).
    frontend_port=3010,
    backend_port=8010,
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
        rx.plugins.RadixThemesPlugin(theme=rx.theme(accent_color="iris", radius="large")),
    ],
)
