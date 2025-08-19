from dash import Dash
from modules.layout import layout
from modules.callbacks import register_callbacks

# 🚀 Initialisation de l'app Dash
app = Dash(__name__, suppress_callback_exceptions=True)
app.title = "International Investment"
app.layout = layout

# 🔗 Enregistrement des callbacks
register_callbacks(app)

# ▶️ Lancement de l'application
if __name__ == '__main__':
    app.run(debug=True)