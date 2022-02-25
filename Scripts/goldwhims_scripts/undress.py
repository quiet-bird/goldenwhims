from turbolib2.events.interactions import register_interaction_run_event_method
from turbolib2.events.zone_spin import has_game_loaded, register_zone_teardown_event
from turbolib2.gizmos.looping_buffs import LoopingBuff
from turbolib2.services.cas_service import TurboOutfitCategory, TurboBodyType
from turbolib2.services.sims_service import get_sims_service, AllSimsGenAgeRule
from turbolib2.wrappers.enum import TurboIntEnum
from turbolib2.wrappers.sim.age import TurboAge
from turbolib2.wrappers.sim.sim import TurboSim
from turbolib2.wrappers.sim.species import TurboSpecies
from enums.buffs_enum import SimBuff
from enums.interactions_enum import SimInteraction
from enums.motives_enum import SimMotive
from enums.statistics_enum import SimStatistic
from wickedwhims.nudity.body.penis.penis_state import set_sim_penis_state
from wickedwhims.nudity.body.sim_body_state import BodyState, get_sim_body_state, set_sim_top_naked_state, set_sim_bottom_naked_state, is_sim_outfit_fullbody, has_sim_outfit_bottom
from wickedwhims.nudity.body.sim_outfit_utils import StripType, strip_outfit, dress_up_outfit
from wickedwhims.nudity.features.underwear.operator import get_sim_underwear_data
from wickedwhims.nudity.features.underwear.outfit import set_sim_underwear_state, has_sim_underwear, get_sim_underwear_state
from wickedwhims.nudity.nudity_settings import NuditySetting, get_nudity_setting
from wickedwhims.nudity.outfit_nudity_reason import NudityReason
from wickedwhims.utils_cas import get_modified_outfit, get_sim_outfit_cas_part, set_body_type_cas_part, is_sim_in_special_outfit
from wickedwhims.nudity.features.situational_undressing.peeing import PeeingOutfitUpdate, OutfitStateBeforePeeing
from goldwhims_scripts.enums.tuning_enums import GoldWhimsTuningId
from goldwhims_scripts.modinfo import ModInfo
from sims.sim import Sim
from sims4communitylib.utils.common_injection_utils import CommonInjectionUtils

PEEING_INTERACTIONS = {
    GoldWhimsTuningId.WWHIMS_INTERACTION_PEE_MALE,
    GoldWhimsTuningId.GWHIMS_INTERACTION_PEE_F_MIDSQUAT_0,
    GoldWhimsTuningId.GWHIMS_INTERACTION_PEE_F_HISQUAT_0
}


def _undress_bottom(sim: Sim):
    if not has_game_loaded():
        return
    if not get_nudity_setting(NuditySetting.PEEING_UNDRESS_STATE):
        return

    turbo_sim = TurboSim(sim)

    if turbo_sim.get_age() < TurboAge.TEEN:
        return
    if get_nudity_setting(NuditySetting.TEENS_NUDITY_STATE) and turbo_sim.get_age() == TurboAge.TEEN:
        return
    if turbo_sim.has_buff(SimBuff.WW_NUDITY_SPECIAL_PEEING_OUTFIT_UPDATE):
        return

    if has_sim_outfit_bottom(turbo_sim):
        bottom_body_state = get_sim_body_state(turbo_sim, TurboBodyType.LOWER_BODY)
        if bottom_body_state != BodyState.NUDE:
            strip_result = strip_outfit(turbo_sim,
                                        strip_type_bottom=StripType.NUDE,
                                        allow_stripping_feet=False,
                                        nudity_reason=NudityReason.TEMP_TOILET_USE)
            if strip_result:
                turbo_sim.set_statistic_value(SimStatistic.WW_NUDITY_SPECIAL_PEEING_OUTFIT_STATE,
                                              OutfitStateBeforePeeing.UNDERWEAR if bottom_body_state == BodyState.UNDERWEAR else OutfitStateBeforePeeing.OUTFIT)
                set_sim_bottom_naked_state(turbo_sim, True)
                set_sim_underwear_state(turbo_sim, TurboBodyType.LOWER_BODY, False)
                turbo_sim.add_buff(SimBuff.WW_NUDITY_SPECIAL_PEEING_OUTFIT_UPDATE)
    elif is_sim_outfit_fullbody(turbo_sim):
        top_state = StripType.UNDERWEAR if has_sim_underwear(turbo_sim, TurboBodyType.UPPER_BODY) and get_sim_underwear_state(turbo_sim, TurboBodyType.UPPER_BODY) else StripType.NUDE
        strip_result = strip_outfit(turbo_sim, strip_type_top=top_state, strip_type_bottom=StripType.NUDE, nudity_reason=NudityReason.TEMP_TOILET_USE)
        if strip_result:
            turbo_sim.set_statistic_value(SimStatistic.WW_NUDITY_SPECIAL_PEEING_OUTFIT_STATE,
                                          OutfitStateBeforePeeing.OUTFIT)
            set_sim_top_naked_state(turbo_sim, True)
            set_sim_bottom_naked_state(turbo_sim, True)
            set_sim_underwear_state(turbo_sim, TurboBodyType.LOWER_BODY, False)
            turbo_sim.add_buff(SimBuff.WW_NUDITY_SPECIAL_PEEING_OUTFIT_UPDATE)


@CommonInjectionUtils.inject_safely_into(ModInfo.get_identity(), PeeingOutfitUpdate, PeeingOutfitUpdate.update.__name__)
def override_peeing_outfit_update(original, self, *args, **kwargs):
    turbo_sim = self.get_turbo_sim()
    peeing_outfit_state = turbo_sim.get_statistic_value(SimStatistic.WW_NUDITY_SPECIAL_PEEING_OUTFIT_STATE)

    if peeing_outfit_state == OutfitStateBeforePeeing.NONE or not is_sim_in_special_outfit(turbo_sim):
        turbo_sim.remove_buff(SimBuff.WW_NUDITY_SPECIAL_PEEING_OUTFIT_UPDATE)
        return
    if not turbo_sim.is_interaction_running(*PEEING_INTERACTIONS):
        _dress_up_sim_from_peeing(turbo_sim)


def _dress_up_sim_from_peeing(turbo_sim: TurboSim):
    peeing_outfit_state = turbo_sim.get_statistic_value(SimStatistic.WW_NUDITY_SPECIAL_PEEING_OUTFIT_STATE)
    if peeing_outfit_state != OutfitStateBeforePeeing.NONE:
        set_sim_penis_state(turbo_sim, False, update_outfit=True)
        last_outfit = get_modified_outfit(turbo_sim)

        if peeing_outfit_state == OutfitStateBeforePeeing.UNDERWEAR:
            set_body_type_cas_part(turbo_sim,
                                   (TurboOutfitCategory.SPECIAL, 0),
                                   TurboBodyType.LOWER_BODY,
                                   get_sim_underwear_data(turbo_sim, last_outfit)[1])
            set_sim_bottom_naked_state(turbo_sim, False)
            set_sim_underwear_state(turbo_sim, TurboBodyType.LOWER_BODY, True)
            turbo_sim.refresh_outfits_data()
        elif peeing_outfit_state == OutfitStateBeforePeeing.OUTFIT and has_sim_outfit_bottom(turbo_sim,
                                                                                             outfit_category_and_index=last_outfit):
            set_body_type_cas_part(turbo_sim,
                                   (TurboOutfitCategory.SPECIAL, 0),
                                   TurboBodyType.LOWER_BODY,
                                   get_sim_outfit_cas_part(turbo_sim,
                                                           TurboBodyType.LOWER_BODY,
                                                           outfit_category_and_index=last_outfit))
            set_body_type_cas_part(turbo_sim,
                                   (TurboOutfitCategory.SPECIAL, 0),
                                   TurboBodyType.TIGHTS,
                                   get_sim_outfit_cas_part(turbo_sim,
                                                           TurboBodyType.TIGHTS,
                                                           outfit_category_and_index=last_outfit))
            set_body_type_cas_part(turbo_sim,
                                   (TurboOutfitCategory.SPECIAL, 0),
                                   TurboBodyType.SOCKS,
                                   get_sim_outfit_cas_part(turbo_sim,
                                                           TurboBodyType.SOCKS,
                                                           outfit_category_and_index=last_outfit))
            set_sim_bottom_naked_state(turbo_sim, False)
            set_sim_underwear_state(turbo_sim, TurboBodyType.LOWER_BODY, True)
            turbo_sim.refresh_outfits_data()
        elif is_sim_outfit_fullbody(turbo_sim, outfit_category_and_index=last_outfit):
            dress_up_outfit(turbo_sim)
        else:
            dress_up_outfit(turbo_sim)

    turbo_sim.set_statistic_value(SimStatistic.WW_NUDITY_SPECIAL_PEEING_OUTFIT_STATE, OutfitStateBeforePeeing.NONE)
    turbo_sim.remove_buff(SimBuff.WW_NUDITY_SPECIAL_PEEING_OUTFIT_UPDATE)
