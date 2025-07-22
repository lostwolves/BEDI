from task_examples.E2E.landOnShip import INFO as land_on_ship_info

from task_examples.S2S.autoLanding_flyToSeaArea import INFO as fly_to_sea_area_info
from task_examples.S2S.autoLanding_searchForShip import INFO as search_for_ship_info
from task_examples.S2S.autoLanding_approachShip import INFO as approach_ship_info

from task_examples.E2E.delivery import INFO as delivery_info
from task_examples.S2S.delivery_flyToPort import INFO as delivery_fly_to_port_info
from task_examples.S2S.delivery_searchForShip import INFO as delivery_search_for_ship_info
from task_examples.S2S.delivery_approachShip import INFO as delivery_approach_ship_info

TASK_INFO = {
    ## Auto Landing Task
    # E2E task mode
    "LandOnShip": land_on_ship_info,

    # S2S task mode
    "FlyToSeaArea": fly_to_sea_area_info,
    "SearchForShip": search_for_ship_info,
    "ApproachShip": approach_ship_info,

    ## Delivery Task
    # E2E task mode
    "Delivery": delivery_info,
    # S2S task mode
    "DeliveryFlyToPort": delivery_fly_to_port_info,
    "DeliverySearchForShip": delivery_search_for_ship_info,
    "DeliveryApproachShip": delivery_approach_ship_info,
}

TASK_MAPPING = {
    "drone_landing": "LandOnShip",
    "fly_to_sea_area": "FlyToSeaArea",
    "search_for_target": "SearchForShip",
    "approach_target": "ApproachShip",

    "delivery": "Delivery",
    "delivery_fly_to_port": "DeliveryFlyToPort",
    "delivery_search_for_ship": "DeliverySearchForShip",
    "delivery_approach_ship": "DeliveryApproachShip",
}