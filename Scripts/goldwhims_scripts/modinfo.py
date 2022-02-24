from sims4communitylib.mod_support.common_mod_info import CommonModInfo


class ModInfo(CommonModInfo):
    # To create a Mod Identity for this mod, simply do ModInfo.get_identity().
    _FILE_PATH: str = str(__file__)

    @property
    def _name(self) -> str:
        return 'GoldenWhims'

    @property
    def _author(self) -> str:
        # This is your name.
        return 'Quietbird'

    @property
    def _base_namespace(self) -> str:
        # This is the name of the root package
        return 'goldwhims_scripts'

    @property
    def _file_path(self) -> str:
        # This is simply a file path that you do not need to change.
        return ModInfo._FILE_PATH
