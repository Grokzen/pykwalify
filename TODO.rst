 - It should be possible to support more then one object type in the same object. This should enable the user to check if a variable is a dict or a string and have different rules validating them both depending on the provided data.

 - Enums must have the ability to pick if it should be case sensetive or not.

 - Fix support for all NYI types

 - Test to implement lambda support in lib mode

 - Try to remove the requirement to have a list when defining a sequence: value. If pykwalify should support multiple types at the same time this might get removed because then it can just be implemented to support more then 1 type of sequence validation.