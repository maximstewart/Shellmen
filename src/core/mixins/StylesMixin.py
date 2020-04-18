# Python imports

# Lib imports
from PyInquirer import style_from_dict, Token

# Application imports



class StylesMixin:
    """
        The StylesMixin has style methods that get called and
        return their respective objects.
    """

    def default(self):
        return style_from_dict({
            Token.Separator: '#6C6C6C',
            Token.QuestionMark: '#FF9D00 bold',
            # Token.Selected: '',  # default
            Token.Selected: '#5F819D',
            Token.Pointer: '#FF9D00 bold',
            Token.Instruction: '',  # default
            Token.Answer: '#5F819D bold',
            Token.Question: '',
        })

    def orange(self):
        return style_from_dict({
            Token.Pointer: '#6C6C6C bold',
            Token.QuestionMark: '#FF9D00 bold',
            Token.Separator: '#FF9D00',
            Token.Selected: '#FF9D00',
            Token.Instruction: '',  # default
            Token.Answer: '#FF9D00 bold',
            Token.Question: '', # default
        })

    def red(self):
        return style_from_dict({
            Token.Pointer: '#c70e0e bold',
            Token.QuestionMark: '#c70e0e bold',
            Token.Separator: '#c70e0e',
            Token.Selected: '#c70e0e',
            Token.Instruction: '',  # default
            Token.Answer: '#c70e0e bold',
            Token.Question: '', # default
        })

    def purple(self):
        return style_from_dict({
            Token.Pointer: '#673ab7 bold',
            Token.QuestionMark: '#673ab7 bold',
            Token.Selected: '#673ab7',
            Token.Separator: '#673ab7',
            Token.Instruction: '',  # default
            Token.Answer: '#673ab7 bold',
            Token.Question: '', # default
        })

    def green(self):
        return style_from_dict({
            Token.Pointer: '#ffde00 bold',
            Token.QuestionMark: '#29a116 bold',
            Token.Selected: '#29a116',
            Token.Separator: '#29a116',
            Token.Instruction: '',  # default
            Token.Answer: '#29a116 bold',
            Token.Question: '',   # default
        })
