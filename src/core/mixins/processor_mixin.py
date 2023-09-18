# Python imports
import os, subprocess

# Lib imports

# Application imports



class ProcessorMixin:
    def execute_program(self, exec_ops):
        parts     = exec_ops.split("||")
        try_exec  = parts[0].strip()
        main_exec = parts[1].strip()

        self.pre_execute(try_exec, main_exec)

    def pre_execute(self, try_exec, main_exec):
        try:
            return self.execute(try_exec)
        except Exception as e:
            logger.debug(f"[Executing Program]\n\t\t Try Exec failed!\n{repr(e)}")

        try:
            return self.execute(main_exec)
        except Exception as e:
            logger.debug(f"[Executing Program]\n\t\t Main Exec failed!\n{repr(e)}")


    def execute(self, option):
        DEVNULL = open(os.devnull, 'w')
        command = option.split("%")[0]

        logger.debug(f"Command: {command}")
        subprocess.Popen(command.split(), cwd=os.getenv("HOME"), start_new_session=True, stdout=DEVNULL, stderr=DEVNULL)
