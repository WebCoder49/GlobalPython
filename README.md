## TODO:
### Working On / Current Bugs
* Importing
```python
"""main.py"""
import turtle as t
t.label = "This is main.py's turtle module instance."
import aux

"""aux.py (in same runtime)"""
import turtle as myturtle
print(myturtle.label) # "This is main.py's turtle module instance."
# Only 1 instance of module in runtime

"""Implementation"""
# Save in globals as .turtle
#   Cannot be accessed
#   Can be imported to location through inheritance
```
### The Queue
* Add support for **more syntaxes and data types**