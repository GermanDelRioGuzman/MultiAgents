from flask import Flask, request, jsonify, g
import json
import traceback
from RobotAgent import ObjectStackingModel, RobotAgent, onto
from ultralytics import YOLO
import numpy as np

app = Flask(__name__)

# Initialize YOLO model
yolo_model = YOLO("yolov8m.pt")
latest_detection = None  # Global variable to store the latest detection

def process_frame(frame):
    global latest_detection
    results = yolo_model(frame, device="mps")
    result = results[0]

    # Use bboxes and classes to identify objects
    bboxes = np.array(result.boxes.xyxy.cpu(), dtype="int")
    classes = np.array(result.boxes.cls.cpu(), dtype="int")

    for cls, bbox in zip(classes, bboxes):
        (x, y, x2, y2) = bbox
        # Calculate center of the bounding box
        center_x = (x + x2) // 2
        center_y = (y + y2) // 2

        # If the object is "in front" of the robot, store detection
        if 300 < center_x < 400 and 200 < center_y < 300:  # Adjust thresholds as needed
            latest_detection = {
                "class": int(cls),
                "center_x": center_x,
                "center_y": center_y,
                "bbox": [int(x), int(y), int(x2), int(y2)]
            }
            break
    else:
        latest_detection = None  # No relevant object detected

@app.route('/get_detection', methods=['GET'])
def get_detection():
    if latest_detection:
        return jsonify(latest_detection)
    else:
        return jsonify({"message": "No object detected"}), 204

def init_model_and_states():
    parameters = {
        'num_objects': 20,
        'grid_size': 10,
    }
    model = ObjectStackingModel(parameters)
    model.setup()
    robot_states = {robot.onto_robot.id: robot.get_state() for robot in model.robots}
    return model, robot_states

@app.before_request
def before_request():
    if not hasattr(app, 'model') or not hasattr(app, 'robot_states'):
        app.model, app.robot_states = init_model_and_states()
    app.logger.debug(f"Current robot states: {app.robot_states}")

@app.route('/gmrs', methods=['POST'])
def robot_action():
    try:
        data = request.json
        
        app.logger.debug(f"Received data: {data}")
        app.logger.debug(f"Ontology classes: {list(onto.classes())}")
        app.logger.debug(f"Ontology individuals: {list(onto.individuals())}")

        if not data or 'id' not in data or 'position' not in data:
            return jsonify({"error": "Invalid input"}), 400

        robot_id = data['id']
        perception = data['position']

        app.logger.debug(f"Current robots in model: {[r.onto_robot.id for r in g.model.robots]}")

        robot = next((r for r in g.model.robots if r.onto_robot.id == robot_id), None)
        if robot is None:
            app.logger.error(f"Robot with id {robot_id} not found.")
            return jsonify({"error": "Robot not found"}), 404

        app.logger.debug(f"Found robot: {robot.onto_robot.id}, Position: {robot.onto_robot.has_position}, Holding: {robot.is_holding_box}")

        perception_json = json.dumps({
            "id": robot_id,
            "position": perception
        })

        app.logger.debug(f"Perception JSON: {perception_json}")

        try:
            action = robot.step(perception_json)
            app.logger.debug(f"Action taken by robot: {action}")
            app.logger.debug(f"Robot state after action: ID: {robot.onto_robot.id}, Holding: {robot.is_holding_box}, Perception: {robot.perception_data}")
            
            # Log the decision-making process
            box_directions = robot.get_box_directions()
            stack_directions = robot.get_stack_directions()
            free_directions = robot.get_free_directions()
            app.logger.debug(f"Boxes found in directions: {box_directions}")
            app.logger.debug(f"Stacks found in directions: {stack_directions}")
            app.logger.debug(f"Free spaces in directions: {free_directions}")
            
        except Exception as e:
            app.logger.error(f"Error in robot.step(): {str(e)}")
            app.logger.error(traceback.format_exc())
            return jsonify({"error": f"Error in robot action: {str(e)}"}), 500

        try:
            g.model.update_environment(robot, action)
        except Exception as e:
            app.logger.error(f"Error in model.update_environment(): {str(e)}")
            app.logger.error(traceback.format_exc())
            return jsonify({"error": f"Error updating environment: {str(e)}"}), 500

        action_parts = action.split('_')
        action_type = action_parts[0]
        direction = action_parts[1] if len(action_parts) > 1 else None

        response = {
            "action": action_type.capitalize()[0],
            "direction": direction
        }

        return jsonify(response)

    except Exception as e:
        app.logger.error(f"An error occurred: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({"error": "An internal server error occurred", "details": str(e)}), 500
    

@app.route('/gmes', methods=['POST'])
def robot_actions():
    try:
        data = request.json
        app.logger.debug(f"Received data: {data}")

        if not isinstance(data, list):
            return jsonify({"error": "Invalid input. Expected an array of robot perceptions."}), 400

        actions = []

        for robot_perception in data:
            if 'id' not in robot_perception or 'position' not in robot_perception:
                return jsonify({"error": "Invalid input. Each robot perception must have 'id' and 'position'."}), 400

            robot_id = robot_perception['id']
            perception = robot_perception['position']

            robot = next((r for r in app.model.robots if r.onto_robot.id == robot_id), None)
            if robot is None:
                app.logger.error(f"Robot with id {robot_id} not found.")
                continue

            stored_state = app.robot_states.get(robot_id)
            app.logger.debug(f"Processing robot: {robot_id}, Stored state: {stored_state}")

            perception_json = json.dumps({
                "id": robot_id,
                "position": perception
            })

            try:
                action = robot.step(perception_json, stored_state)
                app.logger.debug(f"Action taken by robot {robot_id}: {action}")
                
                action_parts = action.split('_')
                action_type = action_parts[0]
                direction = action_parts[1] if len(action_parts) > 1 else None

                actions.append({
                    "id": robot_id,
                    "action": action_type.capitalize()[0],
                    "direction": direction
                })

                app.model.update_environment(robot, action)

                app.robot_states[robot_id] = robot.get_state()
                app.logger.debug(f"Updated state for robot {robot_id}: {app.robot_states[robot_id]}")

            except Exception as e:
                app.logger.error(f"Error in robot.step() for robot {robot_id}: {str(e)}")
                app.logger.error(traceback.format_exc())

        app.model.current_step += 1

        if app.model.check_end_condition():
            app.logger.info("Simulation ended")
            app.model.end()

        app.logger.debug(f"Final robot states after this step: {app.robot_states}")
        return jsonify(actions)

    except Exception as e:
        app.logger.error(f"An error occurred: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({"error": "An internal server error occurred", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
