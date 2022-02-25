from goldwhims_scripts.enums.string_enums import GoldenWhimsStringId
from sims4communitylib.events.event_handling.common_event_registry import CommonEventRegistry
from sims4communitylib.events.zone_spin.events.zone_late_load import S4CLZoneLateLoadEvent
from sims4communitylib.notifications.common_basic_notification import CommonBasicNotification


class GoldenWhimsShowLoadedMessage:
    @staticmethod
    def show_loaded_notification() -> None:
        notification = CommonBasicNotification(
            GoldenWhimsStringId.GOLDWHIMS_LOADED_NOTIFICATION_TITLE,
            GoldenWhimsStringId.GOLDWHIMS_LOADED_NOTIFICATION_DESCRIPTION
        )
        notification.show()

    @staticmethod
    @CommonEventRegistry.handle_events('goldwhims')
    def _show_loaded_notification_when_loaded(event_data: S4CLZoneLateLoadEvent):
        if event_data.game_loaded:
            return

        GoldenWhimsShowLoadedMessage.show_loaded_notification()
