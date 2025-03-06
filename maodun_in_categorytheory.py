#!/usr/bin/env python


import random
from dataclasses import dataclass
from enum import Enum
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class ContradictionType(Enum):
    ANTAGONISM = "antagonism"
    DEPENDENCE = "dependence"
    TRANSFORMATION = "transformation"

@dataclass(frozen=True)
class Relation:
    intensity: float          
    type: ContradictionType   
    active: bool            

class Object:
    def __init__(self, name, importance=1.0, **attributes):
        self.name = name
        self.importance = importance
        self.attributes = attributes

class System:
    def __init__(self):
        self.graph = nx.DiGraph()
    
    def add_object(self, obj: Object):
        self.graph.add_node(obj.name, data=obj)
    
    def add_relation(self, source: Object, target: Object, relation: Relation):
        self.graph.add_edge(source.name, target.name, data=relation)



class DynamicsEngine:
    def __init__(self, system: System, chaos_coeff: float = 3.7):
        self.system = system
        self.chaos_coeff = chaos_coeff
    
    def logistic_map(self, x):
 
        return self.chaos_coeff * x * (1 - x)
    
    def update_relations(self):
        updates = []

        for u, v, data in self.system.graph.edges(data=True):
            relation: Relation = data['data']
            new_intensity = self.logistic_map(relation.intensity)
    
            new_intensity = max(0.0, min(new_intensity, 1.0))

            if relation.type == ContradictionType.ANTAGONISM and new_intensity > 0.9:
                new_type = ContradictionType.DEPENDENCE
            else:
                new_type = relation.type
            new_active = new_intensity > 0.1
            new_relation = Relation(intensity=new_intensity, type=new_type, active=new_active)
            updates.append((u, v, new_relation))
        for u, v, new_relation in updates:
            self.system.graph[u][v]['data'] = new_relation
    
    def focus_main_contradictions(self):
        intensities = [data['data'].intensity for _, _, data in self.system.graph.edges(data=True)]
        if intensities:
            threshold = np.percentile(intensities, 97)
            focused = [(u, v) for u, v, data in self.system.graph.edges(data=True)
                       if data['data'].intensity >= threshold]
            return focused
        return []
    
    def tick(self):
        self.update_relations()
        main_contradictions = self.focus_main_contradictions()
        return main_contradictions



class Visualizer:
    def __init__(self, system: System, dynamics_engine: DynamicsEngine):
        self.system = system
        self.engine = dynamics_engine
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
    
    def update(self, frame):
        main_contradictions = self.engine.tick()
        self.ax.clear()
        

        pos = nx.spring_layout(self.system.graph, seed=42)
        

        node_sizes = [self.system.graph.nodes[n]['data'].importance * 300 for n in self.system.graph.nodes()]
        nx.draw_networkx_nodes(self.system.graph, pos, ax=self.ax, node_size=node_sizes, node_color='lightblue')
        

        nx.draw_networkx_labels(self.system.graph, pos, ax=self.ax)
        

        for u, v, data in self.system.graph.edges(data=True):
            relation: Relation = data['data']
            width = 1 + relation.intensity * 5  
            type_colors = {
                ContradictionType.ANTAGONISM: 'red',
                ContradictionType.DEPENDENCE: 'blue',
                ContradictionType.TRANSFORMATION: 'green'
            }
            nx.draw_networkx_edges(self.system.graph, pos, edgelist=[(u, v)],
                                   width=width, edge_color=type_colors[relation.type], ax=self.ax)

        self.ax.set_title(f"Frame: {frame}, Main contradictions: {len(main_contradictions)}")
    
    def animate(self):
        ani = FuncAnimation(self.fig, self.update, interval=500)
        plt.show()



def main():

    system = System()
    
    objects = [Object(f"Obj{i}", importance=random.uniform(1.0, 5.0)) for i in range(1, 11)]
    for obj in objects:
        system.add_object(obj)
  
    for i in range(len(objects)):
        for j in range(len(objects)):
            if i != j:
                intensity = random.uniform(0, 1)
                relation_type = random.choice(list(ContradictionType))
                active = intensity > 0.1  
                relation = Relation(intensity=intensity, type=relation_type, active=active)
                system.add_relation(objects[i], objects[j], relation)
    
 
    engine = DynamicsEngine(system, chaos_coeff=3.7)
    

    visualizer = Visualizer(system, engine)
    visualizer.animate()

if __name__ == "__main__":
    main()
