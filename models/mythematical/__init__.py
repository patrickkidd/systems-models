from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule
from mesa.visualization.UserParam import UserSettableParameter


from .utils import *
from .ball import *
from .model import *


COLOR_GRATIFIED = "#00ff00"
COLOR_FRUSTRATED = "#000000"
COLOR_NEED = "#ff0000"
COLOR_ENCOUNTERS = "cyan"


def agent_portrayal(agent):

    fill_colors = {
        STATE_FRUSTRATED: "#000000",
        STATE_GRATIFIED: "#00aa00",
        STATE_NEED: "#ff0000",
    }

    fill_colors_encounter = {
        STATE_FRUSTRATED: "#000000aa",
        STATE_GRATIFIED: "#f00aa00aa",
        STATE_NEED: "#ff0000aa",
    }

    stroke_colors = {
        STATE_FRUSTRATED: COLOR_FRUSTRATED,
        STATE_GRATIFIED: "#00ff00",
        STATE_NEED: "#ff0000",
    }

    def _fill_color(agent):
        if agent.encounter:
            return fill_colors_encounter.get(agent.state)
        else:
            return fill_colors.get(agent.state)

    def _stroke_color(agent):
        return stroke_colors.get(agent.state)

    def _x_offset(agent):
        if agent.encounter:
            if id(agent) < id(agent.encounter):
                return -0.15
            else:
                return 0.15
        else:
            return 0

    def _filled(agent):
        return bool(agent.encounter is None)

    def _text(agent):
        if not agent.encounter:
            return str(agent.state_counter)
        else:
            return ""

    def _text_color(agent):
        return "white"

    portrayal = {
        "ID": agent.unique_id,
        "Shape": "circle",
        "Color": _fill_color(agent),
        "stroke_color": _stroke_color(agent),
        "Filled": _filled(agent),
        "Layer": 0,
        "r": 0.5,
        "x_offset": _x_offset(agent),
        "Need Limit": agent._need_limit,
        "Frustration Limit": agent._frustration_limit,
        "Frustratability": agent._frustration_multiplier,
        "State": agent.state,
        "Steps in State": agent.state_counter,
        "ignoredFeatures": ["Layer", "text", "x_offset"]
        # debug
        # "pos": agent.pos,
        # "unique_id": agent.unique_id,
    }
    if agent.model.show_step_counter:
        portrayal.update(
            {
                "text": _text(agent),
                "text_color": _text_color(agent),
            }
        )

    log.debug(
        f"Agent {agent.unique_id}: ({agent.pos[0]}, {agent.pos[1]}), x_offset: {portrayal.get('x_offset')}"
    )
    return portrayal


grid = CanvasGrid(agent_portrayal, SIZE, SIZE, 600, 600)
data_collector = "datacollector"
chart = ChartModule(
    [
        {"Label": "Gratified", "Color": COLOR_GRATIFIED},
        {"Label": "Need", "Color": COLOR_NEED},
        {"Label": "Frustrated", "Color": COLOR_FRUSTRATED},
        {"Label": "Encounters", "Color": COLOR_ENCOUNTERS},
    ],
    SIZE,
    SIZE,
)
server = ModularServer(
    MythematicalModel,
    [grid, chart],
    "Mythematical Social Pool Game",
    {
        "num_balls": UserSettableParameter(
            "slider",
            "Number of balls",
            DEFAULT_NUM_BALLS,
            2,
            40,
            description="Number of balls.",
        ),
        "gratification_limit": UserSettableParameter(
            "slider",
            "Gratification Limit",
            DEFAULT_GRATIFICATION_LIMIT,
            1,
            30,
            description="Calhoun: After a specified period of time elapses. each of the stippled balls will complete its stay in the gratification state and return to the state of needing further contact with other balls.",
        ),
        "gratification_limit_variation": UserSettableParameter(
            "slider",
            "Gratification Limit Variation",
            2,
            0,
            10,
            description="Number of steps the gratification limit can vary more or less.",
        ),
        "need_limit": UserSettableParameter(
            "slider",
            "Need Limit",
            DEFAULT_NEED_LIMIT,
            1,
            30,
            description="Calhoun: Furthermore, each ball from time to time develops a need state for contacting some other ball in an equivalent need state.",
        ),
        "need_limit_variation": UserSettableParameter(
            "slider",
            "Need Limit Variation",
            3,
            0,
            10,
            description="Number of steps the need limit can vary more or less.",
        ),
        "frustration_limit": UserSettableParameter(
            "slider",
            "Frustration Limit",
            5,
            0,
            10,
            description="Steps in before changing from frustrated to to need state.",
        ),
        "frustration_variation": UserSettableParameter(
            "slider",
            "Frustration Variation",
            0,
            0,
            FRUSTRATION_VARIATION_MAX,
            step=FRUSTRATION_VARIATION_STEP,
            description="Range of randomly selected multiplier for how much more frustrated a ball becomes.",
        ),
        "show_step_counter": UserSettableParameter(
            "checkbox", "Show Steps in Current State", value=True
        ),
        "width": SIZE,
        "height": SIZE,
    },
)

if __name__ == "__main__":
    import os

    server.launch()
    os.system(f'open "https://localhost:{server.port}"')
