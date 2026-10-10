from azotea_cli.provision.interfaces import IDisplay

class StdoutDisplay(IDisplay):
    def display(self, text: str) -> None:
        print(text)

__all__=["StdoutDisplay"]
