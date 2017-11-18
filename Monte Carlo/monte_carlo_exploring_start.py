import numpy as np
from grid_world import *

GAMMA = 0.9
ALL_POSSIBLE_ACTIONS = ['U', 'D', 'L', 'R']

def max_dict(d):
    # returns the argmax (key) and max (value) from a dictionary
    # put this into a function since we are using it so often
    max_key = None
    max_val = float('-inf')
    for k, v in d.items():
        if v > max_val:
            max_val = v
            max_key = k
    return max_key, max_val



def play_game(grid, policy):
    # returns a list of states and corresponding returns

    # reset game to start at a random position
    # we need to do this if we have a deterministic policy
    # we would never end up at certain states, but we still want to measure their value
    # this is called the "exploring starts" method
    start_states = list(grid.actions.keys())
    start_idx = np.random.choice(len(start_states))
    grid.set_state(start_states[start_idx])

    s = grid.current_state()
    a = np.random.choice(ALL_POSSIBLE_ACTIONS)  # first action is uniformly random

    # be aware of the timing
    # each triple is s(t), a(t), r(t)
    # but r(t) results from taking action a(t-1) from s(t-1) and landing in s(t)
    states_actions_rewards = [(s, a, 0)]
    seen_states = set()
    while True:
        old_s = grid.current_state()
        r = grid.move(a)
        s = grid.current_state()

        if s in seen_states:
            # hack so that we don't end up in an infinitely long episode
            # bumping into the wall repeatedly
            states_actions_rewards.append((s, None, -100))
            break
        elif grid.game_over():
            states_actions_rewards.append((s, None, r))
            break
        else:
            a = policy[s]
            states_actions_rewards.append((s, a, r))
        seen_states.add(s)

    # calculate the returns by working backwards from the terminal state
    G = 0
    states_actions_returns = []
    first = True
    for s, a, r in reversed(states_actions_rewards):
        # the value of the terminal state is 0 by definition
        # we should ignore the first state we encounter
        # and ignore the last G, which is meaningless since it doesn't correspond to any move
        if first:
            first = False
        else:
            states_actions_returns.append((s, a, G))
        G = r + GAMMA * G
    states_actions_returns.reverse()  # we want it to be in order of state visited
    return states_actions_returns

if __name__ == '__main__':
    grid = negative_grid(step_cost=-0.9)

    print("Rewards: ")
    print_values(grid.rewards, grid)

    # initialize with random valeus for state values and policy
    policy = {}
    for s in grid.actions.keys():
        policy[s] = np.random.choice(ALL_POSSIBLE_ACTIONS)

    Q = {}
    returns = {}
    states = grid.all_states()
    for s in states:
        if s in grid.actions:
            Q[s] = {}
            for a in ALL_POSSIBLE_ACTIONS:
                Q[s][a] = 0
                returns[(s, a)] = []
        else:
            pass

    # Repeat until converge
    deltas = []
    for t in range(2000):
        if t%100 == 0:
            print(t)

        # Generate an episode using pi
        biggest_change = 0

        states_actions_returns = play_game(grid, policy)
        seen_states_action_pairs = set()

        for s, a, G in states_actions_returns:
            # Check if we have already seen s
            # called "first visit" MC policy evaluation
            sa = (s, a)
            if sa not in seen_states_action_pairs:
                old_q = Q[s][a]
                returns[sa].append(G)
                Q[s][a] = np.mean(returns[sa])
                biggest_change = max(biggest_change, np.abs(old_q - Q[s][a]))
                seen_states_action_pairs.add(sa)
        deltas.append(biggest_change)

        # update policy
        for s in policy.keys():
            policy[s] = max_dict(Q[s])[0]

    plt.plot(deltas)
    plt.show()

    print("final policy:")
    print_policy(policy, grid)

    # find V
    V = {}
    for s, Qs in Q.items():
        V[s] = max_dict(Q[s])[1]

    print("final values:")
    print_values(V, grid)
