import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider

aggression_threshold = 1.0
chaos_factor = 0.3  


class StrategicAgent:
    def __init__(self, strategy_type, agent_id):
        self.agent_id = agent_id
        self.power = np.random.uniform(0.5, 1.5)
        self.position = np.random.rand(2) * 10
        self.strategy_type = strategy_type
        self.status = 'maneuver'
        self.vector = np.zeros(2)

    def decide(self, opponents):
        if opponents:
            threat_level = sum(op.power for op in opponents) / self.power
  
            if threat_level < 1.0 * aggression_threshold:
                self.status = 'attack'
                self.vector = self.calculate_best_attack_vector(opponents)
            elif 1.0 * aggression_threshold <= threat_level <= 1.4 * aggression_threshold:
                self.status = 'maneuver'
                self.vector = self.generate_defensive_pattern()
            else:
                self.status = 'retreat'
                self.vector = self.find_safest_escape_route(opponents)
        else:
            self.status = 'maneuver'
            self.vector = self.generate_defensive_pattern()
        return self.status, self.vector

    def calculate_best_attack_vector(self, opponents):
        if not opponents:
            return self.generate_defensive_pattern()
        weakest = min(opponents, key=lambda op: op.power)
        direction = weakest.position - self.position
        norm = np.linalg.norm(direction)
        if norm == 0:
            norm = 1
   
        random_jitter = np.random.uniform(-chaos_factor, chaos_factor, 2)
        return (direction / norm) + random_jitter

    def generate_defensive_pattern(self):
        direction = np.random.uniform(-1, 1, 2)
        norm = np.linalg.norm(direction)
        if norm == 0:
            norm = 1
        random_jitter = np.random.uniform(-chaos_factor/2, chaos_factor/2, 2)
        return (direction / norm) + random_jitter

    def find_safest_escape_route(self, opponents):
        if not opponents:
            return self.generate_defensive_pattern()
        threat_center = np.mean([op.position for op in opponents], axis=0)
        direction = self.position - threat_center
        norm = np.linalg.norm(direction)
        if norm == 0:
            norm = 1
        random_jitter = np.random.uniform(-chaos_factor, chaos_factor, 2)
        return (direction / norm) + random_jitter


class Battlefield:
    def __init__(self, num_agents=50):
        self.agents = self._deploy_forces(num_agents)
        self.time_step_count = 0

    def _deploy_forces(self, num_agents):
        agents = []
        for i in range(num_agents):
            strategy = np.random.choice(['active', 'passive'])
            agents.append(StrategicAgent(strategy, i))
        return agents

    def _detect_in_radius(self, agent, radius):
        foes = []
        for other in self.agents:
            if other.agent_id != agent.agent_id:
                if np.linalg.norm(other.position - agent.position) < radius:
                    foes.append(other)
        return foes

    def _execute_action(self, agent, vector):

        if agent.status == 'attack':
            speed_factor = 0.35
        elif agent.status == 'retreat':
            speed_factor = 0.3
        else:
            speed_factor = 0.25
        chaotic_movement = np.random.uniform(-0.05, 0.05, 2)
        agent.position += vector * speed_factor + chaotic_movement
        agent.position = np.clip(agent.position, 0, 10)

    def _update_power_dynamics(self, agent):
        if agent.status == 'attack':
            decay = 0.02
        elif agent.status == 'retreat':
            decay = 0.015
        else:
            decay = 0.005
        agent.power = max(0.1, agent.power - decay)

    def _rebalance_strategic_equilibrium(self):
        total_power = sum(agent.power for agent in self.agents)
        if total_power < 10:
            for agent in self.agents:
                agent.power += 0.03

    def time_step(self):
        for agent in self.agents:
            visible_foes = self._detect_in_radius(agent, 3.0)
            action, vector = agent.decide(visible_foes)
            self._execute_action(agent, vector)
            self._update_power_dynamics(agent)
        self._rebalance_strategic_equilibrium()
        self.time_step_count += 1


battlefield = Battlefield(num_agents=50)

fig, ax = plt.subplots(figsize=(10, 8))
plt.subplots_adjust(right=0.8, bottom=0.15)
ax.set_facecolor('#000000') 


status_colors = {'attack': '#ff0000', 'maneuver': '#ffff00', 'retreat': '#00ff00'}
power_sizes = lambda power: 100 + power * 200

ax_slider = plt.axes([0.25, 0.05, 0.5, 0.03])
slider = Slider(ax_slider, 'Aggression', 0.5, 2.0, valinit=aggression_threshold, color='#5a9cff')
def update_threshold(val):
    global aggression_threshold
    aggression_threshold = val
slider.on_changed(update_threshold)

trail_history = {agent.agent_id: [agent.position.copy()] for agent in battlefield.agents}

def visualize_battlefield():
    ax.clear()
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_facecolor('#000000')
    ax.grid(True, linestyle='--', alpha=0.3, color='white')
    ax.set_title(f"Chaotic Strategic Battle - Cycle: {battlefield.time_step_count}", fontsize=16, color='white')

    for agent in battlefield.agents:
        color = status_colors[agent.status]
        marker_size = power_sizes(agent.power)
        
        trail_history[agent.agent_id].append(agent.position.copy())
        if len(trail_history[agent.agent_id]) > 30:
            trail_history[agent.agent_id].pop(0)
        trail_positions = np.array(trail_history[agent.agent_id])
        ax.plot(trail_positions[:, 0], trail_positions[:, 1], '-', linewidth=1, alpha=0.7, color=color)
        
        ax.scatter(agent.position[0], agent.position[1], s=marker_size, c=color,
                   edgecolors='white', linewidth=0.5, alpha=0.9)
        
        ax.quiver(agent.position[0], agent.position[1],
                  agent.vector[0], agent.vector[1],
                  color='white', scale=20, width=0.005, alpha=0.8, headwidth=4, headlength=6)

def animate(i):
    battlefield.time_step()
    visualize_battlefield()

ani = FuncAnimation(fig, animate, interval=30)
plt.show()
