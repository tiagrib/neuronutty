from nnutty.controllers.character_controller import CharCtrlType, CharacterController, CharacterSettings

class MultiAnimController(CharacterController):
    def __init__(self, nnutty, 
                 ctrls:list,
                 settings:CharacterSettings = None,
                 parent=None):
        super().__init__(nnutty, ctrl_type=CharCtrlType.MULTI, settings=settings, parent=parent)
        assert(len(ctrls) != 0)
        assert(all([isinstance(ctrl, CharacterController) for ctrl in ctrls]))
        
        self.ctrls = ctrls
        self.reposition_subcontrollers()

    def reposition_subcontrollers(self):
        for i, ctrl in enumerate(self.ctrls):
            ctrl.settings.world_offset = [-len(self.ctrls) + 2*i, 0.0, 0.0]

    def reset(self):
        for ctrl in self.ctrls:
            ctrl.reset()

    def advance_time(self, dt, params=None):
        for ctrl in self.ctrls:
            ctrl.advance_time(dt=dt, params=params)

    def compute(self, dt=None, params=None):
        for ctrl in self.ctrls:
            ctrl.compute(dt=dt, params=params)

    def get_pose(self):
        return [ctrl.get_pose() for ctrl in self.ctrls]
    
    def get_color(self):
        return [ctrl.settings.color for ctrl in self.ctrls]
    
    def get_controllers(self):
        return self.ctrls
    
    def get_cur_time(self):
        return self.ctrls[0].cur_time
    
    def get_plot_data(self, index):
        return self.ctrls[index].get_plot_data()