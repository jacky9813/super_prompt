import typing

ANSIColor = int
class RGBColor(typing.NamedTuple):
    R: int
    G: int
    B: int
Color = typing.Union[ANSIColor, RGBColor]

LogoCharacter = str
CurrentContext = str

class PluginResponse(typing.NamedTuple):
    logo: str
    context: str
    logo_color: typing.Optional[Color]

PluginEntrypoint = typing.Callable[[typing.Dict[str, str]], typing.Optional[PluginResponse]]


class ConfigHint(typing.NamedTuple):
    key: str
    help: str
    default: str
    value_type: type

    def __str__(self) -> str:
        type_name = self.value_type.__name__ if hasattr(self.value_type, "__name__") else "N/A"
        if type_name == "<lambda>":
            type_name = "N/A"
        return f'{self.key} ({type_name}): {self.help} (Default:{self.default})'
