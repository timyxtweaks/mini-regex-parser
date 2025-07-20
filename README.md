This is a little project I made to build my own regex parser — without using Python’s built-in `re` module.  
Everything is done from scratch, step by step, just how it should work.

The goal was to handle the basics: characters, dot, star, plus, question mark, or (|), and grouping with parentheses. Nothing fancy, but enough to check if a string matches a given pattern.

The code is clean and simple, with comments written plainly, so anyone curious can follow along.

---

## How to use it?

Just call the function `da_li_odgovara(regex, text)` with your regex and text, and it will return `True` if they match, or `False` if not.

Examples:

```python
da_li_odgovara("a+", "aaa")      # returns True  
da_li_odgovara("a|b", "b")       # returns True  
da_li_odgovara("(ab)+", "abab")  # returns True  
da_li_odgovara(".", "x")         # returns True  
da_li_odgovara("a?", "")         # returns True  
Why did I make this?
Because I wanted to understand how regex works inside out, and I like messing with algorithms.
Once you see all that needs to happen behind the scenes, you appreciate built-in libraries even more.

Final words
If you’re interested in regex or just programming, take a look.
It’s not meant for heavy production use, but it’s great for learning and understanding the basics.