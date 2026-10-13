from azotea_cli.provision.ports import Display

class StdoutDisplay(Display):
    def display(self, text: str) -> None:
        print(text)

__all__=["StdoutDisplay"]
