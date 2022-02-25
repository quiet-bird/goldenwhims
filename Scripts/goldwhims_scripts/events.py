import random

from goldwhims_scripts.enums.tuning_enums import GoldWhimsTuningId
from goldwhims_scripts.undress import _undress_bottom
from interactions.base.interaction import Interaction
from objects.game_object import GameObject
from sims.sim import Sim
from sims.sim_info import SimInfo
from sims4communitylib.enums.motives_enum import CommonMotiveId
from sims4communitylib.events.event_handling.common_event_registry import CommonEventRegistry
from sims4communitylib.events.interaction.events.interaction_outcome import S4CLInteractionOutcomeEvent
from sims4communitylib.events.interval.common_interval_event_service import CommonIntervalEventRegistry
from sims4communitylib.modinfo import ModInfo
from sims4communitylib.utils.location.common_location_utils import CommonLocationUtils
from sims4communitylib.utils.objects.common_object_location_utils import CommonObjectLocationUtils
from sims4communitylib.utils.objects.common_object_type_utils import CommonObjectTypeUtils
from sims4communitylib.utils.objects.common_object_utils import CommonObjectUtils
from sims4communitylib.utils.resources.common_interaction_utils import CommonInteractionUtils
from sims4communitylib.utils.sims.common_buff_utils import CommonBuffUtils
from sims4communitylib.utils.sims.common_sim_gender_option_utils import CommonSimGenderOptionUtils
from sims4communitylib.utils.sims.common_sim_interaction_utils import CommonSimInteractionUtils
from sims4communitylib.utils.sims.common_sim_location_utils import CommonSimLocationUtils
from sims4communitylib.utils.sims.common_sim_motive_utils import CommonSimMotiveUtils
from sims4communitylib.utils.sims.common_sim_utils import CommonSimUtils
from sims4communitylib.utils.sims.common_trait_utils import CommonTraitUtils, CommonTraitId
from sims4communitylib.utils.terrain.common_terrain_interaction_utils import CommonTerrainInteractionUtils

# Note to self: -50 means bar is yellow, -75 is "has to pee" (orange/red bar), -80 is "really has to pee" (deep red bar)

PEEING_INTERACTIONS = {
    GoldWhimsTuningId.WWHIMS_INTERACTION_PEE_FEMALE,
    GoldWhimsTuningId.WWHIMS_INTERACTION_PEE_MALE,
    GoldWhimsTuningId.EA_INTERACTION_TOILET_USE_SITTING,
    GoldWhimsTuningId.EA_INTERACTION_TOILET_USE_STANDING,
    GoldWhimsTuningId.EA_INTERACTION_TOILETSTALL_USE_SITTING,
    GoldWhimsTuningId.EA_INTERACTION_TOILETSTALL_USE_STANDING,
    151354, 13443
}


def _find_peeing_interaction_callback(inter: Interaction) -> bool:
    return CommonInteractionUtils.get_interaction_id(inter) in PEEING_INTERACTIONS


def _sim_is_peeing(sim_info: SimInfo) -> bool:
    # If this generator returns even one result, the Sim is peeing in some way, so return true
    for inter in CommonSimInteractionUtils.get_queued_or_running_interactions_gen(sim_info,
                                                                                  _find_peeing_interaction_callback):
        return True

    return False


def _find_toilet_callback(gameobj: GameObject):
    return CommonObjectTypeUtils.is_toilet(gameobj) and CommonObjectLocationUtils.is_on_current_lot(gameobj)


def _find_peespot_callback(gameobj: GameObject):
    return gameobj.definition.id == GoldWhimsTuningId.GWHIMS_OBJDEF_PEESPOT and CommonObjectLocationUtils.is_on_current_lot(
        gameobj)


def _queue_pee_on_spot(sim: Sim):
    _undress_bottom(sim)
    sim_info = CommonSimUtils.get_sim_info(sim)

    tpt, ictxt = CommonTerrainInteractionUtils.build_terrain_point_and_interaction_context_from_sim_and_position(
        sim_info,
        CommonSimLocationUtils.get_position(sim_info),
        CommonSimLocationUtils.get_surface_level(sim_info))

    if CommonSimGenderOptionUtils.uses_toilet_standing(sim_info):
        CommonSimInteractionUtils.queue_interaction(sim_info,
                                                    GoldWhimsTuningId.WWHIMS_INTERACTION_PEE_MALE,
                                                    target=tpt,
                                                    interaction_context=ictxt,
                                                    skip_if_running=True)
        return

    interactions = [
        GoldWhimsTuningId.GWHIMS_INTERACTION_PEE_F_MIDSQUAT_0,
        GoldWhimsTuningId.GWHIMS_INTERACTION_PEE_F_HISQUAT_0
    ]

    CommonSimInteractionUtils.queue_interaction(sim_info,
                                                interactions[random.randrange(0, len(interactions))],
                                                target=tpt,
                                                interaction_context=ictxt,
                                                skip_if_running=True)


# Handles desperation peeing pseudo-autonomous behaviour,
# the diuretic atmosphere zone modifier, and the overactive bladder buff.
@CommonIntervalEventRegistry.run_every(ModInfo.get_identity().name, milliseconds=5000)
def _goldwhims_interval_event():
    diuretic_atmos: bool = CommonLocationUtils.current_lot_has_trait(
        GoldWhimsTuningId.GWHIMS_ZONEMOD_DIURETIC_ATMOS)

    for sim_info in CommonSimUtils.get_sim_info_for_all_sims_generator():
        if not CommonSimLocationUtils.is_on_current_lot(sim_info):
            continue

        # Sims who are already peeing will not seek out pee spots or pee-where-standing
        if _sim_is_peeing(sim_info):
            continue

        bladder = CommonSimMotiveUtils.get_bladder_level(sim_info)

        if diuretic_atmos or CommonBuffUtils.has_buff(sim_info, GoldWhimsTuningId.GWHIMS_BUFF_OVERACTIVEBLADDER):
            if bladder >= -65:
                CommonSimMotiveUtils.decrease_motive_level(sim_info, CommonMotiveId.BLADDER, 2.5)

        # Snobbish Sims will not pee-where-standing or seek out pee spots
        if CommonTraitUtils.has_trait(sim_info, CommonTraitId.SNOB):
            continue

        if bladder <= -80:
            _queue_pee_on_spot(sim_info)
        elif bladder <= -60:
            for pspot in CommonObjectUtils.get_instance_for_all_game_objects_generator(_find_peespot_callback):
                if pspot.in_use:
                    continue

                CommonSimInteractionUtils.queue_interaction(sim_info,
                                                            GoldWhimsTuningId.GWHIMS_INTERACTION_GOTO_PEEHERE,
                                                            target=pspot,
                                                            skip_if_running=True)


@CommonEventRegistry.handle_events(ModInfo.get_identity())
def _handle_goto_pee(event_data: S4CLInteractionOutcomeEvent) -> bool:
    inter_id = CommonInteractionUtils.get_interaction_id(event_data.interaction)

    if inter_id == GoldWhimsTuningId.WWHIMS_INTERACTION_PEE_FEMALE:
        _queue_pee_on_spot(event_data.interaction.sim)

    return True
