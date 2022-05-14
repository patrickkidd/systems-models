import mesa
import mesa.time
import mesa.space

import logging

from .utils import STATE_FRUSTRATED, STATE_GRATIFIED, STATE_NEED

log = logging.getLogger(__name__)


class Ball(mesa.Agent):
    def __init__(
        self,
        unique_id,
        model,
        gratification_limit,
        need_limit,
        frustration_limit,
        frustration_multiplier,
    ):
        super().__init__(unique_id, model)

        # Independent variables
        self._gratification_limit = gratification_limit
        self._need_limit = need_limit
        self._frustration_limit = frustration_limit
        self._frustration_multiplier = frustration_multiplier

        # Model state variables
        self.state_counter = 0

        # State step variables
        self.encounter = None

        # Dependent variables
        self._set_state(STATE_GRATIFIED)

    def _set_state(self, state):
        self.state = state
        self.state_counter = 0
        log.info(f"Agent {self.unique_id} -> {state}")

    def step(self):
        # Only allow one encounter per step
        self.encounter = None

        # CALHOUN: Each moves at a constant velocity, as if propelled by some inner force,
        # The physical diameter of each is equal to that of every other ball.
        # All move within a fixed space or area. How often one ball will on the
        # average collide with another will depend upon these three factors,
        # velocity, diameter and area, in relationship to the number of balls
        # present in the area.
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def advance(self):

        # Determine if this agent encounters another on this step.
        other = None
        if not self.encounter:
            for potential_encounter in self.model.grid.get_cell_list_contents(
                [self.pos]
            ):
                if potential_encounter is self:
                    continue
                if not potential_encounter.encounter:
                    encounter = potential_encounter
                    self.encounter = other = potential_encounter
                    potential_encounter.encounter = self
                    break

        state_was = self.state

        if other:

            log.info(
                f"Agent {self.unique_id} & {encounter.unique_id} encounter @ {self.pos} {encounter.pos}\t::\t{encounter.unique_id}"
            )

            if self.state == STATE_GRATIFIED:
                pass

            elif self.state == STATE_NEED:

                if other.state == STATE_GRATIFIED:

                    # CALHOUN: One such ball, "B", by chance encounters a ball which is still in the
                    # gratification state from a prior satisfactory encounter. This latter ball
                    # remains uninfluenced by the encounter with " B" ; it remains stippled.
                    # However, its failure to interact appropriately to the needs of "B" transforms
                    # "B" into a state of frustration indicated by the ball becoming black.
                    self._set_state(STATE_FRUSTRATED)

                elif other.state == STATE_NEED:

                    # CALHOUN: Ball "A" with a bent arrow indicating its path of movement represents
                    # such a ball in the need state of encountering another ball in a like state.
                    # As shown. it does encounter such a ball. Each then gains from the encounter;
                    # each enters a state. which may be designated as gratification. that lasts for
                    # some time after the encounter
                    self._set_state(STATE_GRATIFIED)

                elif other.state == STATE_FRUSTRATED:

                    # CALHOUN: In like fashion, when another ball, "C" , meets a ball in the
                    # frustration state, it too will be thrown into the state of frustration,
                    # in which it will remain for some period of time before returning to the
                    # original need state for contact.
                    self._set_state(STATE_FRUSTRATED)

        if self.state == state_was:
            self.state_counter += 1

        # Time-based updates
        if not other:

            if self.state == STATE_GRATIFIED:

                if self.state_counter >= self._gratification_limit:

                    # CALHOUN: After a specified period of time elapses. each of the stippled
                    # balls will complete its stay in the gratification state and return to the
                    # state of needing further contact with other balls.
                    self._set_state(STATE_NEED)

            elif self.state == STATE_NEED:

                if self.state_counter >= self._need_limit:

                    # CALHOUN:
                    self._set_state(STATE_FRUSTRATED)

            elif self.state == STATE_FRUSTRATED:

                if self.state_counter >= self._frustration_limit:

                    # CALHOUN: it too will be thrown into the state of frustration, in which it
                    # will remain for some period of time before returning to the original need
                    # state for contact.
                    self._set_state(STATE_NEED)

                else:

                    # CALHOUN: The more these balls are frustrated, the more they will try to escape
                    # from the field, the area within which meaningful contacts might occur. They
                    # seek the side pockets of their area of habitation. Here they are not visible
                    # to view; their " dropping out" leads to a lowered estimate of their velocity
                    # in terms of the total path traversed in the contact opportunity area over
                    # extended periods of time.
                    frustration_level = (
                        self.state_counter * self._frustration_multiplier
                    )
                    if frustration_level:
                        log.info(
                            f"TODO Implement increasingly 'deviant' behavior for frustrated agents (frustration_level: {frustration_level})."
                        )
