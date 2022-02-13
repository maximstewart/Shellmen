# Python imports
import os, subprocess

# Lib imports

# Application imports



class ProcessorMixin:
    def execute_program(self, data, entry):
        parts      = entry.split("||")
        title      = parts[0].strip()
        comment    = parts[1].strip()
        chunk_data = data[title.strip()]

        self.logger.info(f"[Executing Program]\n\t\tEntry: {entry}\n\t\tChunk Data: {chunk_data}")
        self.pre_execute(chunk_data)

    def pre_execute(self, option):
        try:
            self.execute(option["tryExec"])
        except Exception as e:
            self.logger.info(f"[Executing Program]\n\t\t Try exec failed!\n{e}")
            try:
                if option["exec"] and len(option["exec"]) > 0:
                    self.execute(option["exec"])
            except Exception as e:
                self.logger.debug(e)


    def execute(self, option):
        DEVNULL = open(os.devnull, 'w')
        command = option.split("%")[0]
        self.logger.debug(command)
        subprocess.Popen(command.split(), cwd=os.getenv("HOME"), start_new_session=True, stdout=DEVNULL, stderr=DEVNULL)
