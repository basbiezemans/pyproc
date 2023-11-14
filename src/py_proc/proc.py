from functools import reduce
from inspect import signature

# A Proc object is an encapsulation of callable code, which can be stored in
# a local variable, passed to a function or another Proc, and can be called.
class Proc:

    def __init__(self, callback):
        "Create a new Proc object."
        sig = signature(callback)
        self.callback = callback
        self.parameters = sig.parameters
        self.arity = min_num_args(sig)
        self.is_variadic = is_variadic(sig)

    def curry(self, *args):
        "Return a curried proc."
        if self.is_variadic:
            return VCurriedProc(self.callback, *args)
        else:
            return FCurriedProc(self.callback, *args)

    def call(self, *args):
        """
        Invoke the callback, and return the value of the last expression
        evaluated in the callback."""
        return self.callback(*args)

    def __call__(self, *args):
        "Called when the instance is “called” as a function."
        return self.call(*args)

    def __rshift__(self, proc):
        "Return a proc that is the composition of this proc and the given proc."
        return Proc(lambda *args: proc(self(*args)))

    def __lshift__(self, proc):
        "Return a proc that is the composition of this proc and the given proc."
        return Proc(lambda *args: self(proc(*args)))


# Fixed arity, curried Proc.
class FCurriedProc(Proc):

    def __init__(self, callback, *args):
        super().__init__(callback)
        self.argv = args

    def curry(self, *args):
        return FCurriedProc(self.callback, *self.argv).call(*args)

    def call(self, *args):
        "Return a curried proc or invoke the callback."
        self.argv += args
        if len(self.argv) < self.arity:
            return self
        else:
            return self.callback(*self.argv)


# Variable arity, curried Proc.
class VCurriedProc(Proc):

    def __init__(self, callback, *args):
        super().__init__(callback)
        self.argv = args

    def curry(self, *args):
        return VCurriedProc(self.callback, *(self.argv + args))

    def __call__(self, *args):
        "Return a curried proc with updated arguments."
        self.argv += args
        return self

    def call(self, *args):
        "Invoke the callback and return its result."
        self.argv += args
        return self.callback(*self.argv)


def min_num_args(sig):
    "Return the number of minimal required parameters."
    return reduce(count_required, sig.parameters.values(), 0)

def count_required(tally, param):
    "Increment and return the tally if a parameter is required."
    required = [
        param.POSITIONAL_OR_KEYWORD,
        param.VAR_POSITIONAL,
    ]
    return tally + 1 if param.kind in required else tally

def is_var_positional(param):
    "Return True if the parameter is variable-positional. False otherwise."
    return param.kind == param.VAR_POSITIONAL

def is_variadic(sig):
    "Return True if any positional parameter is variable. False otherwise."
    return any(map(is_var_positional, sig.parameters.values()))
