from MP import MP

class BRAIN(MP):
    def run_impl(self):
        if len(self.md["Objects"]) > 0:
            if self.md["Objects"][0] == "Ball":
                print "BRAIN: We have seen a ball!"
                self.md["Objects"] = [] # clear object-queue again

                # send motor-command
                self.md["Move"] = [50,0] # speed, angle
