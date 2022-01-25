# Python imports
import os, subprocess

# Lib imports

# Application imports



class ProcessorMixin:
    def execute_program(self, group, entry):
        parts   = entry.split("||")
        program = parts[0].strip()
        comment = parts[1].strip()

        if "Search..." in group or "Favorites" in group:
            group_keys = self.menu_data.keys()
            for group_key in group_keys:
                self.pre_execute(self.menu_data[group_key], program, comment)
        else:
            self.pre_execute(self.menu_data[group], program, comment)


    def pre_execute(self, options, program, comment):
        for opt in options:
            if program in opt["title"]:
                keys = opt.keys()
                if comment in opt["comment"] or comment in opt["fileName"]:
                    try:
                        self.execute(opt["tryExec"])
                    except Exception as e:
                        try:
                            if "exec" in keys and len(opt["exec"]):
                                self.execute(opt["exec"])
                        except Exception as e:
                            self.logger.debug(e)


    def execute(self, option):
        DEVNULL = open(os.devnull, 'w')
        command = option.split("%")[0]
        self.logger.debug(command)
        subprocess.Popen(command.split(), cwd=os.getenv("HOME"), start_new_session=True, stdout=DEVNULL, stderr=DEVNULL)
