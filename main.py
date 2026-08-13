#!/usr/bin/env python3


from parser import Parser
from error import ParserError


if __name__ == "__main__":
    p = Parser()
    try:
        p.parse("config.txt")
    except ParserError as e:
        print(f"Error: {e}")
    print("Success!")
