import numpy as np


class BowenFamilySystem:
    def __init__(self, num_agents, max_age, init_anxiety, init_dos):
        self.num_agents = num_agents
        self.max_age = max_age
        self.init_anxiety = init_anxiety
        self.init_dos = init_dos
        self.anxiety = np.full(num_agents, init_anxiety)
        self.dos = np.full(num_agents, init_dos)
        self.age = np.zeros(num_agents, dtype=int)
        self.pair_bonds = set()
        self.children = [[] for _ in range(num_agents)]

    def step(self):
        # Increase age
        self.age += 1

        # Choose pair-bonds among adult agents
        adults = self.age >= 18
        available = np.where(
            [len(self.children[i]) < 4 for i in range(self.num_agents)]
        )[0]
        free_agents = np.intersect1d(np.where(adults)[0], available)
        for i in free_agents:
            # Find a partner with similar DOS
            j = np.random.choice(
                np.where(adults & (self.dos == self.dos[i]))[0], size=1
            )
            if len(j) > 0:
                # Form a pair-bond
                self.pair_bonds.add(frozenset([i, j[0]]))

        # Bind anxiety in pair-bonds with high anxiety
        high_anxiety = np.where(self.anxiety >= 7)[0]
        for pb in self.pair_bonds:
            if len(high_anxiety & pb) == 2:
                # Choose an anxiety binding mechanism
                parents = np.array(list(pb))
                children = np.concatenate(self.children[parents])
                if len(children) > 0 and np.random.random() < 0.25:
                    # Use child projection process
                    target = np.random.choice(children)
                    dos_diff = np.random.normal(0, 0.1)
                    self.dos[target] = max(
                        0, min(1, self.dos[parents].mean() + dos_diff)
                    )
                    self.anxiety[target] = max(
                        0, min(10, self.anxiety[parents].mean() + 2)
                    )
                    for sib in self.children[parents[0]]:
                        if sib != target:
                            self.dos[sib] = max(
                                0,
                                min(
                                    1,
                                    self.dos[parents].mean()
                                    - dos_diff / (len(self.children[parents[0]]) - 1),
                                ),
                            )
                            self.anxiety[sib] = max(
                                0, min(10, self.anxiety[parents].mean())
                            )
                else:
                    # Use another mechanism
                    mechanism = np.random.choice(
                        ["distance", "conflict", "reciprocity"]
                    )
                    if mechanism == "distance":
                        for p in parents:
                            self.anxiety[p] = max(0, min(10, self.anxiety[p] - 1))
                    elif mechanism == "conflict":
                        for p in parents:
                            self.anxiety[p] = max(0, min(10, self.anxiety[p] + 1))
                    elif mechanism == "reciprocity":
                        for p in parents:
                            self.anxiety[p] = max(
                                0,
                                min(
                                    10,
                                    self.anxiety[p]
                                    + (-1 if self.age[p] % 2 == 0 else 1),
                                ),
                            )

        # Reproduce in pair-bonds with low anxiety
        low_anxiety = np.where(self.anxiety < 7)[0]
        for pb in self.pair_bonds:
            if len(high_anxiety & pb) == 0:
                parents = np.array(list(pb))
                n_children = np.random.randint(2, 4)
                # Reproduce with 2 children
                for _ in range(n_children):
                    child_dos = np.random.normal(self.dos[parents].mean(), 0.1)
                    child_dos = max(0, min(1, child_dos))
                    child_anxiety = np.random.normal(
                        self.anxiety[parents].mean(), 1
                    )
                    child_anxiety = max(0, min(10, child_anxiety))
                    self.dos = np.concatenate([self.dos, [child_dos]])
                    self.anxiety = np.concatenate([self.anxiety, [child_anxiety]])
                    self.age = np.concatenate([self.age, [0]])
                    self.children[parents[0]].append(self.num_agents)
                    self.children[parents[1]].append(self.num_agents)
                    self.num_agents += 1

        # Clip DOS and anxiety levels
        self.dos = np.clip(self.dos, 0, 1)
        self.anxiety = np.clip(self.anxiety, 0, 10)
