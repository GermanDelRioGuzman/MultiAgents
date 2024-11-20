# MultiAgents
This project focuses on the design and implementation of a multi-agent robotic system aimed at organizing a warehouse. The entire setup will be visualized in a 3D environment utilizing computer graphics, while object recognition will be powered by computer vision technologies.

## Part 1: Multiagent Systems
In this part, you are tasked with programming five robots to organize a disordered warehouse filled with objects. The robots can move in any direction, pick up and stack objects, and detect their surroundings using sensors. The main goal is to sort all items into groups of a maximum of five objects. Key elements of the simulation include initializing starting positions, tracking the time taken for sorting, and the number of movements made by each robot while exploring strategies for efficiency in their operations.


## Part 2: Computer Graphics
This phase involves creating a 3D representation of the warehouse and the robots. You need to model various components, such as shelves, objects, and robots, applying materials and textures. The animation component requires implementing robot movement across the warehouse and ensuring collision detection. Lighting elements, including directional and point lights on each robot, must also be incorporated.


## Part 3: Computer Vision
In the final part, the focus is on using computer vision to identify objects being manipulated by the robots. Each robot, equipped with a camera, will send visual data to a vision model, possibly utilizing frameworks like YOLO or SAM. When a robot interacts with an object, it should convey the identification of the object through a visual signal, enhancing the robots' operational context.


Overall, the project emphasizes the integration of multiagent systems, computer graphics, and computer vision to create an efficient warehouse organization solution.
