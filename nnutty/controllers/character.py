from nnutty.controllers.character_controller import CharacterController

class BodyModel():
    def __init__(self, name: str):
        self.name = name

class Character():
    def __init__(self, body_model: BodyModel, controller: CharacterController):
        self.controller = controller
        self.body_model = body_model

    def reset(self):
        self.controller.reset()

    def advance_time(self, dt, params={}):
        self.controller.advance_time(dt, params)

    def get_pose(self):
        return self.controller.get_pose()

    def get_color(self):
        return self.controller.get_color()