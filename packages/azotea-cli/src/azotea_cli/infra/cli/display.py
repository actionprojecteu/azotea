from azotea_cli.provision.interfaces import Display

class StdoutDisplay(Display):
    def display(self, text: str) -> None:
        print(text)

__all__=["StdoutDisplay"]
