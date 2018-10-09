import numpy as np

from irl_benchmark.utils.utils import unwrap_env
from irl_benchmark.irl.feature.feature_wrapper import FeatureWrapper


class BaseIRLAlgorithm(object):
    '''The (abstract) base class for all IRL algorithms.'''
    def __init__(self, env, expert_trajs, rl_alg_factory):
        '''Set environment, expert trajectories, and RL algorithm factory.

        Args:
          env : gym environment
          expert_trajs : list of expert trajectories (see irl/collect)
          rl_alg_factory : function taking an environment and returning
                           an RL agent
        '''
        self.env = env
        self.expert_trajs = expert_trajs
        self.rl_alg_factory = rl_alg_factory

    def train(self, time_limit=300, rl_time_per_iteration=30):
        '''Train up to time_limit seconds.

        Args:
          time_limit: total training time in seconds
          rl_time_per_iteration: RL training time per step in seconds.

        Returns nothing.
        '''
        raise NotImplementedError()

    def get_reward_function(self):
        '''Return the current reward function estimate.'''
        raise NotImplementedError()

    def feature_count(self, trajs):
        '''Return empirical discounted feature counts of input trajectories.

        Args:
        trajs -- `list` of dictionaries w/ key 'features'

        Returns:
        feature_count -- `np.ndarray` w/ shape of features,
                         i.e. one scalar feature count per feature
        '''
        feature_sum = np.zeros(unwrap_env(self.env,
                                          FeatureWrapper).feature_shape())
        for traj in trajs:
            gammas = self.gamma ** np.arange(len(traj['features']))
            feature_sum += np.sum(
                gammas.reshape(-1, 1) * np.array(traj['features']), axis=0)
        feature_count = feature_sum / len(trajs)
        return feature_count

    def joint_prob_of_actions(self, traj):
        '''Return joint probability of traj.

        This is the function U from Boularias et al. (2011, p. 185),
        which they describe as 'the joint probability of the actions
        conditioned on the states in [traj]'.
        '''
        raise NotImplementedError()

    def policy_prob_of_actions(self, traj, policy):
        '''Return product of the policy's action probabilities for traj.

        For now assumes that policy is represented as table.'''
        states = traj['states']
        actions = traj['actions']
        probs = [policy[states[i]][actions[i]] for i in range(len(states))]
        return np.prod(np.array(probs))
