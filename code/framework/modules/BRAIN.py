from MP import MP

class BRAIN(MP):
    def run_impl(self):
        if "US1" in self.md:
            if self.md["US1"] < 30:
                # send motor-command
                self.md["Move"] = [50,0] # speed, angle
