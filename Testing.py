def my_decorator(func):

    # Do something before the original function is called
    print("First")
    func()
    print("Last")
    # Do something after the original function is called
    return    


@my_decorator
def my_function():
    # Original function implementation
    print("Middle")


my_function()