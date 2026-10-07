class AzoteaError(Exception):
    """Azotea Error"""
    def __str__(self):
           msg = self.__doc__
           return f"{msg}: {self.args[0]}." if self.args else f"{msg}."
