import random


class FamilyAgent:
    def __init__(
        self,
        id,
        age,
        gender,
        anxiety_level,
        differentiation_of_self,
        sibling_ds_levels=[],
    ):
        self.id = id
        self.age = age
        self.gender = gender
        self.anxiety_level = anxiety_level
        self.differentiation_of_self = differentiation_of_self
        self.sibling_ds_levels = sibling_ds_levels
        self.interactions = []
        self.partner = None

    def interact(self, other_agent):
        if self.id == other_agent.id:
            return
        self.interactions.append(other_agent)
        if self.anxiety_level > 0.5:
            if self.differentiation_of_self > other_agent.differentiation_of_self:
                self.distance(other_agent)
            elif self.differentiation_of_self < other_agent.differentiation_of_self:
                self.child_projection(other_agent)
            else:
                self.overfunctioning(other_agent)

    def distance(self, other_agent):
        if random.random() < self.anxiety_level:
            if not self.partner and not other_agent.partner:
                return
            elif self.partner == other_agent or other_agent.partner == self:
                return
            elif self.partner and not other_agent.partner:
                self.overfunctioning(self.partner)
            elif other_agent.partner and not self.partner:
                self.overfunctioning(other_agent.partner)
            else:
                self.conflict(self.partner, other_agent.partner)

    def conflict(self, partner1, partner2):
        if random.random() < self.anxiety_level:
            if self.differentiation_of_self < partner1.differentiation_of_self:
                partner1.underfunctioning(self)
            elif self.differentiation_of_self < partner2.differentiation_of_self:
                partner2.underfunctioning(self)
            else:
                self.underfunctioning(partner1)
                self.underfunctioning(partner2)

    def overfunctioning(self, other_agent):
        if random.random() < self.anxiety_level:
            if self.partner and self.partner != other_agent:
                self.underfunctioning(self.partner)
            if other_agent.partner and other_agent.partner != self:
                self.underfunctioning(other_agent.partner)
            self.partner = other_agent

    def underfunctioning(self, other_agent):
        if random.random() < self.anxiety_level:
            self.partner = None
            other_agent.partner = None

    def child_projection(self, other_agent):
        if random.random() < self.anxiety_level:
            if not other_agent.partner:
                return
            elif self.partner == other_agent or other_agent.partner == self:
                return
            elif self.differentiation_of_self < other_agent.differentiation_of_self:
                self.overfunctioning(other_agent.partner)
            else:
                other_agent.partner.overfunctioning(self)

    def reproduce(self, partner):
        if self.gender == partner.gender or self.partner or partner.partner:
            return None

        parent_ds_levels = [
            self.differentiation_of_self,
            partner.differentiation_of_self,
        ]
        child_ds_levels = []
        for i in range(2):
            projection = random.uniform(0.8, 1.2)
            child_ds_levels.append(
                (
                    parent_ds_levels[i] * projection
                    + parent_ds_levels[(i + 1) % 2] * (1 - projection)
                )
            )
        child_anxiety_level = min(
            max(
                random.gauss((self.anxiety_level + partner.anxiety_level) / 2, 0.2), 0.0
            ),
            1.0,
        )
        child_gender = random.choice(["M", "F"])
        child = FamilyAgent(
            id=None,
            age=0,
            gender=child_gender,
            anxiety_level=child_anxiety_level,
            differentiation_of_self=child_ds_levels[0],
            sibling_ds_levels=child_ds_levels[1:],
        )
        return child


class FamilySystem:
    def __init__(self, agents):
        self.agents = agents

    def simulate(self, num_steps):
        for i in range(num_steps):
            for agent in self.agents:
                for other_agent in self.agents:
                    agent.interact(other_agent)
            for agent in self.agents:
                agent.anxiety_level = max(
                    min(agent.anxiety_level + random.uniform(-0.1, 0.1), 1), 0
                )
            new_agents = []
            for agent in self.agents:
                if agent.age >= 30 and not agent.partner and random.random() < 0.1:
                    partner = random.choice(
                        [
                            a
                            for a in self.agents
                            if a.id != agent.id and a.age >= 30 and not a.partner
                        ]
                    )
                    child = agent.reproduce(partner)
                    if child:
                        new_agents.append(child)
            self.agents.extend(new_agents)

    def get_agent_anxiety_levels(self):
        return [agent.anxiety_level for agent in self.agents]


if __name__ == "__main__":
    fs = FamilySystem(5)
    fs.simulate(10)
