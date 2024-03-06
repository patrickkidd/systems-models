import numpy as np


class FamilySystem:
    def __init__(
        self, num_agents, max_generations, initial_diff_range, repro_prob, bind_probs
    ):
        self.num_agents = num_agents
        self.max_generations = max_generations
        self.initial_diff_range = initial_diff_range
        self.repro_prob = repro_prob
        self.bind_probs = bind_probs
        self.generations = []
        self._initialize_generations()

    def _initialize_generations(self):
        for i in range(self.max_generations):
            generation = []
            if i == 0:
                for j in range(self.num_agents):
                    agent_diff = np.random.uniform(
                        self.initial_diff_range[0], self.initial_diff_range[1]
                    )
                    generation.append(Agent(agent_diff))
            else:
                for j in range(self.num_agents):
                    parent1, parent2 = self._select_parents(self.generations[i - 1])
                    child = self._reproduce(parent1, parent2)
                    generation.append(child)
            self.generations.append(generation)

    def _select_parents(self, generation):
        parents = np.random.choice(generation, 2, replace=False)
        return parents[0], parents[1]

    def _reproduce(self, parent1, parent2):
        child_diff = (parent1.diff_of_self + parent2.diff_of_self) / 2
        if np.random.uniform() < self.repro_prob:
            return Agent(child_diff)
        else:
            return parent1


class Agent:
    def __init__(self, diff_of_self):
        self.diff_of_self = diff_of_self

    def bind_anxiety(self, agents):
        bind_probs = agents[0].family_system.bind_probs
        available_agents = [agent for agent in agents if agent != self]
        available_agents.sort(
            key=lambda agent: abs(self.diff_of_self - agent.diff_of_self)
        )
        for agent in available_agents:
            bind_prob = bind_probs[self._determine_bind_type(agent)]
            if np.random.uniform() < bind_prob:
                self.diff_of_self = self._adjust_diff_of_self(agent.diff_of_self)
                break

    def _determine_bind_type(self, other_agent):
        diff = self.diff_of_self - other_agent.diff_of_self
        if diff > 0:
            return 0  # distance
        elif diff < -10:
            return 1  # conflict
        elif diff < 0:
            return 2  # overfunctioning/underfunctioning reciprocity
        else:
            return 3  # child projection

    def _adjust_diff_of_self(self, other_diff):
        diff = self.diff_of_self - other_diff
        if diff > 0:
            return other_diff - np.random.uniform(0, diff)
        else:
            return other_diff + np.random.uniform(0, -diff)

    def __repr__(self):
        return f"Agent({self.diff_of_self:.2f})"
