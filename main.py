"""Point d'entrée de l'application."""

from UI.main_menu import MainMenu


def main():
    app = MainMenu()
    app.mainloop()


if __name__ == "__main__":
    main()
