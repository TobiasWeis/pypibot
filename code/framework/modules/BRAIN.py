from MP import MP
import time

class BRAIN(MP):
    def init(self):
        self.issued_fwd = False
        self.issued_left = False
        self.issued_right = False
        self.issued_bwd = False

    def run_impl(self):
        # FIXME: just to test the motor module
        if not self.issued_fwd:
            self.issued_fwd = True
            self.md["Move"] = [50, "forward"]
        elif not self.issued_left:
            self.issued_left = True
            self.md["Move"] = [50, "left"]
        elif not self.issued_right:
            self.issued_right = True
            self.md["Move"] = [50, "right"]
        elif not self.issued_bwd:
            self.issued_bwd = True
            self.md["Move"] = [50, "backward"]
        time.sleep(2)

        if "US1" in self.md:
            if self.md["US1"] < 30:
                # send motor-command
                self.md["Move"] = [50,0] # speed, angle
