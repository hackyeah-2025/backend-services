from fastapi import FastAPI

app = FastAPI()

# # Example class
# class Calculator:
#     def add(self, a: int, b: int) -> int:
#         return a + b
    
#     def multiply(self, a: int, b: int) -> int:
#         return a * b

# calc = Calculator()

# @app.get("/add")
# def add_numbers(a: int, b: int):
#     result = calc.add(a, b)
#     return {"operation": "addition", "a": a, "b": b, "result": result}

# @app.get("/multiply")
# def multiply_numbers(a: int, b: int):
#     result = calc.multiply(a, b)
#     return {"operation": "multiplication", "a": a, "b": b, "result": result}


@app.get("/")
# 3. Define the path operation function
async def read_root():
    return {"message": "Hello World"}