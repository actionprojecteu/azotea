from . import register, statistics

from .interfaces import IProcessing

class Processing(IProcessing):
    def register(self, images_dir: str, depth: int) -> None:
        register.register(images_dir, depth)
    def statistics(self) -> None:
        statistics.compute()
