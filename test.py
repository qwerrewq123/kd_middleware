class A:
    def __init__(self):
        self.a = self.a()
    def a(self):
        return 1
a = A()
print(a.a)