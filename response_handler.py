import copy

from config import ACTIONS_MAPPING_CONFIG


# Consts.
DEFAULT_CONFIG_KEY = "default"

COCO_STANDARD_RESPONSE = {
    "action_name": "",
    "component_done": False,  # Bool
    "component_failed": False,  # Bool
    "confidence": 1,
    "out_of_context": False,  # Bool
    "response": "",
    "response_time": 0.0,
    "updated_context": {}
}


class ResponseHandlerException(Exception):
    pass


# functions
def handle(component_id, houndify_json_response, response_time_seconds=0.0):
    """
    Receives a Houndify JSON result and formats it to a standard CoCo
    component response format.

    Arguments:
        component_id (string): Target Houndify component ID, client config file
        path.
        houndify_json_response (dict): Houndify JSON response.
        response_time_seconds (float): The time between the request and when
        the response was received.

    Returns:
        Result in a CoCo standard format. (dict)
    """
    mapping_config = ACTIONS_MAPPING_CONFIG.get(component_id) or \
                     ACTIONS_MAPPING_CONFIG.get(DEFAULT_CONFIG_KEY)

    coco_standard_response = copy.deepcopy(COCO_STANDARD_RESPONSE)

    results = houndify_json_response.get("AllResults")

    if results:
        action_name = results[0]["CommandKind"]

        written_response = results[0]["WrittenResponse"] or\
                                             results[0]["WrittenResponseLong"]

    else:
        action_name = houndify_json_response.get("CommandKind")
        written_response = houndify_json_response.get("WrittenResponse") or\
                           houndify_json_response.get("WrittenResponseLong")

        if not action_name and written_response:
            raise ResponseHandlerException("No results received.")

    coco_standard_response["action_name"] = action_name
    coco_standard_response["response"] = written_response
    coco_standard_response["response_time"] = response_time_seconds

    coco_standard_response["confidence"] = 1.0  # Default.

    coco_standard_response["component_done"] = \
        (mapping_config.get("COMPLETE_ACTION") == action_name)

    coco_standard_response["component_failed"] = \
        (mapping_config.get("FAILED_ACTION") == action_name)

    coco_standard_response["out_of_context"] = \
        (mapping_config.get("OUT_OF_CONTEXT_ACTION") == action_name)

    return coco_standard_response
